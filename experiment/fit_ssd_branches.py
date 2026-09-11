#!/usr/bin/env python
"""DEPRECATED historical MLX comparison fitter.

Active training uses ``experiment/fit_ssd_branches_torch.py`` with the
Torch + Lightning stack. This module remains importable for parent-run
manual-mlx comparison rows.

experiment/fit_ssd_branches.py — 固定 B_ss 下 R 分支半可分离拟合器（spec §5）。

参数化（§5.1）：M̂_ij = Σ_ρ w_ρ exp(Φ_ρ(i)−Φ_ρ(j)) ⟨Q_ρi, K_ρj⟩，j<i；对角与上三角恒 0（diag_mode=zero）。
数值有界（§5.1 实现选择，记录于 provenance）：每分支减去标量 Amax_ρ = max_i Φ − min_j Φ，
以 exp(A−Amax) ≤ 1 计算，等效权重 w_ρ·exp(Amax_ρ) 可微分地进入计算图；这是重参数化，不改变可表达集合。
优化（§5.6）：Adam(0.9, 0.999, 1e-8)，全批量，逐组学习率 + 余弦退火到 1e-4，
步数上限默认 600，连续 20 步相对下降 <1e-5 早停，全局梯度 norm 裁剪 1.0，mlx float32（Metal）。
warm-start（§5.5）：R=2k 的前 k 分支继承 R=k 解（列取前一半、g 复制、w 折半），其余新随机。

fit_one(...) 供 evaluation/attn_spectral_probe.py 以库形式调用；也可 CLI 单跑一个探针。
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

DEFAULTS = {
    "B_ss": 32, "steps": 600, "lr": {"QK": 3e-2, "g": 1e-2, "w": 1e-3},
    "lr_min": 1e-4, "betas": (0.9, 0.999), "adam_eps": 1e-8,
    "clip": 1.0, "early_window": 20, "early_rel_tol": 1e-5, "seed": 20260908,
}


def derive_seed(probe_id: str, R: int, chain_mode: str, base_seed: int,
                init="orthogonal_small", optimizer="adam_coordinate", steps=600) -> int:
    h = hashlib.sha256(f"{probe_id}|{R}|{chain_mode}|{init}|{optimizer}|{steps}".encode()).digest()
    return (int.from_bytes(h[:8], "big") % (2 ** 31)) + base_seed


def dof_count(L: int, R: int, N: int, chain: str = "per") -> int:
    """derivation.md §5.2 公式：Σ_ρ (2LN_ρ − N_ρ²) + 链参数。"""
    chain_params = (L - 1) * (R if chain == "per" else 1)
    return R * (2 * L * N - N * N) + chain_params


# ---------------------------------------------------------------- mlx 拟合

def fit_one(M_target, R, N, seed, *, steps=600, chain="per", warm=None,
            diag_mode="zero", lr=None, lr_min=1e-4, clip=1.0,
            early_window=20, early_rel_tol=1e-5, init="orthogonal_small",
            optimizer="adam_coordinate", scale_factor=None):
    """拟合单个探针。M_target: (L,L) float32 numpy（严格下三角区外的值被忽略）。

    返回 dict(Q,K,g,w,steps,converged,loss_elem,grad_norm,dof,wall_s,seed)。
    warm: 上一档 R/2 的解（同形状键）；None 表示随机初始化。
    """
    import mlx.core as mx

    M = mx.array(np.ascontiguousarray(M_target, dtype=np.float32))
    L = M.shape[0]
    key = mx.random.key(seed % (2 ** 32 - 1))
    kq, key = mx.random.split(key)
    Q0 = _init_factors(mx, R, L, N, kq, warm, "Q", init=init, scale_factor=scale_factor)
    K0 = _init_factors(mx, R, L, N, key, warm, "K", init=init, scale_factor=scale_factor)
    if chain == "per":
        g0 = np.zeros((R, L - 1), dtype=np.float32)
        if warm is not None:
            wg = warm["g"]
            wg = wg if wg.ndim == 2 else wg[None]
            for rho in range(min(R, wg.shape[0])):
                g0[rho] = wg[rho]
    else:
        g0 = np.zeros((L - 1,), dtype=np.float32)
        if warm is not None and warm["g"].ndim == 2:
            g0 = warm["g"][0].astype(np.float32).copy()
    w0 = np.full((R,), 1.0 / R, dtype=np.float32)
    if warm is not None:
        wo = np.asarray(warm["w"], dtype=np.float32).ravel()
        for rho in range(min(R, wo.shape[0])):
            w0[rho] = wo[rho] / 2.0

    mask = mx.array(np.tril(np.ones((L, L), dtype=np.float32), k=-1))
    params = {"Q": mx.array(Q0), "K": mx.array(K0), "g": mx.array(g0), "w": mx.array(w0)}

    lrs = lr or DEFAULTS["lr"]
    group_lr = {"Q": lrs["QK"], "K": lrs["QK"], "g": lrs["g"], "w": lrs["w"]}
    m = {k: mx.zeros_like(v) for k, v in params.items()}
    v = {k: mx.zeros_like(v) for k, v in params.items()}
    if optimizer not in ("adam_coordinate", "gauge_equivariant_shared_scalar"):
        raise ValueError(f"unknown optimizer: {optimizer}")
    global_v = mx.array(0.0)
    b1, b2 = DEFAULTS["betas"]
    aeps = DEFAULTS["adam_eps"]

    def loss_fn(p):
        return _loss(p, M, mask, chain)

    grad_fn = mx.grad(loss_fn)
    prev = float(loss_fn(params))
    losses, t0 = [prev], time.time()
    small = 0
    converged = False
    gnorm = 0.0
    for t in range(steps):
        grads = grad_fn(params)
        gs = {k: grads[k] for k in params}
        gn = math_sqrt(mx, sum(mx.sum(g * g) for g in gs.values()))
        gnorm = float(gn)
        scale = min(1.0, float(clip) / (gnorm + 1e-12))
        frac = t / max(steps - 1, 1)
        if optimizer == "gauge_equivariant_shared_scalar":
            flat = mx.concatenate([mx.reshape(gs[k], (-1,)) for k in params])
            global_v = b2 * global_v + (1 - b2) * mx.mean(flat * flat)
            vh_global = global_v / (1 - b2 ** (t + 1))
        for k in params:
            g = gs[k] * scale
            m[k] = b1 * m[k] + (1 - b1) * g
            if optimizer == "gauge_equivariant_shared_scalar":
                vh = vh_global
            else:
                v[k] = b2 * v[k] + (1 - b2) * g * g
                vh = v[k] / (1 - b2 ** (t + 1))
            mh = m[k] / (1 - b1 ** (t + 1))
            lr_t = lr_min + (group_lr[k] - lr_min) * 0.5 * (1 + np.cos(np.pi * frac))
            params[k] = params[k] - lr_t * mh / (mx.sqrt(vh) + aeps)
        cur = float(loss_fn(params))
        losses.append(cur)
        rel = (prev - cur) / max(prev, 1e-30)
        small = small + 1 if rel < early_rel_tol else 0
        prev = cur
        if small >= early_window:
            converged = True
            break
    mx.eval(*params.values())
    out = {
        "Q": np.asarray(params["Q"], dtype=np.float32),
        "K": np.asarray(params["K"], dtype=np.float32),
        "g": np.asarray(params["g"], dtype=np.float32),
        "w": np.asarray(params["w"], dtype=np.float32),
        "steps": len(losses) - 1, "converged": bool(converged),
        "loss_elem": float(losses[-1]), "grad_norm": float(gnorm),
        "dof": dof_count(L, R, N, chain), "wall_s": round(time.time() - t0, 2),
        "seed": int(seed), "final_losses": [losses[0], losses[-1]],
    }
    return out


def math_sqrt(mx, x):
    return mx.sqrt(x)


def _init_factors(mx, R, L, N, key, warm, which, init="orthogonal_small", scale_factor=None):
    """高斯 scale N^{-1/2} → 逐分支 QR 正交化（§5.1）；warm 时前一半分支继承旧解列前 N 维。"""
    scale = float(scale_factor if scale_factor is not None else (4.0 if init == "balanced_large" else 1.0))
    G = np.asarray(mx.random.normal((R, L, N), key=key)) * scale / np.sqrt(N)
    out = np.empty((R, L, N), dtype=np.float32)
    for rho in range(R):
        q, _ = np.linalg.qr(G[rho])            # numpy QR（Metal 不支持 qr 在默认 GPU stream）
        out[rho] = q
    if warm is not None:
        wo = warm[which]          # (R_old, L, N_old)
        for rho in range(min(R, wo.shape[0])):
            out[rho] = wo[rho][:, :N]
    return out


def _loss(p, M, mask, chain):
    import mlx.core as mx
    Q, K, g, w = p["Q"], p["K"], p["g"], p["w"]
    R = Q.shape[0]
    if chain == "per":
        phi = mx.concatenate([mx.zeros((R, 1)), mx.cumsum(g, axis=1)], axis=1)     # (R,L)
    else:
        phi1 = mx.concatenate([mx.zeros((1,)), mx.cumsum(g)])                      # (L,)
        phi = mx.repeat(phi1[None], R, axis=0)
    A = phi[:, :, None] - phi[:, None, :]                                           # (R,L,L)
    Amax = mx.clip(A.max(axis=(1, 2), keepdims=True), 0.0, 60.0)  # 重参数化位移（可微，梯度自洽抵消）
    decay = mx.exp(A - Amax)                                                        # ≤1
    inner = mx.einsum("rin,rjn->rij", Q, K)
    eff_w = (w * mx.exp(Amax[:, 0, 0]))[:, None, None]
    Mhat = (eff_w * decay * inner * mask[None]).sum(0)
    E = (Mhat - M) * mask
    return mx.sum(E * E)


# ---------------------------------------------------------------- float64 重建（评测器口径）

def rebuild_mhat(Q, K, g, w, chain, L):
    """§5.1 公式的 numpy float64 重建（带同样的 Amax 位移，纯数值稳定）。"""
    R = Q.shape[0]
    Q, K = Q.astype(np.float64), K.astype(np.float64)
    g = g.astype(np.float64)
    if chain == "per":
        phi = np.concatenate([np.zeros((R, 1)), np.cumsum(g, axis=1)], axis=1)
    else:
        phi1 = np.concatenate([[0.0], np.cumsum(g)])
        phi = np.repeat(phi1[None], R, axis=0)
    A = phi[:, :, None] - phi[:, None, :]
    Amax = np.clip(A.max(axis=(1, 2), keepdims=True), 0.0, 60.0)
    decay = np.exp(A - Amax)
    inner = np.einsum("rin,rjn->rij", Q, K)
    eff_w = (w.astype(np.float64) * np.exp(Amax[:, 0, 0]))[:, None, None]
    mask = np.tril(np.ones((L, L)), k=-1)
    return (eff_w * decay * inner * mask[None]).sum(0)


# ---------------------------------------------------------------- CLI（单探针，供校准）

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-file", required=True)
    ap.add_argument("--probe-id", required=True)
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--B-ss", type=int, default=DEFAULTS["B_ss"])
    ap.add_argument("--chain", default="per", choices=["per", "shared"])
    ap.add_argument("--seed", type=int, default=DEFAULTS["seed"])
    ap.add_argument("--optimizer", default="adam_coordinate")
    ap.add_argument("--init", default="orthogonal_small")
    ap.add_argument("--out", required=True, help=".npz 输出路径")
    ap.add_argument("--steps", type=int, default=600)
    args = ap.parse_args()

    M = np.load(args.probe_file)
    N = args.B_ss // args.R
    seed = derive_seed(args.probe_id, args.R, args.chain, args.seed,
                       args.init, args.optimizer, args.steps)
    res = fit_one(M, args.R, N, seed, steps=args.steps, chain=args.chain,
                  init=args.init, optimizer=args.optimizer)
    np.savez(args.out, **{k: np.asarray(v) for k, v in res.items()})
    print(json.dumps({k: res[k] for k in ("steps", "converged", "loss_elem", "wall_s", "dof")}))


if __name__ == "__main__":
    main()
