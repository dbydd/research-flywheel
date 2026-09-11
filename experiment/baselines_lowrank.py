#!/usr/bin/env python
"""experiment/baselines_lowrank.py — 同预算低秩基线（spec §6）。

1. 截断 SVD：矩阵先按严格下三角 mask 置零（保持因果支撑），numpy.linalg.svd float64，
   取前 r 项重构；r ∈ {2,4,8,16,32,64}，主判定 r=32。
2. HSS：二分成树，D=4，每层 ℓ 把当前各块的严格下三角非对角子块换成秩 p_ℓ 截断 SVD，
   对角子块递归；p=(8,8,8,8)；粗层→细层、块按索引升序。叶子对角块（32×32）保留原值
   （实现选择，记录于 provenance）。
3. 全部确定性（LAPACK），无随机项。
"""
import numpy as np

R_GRID = (2, 4, 8, 16, 32, 64)
HSS_P_DEFAULT = (8, 8, 8, 8)


def causal_mask_strict(L: int) -> np.ndarray:
    return np.tril(np.ones((L, L), dtype=np.float64), k=-1)


def truncated_svd(M, r: int):
    """rank-r 截断 SVD 重构（float64）。返回 (Mhat, sigma_next)。"""
    M64 = np.asarray(M, dtype=np.float64)
    U, s, Vt = np.linalg.svd(M64, full_matrices=False)
    Mhat = (U[:, :r] * s[:r]) @ Vt[:r]
    sigma_next = float(s[r]) if r < len(s) else 0.0
    return Mhat, sigma_next


def hss_approx(M, p_levels=HSS_P_DEFAULT):
    """层级二分 HSS 近似：非对角左下块截断 SVD，对角块递归（粗→细，块按索引升序）。"""
    M64 = np.asarray(M, dtype=np.float64)
    L = M64.shape[0]
    mask = causal_mask_strict(L)
    A = M64 * mask

    def rec(B, p_list, off):
        n = B.shape[0]
        if not p_list or n < 2:
            return B
        h = n // 2
        out = np.zeros_like(B)
        # 严格下三角非对角子块（左下象限）→ 秩 p 截断 SVD
        p = p_list[0]
        Bl = B[h:, :h]  # 左下象限整体处于严格下三角区，无需再 mask
        U, s, Vt = np.linalg.svd(Bl, full_matrices=False)
        r = min(p, min(Bl.shape))
        out[h:, :h] = (U[:, :r] * s[:r]) @ Vt[:r]
        # 右上象限在上三角区，恒 0（保持因果支撑）
        # 对角象限递归（索引升序：先左上后右下）
        out[:h, :h] = rec(B[:h, :h], p_list[1:], (off[0], off[0]))
        out[h:, h:] = rec(B[h:, h:], p_list[1:], (off[0] + h, off[0] + h))
        return out

    return rec(A, list(p_levels), (0, 0))


def hss_dof(L: int, p_levels=HSS_P_DEFAULT) -> int:
    """名义参数量 2L·Σp（derivation.md §6 口径）。"""
    return int(2 * L * sum(p_levels))


def curve(M, kinds=("svd", "hss"), r_grid=R_GRID, d: int = 4):
    """逐秩「预算—误差」曲线数据（spec §6.3）。返回行列表。"""
    rows = []
    M64 = np.asarray(M, dtype=np.float64)
    mask = causal_mask_strict(M64.shape[0])
    A = M64 * mask
    for r in r_grid:
        if "svd" in kinds:
            Mhat, s_next = truncated_svd(A, r)
            E = Mhat - A
            rows.append({"method": "svd", "budget": r, "nominal_dof": 2 * A.shape[0] * r - r * r + r,
                         "L_elem": float(np.sum(E * E)),
                         "L_op": float(np.linalg.svd(E, compute_uv=False)[0]),
                         "sigma_next": s_next})
        if "hss" in kinds:
            Mhat = hss_approx(A, p_levels=(r,) * d)
            E = Mhat - A
            rows.append({"method": "hss", "budget": r, "nominal_dof": hss_dof(A.shape[0], (r,) * d),
                         "L_elem": float(np.sum(E * E)),
                         "L_op": float(np.linalg.svd(E, compute_uv=False)[0]),
                         "sigma_next": None})
    return rows
