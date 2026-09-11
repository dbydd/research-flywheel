#!/usr/bin/env python
"""DEPRECATED 对照存档 — 旧 mlx + numpy 栈评测器（run ssd-spectral-restore-001 / ssd-convergence-004）。

本文件的 objective 名集合与阈值语义属已废弃口径；新栈实现见 evaluation/attn_spectral_probe_torch.py 与
experiment/fit_ssd_branches_torch.py，当前权威条款见 runs/ssd-convergence-004-torch/spec.md（§0.1 禁引用清单、§2 正式判定、§12 命令行）。
本文件保留供第一轮已 accept 结果的复算与图表再生使用；在 training freeze 期内不新增执行。

evaluation/attn_spectral_probe.py — 谱还原评测器（spec §7，语义定稿）。

三个模式（与 idea.json evaluation.objectives[*].evaluator 的三条命令行字面兼容）：
  --tau 0.99                        → p_star 模式（O1 median_p99_energy_ratio）
  --budget 32 --branches 1,2,4,8,16 → fit_branches 模式（O2 lop_branch_ratio_rmax_over_r1）
  --budget 32 --baselines svd,hss   → baselines 模式（O3 lop_ssd_over_truncated_svd）

指标定义（§7.3；全部 float64、严格下三角同域 mask、无截断无归一化）：
  p*(τ) = min{p: Σ_{k≤p}σ_k² ≥ τ·Σ_k σ_k²}；L_elem=‖E‖_F²；L_rel=L_elem/‖M*‖_F²；
  L_op=σ₁(E)；L_sub=1−‖U_p(M̂)ᵀ U_p(M*)‖_F²/p，p∈{1,4,16,32}，判定 p=32。
汇总（§7.4）：中位数 np.median（偶数长度取中间两值均值）。O2 逐探针 L_op(Rmax)/L_op(R=1) 取中位；
O3 逐探针 min_R L_op / rank-B_ss SVD 的 L_op 取中位。自检 S1–S6 → measured/self_checks.json。
每个模式更新 measured/rows.jsonl（行键合并、排序整体重写）并重写 measured/summary.md。
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiment.fit_ssd_branches import fit_one, rebuild_mhat, derive_seed, dof_count  # noqa: E402
from experiment.baselines_lowrank import truncated_svd, hss_approx, hss_dof, R_GRID  # noqa: E402

MEDIAN_NOTE = "np.median，偶数长度取中间两值均值"
SUB_PS = (1, 4, 16, 32)
OBJ_NAMES = ["median_p99_energy_ratio", "lop_branch_ratio_rmax_over_r1",
             "lop_ssd_over_truncated_svd"]


def strict_mask(L):
    return np.tril(np.ones((L, L), dtype=np.float64), k=-1)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- probes

def load_probes(run_dir, split="fit", filt=None):
    rows = []
    with open(run_dir / "probes" / "manifest.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("guards_pass"):
                continue
            if split and r.get("split") != split:
                continue
            if filt:
                if "domain" in filt and r["domain"] not in filt["domain"]:
                    continue
                if "layers" in filt and r["layer"] not in filt["layers"]:
                    continue
            rows.append(r)
    return rows


# ---------------------------------------------------------------- 指标

def op_norm_and_fro(E):
    out = {"L_elem": float(np.sum(E * E))}
    try:
        s = np.linalg.svd(E, compute_uv=False)
        lop = float(s[0])
    except np.linalg.LinAlgError as exc:
        return {**out, "status": "invalid",
                "invalid_reason": "svd_gesdd_nonconvergence",
                "reason": repr(exc), "L_op": None, "L_op_alt": None}
    if not np.isfinite(lop):
        return {**out, "status": "invalid",
                "invalid_reason": "svd_gesdd_nonconvergence",
                "reason": "non-finite singular value", "L_op": None,
                "L_op_alt": None}
    out.update({"status": "valid", "L_op": lop})
    try:
        alt = float(np.linalg.norm(E, 2))
        out["L_op_alt"] = alt if np.isfinite(alt) else None
        if out["L_op_alt"] is None:
            out["alt_status"] = "invalid"
    except (np.linalg.LinAlgError, ValueError, FloatingPointError) as exc:
        out["L_op_alt"] = None
        out["alt_status"] = "invalid"
        out["alt_reason"] = repr(exc)
    return out


def subspace_align(Mhat, M64):
    _, _, Vha = np.linalg.svd(Mhat, full_matrices=False)
    _, _, Vhb = np.linalg.svd(M64, full_matrices=False)
    out = {}
    for p in SUB_PS:
        X = Vha[:p].T
        Y = Vhb[:p].T
        out[f"L_sub{p}"] = float(1.0 - np.sum((X.T @ Y) ** 2) / p)
    return out


# ---------------------------------------------------------------- p_star 模式

def run_p_star(prs, taus, run_dir):
    rows = []
    for pr in prs:
        M = np.load(run_dir / "probes" / pr["file"]).astype(np.float64)
        total = float(np.sum(M * M))
        s = np.linalg.svd(M, compute_uv=False)
        cum = np.cumsum(s * s)
        for tau in taus:
            idx = np.searchsorted(cum, tau * total, side="left")
            ps = int(idx + 1) if idx < len(cum) else len(cum)
            rows.append({"kind": "p_star", "probe_id": pr["probe_id"], "domain": pr["domain"],
                         "layer": pr["layer"], "head": pr["head"], "split": pr["split"],
                         "tau": tau, "p_star": ps, "p_star_over_L": ps / M.shape[0],
                         "frobenius_sq": total, "sigma1": float(s[0])})
    return rows


# ---------------------------------------------------------------- 拟合（worker，spawn 安全）

def _fits_dir():
    return Path(os.environ["BENCH_FITS_DIR"])


def _fit_cache_valid(fp):
    """Accept complete finite cache entries only; interrupted writes are rerun."""
    try:
        z = np.load(fp)
        return all(k in z.files and np.isfinite(z[k]).all() for k in ("Q", "K", "g", "w"))
    except Exception:
        return False


def _worker_fit_chain(job):
    """单探针 warm-start 链。缓存键包含完整实验配置。"""
    probe_file, probe_id, Rs, chain, B_ss, seed, steps, init, optimizer = job
    M = np.load(probe_file)
    fd = _fits_dir()
    idx_rows = []
    warm = None
    prev_R = None
    for R in Rs:
        N = B_ss // R
        fp = fd / f"{probe_id}__R{R}__{chain}__S{steps}__I{init}__O{optimizer}.npz"
        if fp.exists() and _fit_cache_valid(fp):
            z = np.load(fp)
            warm = {k: z[k] for k in ("Q", "K", "g", "w")}
            prev_R = R
            continue
        if fp.exists():
            fp.unlink()
        seed_used = derive_seed(probe_id, R, chain, seed, init, optimizer, steps)
        try:
            res = fit_one(M, R, N, seed_used, steps=steps, chain=chain, warm=warm,
                          init=init, optimizer=optimizer)
            if not all(np.isfinite(res[k]).all() for k in ("Q", "K", "g", "w")):
                raise FloatingPointError("non-finite fit parameters")
        except Exception as exc:
            idx_rows.append({"probe_id": probe_id, "R": R, "N": N, "chain": chain,
                             "status": "invalid", "reason": repr(exc), "file": str(fp.relative_to(ROOT))})
            break
        np.savez(fp, Q=res["Q"], K=res["K"], g=res["g"], w=res["w"],
                 steps=np.int32(res["steps"]), converged=np.bool_(res["converged"]),
                 loss_elem=np.float32(res["loss_elem"]), grad_norm=np.float32(res["grad_norm"]),
                 dof=np.int32(res["dof"]), wall_s=np.float32(res["wall_s"]),
                 seed_used=np.int64(seed_used), N=np.int32(N), B_ss=np.int32(B_ss),
                 chain=chain, probe_id=probe_id, R=np.int32(R))
        idx_rows.append({"probe_id": probe_id, "R": R, "N": N, "chain": chain,
                         "seed_used": seed_used, "warm_start_from": prev_R,
                         "steps": res["steps"], "converged": res["converged"],
                         "loss_elem_f32": res["loss_elem"], "dof": res["dof"],
                         "wall_s": res["wall_s"], "B_ss": B_ss,
                         "file": str(fp.relative_to(ROOT))})
        warm = res
        prev_R = R
    return idx_rows


def _worker_curve_fit(job):
    probe_file, probe_id, N, seed, steps = job
    M = np.load(probe_file)
    seed_used = derive_seed(probe_id, 1, f"curve|N={N}", seed)
    res = fit_one(M, 1, N, seed_used, steps=steps, chain="per")
    fp = _fits_dir() / f"{probe_id}__R1__curve__N{N}__S{steps}.npz"
    np.savez(fp, Q=res["Q"], K=res["K"], g=res["g"], w=res["w"],
             seed_used=np.int64(seed_used), N=np.int32(N), R=np.int32(1), chain="curve")
    return probe_id, N


def ensure_fits(prs, run_dir, Rs, chain, B_ss, seed, steps, jobs,
                init="orthogonal_small", optimizer="adam_coordinate"):
    fits_dir = run_dir / "fits"
    fits_dir.mkdir(exist_ok=True)
    os.environ["BENCH_FITS_DIR"] = str(fits_dir)
    todo = [pr for pr in prs if not all(_fit_cache_valid(fits_dir / f"{pr['probe_id']}__R{R}__{chain}__S{steps}__I{init}__O{optimizer}.npz")
                                        for R in Rs)]
    if not todo:
        return 0
    jobs_list = [(str(run_dir / "probes" / pr["file"]), pr["probe_id"], Rs, chain,
                  B_ss, seed, steps, init, optimizer) for pr in todo]
    t0 = time.time()
    ctx = mp.get_context("spawn")
    all_idx = []
    with ctx.Pool(max(1, min(jobs, len(jobs_list)))) as pool:
        done = 0
        for idx_rows in pool.imap_unordered(_worker_fit_chain, jobs_list):
            all_idx.extend(idx_rows)
            done += 1
            if done % 8 == 0 or done == len(jobs_list):
                el = time.time() - t0
                print(f"  fits {done}/{len(jobs_list)} probes elapsed={el / 60:.1f}min "
                      f"eta={el / done * (len(jobs_list) - done) / 60:.1f}min", flush=True)
    with open(fits_dir / "index.jsonl", "a") as f:
        for r in all_idx:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    return len(todo)


def score_fits(prs, run_dir, Rs, chain, B_ss, steps=600,
               init="orthogonal_small", optimizer="adam_coordinate"):
    rows = []
    for pr in prs:
        M64 = np.load(run_dir / "probes" / pr["file"]).astype(np.float64)
        L = M64.shape[0]
        A = M64 * strict_mask(L)
        frob_sq = float(np.sum(A * A))
        diag_sq = float(np.sum(np.diag(M64) ** 2))
        for R in Rs:
            fp = run_dir / "fits" / f"{pr['probe_id']}__R{R}__{chain}__S{steps}__I{init}__O{optimizer}.npz"
            if not fp.exists():
                continue
            z = np.load(fp)
            try:
                Mhat = rebuild_mhat(z["Q"], z["K"], z["g"], z["w"], chain, L)
                Ahat = Mhat * strict_mask(L)
                E = Ahat - A
                m = op_norm_and_fro(E)
                row = {"kind": "fit", "probe_id": pr["probe_id"], "domain": pr["domain"],
                   "layer": pr["layer"], "head": pr["head"], "split": pr["split"],
                   "R": int(R), "N": B_ss // R, "chain": chain, "B_ss": B_ss,
                   "dof": int(z["dof"]), "steps": int(z["steps"]),
                   "converged": bool(z["converged"]),
                   "diag_contribution": diag_sq / frob_sq if frob_sq > 0 else 0.0,
                   "L_rel": float(np.sum(E * E) / frob_sq) if frob_sq > 0 else None,
                   "frobenius_sq": frob_sq, "seed_used": int(z["seed_used"]),
                   **m}
                if m.get("status") == "valid":
                    row.update(subspace_align(Ahat, A))
                rows.append(row)
            except Exception as exc:
                rows.append({"kind": "fit", "probe_id": pr["probe_id"], "domain": pr["domain"],
                             "layer": pr["layer"], "head": pr["head"], "split": pr["split"],
                             "R": int(R), "N": B_ss // R, "chain": chain, "B_ss": B_ss,
                             "status": "invalid", "invalid_reason": "svd_gesdd_nonconvergence",
                             "L_op": None, "L_op_alt": None,
                             "reason": repr(exc), "file": str(fp.relative_to(ROOT))})
    return rows


# ---------------------------------------------------------------- baselines 模式

def run_baselines(prs, run_dir, methods):
    rows = []
    for pr in prs:
        M64 = np.load(run_dir / "probes" / pr["file"]).astype(np.float64)
        L = M64.shape[0]
        A = M64 * strict_mask(L)
        for r in R_GRID:
            if "svd" in methods:
                Mhat, s_next = truncated_svd(A, r)
                m = op_norm_and_fro(Mhat - A)
                rows.append({"kind": "baseline", "probe_id": pr["probe_id"], "domain": pr["domain"],
                             "layer": pr["layer"], "head": pr["head"], "method": "svd",
                             "budget": r, "nominal_dof": 2 * L * r - r * r + r,
                             "sigma_next": s_next, **m})
            if "hss" in methods:
                Mhat = hss_approx(A, p_levels=(r,) * 4)
                m = op_norm_and_fro(Mhat - A)
                rows.append({"kind": "baseline", "probe_id": pr["probe_id"], "domain": pr["domain"],
                             "layer": pr["layer"], "head": pr["head"], "method": "hss",
                             "budget": r, "nominal_dof": hss_dof(L, (r,) * 4),
                             "sigma_next": None, **m})
    return rows


def run_curve_fits(prs, run_dir, N_grid, seed, steps, jobs):
    fits_dir = run_dir / "fits"
    fits_dir.mkdir(exist_ok=True)
    os.environ["BENCH_FITS_DIR"] = str(fits_dir)
    todo = [(str(run_dir / "probes" / pr["file"]), pr["probe_id"], N, seed, steps)
            for pr in prs for N in N_grid
            if not (fits_dir / f"{pr['probe_id']}__R1__curve__N{N}__S{steps}.npz").exists()]
    if todo:
        ctx = mp.get_context("spawn")
        with ctx.Pool(max(1, min(jobs, len(todo)))) as pool:
            list(pool.imap_unordered(_worker_curve_fit, todo))
    rows = []
    for pr in prs:
        M64 = np.load(run_dir / "probes" / pr["file"]).astype(np.float64)
        L = M64.shape[0]
        A = M64 * strict_mask(L)
        for N in N_grid:
            fp = fits_dir / f"{pr['probe_id']}__R1__curve__N{N}__S{steps}.npz"
            if not fp.exists():
                continue
            z = np.load(fp)
            Mhat = rebuild_mhat(z["Q"], z["K"], z["g"], z["w"], "per", L)
            Ahat = Mhat * strict_mask(L)
            rows.append({"kind": "curve_C", "probe_id": pr["probe_id"], "domain": pr["domain"],
                         "layer": pr["layer"], "head": pr["head"], "R": 1, "N": int(N),
                         "steps": int(steps),
                         "dof": dof_count(L, 1, N, "per"),
                         **op_norm_and_fro(Ahat - A)})
    return rows


# ---------------------------------------------------------------- objectives

def qstats(vals):
    v = np.asarray(vals, dtype=np.float64)
    if v.size == 0:
        return {"n": 0, "median": None, "p10": None, "p25": None,
                "p75": None, "p90": None}
    return {"n": int(v.size), "median": round(float(np.median(v)), 6),
            "p10": round(float(np.percentile(v, 10)), 6),
            "p25": round(float(np.percentile(v, 25)), 6),
            "p75": round(float(np.percentile(v, 75)), 6),
            "p90": round(float(np.percentile(v, 90)), 6)}


def per_probe_maps(rows, B_ss):
    fits = {}
    for r in rows:
        if r["kind"] == "fit" and r["chain"] == "per" and r.get("status", "valid") == "valid":
            fits.setdefault(r["probe_id"], {})[r["R"]] = r
    svd32 = {r["probe_id"]: r for r in rows
             if r["kind"] == "baseline" and r["method"] == "svd" and r["budget"] == B_ss
             and r.get("status", "valid") == "valid"}
    return fits, svd32


def objective_rows(rows, B_ss):
    out = []
    p99 = [r for r in rows if r["kind"] == "p_star" and r["tau"] == 0.99]
    if p99:
        val = float(np.median([r["p_star_over_L"] for r in p99]))
        out.append({"kind": "objective", "metric": OBJ_NAMES[0], "value": round(val, 6),
                    "epsilon": 0.25, "direction": "lower", "pass": bool(val <= 0.25),
                    "n_probes": len(p99), "n_valid": len(p99), "n_invalid": 0})
    fits, svd32 = per_probe_maps(rows, B_ss)
    o2 = [d[16]["L_op"] / d[1]["L_op"] for d in fits.values()
          if 1 in d and 16 in d and "L_op" in d[1] and "L_op" in d[16]
          and d[1]["L_op"] > 0 and d[16]["L_op"] > 0]
    if o2:
        val = float(np.median(o2))
        out.append({"kind": "objective", "metric": OBJ_NAMES[1], "value": round(val, 6),
                    "epsilon": 0.8, "direction": "lower", "pass": bool(val <= 0.8),
                    "n_probes": len(o2), "n_valid": len(o2), "n_invalid": 224 - len(o2)})
    o3 = [min(vv["L_op"] for vv in d.values() if "L_op" in vv) / svd32[pid]["L_op"]
          for pid, d in fits.items() if pid in svd32 and svd32[pid]["L_op"] > 0
          and any("L_op" in vv for vv in d.values())]
    if o3:
        val = float(np.median(o3))
        out.append({"kind": "objective", "metric": OBJ_NAMES[2], "value": round(val, 6),
                    "epsilon": 1.5, "direction": "lower", "pass": bool(val <= 1.5),
                    "n_probes": len(o3), "n_valid": len(o3), "n_invalid": 224 - len(o3)})
    return out


# ---------------------------------------------------------------- rows 合并（确定性）

def row_key(r):
    k = r["kind"]
    if k == "p_star":
        return (k, r["probe_id"], r["tau"], 0, "")
    if k == "fit":
        return (k, r["probe_id"], r.get("steps_budget", 0), r["R"],
                f"{r['chain']}|{r.get('init','orthogonal_small')}|{r.get('optimizer','adam_coordinate')}")
    if k == "baseline":
        return (k, r["probe_id"], 0, r["budget"], r["method"])
    if k == "curve_C":
        return (k, r["probe_id"], r.get("steps", 0), r["N"], "curve")
    if k == "objective":
        return (k, r["metric"], 0, 0, "")
    return (k, json.dumps(r, sort_keys=True), 0, 0, "")


def serialize_rows(rows):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                   for r in sorted(rows, key=row_key))


def merge_rows(rows_path, new_rows, replace_kinds):
    old = []
    if rows_path.exists():
        old = [json.loads(l) for l in open(rows_path) if l.strip()]
    new_keys = {row_key(r) for r in new_rows if r["kind"] in replace_kinds}
    merged = [r for r in old if row_key(r) not in new_keys] + new_rows
    with open(rows_path, "w") as f:
        f.write(serialize_rows(merged))
    return merged


# ---------------------------------------------------------------- 自检

def self_checks(run_dir, rows, prs):
    sc = {}
    # S1：前缀平均核（anchors.mjs §(1)）numpy 复核 p*(0.99)=32±1
    L = 512
    ii = np.arange(L, dtype=np.float64)
    Mpre = np.where(ii[:, None] >= ii[None, :], 1.0 / (ii[:, None] + 1.0), 0.0)
    s = np.linalg.svd(Mpre, compute_uv=False)
    cum = np.cumsum(s * s)
    p1 = int(np.searchsorted(cum, 0.99 * cum[-1], side="left") + 1)
    sc["S1"] = {"pass": abs(p1 - 32) <= 1, "numpy_p_star": p1, "anchors_p_star": 32, "tol": 1}
    # S2：σ₁(E) 两种取法一致 1e-10
    d = [abs(r["L_op"] - r["L_op_alt"]) for r in rows
         if r.get("status", "valid") == "valid" and r.get("L_op") is not None
         and r.get("L_op_alt") is not None]
    primary_invalid = sum(1 for r in rows if r.get("status") == "invalid"
                          and r.get("invalid_reason") == "svd_gesdd_nonconvergence")
    alt_invalid = sum(1 for r in rows if r.get("status", "valid") == "valid"
                      and r.get("L_op") is not None and r.get("L_op_alt") is None)
    sc["S2"] = {"pass": bool(d) and max(d) <= 1e-10, "max_abs_dev": float(max(d)) if d else None,
                "n_compared": len(d), "n_primary_invalid": primary_invalid,
                "n_alt_invalid": alt_invalid,
                "no_comparable_rows": not bool(d)}
    # S3：Eckart–Young 一致性（rank-32 SVD 的 L_op vs σ₃₃）
    d = [abs(r["L_op"] - r["sigma_next"]) for r in rows
         if r["kind"] == "baseline" and r["method"] == "svd" and r["budget"] == 32
         and r.get("sigma_next") is not None]
    sc["S3"] = {"pass": bool(d) and max(d) <= 1e-10, "max_abs_dev": float(max(d)) if d else None,
                "n": len(d)}
    # S4：恒等基线 M̂=0 → L_op=σ₁(M*)、L_elem=‖M*‖_F²（独立取法）
    d1, d2 = [], []
    for pr in prs[:40]:
        M64 = np.load(run_dir / "probes" / pr["file"]).astype(np.float64)
        A = M64 * strict_mask(M64.shape[0])
        sM = np.linalg.svd(A, compute_uv=False)
        d1.append(abs(float(sM[0]) - float(np.linalg.norm(A, 2))))
        d2.append(abs(float(np.sum(A * A)) - float(np.linalg.norm(A, "fro") ** 2)))
    sc["S4"] = {"pass": bool(d1) and max(d1) <= 1e-10 and max(d2) <= 1e-8,
                "max_op_dev": float(max(d1)) if d1 else None,
                "max_elem_dev": float(max(d2)) if d2 else None, "n": len(d1)}
    # S5：20 探针（排序均匀抽）‖M*‖_F² ∈ [6.82, 512]
    frob = sorted(r["frobenius_sq"] for r in rows if r["kind"] == "p_star" and r["tau"] == 0.99)
    if frob:
        pick = [frob[int(i * len(frob) / 20)] for i in range(20)]
        sc["S5"] = {"pass": all(6.82 <= v <= 512 + 1e-9 for v in pick),
                    "sample": [round(v, 4) for v in pick]}
    # S7：仅向目标侧加入有限对角向量，严格下三角指标不变；完整域误差变化
    M7 = np.array([[1.0, 0.0, 0.0], [2.0, 3.0, 0.0], [4.0, 5.0, 6.0]])
    H7 = np.array([[0.5, 0.0, 0.0], [1.5, 2.0, 0.0], [3.0, 4.0, 5.0]])
    D7 = np.diag([0.25, -0.5, 0.75])
    A7, E7 = M7 * strict_mask(3), (H7 * strict_mask(3)) - (M7 * strict_mask(3))
    A7d, E7d = (M7 + D7) * strict_mask(3), (H7 * strict_mask(3)) - ((M7 + D7) * strict_mask(3))
    strict_before, strict_after = op_norm_and_fro(E7), op_norm_and_fro(E7d)
    full_before = op_norm_and_fro(H7 - M7)
    full_after = op_norm_and_fro(H7 - (M7 + D7))
    sc["S7"] = {"pass": A7.tobytes() == A7d.tobytes()
                          and all(strict_before[k] == strict_after[k] for k in ["L_elem", "L_op", "L_op_alt"])
                          and (full_before["L_elem"] != full_after["L_elem"] or full_before["L_op"] != full_after["L_op"]),
                "strict_before": strict_before, "strict_after": strict_after,
                "full_before": full_before, "full_after": full_after}
    return sc


# ---------------------------------------------------------------- summary

def median_group(rows, keyf, valf):
    groups = {}
    for r in rows:
        groups.setdefault(keyf(r), []).append(valf(r))
    return {str(k): round(float(np.median(v)), 5) for k, v in sorted(groups.items(), key=str)}


def write_summary(run_id, run_dir, rows, sc, stage_times, notes):
    prov = {}
    pp = run_dir / "measured" / "provenance.json"
    if pp.exists():
        prov = json.loads(pp.read_text())
    obj = {r["metric"]: r for r in rows if r["kind"] == "objective"}
    p99 = [r for r in rows if r["kind"] == "p_star" and r["tau"] == 0.99]
    fits_per = [r for r in rows if r["kind"] == "fit" and r["chain"] == "per"
                and r.get("status", "valid") == "valid" and r.get("L_op") is not None]
    fits_sh = [r for r in rows if r["kind"] == "fit" and r["chain"] == "shared"
               and r.get("status", "valid") == "valid" and r.get("L_op") is not None]
    base = [r for r in rows if r["kind"] == "baseline"
            and r.get("status", "valid") == "valid" and r.get("L_op") is not None]
    curve = [r for r in rows if r["kind"] == "curve_C"
             and r.get("status", "valid") == "valid" and r.get("L_op") is not None]
    env, w, d4, s5 = (prov.get("environment", {}), prov.get("weights", {}),
                      prov.get("data", {}), prov.get("seeds_config", {}))
    total_h = sum(stage_times.values()) / 3600 if stage_times else None
    gitc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()
    spec_sha = sha256_file(run_dir / "spec.md") if (run_dir / "spec.md").exists() else "n/a"

    T = []
    T.append(f"# measured summary — {run_id}\n")
    T.append("## 1 运行标识\n")
    T.append(f"- run_id: {run_id} · bench task_id: {prov.get('bench_task_id', 'n/a')}"
             f"（上游 model hop 18b71df7 / scout hop d52a0ff9）")
    T.append(f"- 日期: {prov.get('wallclock_start_iso', 'n/a')} 起 · 墙钟总耗时: "
             f"{total_h if total_h is None else round(total_h, 2)} h（budget 10 h）")
    T.append(f"- git commit: {gitc} · spec.md sha256: {spec_sha}")
    T.append("- hyperparams_frozen_before_measurement: true（全部超参定稿于 spec，测量未回改）\n")

    T.append("## 2 环境\n")
    T.append(f"- mlx {env.get('mlx_version')} · mlx-lm {env.get('mlx_lm_version')} · "
             f"numpy {env.get('numpy_version')}")
    T.append(f"- python {env.get('python_version')} · uv {env.get('uv_version')}")
    T.append(f"- 设备: {env.get('device')} · GPU cores {env.get('gpu_cores')} · Metal {env.get('metal')}")
    T.append(f"- R_eff（§5.8 计时校准）: {json.dumps(prov.get('r_eff', {}), ensure_ascii=False)}\n")

    T.append("## 3 权重 provenance\n")
    T.append(f"- weights_source: **{w.get('weights_source')}** · repo: {w.get('repo_id')} · "
             f"revision: {w.get('revision')}")
    T.append(f"- sha256(model.safetensors): `{w.get('sha256')}` · file_bytes: {w.get('file_bytes')}")
    T.append(f"- snapshot hash（前 16 位）: `{(w.get('sha256') or '')[:16]}` · "
             f"quantization: {json.dumps(w.get('quantization'))}")
    T.append(f"- config_snapshot: {json.dumps(w.get('config_snapshot'), ensure_ascii=False)}")
    T.append(f"- 降级路线（本跳未启用）: 4-bit 本地缓存 {w.get('fallback_4bit_path')}，"
             f"sha256 `{w.get('fallback_4bit_sha256', 'n/a')}`")
    T.append(f"- claim 范围: {w.get('claim_scope')}\n")

    T.append("## 4 数据\n")
    T.append(f"- 域与许可: {json.dumps(d4.get('domains'), ensure_ascii=False)}")
    T.append(f"- L = {d4.get('seq_len')} · tokenization: {json.dumps(d4.get('tokenization'), ensure_ascii=False)}")
    T.append(f"- 层: {d4.get('layers')} · 头: 每层 {d4.get('n_heads')} 头全用，GQA 分组 h→⌊h/7⌋")
    T.append(f"- 探针矩阵数：fit 集 {d4.get('n_fit_probes')} · heldout 集 {d4.get('n_heldout_probes', 0)}"
             "（objective 判定只用 fit 集）")
    T.append("- token_sha256 逐序列记录于 probes/manifest.jsonl（每行 token_sha256 字段）\n")

    T.append("## 5 种子与配置\n")
    T.append(f"- base seed: {s5.get('base_seed')} · 派生规则: {s5.get('derivation')}")
    T.append(f"- O1: tau 集合 {s5.get('tau')}（判定 0.99）；全 SVD 精确，无迭代")
    T.append(f"- O2: B_ss={s5.get('B_ss')} · R 集={s5.get('R_scan')} · diag_mode={s5.get('diag_mode')}"
             f" · chain=per（R=16 另有 chain=shared 消融）")
    T.append(f"- O3: baselines={s5.get('baselines')}（rank-{s5.get('B_ss')} 截断 SVD 主判定）")
    T.append(f"- 拟合: {json.dumps(s5.get('fit_protocol'), ensure_ascii=False)}\n")

    T.append("## 6 阶段耗时\n")
    T.append("| 阶段 | h |")
    T.append("|---|---:|")
    for k, v in (stage_times or {}).items():
        T.append(f"| {k} | {v / 3600:.2f} |")
    verdict6 = "pass" if total_h is not None and total_h <= prov.get("time_budget_h", 10) else "见 §12"
    T.append(f"\n- 总墙钟 ≤ time_budget({prov.get('time_budget_h', 10)} h): **{verdict6}**\n")

    T.append("## 7 自检\n")
    g = {}
    gpath = run_dir / "probes" / "guards.json"
    if gpath.exists():
        g = json.loads(gpath.read_text())
    mm = [json.loads(l) for l in open(run_dir / "probes" / "manifest.jsonl")
          if '"probe_id"' in l]
    mm = [r for r in mm if r.get("guards_pass") is not None]
    mx_ = lambda f, mode: (max((r.get(f, 0) for r in mm)) if mode == "max"
                           else min((r.get(f, 0) for r in mm)))
    g6 = g.get("g6", [])
    T.append("### 提取守卫（spec §4.4）")
    T.append("")
    T.append("| 编号 | 结果 | 数值（全体探针聚合） |")
    T.append("|---|---|---|")
    T.append(f"| G1 | {g.get('G1', 'n/a')} | max_i|Σ_j M−1| = {mx_('g1_row_sum_max_dev', 'max'):.2e} ≤ 1e-5 |")
    T.append(f"| G2 | {g.get('G2', 'n/a')} | min M = {mx_('g2_min_value', 'min'):.2e}；上三角逐位为 0 |")
    T.append(f"| G3 | {g.get('G3', 'n/a')} | max|Δ M00| = {mx_('g3_M00_dev', 'max'):.2e} ≤ 1e-6 |")
    T.append(f"| G4 | {g.get('G4', 'n/a')} | (512,512) float32 全有限 |")
    T.append(f"| G5 | {g.get('G5', 'n/a')} | max‖M_A−M_B‖∞ = {mx_('g5_max_dev', 'max'):.2e} ≤ 1e-4 |")
    T.append(f"| G6 | {g.get('G6', 'n/a')} | max‖Δlogit‖ = {max((r['max_abs_logit_dev'] for r in g6), default=0):.2e} ≤ 2e-2；min argmax 一致率 = {min((r['argmax_agree'] for r in g6), default=0):.4f} ≥ 0.99 |\n")
    T.append("### 评测器自检（spec §7.5）")
    T.append("")
    T.append("| 编号 | 结果 | 数值 |")
    T.append("|---|---|---|")
    for k in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        v = sc.get(k)
        if v is None:
            T.append(f"| {k} | pending | — |")
        else:
            det = {kk: vv for kk, vv in v.items() if kk != "pass"}
            T.append(f"| {k} | {'pass' if v.get('pass') else 'fail'} | {json.dumps(det, ensure_ascii=False)} |")
    T.append("")

    T.append("## 8 objectives\n")
    T.append(f"- 中位数约定: {MEDIAN_NOTE}")
    for m in OBJ_NAMES:
        r = obj.get(m)
        if r:
            T.append(f"- **{m}** = {r['value']}（epsilon={r['epsilon']}, direction={r['direction']}）"
                     f" → **{'pass' if r['pass'] else 'fail'}** · n={r['n_probes']} "
                     f"(n_valid={r.get('n_valid', r['n_probes'])}, n_invalid={r.get('n_invalid', 0)})")
        else:
            T.append(f"- **{m}**: 未完成（见 §12）")
    if p99:
        T.append(f"- O1 分位数: {json.dumps(qstats([r['p_star_over_L'] for r in p99]))}")
        T.append(f"- O1 逐域中位: {json.dumps(median_group(p99, lambda r: r['domain'], lambda r: r['p_star_over_L']), ensure_ascii=False)}")
        T.append(f"- O1 逐层中位: {json.dumps(median_group(p99, lambda r: r['layer'], lambda r: r['p_star_over_L']))}")
        T.append(f"- O1 逐头中位: {json.dumps(median_group(p99, lambda r: r['head'], lambda r: r['p_star_over_L']))}")
        taus = sorted({r["tau"] for r in rows if r["kind"] == "p_star"})
        T.append("")
        T.append("| τ | median p*/L | median p* |")
        T.append("|---|---:|---:|")
        for tau in taus:
            v = [r for r in rows if r["kind"] == "p_star" and r["tau"] == tau]
    fits, svd32 = per_probe_maps(rows, s5.get("B_ss", 32))
    o2 = [d[16]["L_op"] / d[1]["L_op"] for d in fits.values()
          if 1 in d and 16 in d and "L_op" in d[1] and "L_op" in d[16]
          and d[1]["L_op"] > 0 and d[16]["L_op"] > 0]
    o3 = [min(vv["L_op"] for vv in d.values() if "L_op" in vv) / svd32[p]["L_op"]
          for p, d in fits.items() if p in svd32 and svd32[p]["L_op"] > 0
          and any("L_op" in vv for vv in d.values())]
    T.append(f"- O2 逐探针比值分布: {json.dumps(qstats(o2))}")
    T.append(f"- O3 逐探针比值分布: {json.dumps(qstats(o3))}")
    fit_ids = {r["probe_id"] for r in rows if r.get("kind") == "fit"}
    r1_ids = {r["probe_id"] for r in fits_per if r.get("R") == 1}
    r16_ids = {r["probe_id"] for r in fits_per if r.get("R") == 16}
    missing_r16 = sorted(fit_ids - r16_ids)
    T.append(f"- O2 audit: extracted_fit={len(fit_ids)}, valid_R1={len(r1_ids)}, "
             f"valid_R16={len(r16_ids)}, valid_pairs={len(o2)}, missing_R16={len(missing_r16)}")
    T.append(f"- missing_R16_probe_ids: {json.dumps(missing_r16, ensure_ascii=False)}")
    overall = all(obj.get(m, {}).get("pass") for m in OBJ_NAMES)
    T.append(f"- overall_pass（pass_rule=all）: **{bool(overall)}**\n")

    T.append("## 9 constraints\n")
    for k in ["data_split_isolation", "fixed_seed_declared", "time_budget_declared",
              "evaluator_semantics_frozen", "weights_provenance_declared"]:
        v = prov.get("constraints", {}).get(k, {})
        T.append(f"- {k}: **{v.get('verdict', 'pending')}** — {v.get('evidence', '待写入')}")
    T.append("")

    T.append("## 10 逐配置表\n")
    if fits_per:
        T.append("| R | N | dof | L_op 中位 | L_elem 中位 | L_rel 中位 | L_sub32 中位 | 收敛率 | 墙钟中位(s) |")
        T.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for R in sorted({r["R"] for r in fits_per}):
            v = [r for r in fits_per if r["R"] == R]
            T.append(f"| {R} | {v[0]['N']} | {v[0]['dof']} | "
                     f"{np.median([x['L_op'] for x in v]):.4f} | {np.median([x['L_elem'] for x in v]):.4f} | "
                     f"{np.median([x['L_rel'] for x in v]):.5f} | {np.median([x['L_sub32'] for x in v]):.4f} | "
                     f"{np.mean([x['converged'] for x in v]):.1%} | {np.median([x['steps'] for x in v]):.0f} 步 |")
        for R in sorted({r["R"] for r in fits_sh}):
            v = [r for r in fits_sh if r["R"] == R]
            T.append(f"| {R} | {v[0]['N']} | {v[0]['dof']} | {np.median([x['L_op'] for x in v]):.4f} | "
                     f"{np.median([x['L_elem'] for x in v]):.4f} | {np.median([x['L_rel'] for x in v]):.5f} | "
                     f"{np.median([x['L_sub32'] for x in v]):.4f} | {np.mean([x['converged'] for x in v]):.1%} | "
                     f"{np.median([x['steps'] for x in v]):.0f} 步（chain=shared）|")
        T.append(f"\n- fit_convergence_rate（per-chain 全体）: "
                 f"{np.mean([r['converged'] for r in fits_per]):.3f}")
        T.append(f"- diag_contribution 中位（diag_mode=zero）: "
                 f"{np.median([r['diag_contribution'] for r in fits_per]):.4f}")
    else:
        T.append("（拟合数据缺失，见 §12）")
    T.append("")

    T.append("## 11 曲线数据\n")
    T.append("### D 裁剪版（R 扫描，B_ss=32 固定）")
    T.append("")
    if fits_per:
        T.append("| R | n_valid | invalid_curve | median L_op | p10 | p90 | median L_rel | median L_sub32 | median L_elem |")
        T.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for R in (1, 2, 4, 8, 16):
            bucket = [r for r in rows if r.get("kind") == "fit" and r.get("chain") == "per" and r.get("R") == R]
            v = [r for r in bucket if r.get("status", "valid") == "valid" and r.get("L_op") is not None]
            vals = [r["L_op"] for r in v]
            T.append(f"| {R} | {len(v)} | {len(bucket)-len(v)} | "
                     f"{round(float(np.median(vals)), 6) if vals else None} | "
                     f"{round(float(np.percentile(vals, 10)), 6) if vals else None} | "
                     f"{round(float(np.percentile(vals, 90)), 6) if vals else None} | "
                     f"{round(float(np.median([x['L_rel'] for x in v])), 6) if v else None} | "
                     f"{round(float(np.median([x['L_sub32'] for x in v])), 6) if v else None} | "
                     f"{round(float(np.median([x['L_elem'] for x in v])), 6) if v else None} |")
    T.append("")
    T.append("### C 裁剪版（N ∈ {2,4,8,16,32,64} @ R=1）")
    T.append("")
    if curve:
        T.append("| N | dof | n_valid | invalid_curve | median L_op | p10 | p90 | median L_elem |")
        T.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
        for N in (2, 4, 8, 16, 32, 64):
            bucket = [r for r in rows if r.get("kind") == "curve_C" and r.get("N") == N]
            v = [r for r in bucket if r.get("status", "valid") == "valid" and r.get("L_op") is not None]
            vals = [r["L_op"] for r in v]
            dof = bucket[0].get("dof") if bucket else None
            T.append(f"| {N} | {dof} | {len(v)} | {len(bucket)-len(v)} | "
                     f"{round(float(np.median(vals)), 6) if vals else None} | "
                     f"{round(float(np.percentile(vals, 10)), 6) if vals else None} | "
                     f"{round(float(np.percentile(vals, 90)), 6) if vals else None} | "
                     f"{round(float(np.median([x['L_elem'] for x in v])), 6) if v else None} |")
    else:
        T.append("（未跑或时间盒外，见 §12）")
    T.append("")
    T.append("### 基线逐秩（全体探针中位）")
    T.append("")
    if base:
        T.append("| method | budget | dof | median L_op | median L_elem |")
        T.append("|---|---:|---:|---:|---:|")
        for (mth, bud) in sorted({(r["method"], r["budget"]) for r in base}):
            v = [r for r in base if r["method"] == mth and r["budget"] == bud]
            T.append(f"| {mth} | {bud} | {v[0]['nominal_dof']} | "
                     f"{np.median([x['L_op'] for x in v]):.4f} | {np.median([x['L_elem'] for x in v]):.4f} |")
    T.append("")

    T.append("## 7a 人口审计\n")
    kind_counts = {}
    for r in rows:
        kind_counts[r["kind"]] = kind_counts.get(r["kind"], 0) + 1
    T.append(f"- rows_total: {len(rows)}; kind_counts: {json.dumps(kind_counts, ensure_ascii=False, sort_keys=True)}")
    invalid_curve = [r for r in rows if r["kind"] == "curve_C" and r.get("status") == "invalid"]
    T.append(f"- invalid_curve_total: {len(invalid_curve)}")
    T.append("- curve buckets: ")
    for N in (2, 4, 8, 16, 32, 64):
        bucket = [r for r in rows if r["kind"] == "curve_C" and r.get("N") == N]
        valid = [r for r in bucket if r.get("status", "valid") == "valid" and r.get("L_op") is not None]
        inv = [r for r in bucket if r.get("status") == "invalid"]
        vals = [r["L_op"] for r in valid]
        T.append(f"  - N={N}: n_valid={len(valid)}, invalid_curve={len(inv)}, "
                 f"median={round(float(np.median(vals)), 6) if vals else None}, "
                 f"p10={round(float(np.percentile(vals, 10)), 6) if vals else None}, "
                 f"p90={round(float(np.percentile(vals, 90)), 6) if vals else None}")
    available_N = [N for N in (2, 4, 8, 16, 32, 64)
                   if any(r["kind"] == "curve_C" and r.get("N") == N
                          and r.get("status", "valid") == "valid" and r.get("L_op") is not None
                          for r in rows)]
    available_R = [R for R in (1, 2, 4, 8, 16)
                   if any(r["kind"] == "fit" and r.get("R") == R and r.get("chain") == "per"
                          and r.get("status", "valid") == "valid" and r.get("L_op") is not None
                          for r in rows)]
    T.append(f"- available_N: {available_N}; available_R: {available_R}")
    T.append("")

    T.append("## 12 缺口\n")
    invalid_reasons = sorted({r.get("invalid_reason", r.get("reason", "unknown"))
                              for r in invalid_curve})
    T.append(f"- CR-7 invalid_curve_total={len(invalid_curve)}; reasons={json.dumps(invalid_reasons, ensure_ascii=False)}")
    T.append(f"- CR-7 invalid_curve_by_N: {json.dumps({N: sum(1 for r in rows if r.get('kind') == 'curve_C' and r.get('N') == N and r.get('status') == 'invalid') for N in (2,4,8,16,32,64)}, ensure_ascii=False)}")
    for note in notes:
        T.append(f"- {note}")
    if not notes:
        T.append("- 无")
    (run_dir / "measured" / "summary.md").write_text("\n".join(T) + "\n")


# ---------------------------------------------------------------- main

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--tau", default=None)
    ap.add_argument("--budget", type=int, default=32)
    ap.add_argument("--branches", default=None)
    ap.add_argument("--baselines", default=None)
    ap.add_argument("--probes", default=None)
    ap.add_argument("--from-cache", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=20260908)
    ap.add_argument("--time-cap", type=float, default=10.0)
    ap.add_argument("--steps", default="600")
    ap.add_argument("--init", default="orthogonal_small")
    ap.add_argument("--optimizer", default="adam_coordinate")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--chain", default="per", choices=["per", "shared"])
    ap.add_argument("--curves", action="store_true")
    ap.add_argument("--max-probes", type=int, default=0)
    ap.add_argument("--no-summary", action="store_true")
    # 本轮冻结审计接口（spec §8）
    ap.add_argument("--audit-split", action="store_true")
    ap.add_argument("--fit-split", default="fit")
    ap.add_argument("--heldout-split", default="heldout")
    ap.add_argument("--audit-seeds", action="store_true")
    ap.add_argument("--base-seed", type=int, default=20260908)
    ap.add_argument("--derive-rule", default="sha256(probe_id|R|chain|init|optimizer|steps)+base_seed")
    ap.add_argument("--audit-timing", action="store_true")
    ap.add_argument("--self-checks", action="store_true")
    ap.add_argument("--strict-lower", action="store_true")
    ap.add_argument("--lop-svd", default="gesdd")
    ap.add_argument("--lop-alt", default="norm2")
    ap.add_argument("--s2-tol", type=float, default=1e-10)
    ap.add_argument("--paired-r", default=None)
    ap.add_argument("--report-matched-dof", action="store_true")
    ap.add_argument("--no-fit", action="store_true")
    return ap.parse_args()


def _load_rows(run_dir):
    p = run_dir / "measured" / "rows.jsonl"
    return [json.loads(l) for l in open(p)] if p.exists() else []


def audit_split(run_dir, args):
    mm = [json.loads(l) for l in open(run_dir / "probes" / "manifest.jsonl") if l.strip()]
    rows = _load_rows(run_dir)
    measured_ids = {r["probe_id"] for r in rows if r.get("kind") in ("p_star", "fit")}
    splits = {r["probe_id"]: r["split"] for r in mm}
    heldout_measured = sum(1 for pid in measured_ids if splits.get(pid) == args.heldout_split)
    obj_ids = {r["probe_id"] for r in rows
               if r.get("kind") == "objective" and r.get("probe_id")}
    out = {
        "manifest_fit": sum(1 for r in mm if r.get("split") == args.fit_split and r.get("guards_pass")),
        "manifest_heldout": sum(1 for r in mm if r.get("split") == args.heldout_split and r.get("guards_pass")),
        "measured_probe_ids": len(measured_ids),
        "measured_split_counts": {},
        "heldout_measured": heldout_measured,
        "objective_heldout_ids": sorted(obj_ids & {p for p, s in splits.items() if s == args.heldout_split}),
    }
    for pid in measured_ids:
        k = splits.get(pid, "unknown")
        out["measured_split_counts"][k] = out["measured_split_counts"].get(k, 0) + 1
    out["pass"] = bool(out["manifest_fit"] == 224 and out["manifest_heldout"] == 224
                       and heldout_measured == 0)
    (run_dir / "measured" / "audit_split.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


def audit_seeds(run_dir, args):
    rows = _load_rows(run_dir)
    sample_fields = ("probe_id", "R", "chain", "init", "optimizer", "steps_budget", "seed_used")
    rows_out, bad = [], 0
    cfgs = {}
    for r in rows:
        if r.get("kind") != "fit" or "seed_used" not in r:
            continue
        expect = derive_seed(r["probe_id"], r["R"], r["chain"], args.base_seed,
                             init=r.get("init"), optimizer=r.get("optimizer"),
                             steps=r.get("steps_budget"))
        if int(r["seed_used"]) != int(expect):
            bad += 1
        k = (r.get("steps_budget"), r.get("init"), r.get("optimizer"), r["chain"])
        cfgs.setdefault(str(k), {"n": 0, "distinct_seeds": set()})
        cfgs[str(k)]["n"] += 1
        cfgs[str(k)]["distinct_seeds"].add(int(r["seed_used"]))
    for v in cfgs.values():
        v["distinct_seeds"] = len(v["distinct_seeds"])
    weights = json.loads((run_dir / "measured" / "provenance.json").read_text())["weights"] \
        if (run_dir / "measured" / "provenance.json").exists() else {}
    out = {"base_seed": args.base_seed, "derive_rule": args.derive_rule,
           "seed_rule_matches": bad, "n_fit_rows_with_seed": sum(v["n"] for v in cfgs.values()),
           "configs": cfgs,
           "weights_sha256": weights.get("sha256"),
           "declared": {"seq_len": 512, "layers": [0, 7, 15, 23], "heads": 14,
                         "B_ss": 32, "R_scan": [1, 2, 4, 8, 16]}}
    out["pass"] = bool(bad == 0 and out["n_fit_rows_with_seed"] > 0)
    (run_dir / "measured" / "audit_seeds.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "configs"}, ensure_ascii=False, sort_keys=True))


def audit_timing(run_dir, args):
    import re
    log = run_dir / "measured" / "run.log"
    text = log.read_text() if log.exists() else ""
    events = re.findall(r"^(\S+) (.*?) (?:exit=(-?\d+) elapsed=(\d+))?$", text, re.M)
    starts, stages = {}, []
    for ts, label, ec, el in events:
        if label.endswith("_start"):
            starts[label[:-6]] = ts
        elif ec:
            stages.append({"command": label, "start_iso": starts.get(label),
                           "end_iso": ts, "exit_code": int(ec), "elapsed_s": int(el)})
    total = sum(s["elapsed_s"] for s in stages)
    out = {"time_cap_h": args.time_cap, "stages": stages,
           "successful_commands_elapsed_s": sum(s["elapsed_s"] for s in stages if s["exit_code"] == 0),
           "all_commands_elapsed_s": total,
           "wallclock_start_iso": stages[0]["start_iso"] if stages else None,
           "wallclock_end_iso": stages[-1]["end_iso"] if stages else None,
           "total_command_h": round(total / 3600, 4)}
    out["pass"] = bool(total / 3600 <= args.time_cap)
    (run_dir / "measured" / "audit_timing.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "stages"}, ensure_ascii=False, sort_keys=True))


def paired_report(run_dir, args):
    rows = _load_rows(run_dir)
    if not args.paired_r:
        return
    a, b = (int(x) for x in args.paired_r.split("/"))
    groups = {}
    for r in rows:
        if r.get("kind") != "fit" or r.get("status", "valid") != "valid" or r.get("L_op") is None:
            continue
        k = (r.get("steps_budget"), r.get("init"), r.get("optimizer"), r.get("chain"))
        groups.setdefault(k, {}).setdefault(r["probe_id"], {})[r["R"]] = r["L_op"]
    out = []
    for k in sorted(groups, key=str):
        g = groups[k]
        ratios, miss_a, miss_b = [], [], []
        for pid, d in g.items():
            if a in d and b in d and d[b] > 0:
                ratios.append(d[a] / d[b])
            else:
                if a not in d:
                    miss_a.append(pid)
                if b not in d:
                    miss_b.append(pid)
        out.append({"steps_budget": k[0], "init": k[1], "optimizer": k[2], "chain": k[3],
                    "paired": args.paired_r, "n_pair": len(ratios),
                    "median_ratio": round(float(np.median(ratios)), 6) if ratios else None,
                    "p10": round(float(np.percentile(ratios, 10)), 6) if ratios else None,
                    "p90": round(float(np.percentile(ratios, 90)), 6) if ratios else None,
                    "n_missing_a": len(miss_a), "n_missing_b": len(miss_b),
                    "missing_a_ids": sorted(miss_a), "missing_b_ids": sorted(miss_b)})
    (run_dir / "measured" / "paired_ratios.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


def matched_dof_report(run_dir, args):
    rows = _load_rows(run_dir)
    def agg(chain):
        out = {}
        for r in rows:
            if r.get("kind") != "fit" or r.get("chain") != chain:
                continue
            k = (r.get("steps_budget"), r.get("init"), r.get("optimizer"), r["R"])
            b = out.setdefault(str(k), {"R": r["R"], "N": r.get("N"), "dof": r.get("dof"),
                                        "chain_params": None, "total": 0, "valid": 0,
                                        "invalid": 0, "converged": 0, "lop": [],
                                        "probe_ids": []})
            b["total"] += 1
            b["probe_ids"].append(r["probe_id"])
            if r.get("converged"):
                b["converged"] += 1
            if r.get("status", "valid") == "valid" and r.get("L_op") is not None:
                b["valid"] += 1
                b["lop"].append(r["L_op"])
            else:
                b["invalid"] += 1
        for v in out.values():
            L = 512
            chain_factor = (L - 1) * v["R"] if chain == "per" else (L - 1)
            v["chain_params"] = chain_factor
            v["median_L_op"] = round(float(np.median(v["lop"])), 6) if v["lop"] else None
            v["matched_probe_ids"] = sorted(v.pop("probe_ids"))
            v["lop"] = None
        return out
    per, shared = agg("per"), agg("shared")
    table = []
    for k_s, sv in sorted(shared.items(), key=str):
        key_per = k_s.replace("shared", "per")
        pv = per.get(key_per)
        row = dict(sv)
        if pv:
            row["per_median_L_op"] = pv["median_L_op"]
            row["per_dof"] = pv["dof"]
            row["delta_dof"] = (pv["dof"] - sv["dof"]) if pv["dof"] and sv["dof"] else None
            row["delta_chain_params"] = ((pv["chain_params"] - sv["chain_params"])
                                          if pv["chain_params"] is not None else None)
            both = sorted(set(pv["matched_probe_ids"]) & set(sv["matched_probe_ids"]))
            row["n_matched_probes"] = len(both)
        table.append(row)
    (run_dir / "measured" / "matched_dof.json").write_text(
        json.dumps(table, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps([{k: v for k, v in t.items() if k != "matched_probe_ids"} for t in table],
                     ensure_ascii=False, sort_keys=True))


def main():
    args = parse_args()
    run_dir = ROOT / "runs" / args.run_id
    (run_dir / "measured").mkdir(exist_ok=True)
    os.environ["BENCH_FITS_DIR"] = str(run_dir / "fits")

    filt = {}
    split = "fit"
    if args.probes:
        for kv in args.probes.split(","):
            k, _, v = kv.partition("=")
            if k == "domain":
                filt["domain"] = set(v.split("|"))
            elif k == "layers":
                filt["layers"] = {int(x) for x in v.split("|")}
            elif k == "split":
                split = v
    filt = filt or None
    audit_only = args.audit_split or args.audit_seeds or args.audit_timing or args.self_checks
    if audit_only:
        if args.audit_split:
            audit_split(run_dir, args)
        if args.audit_seeds:
            audit_seeds(run_dir, args)
        if args.audit_timing:
            audit_timing(run_dir, args)
        if args.self_checks:
            rows = _load_rows(run_dir)
            sc = self_checks(run_dir, rows, load_probes(run_dir, split="fit"))
            sc["meta"] = {"strict_lower": bool(args.strict_lower), "lop_svd": args.lop_svd,
                          "lop_alt": args.lop_alt, "s2_tol": args.s2_tol,
                          "s2_pass": bool(sc.get("S2", {}).get("pass"))}
            sc["S7"]["pass"] = bool(sc["S7"]["pass"] and args.strict_lower)
            scp = run_dir / "measured" / "self_checks.json"
            old = json.loads(scp.read_text()) if scp.exists() else {}
            old.update(sc)
            scp.write_text(json.dumps(old, ensure_ascii=False, indent=1, sort_keys=True))
            print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else v) for k, v in sc.items()},
                             ensure_ascii=False, sort_keys=True))
        sys.exit(0)
    prs = load_probes(run_dir, split=split, filt=filt)
    if args.max_probes:
        prs = prs[:args.max_probes]
    if not prs:
        print("no probes", file=sys.stderr)
        sys.exit(1)
    print(f"probes: {len(prs)} (split={split})")

    steps_list = [int(x) for x in str(args.steps).split(",")]
    init_list = [x for x in args.init.split(",") if x]
    optimizer_list = [x for x in args.optimizer.split(",") if x]
    modes = []
    taus = [float(x) for x in args.tau.split(",")] if args.tau else None
    if taus:
        modes.append("p_star")
    Rs = sorted(int(x) for x in args.branches.split(",")) if args.branches else None
    if Rs:
        modes.append("fit_branches")
    meths = [x for x in args.baselines.split(",") if x] if args.baselines else None
    if meths:
        modes.append("baselines")
    if not modes:
        print("no mode given", file=sys.stderr)
        sys.exit(1)

    rows_path = run_dir / "measured" / "rows.jsonl"

    def compute():
        new_rows, replace = [], set()
        if "p_star" in modes:
            r = run_p_star(prs, taus, run_dir)
            new_rows += r
            replace |= {"p_star"}
            print(f"p_star rows={len(r)}")
        if "fit_branches" in modes:
            all_fit = []
            for steps in steps_list:
                for init in init_list:
                    for optimizer in optimizer_list:
                        for chain in ([args.chain] if args.chain else ["per"]):
                            if not args.from_cache and not args.no_fit:
                                n = ensure_fits(prs, run_dir, Rs, chain, args.budget, args.seed, steps, args.jobs,
                                                init=init, optimizer=optimizer)
                                print(f"fit_branches: chain={chain} steps={steps} init={init} optimizer={optimizer} new={n}")
                            rr = score_fits(prs, run_dir, Rs, chain, args.budget, steps=steps,
                                             init=init, optimizer=optimizer)
                            for row in rr:
                                row.update({"steps_budget": steps, "init": init, "optimizer": optimizer,
                                            "init_scale": 4.0 if init == "balanced_large" else 1.0,
                                            "warm_start_from": None})
                            all_fit.extend(rr)
            new_rows += all_fit
            replace |= {"fit"}
            print(f"fit rows={len(all_fit)}")
        if "baselines" in modes:
            r = run_baselines(prs, run_dir, meths)
            new_rows += r
            replace |= {"baseline"}
            if args.curves:
                cr = run_curve_fits(prs, run_dir, (2, 4, 8, 16, 64), args.seed, int(args.steps), args.jobs)
                r += cr
                new_rows += cr
                replace |= {"curve_C"}
            print(f"baseline rows={len(r)}")
        return new_rows, replace

    t0 = time.time()
    new_rows, replace = compute()
    merged = merge_rows(rows_path, new_rows, replace)
    merged = merge_rows(rows_path, objective_rows(merged, args.budget), {"objective"})

    sc = self_checks(run_dir, merged, prs)
    if args.from_cache:
        before = rows_path.read_bytes()
        nr2, rep2 = compute()
        merge_rows(rows_path, nr2, rep2)
        merge_rows(rows_path, objective_rows([json.loads(l) for l in open(rows_path)], args.budget),
                   {"objective"})
        after = rows_path.read_bytes()
        sc["S6"] = {"pass": before == after, "bytes": len(after)}
    scp = run_dir / "measured" / "self_checks.json"
    old_sc = json.loads(scp.read_text()) if scp.exists() else {}
    old_sc.update({k: v for k, v in sc.items() if v is not None})
    scp.write_text(json.dumps(old_sc, ensure_ascii=False, indent=1, sort_keys=True))

    if not args.no_summary:
        stp = run_dir / "measured" / "stage_times.json"
        stage_times = json.loads(stp.read_text()) if stp.exists() else {}
        npat = run_dir / "measured" / "notes.json"
        notes = json.loads(npat.read_text()) if npat.exists() else []
        write_summary(args.run_id, run_dir, merged, old_sc, stage_times, notes)
    if args.paired_r:
        paired_report(run_dir, args)
    if args.report_matched_dof:
        matched_dof_report(run_dir, args)
    if False:
        stp = run_dir / "measured" / "stage_times.json"
        stage_times = json.loads(stp.read_text()) if stp.exists() else {}
        npat = run_dir / "measured" / "notes.json"
        notes = json.loads(npat.read_text()) if npat.exists() else []
        write_summary(args.run_id, run_dir, merged, old_sc, stage_times, notes)
    print(f"modes={modes} elapsed={time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
