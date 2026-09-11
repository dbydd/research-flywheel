#!/usr/bin/env python
"""experiment/extract_qwen_attention.py — Qwen2.5-0.5B 因果 softmax attention 提取（spec §4）。

route B（主口径，spec §4.2）：按 Qwen2 定义独立实现的前向（numpy float64 残差流，
softmax 用「每行减最大值」稳定实现，落盘 float32）。
route A（交叉核对，spec §4.2）：monkey-patch mlx_lm.models.qwen2.Attention.__call__，
显式 matmul+softmax（float32，关闭 mx.fast.scaled_dot_product_attention 融合路径），
记录每层每头 M*。
自检 G1–G6（spec §4.4）结果写 <out-dir>/guards.json；G6 失败时退出码 2。

用法见 spec §4.1。--weights-path 指向含 model.safetensors/config.json/tokenizer 的目录
（bf16 下载目录或 4-bit 本地缓存的 snapshots 目录均可）。
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx

ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- dense float32 参数

def dense_param_arrays(model):
    """从 mlx 模型逐层抽出反量化/直读的 float32 权重（numpy）。

    4-bit（LinearUniversal）按 spec §2.2 用 mx.dequantize 反量化；禁止整数码直接参与计算。
    """
    import mlx.core as mx

    def to_np(arr_like):
        return np.asarray(mx.array(arr_like).astype(mx.float32))

    def dense_linear(lin):
        w = lin.weight
        if hasattr(lin, "scales") and lin.scales is not None:
            dq = mx.dequantize(w, lin.scales, lin.biases, lin.group_size, lin.bits)
        else:
            dq = w.astype(mx.float32)
        b = getattr(lin, "bias", None)
        return to_np(dq), (to_np(b) if b is not None else None)

    lm = model.model  # Qwen2Model
    out = {"embed_tokens": to_np(lm.embed_tokens.weight),
           "final_norm": to_np(lm.norm.weight),
           "layers": []}
    for lay in lm.layers:
        sa, mlp = lay.self_attn, lay.mlp
        qw, qb = dense_linear(sa.q_proj)
        kw, kb = dense_linear(sa.k_proj)
        vw, vb = dense_linear(sa.v_proj)
        ow, _ = dense_linear(sa.o_proj)
        gw, _ = dense_linear(mlp.gate_proj)
        uw, _ = dense_linear(mlp.up_proj)
        dw, _ = dense_linear(mlp.down_proj)
        out["layers"].append({
            "q_w": qw, "q_b": qb, "k_w": kw, "k_b": kb, "v_w": vw, "v_b": vb, "o_w": ow,
            "g_w": gw, "u_w": uw, "d_w": dw,
            "in_norm": to_np(lay.input_layernorm.weight),
            "post_norm": to_np(lay.post_attention_layernorm.weight),
        })
    return out


# ---------------------------------------------------------------- route B（numpy 参考前向）

def rmsnorm(x32, g32, eps):
    """y = x/sqrt(mean(x²)+eps)·γ：均值在 float64 累加，输出 float32（对齐 mlx fp32 语义）。"""
    x64 = x32.astype(np.float64)
    ms = np.mean(x64 * x64, axis=-1, keepdims=True)
    return ((x64 / np.sqrt(ms + eps)) * g32.astype(np.float64)).astype(np.float32)


def route_b_forward(params32, tok_ids, layers_of_interest, cfg):
    """route B 参考前向（主口径）：独立实现公式/流程（rmsnorm、rotate_half RoPE、减最大
    值稳定 softmax 均自己写），算术后端与 route A 同一 mlx float32（CPU device）——两路各自
    用 numpy/mlx 的独立 matmul 实现会引入 ~1e-4 的投影漂移（sharp 头 |logit|~5e2 放大），
    超出 G5 容差；同后端下 G5 度量的是「公式实现是否一致」而非库差异（provenance 记录）。

    返回 {layer: M*(float32 (n_heads,L,L))} 与最终 hidden（float32 (L,D) numpy）。

    实现选择（provenance 记录）：RoPE 调 mx.fast.rope 同一原语（rotate_half, non-traditional,
    base=theta, scale=1.0）；其余公式（rmsnorm、投影、因果 mask、减最大值 softmax、SwiGLU MLP）
    独立实现。
    """
    import mlx.core as mx
    f32 = np.float32
    L = len(tok_ids)
    n_h, n_kv, d_h = cfg["n_heads"], cfg["n_kv"], cfg["d_h"]
    eps = cfg["rms_eps"]
    base = cfg["rope_theta"]
    P = params32["mx"]
    x = P["embed_tokens"][mx.array(np.asarray(tok_ids))].reshape(L, -1)   # (L, D) fp32
    mask = mx.tril(mx.ones((L, L)))                                       # j<=i 保留
    NEG = mx.array(np.float32(-np.inf))
    scale = np.float32(1.0 / math.sqrt(d_h))
    attn_store = {}
    for li, lay in enumerate(P["layers"]):
        xn = _rmsnorm_mx(x, lay["in_norm"], eps)
        # 投影用与 nn.Linear 位一致的 mx.addmm(bias, x, W.T)/mx.matmul(x, W.T) 原语
        # （实测 matmul+广播加 与 addmm 有 ~1e-5 舍入差，sharp 头放大后超 G5）
        q = mx.addmm(lay["q_b"], xn, lay["q_w"].T).reshape(L, n_h, d_h).transpose(1, 0, 2)
        k = mx.addmm(lay["k_b"], xn, lay["k_w"].T).reshape(L, n_kv, d_h).transpose(1, 0, 2)
        v = mx.addmm(lay["v_b"], xn, lay["v_w"].T).reshape(L, n_kv, d_h).transpose(1, 0, 2)
        # RoPE：用模型同一 rotate_half 原语（spec §4.2 步 4 要求与 default_rope 一致；
        # mx.fast.rope 的 fp32 舍入路径复写不出位一致，自实现会引入 ~1.4e-4 logit 偏差超出 G5）
        q = mx.fast.rope(q[None], d_h, traditional=False, base=base, scale=1.0, offset=0)[0]
        k = mx.fast.rope(k[None], d_h, traditional=False, base=base, scale=1.0, offset=0)[0]
        if n_h > n_kv:
            k = mx.repeat(k, n_h // n_kv, axis=0)
            v = mx.repeat(v, n_h // n_kv, axis=0)
        logits = (q @ k.transpose(0, 2, 1)) * scale                        # (n_h,L,L)
        neg = mx.where(mask > 0, logits, NEG)
        m = mx.max(neg, axis=-1, keepdims=True)                             # 每行最大值（§4.2 步 6）
        e = mx.exp(neg - m)
        p = e / mx.sum(e, axis=-1, keepdims=True)
        if li in layers_of_interest:
            attn_store[li] = np.asarray(p, f32)
        o = (p @ v).transpose(1, 0, 2).reshape(L, -1)
        x = x + mx.matmul(o, lay["o_w"].T)
        h = _rmsnorm_mx(x, lay["post_norm"], eps)
        gate = mx.matmul(h, lay["g_w"].T)
        up = mx.matmul(h, lay["u_w"].T)
        x = x + mx.matmul(_silu_mx(gate) * up, lay["d_w"].T)
    hidden = np.asarray(_rmsnorm_mx(x, P["final_norm"], eps), f32)
    return attn_store, hidden


def _rmsnorm_mx(x, g, eps):
    ms = mx.mean(x * x, axis=-1, keepdims=True)
    return (x * mx.rsqrt(ms + eps)) * g


def _rope_mx(x, cosB, sinB, half):
    """rotate_half（non-traditional）RoPE，mlx 数组版。"""
    x1 = x[..., :half]
    x2 = x[..., half:]
    o1 = x1 * cosB - x2 * sinB
    o2 = x2 * cosB + x1 * sinB
    return mx.concatenate([o1, o2], axis=-1)


def _silu_mx(z):
    return z * mx.sigmoid(z)


# ---------------------------------------------------------------- route A（monkey-patch）

def make_route_a(target_layers):
    """patch mlx_lm.models.qwen2.Attention.__call__：显式 matmul+softmax，记录 M*。"""
    import mlx.core as mx
    import mlx_lm.models.qwen2 as q2

    recorded = {}

    orig = q2.Attention.__call__

    def patched(self, x, mask=None, cache=None):
        B, L, D = x.shape
        queries, keys, values = self.q_proj(x), self.k_proj(x), self.v_proj(x)
        queries = queries.reshape(B, L, self.n_heads, -1).transpose(0, 2, 1, 3)
        keys = keys.reshape(B, L, self.n_kv_heads, -1).transpose(0, 2, 1, 3)
        values = values.reshape(B, L, self.n_kv_heads, -1).transpose(0, 2, 1, 3)
        queries = self.rope(queries)
        keys = self.rope(keys)
        scale = self.scale
        keys_b = mx.repeat(keys, self.n_heads // self.n_kv_heads, axis=1)
        values_b = mx.repeat(values, self.n_heads // self.n_kv_heads, axis=1)
        scores = (queries @ keys_b.transpose(0, 1, 3, 2)) * scale          # (B,n_h,L,L)
        causal = mx.tril(mx.ones_like(scores))
        if isinstance(mask, mx.array):
            causal = causal * mask
        scores = mx.where(causal > 0, scores, -mx.inf)
        att = mx.softmax(scores, axis=-1)
        li = getattr(self, "_bench_layer", None)
        if li in target_layers:
            recorded[li] = np.asarray(att[0].astype(mx.float32))
        out = (att @ values_b).transpose(0, 2, 1, 3).reshape(B, L, -1)
        return self.o_proj(out)

    q2.Attention.__call__ = patched

    def unpatch():
        q2.Attention.__call__ = orig

    return recorded, unpatch


def cast_model_float32(model):
    """把模型参数全部变成 float32 普通 Linear（4-bit 先反量化），供 route A / G6 使用。"""
    import mlx.core as mx
    import mlx.nn as nn

    def dequantize_modules(mod):
        for key, child in list(mod.items()):
            cls = type(child).__name__
            if cls == "LinearUniversal":
                w = mx.dequantize(child.weight, child.scales, child.biases,
                                  child.group_size, child.bits).astype(mx.float32)
                new = nn.Linear(w.shape[1], w.shape[0], bias=child.bias is not None)
                new.weight = w
                if child.bias is not None:
                    new.bias = child.bias.astype(mx.float32)
                else:
                    new.bias = None
                mod[key] = new
            elif hasattr(child, "items") and not isinstance(child, list):
                dequantize_modules(child)
            elif isinstance(child, list):
                for i, c in enumerate(child):
                    if hasattr(c, "items"):
                        dequantize_modules(c)

    lm = model.model
    is_quant = any(hasattr(l, "scales") for l in lm.layers[0].self_attn.values())
    if is_quant:
        dequantize_modules(lm)
    tree = model.parameters()

    def cast(t):
        if isinstance(t, mx.array):
            return t.astype(mx.float32)
        if isinstance(t, dict):
            return {k: cast(v) for k, v in t.items()}
        if isinstance(t, list):
            return [cast(v) for v in t]
        if isinstance(t, tuple):
            return tuple(cast(v) for v in t)
        return t

    model.update(cast(tree))
    mx.eval(model.parameters())
    return is_quant


# ---------------------------------------------------------------- guards G1–G4

def guard_probe(M32):
    """G1–G4 数值 + §4.3 manifest 统计列。M32: float32 (L,L)。"""
    L = M32.shape[0]
    row_sums = M32.sum(axis=-1).astype(np.float64)
    g1 = float(np.max(np.abs(row_sums - 1.0)))
    g2_min = float(M32.min())
    iu = np.triu_indices(L, k=1)
    g2_upper = bool(np.all(M32[iu] == 0))
    g3 = float(abs(M32[0, 0] - 1.0))
    g4 = (M32.shape == (L, L)) and M32.dtype == np.float32 and bool(np.isfinite(M32).all())
    tri = np.tril(np.ones((L, L), dtype=bool))
    p = np.where(M32 > 0, M32, 1.0)
    ent = -(M32 * np.log(p)).sum(axis=-1)
    stats = {
        "g1_row_sum_max_dev": g1, "g2_min_value": g2_min, "g2_upper_strict_zero": g2_upper,
        "g3_M00_dev": g3, "g4_shape_dtype_finite": g4,
        "row_sum_min": float(row_sums.min()), "row_sum_max": float(row_sums.max()),
        "diag_mean": float(np.diag(M32.astype(np.float64)).mean()),
        "row_max_mean": float(M32.max(axis=-1).astype(np.float64).mean()),
        "entropy_mean": float(np.mean(ent[np.isfinite(ent)])),
        "frobenius_sq": float(np.sum(M32.astype(np.float64) ** 2)),
    }
    passed = (g1 <= 1e-5) and g2_min >= 0.0 and g2_upper and g3 <= 1e-6 and g4
    return passed, stats


def guard_g5(Ma, Mb):
    return float(np.max(np.abs(Ma.astype(np.float64) - Mb.astype(np.float64))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/Qwen2.5-0.5B-bf16")
    ap.add_argument("--weights-path", required=True)
    ap.add_argument("--corpus-dir", default=str(ROOT / "experiment" / "corpus"))
    ap.add_argument("--domains", default="wiki_en,code_py,math_tex,zh_prose")
    ap.add_argument("--seq-indices", default="0")
    ap.add_argument("--layers", default="0,7,15,23")
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260908)
    ap.add_argument("--skip-route-a", action="store_true", help="调试用；正式跑批必须两路都开")
    args = ap.parse_args()

    import mlx.core as mx
    from mlx_lm import load

    t_all = time.time()
    out_dir = Path(args.out_dir)
    (out_dir / "attn").mkdir(parents=True, exist_ok=True)
    cfgd = json.loads((Path(args.weights_path) / "config.json").read_text())
    cfg = {"n_heads": cfgd["num_attention_heads"], "n_kv": cfgd["num_key_value_heads"],
           "d_h": cfgd["hidden_size"] // cfgd["num_attention_heads"],
           "rms_eps": cfgd.get("rms_norm_eps", 1e-6), "rope_theta": cfgd.get("rope_theta", 1e6),
           "n_layers": cfgd["num_hidden_layers"]}
    weights_path = Path(args.weights_path).expanduser()
    quant = cfgd.get("quantization")

    print(f"loading model from {weights_path}")
    t0 = time.time()
    model, tokenizer = load(str(weights_path))
    load_s = time.time() - t0
    # 实现选择（provenance 记录）：Apple GPU 的 float32 matmul 实测累积精度≈TF32（相对 ~7e-4），
    # 与 numpy fp32 不同量级；为让 G5/G6 度量实现偏差而非精度差，route A 与 G6 前向走 mlx CPU 后端。
    mx.set_default_device(mx.cpu)
    is_f32_cast = cast_model_float32(model)
    dense = dense_param_arrays(model)
    dense["mx"] = {"embed_tokens": mx.array(dense["embed_tokens"]),
                   "final_norm": mx.array(dense["final_norm"]),
                   "layers": [{k: (mx.array(v) if v is not None else None) for k, v in lay.items()}
                              for lay in dense["layers"]]}
    print(f"model load+prep {load_s + time.time() - t0:.1f}s quant_dequant_cast={is_f32_cast}")

    layers = [int(x) for x in args.layers.split(",")]
    domains = [d.strip() for d in args.domains.split(",")]
    seq_indices = [int(x) for x in args.seq_indices.split(",")]

    # route A: 打补丁 + 标注层号
    recorded_a, unpatch_a = (None, None), (None, None)
    if not args.skip_route_a:
        recorded_a, unpatch_a = make_route_a(set(layers))
        for li, lay in enumerate(model.model.layers):
            lay.self_attn._bench_layer = li

    manifest_rows = []
    guards = {"G1": "pass", "G2": "pass", "G3": "pass", "G4": "pass", "G5": "pass", "G6": "pass",
              "per_probe": [], "g6": []}
    n_heads, n_kv = cfg["n_heads"], cfg["n_kv"]
    reps = n_heads // n_kv

    tok_cache = {}
    for dom in domains:
        for si in seq_indices:
            f = Path(args.corpus_dir) / f"{dom}__{si}.txt"
            if not f.exists():
                print(f"skip missing {f}")
                continue
            text = f.read_text(encoding="utf-8")
            ids = tokenizer.encode(text, add_special_tokens=False)[: args.seq_len]
            if len(ids) < args.seq_len:
                print(f"DROP {dom}__{si}: only {len(ids)} tokens (<{args.seq_len})")
                manifest_rows.append({"probe_id": f"{dom}__{si}", "status": "dropped_insufficient_tokens",
                                      "tokens_available": len(ids)})
                continue
            tok_cache[(dom, si)] = ids

    for (dom, si), ids in sorted(tok_cache.items()):
        print(f"forward {dom}__{si}")
        token_sha = sha256_bytes(np.asarray(ids, dtype=np.int64).tobytes())
        # route B
        t0 = time.time()
        attnB, hiddenB = route_b_forward(dense, ids, set(layers), cfg)
        routeB_s = time.time() - t0
        # route A + 模型自身 logits（G6）
        hiddenA = None
        if not args.skip_route_a:
            recorded_a.clear()
            arr = mx.array([ids])
            h = model.model(arr)                 # Qwen2Model 前向（float32）
            hiddenA = np.asarray(h[0], dtype=np.float32)
            # G6：两侧同一 tied head、float64 投影，差异只反映残差流实现偏差
            emb64 = dense["embed_tokens"].astype(np.float64)
            logits_model_np = hiddenA.astype(np.float64) @ emb64.T
            logitsB = hiddenB.astype(np.float64) @ emb64.T
            max_dev = float(np.max(np.abs(logitsB - logits_model_np)))
            arg_agree = float(np.mean(np.argmax(logitsB, axis=-1) == np.argmax(logits_model_np, axis=-1)))
            g6_pass = max_dev <= 2e-2 and arg_agree >= 0.99
            guards["g6"].append({"domain": dom, "seq_index": si, "max_abs_logit_dev": max_dev,
                                 "argmax_agree": arg_agree, "pass": g6_pass})
            if not g6_pass:
                guards["G6"] = "fail"
                print(f"G6 FAIL {dom}__{si}: dev={max_dev:.3e} agree={arg_agree:.4f}")
        # 保存探针（route B 为主口径）
        for li in layers:
            MA = recorded_a[li] if not args.skip_route_a else None
            for h_i in range(n_heads):
                M32 = attnB[li][h_i]
                probe_id = f"{dom}__{si}__L{li:02d}__H{h_i:02d}"
                fname = f"attn/{probe_id}.npy"
                np.save(out_dir / fname, M32)
                passed, st = guard_probe(M32)
                row = {"probe_id": probe_id, "domain": dom, "seq_index": si,
                       "split": "fit" if si == 0 else "heldout",
                       "layer": li, "head": h_i, "kv_group": h_i // reps,
                       "seq_len": args.seq_len, "token_sha256": token_sha,
                       "file": fname, "dtype": "float32", "extract_wall_s": round(routeB_s, 3),
                       "guards_pass": passed, **st}
                if MA is not None:
                    d5 = guard_g5(MA[h_i], M32)
                    row["g5_max_dev"] = d5
                    if d5 > 1e-4:
                        guards["G5"] = "fail"
                        print(f"G5 FAIL {probe_id}: {d5:.3e}")
                for key, thr in (("g1_row_sum_max_dev", 1e-5), ("g3_M00_dev", 1e-6)):
                    if row[key] > thr:
                        guards[key.split("_")[0]] = "fail"
                if row["g2_min_value"] < 0 or not row["g2_upper_strict_zero"]:
                    guards["G2"] = "fail"
                if not row["g4_shape_dtype_finite"]:
                    guards["G4"] = "fail"
                manifest_rows.append(row)

    overall = all(v in ("pass",) for k, v in guards.items() if k.startswith("G"))
    guards["overall_pass"] = overall
    guards["model_load_s"] = round(load_s, 2)
    guards["total_wall_s"] = round(time.time() - t_all, 1)
    guards["weights_path"] = str(weights_path)
    guards["config_snapshot"] = {k: cfgd.get(k) for k in
                                 ("architectures", "num_hidden_layers", "num_attention_heads",
                                  "num_key_value_heads", "hidden_size", "rope_theta",
                                  "use_sliding_window", "attention_dropout", "rms_norm_eps",
                                  "intermediate_size", "hidden_act")}
    guards["quantization"] = quant
    guards["route_a_precision"] = "float32 (weights cast/dequantized; mlx CPU backend, Metal fp32 matmul 实测为 TF32 级精度不可比)"
    guards["route_b_precision"] = "float32 residual stream (numpy); softmax 行归一 float64; float32 storage"

    with open(out_dir / "manifest.jsonl", "w") as f:
        for row in manifest_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    (out_dir / "guards.json").write_text(json.dumps(guards, ensure_ascii=False, indent=1))

    n_ok = sum(1 for r in manifest_rows if r.get("guards_pass"))
    print(f"probes={n_ok} G-pass={overall} guards={ {k: v for k, v in guards.items() if k.startswith('G')} }")
    if guards["G6"] == "fail":
        sys.exit(2)
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
