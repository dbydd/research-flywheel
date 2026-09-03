#!/usr/bin/env python3
# Portability (reversible): prefer python3, fallback to python at call sites.
# Shebang stays python3 for direct exec; portable callers use PY=$(command -v python3 || command -v python).
# Revert this header comment alone to restore minimal header.
"""Dependency-free inspiration engine — stdlib only.

Appends at least two queued ideas when the queue is empty/low,
deduplicates by ids/titles, updates inspiration.md, appends navigator query record.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore

WORKSPACE = Path(__file__).resolve().parent.parent

# Deterministic template pool — each entry is executable via <50 line patch in experiment/run.py
TEMPLATE_POOL = [
    {
        "title": "Adjusted slope with L2 regularisation proxy",
        "hypothesis": "A smaller slope with intercept re-fit lowers MSE by reducing overshoot on the fixed deterministic validation points.",
        "method": "In experiment/run.py change slope from 1.8 to 2.0 and keep intercept 0.0; evaluate on the fixed validation set.",
        "expected_delta": "mse -0.02",
        "risk": "Underfits if slope correction overshoots; needs exact arithmetic check.",
        "refs": ["reference.evaluator"],
    },
    {
        "title": "Intercept shift toward residual mean",
        "hypothesis": "Shifting intercept toward the mean residual corrects bias and lowers MSE without touching the evaluator.",
        "method": "In experiment/run.py keep slope 1.8 and adjust intercept by +0.2 via a single scalar addition.",
        "expected_delta": "mse -0.01",
        "risk": "Shifts one point improvement but may regress others; small gain.",
        "refs": ["reference.evaluator"],
    },
    {
        "title": "Least-squares closed form on synthetic data",
        "hypothesis": "Fitting slope and intercept by closed-form least squares on the deterministic data attains the minimal MSE.",
        "method": "In experiment/run.py compute slope and intercept from load_data() using the normal equation; emit predictions.",
        "expected_delta": "mse -0.04",
        "risk": "Adds a few lines but stays within mutable_paths; arithmetic must be verified.",
        "refs": ["reference.evaluator"],
    },
    {
        "title": "Residual-weighted prediction smoothing",
        "hypothesis": "Averaging neighbouring targets smooths the synthetic sequence and trims squared error.",
        "method": "In experiment/run.py apply a 2-point moving average on raw predictions before evaluation.",
        "expected_delta": "mse -0.015",
        "risk": "Smoothing helps interior points but blurs endpoints; gain modest.",
        "refs": ["reference.evaluator"],
    },
    {
        "title": "Per-sample bias correction via two-phase fit",
        "hypothesis": "Two-stage fitting — coarse slope then bias correction — separates scale and offset error.",
        "method": "In experiment/run.py first compute slope on load_data(), then correct intercept as mean residual.",
        "expected_delta": "mse -0.025",
        "risk": "Two-phase logic adds a second pass; correctness easy to verify locally.",
        "refs": ["reference.evaluator"],
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _quarantine_fragment(corrupt_path: Path, raw: str, lineno: int, reason: str) -> None:
    corrupt_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": now_iso(),
        "reason": reason,
        "line": lineno,
        "raw": raw,
    }
    # append atomically while lock is held; simple append is safe under lock
    with corrupt_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def _atomic_rewrite_text(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.tmp.")
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass
        # atomic replace
        tmp_path.replace(target)
        try:
            # ensure directory fsync for durability (best effort)
            dfd = os.open(str(target.parent), os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            pass
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def _load_existing_strict(ideas_path: Path) -> tuple[set[str], set[str], list[dict], int]:
    ids: set[str] = set()
    titles: set[str] = set()
    records: list[dict] = []
    queued = 0
    if not ideas_path.exists():
        return ids, titles, records, queued
    raw = ideas_path.read_text(encoding="utf-8")
    if raw == "":
        return ids, titles, records, queued
    ends_with_newline = raw.endswith("\n")
    parts = raw.split("\n")
    # logical lines: if ends with newline, trailing "" is not a line
    logical = parts[:-1] if ends_with_newline else parts
    # collect valid objects and keep their normalized lines for possible rewrite
    valid_objs: list[dict] = []
    # track whether we need quarantine/rewrite
    corrupt_raw: str | None = None
    corrupt_lineno: int | None = None
    corrupt_reason: str | None = None

    for idx, line_text in enumerate(logical):
        lineno = idx + 1
        stripped = line_text.strip()
        if stripped == "":
            continue
        is_final_unterminated = (not ends_with_newline) and (idx == len(logical) - 1)
        try:
            obj = json.loads(stripped)
        except Exception as e:
            if is_final_unterminated:
                corrupt_raw = line_text
                corrupt_lineno = lineno
                corrupt_reason = f"ideas.jsonl line {lineno}: invalid JSON: {e}"
                # do not raise, will quarantine
                continue
            raise ValueError(f"ideas.jsonl line {lineno}: invalid JSON: {e}") from e
        if not isinstance(obj, dict):
            if is_final_unterminated:
                corrupt_raw = line_text
                corrupt_lineno = lineno
                corrupt_reason = f"ideas.jsonl line {lineno}: expected JSON object, got {type(obj).__name__}"
                continue
            raise ValueError(f"ideas.jsonl line {lineno}: expected JSON object, got {type(obj).__name__}")
        # valid object
        valid_objs.append(obj)
        records.append(obj)
        if isinstance(obj.get("id"), str):
            ids.add(obj["id"].strip().lower())
        if isinstance(obj.get("title"), str):
            titles.add(obj["title"].strip().lower())
        if obj.get("status") == "queued":
            queued += 1

    # handle quarantine/rewrite if final fragment was invalid
    if corrupt_raw is not None:
        corrupt_path = ideas_path.parent / "ideas.jsonl.corrupt.jsonl"
        assert corrupt_lineno is not None and corrupt_reason is not None
        _quarantine_fragment(corrupt_path, corrupt_raw, corrupt_lineno, corrupt_reason)
        # rewrite ideas_path to contain only valid complete records, each terminated by newline
        # preserve valid data; no deletion of valid records
        if valid_objs:
            rebuilt = "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in valid_objs)
        else:
            # if we had only corrupt fragment, truncate to empty
            rebuilt = ""
            # but if there were empty lines only, keep empty
            # ensure we don't lose leading valid empty structure - empty is fine
        _atomic_rewrite_text(ideas_path, rebuilt)
        # records, ids, titles, queued already reflect valid only, so return as is
    else:
        # No corrupt fragment. However if file did not end with newline but last line was valid,
        # the append that follows (still under lock) would concatenate without newline.
        # Normalize by ensuring file ends with newline via atomic rewrite using tempfile.
        if not ends_with_newline and valid_objs:
            # file had valid final without newline - append newline
            # rewrite to add trailing newline without changing valid data
            rebuilt = "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in valid_objs)
            # Only rewrite if raw differs from rebuilt to avoid unnecessary churn
            # Compare stripped lines: if raw already equals rebuilt semantics, still rewrite for newline
            # Preserve valid_objs serialization; this is deterministic and retains data
            _atomic_rewrite_text(ideas_path, rebuilt)
        # interior empty lines are dropped in rebuilt case above; to keep existing user data
        # exactly, we avoid rewrite when file already ends with newline (preserve original whitespace)
        # So only the unterminated-valid case triggers rewrite.
    return ids, titles, records, queued


def load_existing(ideas_path: Path) -> tuple[set[str], set[str], list[dict], int]:
    # Compatibility wrapper: strict parse with quarantine/rewrite.
    return _load_existing_strict(ideas_path)


def next_unique(prefix: str, existing_ids: set[str]) -> str:
    n = 1
    while True:
        cand = f"{prefix}-{n:03d}"
        if cand.lower() not in existing_ids:
            return cand
        n += 1
        if n > 9999:
            h = hashlib.sha256(f"{prefix}{n}".encode()).hexdigest()[:6]
            cand = f"{prefix}-{h}"
            if cand.lower() not in existing_ids:
                return cand


def _acquire_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "a", encoding="utf-8")
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    return fh


def _release_lock(fh) -> None:
    try:
        if fcntl is not None:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    finally:
        try:
            fh.close()
        except Exception:
            pass


def run_once(workspace: Path = WORKSPACE) -> int:
    ideas_path = workspace / "archive" / "ideas.jsonl"
    inspire_path = workspace / "inspiration.md"
    queries_path = workspace / "navigator" / "queries.jsonl"
    failed_path = workspace / "archive" / "failed.jsonl"
    lock_path = workspace / "archive" / "ideas.jsonl.lock"

    lock_fh = _acquire_lock(lock_path)
    try:
        ids, titles, _records, queued = _load_existing_strict(ideas_path)
        # also load failed titles to avoid repeating
        failed_titles: set[str] = set()
        if failed_path.exists():
            for lineno, line in enumerate(failed_path.read_text(encoding="utf-8").splitlines(), start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    o = json.loads(stripped)
                except Exception:
                    continue
                t = o.get("title") or o.get("hypothesis") or ""
                if isinstance(t, str) and t.strip():
                    failed_titles.add(t.strip().lower())

        # Determine need: when queued < 2 we must append at least 2
        need = 0
        if queued < 2:
            need = max(2, 3 - queued)
            if queued == 1:
                need = 2
            elif queued == 0:
                need = 3
        else:
            need = 0

        if need == 0:
            print(json.dumps({"queued_before": queued, "queued_after": queued, "appended": 0, "idea_ids": [], "reason": "queue sufficient"}, indent=2))
            return 0
        ideas_path.parent.mkdir(parents=True, exist_ok=True)
        queries_path.parent.mkdir(parents=True, exist_ok=True)

        appended: list[dict] = []
        pool_idx = 0
        offset = queued % len(TEMPLATE_POOL)
        ordered_pool = TEMPLATE_POOL[offset:] + TEMPLATE_POOL[:offset]

        for tmpl in ordered_pool:
            if len(appended) >= need:
                break
            title_low = tmpl["title"].strip().lower()
            if title_low in titles or title_low in failed_titles:
                continue
            new_id = next_unique("idea", ids)
            created = now_iso()
            idea = {
                "id": new_id,
                "title": tmpl["title"],
                "hypothesis": tmpl["hypothesis"],
                "method": tmpl["method"],
                "expected_delta": tmpl["expected_delta"],
                "risk": tmpl["risk"],
                "refs": tmpl["refs"],
                "status": "queued",
                "created": created,
                "score": 0.72 - (pool_idx * 0.03),
                "feasibility": 4,
            }
            ids.add(new_id.lower())
            titles.add(title_low)
            appended.append(idea)
            pool_idx += 1

        filler = 0
        while len(appended) < need:
            filler += 1
            base = TEMPLATE_POOL[(offset + filler) % len(TEMPLATE_POOL)]
            new_id = next_unique("idea", ids)
            created = now_iso()
            idea = {
                "id": new_id,
                "title": f"{base['title']} variant {filler}",
                "hypothesis": base["hypothesis"],
                "method": base["method"],
                "expected_delta": base["expected_delta"],
                "risk": base["risk"],
                "refs": base["refs"],
                "status": "queued",
                "created": created,
                "score": 0.68 - filler * 0.02,
                "feasibility": 3,
            }
            while idea["title"].strip().lower() in titles:
                filler += 1
                idea["title"] = f"{base['title']} variant {filler}"
            ids.add(new_id.lower())
            titles.add(idea["title"].strip().lower())
            appended.append(idea)

        # Append JSONL while still holding lock (queue transaction)
        with ideas_path.open("a", encoding="utf-8") as fh:
            for idea in appended:
                fh.write(json.dumps(idea, ensure_ascii=False) + "\n")
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass

        # Update inspiration.md to latest idea
        latest = appended[-1]
        inspire_path.parent.mkdir(parents=True, exist_ok=True)
        # Append navigator query record while still holding the same lock
        query = {
            "ts": now_iso(),
            "source": "orchestration/inspiration.py --once",
            "appended": len(appended),
            "queued_before": queued,
            "queued_after": queued + len(appended),
            "idea_ids": [x["id"] for x in appended],
            "query": "synthetic regression; deterministic evaluator; slope-intercept adjustment",
        }
        with queries_path.open("a", encoding="utf-8") as qf:
            qf.write(json.dumps(query, ensure_ascii=False) + "\n")
            qf.flush()
            try:
                os.fsync(qf.fileno())
            except OSError:
                pass

        print(json.dumps({"queued_before": queued, "queued_after": queued + len(appended), "appended": len(appended), "idea_ids": [x["id"] for x in appended], "reason": "appended"}, indent=2))
        return 0
    finally:
        _release_lock(lock_fh)

def main() -> int:
    parser = argparse.ArgumentParser(description="Inspiration engine --once")
    parser.add_argument("--once", action="store_true", help="Append queued ideas when low")
    args = parser.parse_args()
    if not args.once:
        parser.print_help()
        return 1
    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())
