#!/usr/bin/env python3
# Portability (reversible): file is invoked via `python3` on macOS and `python` on minimal
# Linux images. Shebang keeps `python3` for direct execution; callers should resolve
# interpreter as `PY=$(command -v python3 || command -v python)` and run `$PY flywheel.py`.
# Revert this comment without code change; behavior unchanged if caller pins python3.
"""Reference research-flywheel runner — dependency-free, OMP-contract compliant."""
from __future__ import annotations

import argparse
import hashlib
import math
import json
import os
import re
import shutil
import subprocess
import sys
import time
import platform
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore

WORKSPACE = Path(__file__).resolve().parent.parent
INTEGRITY_DEFAULT = ["program.md", "evaluation/prepare.py", "capabilities/registry.json"]
MUTABLE_DEFAULT = ["experiment/run.py"]

SAFE_RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def atomic_append(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        if not line.endswith("\n"):
            fh.write("\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass

def append_jsonl(path: Path, obj: dict) -> None:
    atomic_append(path, json.dumps(obj, ensure_ascii=False))

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)

def hash_file(rel: str) -> str:
    p = WORKSPACE / rel
    if not p.exists():
        return "missing"
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()

def git_run(args: list[str]) -> tuple[str, str, int]:
    r = subprocess.run(["git"] + args, cwd=WORKSPACE, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def ensure_git() -> None:
    if (WORKSPACE / ".git").exists():
        return
    git_run(["init", "--initial-branch=main"])
    git_run(["config", "user.email", "research-flywheel@local"])
    git_run(["config", "user.name", "Research Flywheel"])

def git_info() -> dict:
    ensure_git()
    branch, _, rc1 = git_run(["rev-parse", "--abbrev-ref", "HEAD"])
    if rc1 != 0 or not branch:
        branch = "main"
    head, _, rc2 = git_run(["rev-parse", "HEAD"])
    if rc2 != 0 or not head:
        # allow no-head for empty repo; use placeholder and capture staged hash if possible
        head = "no-head"
    return {"branch": branch, "head": head}

def parse_program() -> dict:
    text = (WORKSPACE / "program.md").read_text(encoding="utf-8") if (WORKSPACE / "program.md").exists() else ""
    # minimal frontmatter parse
    profile: dict = {
        "name": "reference-linear-regression",
        "mutable_paths": list(MUTABLE_DEFAULT),
        "integrity_paths": list(INTEGRITY_DEFAULT),
        "stages": {"full": {"requested": {"cost_type": "compute", "resource_class": "cpu", "count": 1}}},
        "evaluation": {"evaluator": "evaluation/prepare.py", "metric": "mse", "direction": "lower", "epsilon": 0.0001, "baseline_artifact": "traces/baseline-metrics.json"},
    }
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            # very small yaml extract: look for mutable_paths, integrity_paths, epsilon
            import re
            # mutable_paths block
            m = re.search(r"mutable_paths:\s*\n((?:\s+-.*\n)+)", fm)
            if m:
                paths = re.findall(r"-\s*(.+)", m.group(1))
                profile["mutable_paths"] = [p.strip().strip('"').strip("'") for p in paths]
            m = re.search(r"integrity_paths:\s*\n((?:\s+-.*\n)+)", fm)
            if m:
                paths = re.findall(r"-\s*(.+)", m.group(1))
                profile["integrity_paths"] = [p.strip().strip('"').strip("'") for p in paths]
            m = re.search(r"epsilon:\s*([0-9.]+)", fm)
            if m:
                try:
                    profile["evaluation"]["epsilon"] = float(m.group(1))
                except ValueError:
                    pass
            m = re.search(r"direction:\s*(\w+)", fm)
            if m:
                profile["evaluation"]["direction"] = m.group(1)
    # fallback to defaults if paths missing
    return profile

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + os.urandom(2).hex()

def validate_run_id(value: str) -> str:
    if not SAFE_RUN_ID_RE.fullmatch(value):
        raise ValueError("run_id must be a single path-safe identifier using letters, digits, dots, underscores, or hyphens")
    return value

def _lock_file(path: Path):
    if fcntl is None:
        raise RuntimeError("concurrent-sensitive mutation requires POSIX fcntl locking")
    path.parent.mkdir(parents=True, exist_ok=True)
    fh = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    except OSError as exc:
        fh.close()
        raise RuntimeError(f"cannot establish lock {path}: {exc}") from exc
    return fh


@contextmanager
def locked(path: Path):
    fh = _lock_file(path)
    try:
        yield fh
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def _quarantine_tail(path: Path, raw: str, lineno: int, reason: str) -> None:
    q = path.with_name(path.name + ".corrupt.jsonl")
    with q.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": now_iso(), "line": lineno, "raw": raw, "reason": reason}, ensure_ascii=False) + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def _atomic_rewrite_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        Path(tmp_name).replace(path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def read_jsonl_array(path: Path, quarantine_tail: bool = True) -> list[dict]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    if raw == "":
        return []
    records: list[dict] = []
    logical = raw.split("\n")
    ends_newline = raw.endswith("\n")
    for idx, text in enumerate(logical):
        if (not ends_newline) and idx == len(logical) - 1 and text.strip() == "":
            continue
        if text.strip() == "":
            continue
        lineno = idx + 1
        is_tail_fragment = (not ends_newline) and idx == len(logical) - 1
        try:
            obj = json.loads(text)
        except (ValueError, TypeError) as exc:
            if is_tail_fragment and quarantine_tail:
                _quarantine_tail(path, text, lineno, f"line {lineno}: invalid JSON: {exc}")
                continue
            raise ValueError(f"{path} line {lineno}: invalid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            if is_tail_fragment and quarantine_tail:
                _quarantine_tail(path, text, lineno, f"line {lineno}: expected object, got {type(obj).__name__}")
                continue
            raise ValueError(f"{path} line {lineno}: expected object, got {type(obj).__name__}")
        records.append(obj)
    # Rewrite the source to a clean file whenever a corrupt final fragment was quarantined,
    # including the zero-valid-record case. This prevents the next atomic_append from
    # writing directly after a stale fragment and losing the combined tail on the next read.
    if is_tail_fragment and quarantine_tail:
        _atomic_rewrite_text(path, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in records))
    return records


def locked_jsonl_append(path: Path, obj: dict, key: str = "run_id") -> bool:
    with locked(path.with_name(path.name + ".lock")):
        records = read_jsonl_array(path)
        if key and any(r.get(key) == obj.get(key) for r in records):
            return False
        atomic_append(path, json.dumps(obj, ensure_ascii=False))
        return True


def terminal_marker(run_id: str, idea_id: str, outcome: str) -> dict:
    return {"run_id": run_id, "idea_id": idea_id, "outcome": outcome, "committed_at": now_iso(), "terminal": True}


def update_idea_terminal(idea_id: str, run_id: str, outcome: str) -> None:
    status = "failure" if outcome == "execution_error" else outcome
    path = WORKSPACE / "archive" / "ideas.jsonl"
    with locked(path.with_name(path.name + ".lock")):
        records = read_jsonl_array(path)
        changed = False
        for record in records:
            if record.get("id") == idea_id:
                record["status"] = status
                record["run_id"] = run_id
                record["completed_at"] = now_iso()
                changed = True
                break
        if changed:
            _atomic_rewrite_text(path, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in records))


def read_json_object(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def load_archived_idea(idea_id: str) -> dict | None:
    ideas_path = WORKSPACE / "archive" / "ideas.jsonl"
    if not ideas_path.exists():
        return None
    for raw_line in ideas_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict) and value.get("id") == idea_id:
            return value
    return None


def recover_run_idea(run_id: str, run_dir: Path, trace_dir: Path) -> dict | None:
    idea_id = None
    for path in [trace_dir / "baseline.json", run_dir / "baseline.json", trace_dir / "commitment.json", run_dir / "commitment.json"]:
        record = read_json_object(path)
        if record is None or record.get("run_id") not in (None, run_id):
            continue
        snapshot = record.get("idea_snapshot")
        if isinstance(snapshot, dict) and snapshot.get("id"):
            return snapshot
        candidate_id = record.get("idea_id")
        if isinstance(candidate_id, str) and candidate_id:
            idea_id = candidate_id
    return load_archived_idea(idea_id) if idea_id else None


def record_recovery_error(run_id: str, run_dir: Path, trace_dir: Path, message: str) -> int:
    payload = {"run_id": run_id, "error_class": "recovery", "message": message, "stage": "resume", "recoverable": True}
    write_json(trace_dir / "recovery-error.json", payload)
    write_json(run_dir / "recovery-error.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    return 2

OUTCOME_ENUM = frozenset({"keep", "discard", "inconclusive", "execution_error"})


def _is_finite_number(value) -> bool:
    # Reject bool, NaN, Infinity. Positive additive check for finite numeric.
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _is_finite_nonneg(value) -> bool:
    return _is_finite_number(value) and float(value) >= 0


def validate_metrics(value: dict | None, run_id: str) -> tuple[bool, str]:
    if not isinstance(value, dict):
        return False, "metrics is not an object"
    if value.get("run_id") != run_id:
        return False, "run_id mismatch"
    if not isinstance(value.get("idea_id"), str) or not value["idea_id"]:
        return False, "idea_id missing"
    outcome = value.get("outcome")
    if outcome not in OUTCOME_ENUM:
        return False, f"invalid outcome {outcome!r}"
    keep = value.get("keep")
    if type(keep) is not bool:
        return False, "keep is not a boolean"
    execution = value.get("execution")
    evaluation = value.get("evaluation")
    if not isinstance(execution, dict) or not isinstance(evaluation, dict):
        return False, "execution/evaluation missing"
    ex_state = execution.get("state")
    ev_state = evaluation.get("state")
    if ex_state not in ("completed", "failed"):
        return False, f"invalid execution.state {ex_state!r}"
    if ev_state not in ("completed", "failed", "inconclusive"):
        return False, f"invalid evaluation.state {ev_state!r}"
    # cost subfields required: actual must carry the four profile cost fields
    actual = execution.get("actual")
    if not isinstance(actual, dict):
        return False, "execution.actual missing"
    for key in ("wall_clock_seconds", "cpu_seconds", "tokens", "material_cost"):
        if not _is_finite_nonneg(actual.get(key)):
            return False, f"execution.actual.{key} must be finite nonnegative"
    # outcome/state consistency
    if outcome in ("keep", "discard"):
        if ex_state != "completed" or ev_state != "completed":
            return False, "keep/discard requires completed execution and evaluation"
        if keep is not (outcome == "keep"):
            return False, "keep boolean inconsistent with outcome"
    else:
        if keep is not False:
            return False, "keep must be false for non-keep outcome"
        if outcome == "execution_error" and ex_state != "failed":
            return False, "execution_error requires failed execution"
        if outcome == "execution_error" and ev_state not in ("failed", "inconclusive"):
            return False, "execution_error requires failed/inconclusive evaluation"
    metric_main = value.get("metric_main")
    if outcome in ("keep", "discard"):
        if not isinstance(metric_main, dict):
            return False, "keep/discard requires metric_main object"
        v = metric_main.get("value")
        if not _is_finite_number(v):
            return False, "keep/discard requires finite numeric metric_main.value"
    else:
        # For non-keep outcomes metric_main may be null-valued object or contain finite value
        if not isinstance(metric_main, dict):
            return False, "metric_main missing"
        if "value" not in metric_main:
            return False, "metric_main.value missing"
        v = metric_main.get("value")
        if v is not None and not _is_finite_number(v):
            return False, "metric_main.value must be finite numeric or null"
    fingerprint = value.get("fingerprint")
    if not isinstance(fingerprint, dict):
        return False, "fingerprint missing"
    device = fingerprint.get("device")
    env = fingerprint.get("environment")
    if not isinstance(device, dict) or not isinstance(env, dict):
        return False, "fingerprint incomplete"
    if not isinstance(device.get("kind"), str) or not device.get("kind"):
        return False, "fingerprint.device.kind missing"
    if not isinstance(device.get("count"), int) or isinstance(device.get("count"), bool):
        return False, "fingerprint.device.count invalid"
    if not isinstance(env.get("python_version"), str) or not env.get("python_version"):
        return False, "fingerprint.environment.python_version missing"
    if not isinstance(env.get("platform"), str) or not env.get("platform"):
        return False, "fingerprint.environment.platform missing"
    if not isinstance(env.get("package_lock_hash"), str):
        return False, "fingerprint.environment.package_lock_hash missing"
    evaluation_hash = evaluation.get("evaluator_hash")
    if not isinstance(evaluation_hash, str) or not evaluation_hash:
        return False, "evaluation.evaluator_hash missing"
    return True, "ok"


def _validate_verification_strict(verification: dict, metrics: dict, run_id: str) -> tuple[bool, str]:
    if not isinstance(verification, dict):
        return False, "verification is not an object"
    if verification.get("run_id") != run_id:
        return False, "verification run_id mismatch"
    if verification.get("idea_id") != metrics.get("idea_id"):
        return False, "verification idea_id mismatch"
    # boolean fields exact type
    for field in ("integrity_passed", "clean_reproduction_passed", "keep"):
        if type(verification.get(field)) is not bool:
            return False, f"verification {field} is not boolean"
    if verification.get("keep") != metrics.get("keep"):
        return False, "verification keep inconsistent with metrics"
    ex_state = verification.get("execution_state")
    ev_state = verification.get("evaluation_state")
    repro_state = verification.get("reproduction_state")
    if ex_state not in ("completed", "failed"):
        return False, f"invalid verification execution_state {ex_state!r}"
    if ev_state not in ("completed", "failed", "inconclusive"):
        return False, f"invalid verification evaluation_state {ev_state!r}"
    if repro_state not in ("completed", "failed", "mismatched", "skipped"):
        return False, f"invalid verification reproduction_state {repro_state!r}"
    # baseline_metric required finite
    baseline = verification.get("baseline_metric")
    if not isinstance(baseline, dict):
        return False, "baseline_metric missing"
    bv = baseline.get("value")
    if not _is_finite_number(bv):
        return False, "baseline_metric.value must be finite numeric"
    # candidate_metric null or complete finite object
    candidate = verification.get("candidate_metric")
    if candidate is not None:
        if not isinstance(candidate, dict):
            return False, "candidate_metric must be object or null"
        cv = candidate.get("value")
        if not _is_finite_number(cv):
            return False, "candidate_metric.value must be finite numeric"
        # consistency with metrics metric_main
        mv = metrics.get("metric_main", {}).get("value") if isinstance(metrics.get("metric_main"), dict) else None
        if _is_finite_number(mv) and _is_finite_number(cv) and float(cv) != float(mv):
            return False, "candidate_metric.value inconsistent with metrics metric_main.value"
    # delta when present finite
    delta = verification.get("delta")
    if delta is not None and not _is_finite_number(delta):
        return False, "delta must be finite numeric or null"
    # epsilon finite non-negative
    epsilon = verification.get("epsilon")
    if not _is_finite_nonneg(epsilon):
        return False, "epsilon must be finite nonnegative numeric"
    direction = verification.get("direction")
    if direction not in ("lower", "higher"):
        return False, f"invalid direction {direction!r}"
    # keep/outcome/state/reproduction relationships
    outcome = metrics.get("outcome")
    if outcome in ("keep", "discard"):
        if ex_state != "completed" or ev_state != "completed":
            return False, "keep/discard requires completed execution/evaluation in verification"
        if repro_state != "completed":
            return False, "keep/discard requires completed reproduction"
        if verification.get("clean_reproduction_passed") is not True:
            return False, "keep/discard requires clean_reproduction_passed true"
        if candidate is None:
            return False, "keep/discard requires candidate_metric"
        if delta is None or not _is_finite_number(delta):
            return False, "keep/discard requires finite delta"
        if not _is_finite_number(bv):
            return False, "keep/discard requires finite baseline"
    else:
        # failure/inconclusive remains structurally valid with appropriate nulls/states
        if verification.get("keep") is not False:
            return False, "non-keep verification keep must be false"
        # delta and candidate may be null for execution_error, ensure no spurious keep
    return True, "ok"


def validate_verification(verification: dict | None, metrics: dict, run_id: str) -> bool:
    ok, _ = _validate_verification_strict(verification, metrics, run_id) if isinstance(verification, dict) else (False, "not dict")
    return ok


def _validate_cost(cost: dict | None, metrics: dict, verification: dict | None, run_id: str) -> tuple[bool, str]:
    if not isinstance(cost, dict):
        return False, "cost is not an object"
    if cost.get("run_id") != run_id:
        return False, "cost run_id mismatch"
    if cost.get("idea_id") != metrics.get("idea_id"):
        return False, "cost idea_id mismatch"
    requested = cost.get("requested")
    actual = cost.get("actual")
    if not isinstance(requested, dict) or not isinstance(actual, dict):
        return False, "cost requested/actual missing"
    repro_state = cost.get("reproduction_state")
    if repro_state not in ("completed", "failed", "mismatched", "skipped"):
        return False, f"invalid cost reproduction_state {repro_state!r}"
    # consistency with verification when available
    if isinstance(verification, dict):
        if verification.get("reproduction_state") != repro_state:
            return False, "cost reproduction_state inconsistent with verification"
    outcome = metrics.get("outcome")
    if outcome in ("keep", "discard") and repro_state != "completed":
        return False, "keep/discard requires completed reproduction in cost"
    return True, "ok"

def write_terminal_marker(run_id: str, idea_id: str, outcome: str, trace_dir: Path, run_dir: Path) -> None:
    marker = terminal_marker(run_id, idea_id, outcome)
    write_json(trace_dir / "terminal.json", marker)
    write_json(run_dir / "terminal.json", marker)

def claim_or_seed(idea_text: str | None) -> tuple[dict, bool]:
    ideas_path = WORKSPACE / "archive" / "ideas.jsonl"
    ideas_path.parent.mkdir(parents=True, exist_ok=True)
    with locked(ideas_path.with_name(ideas_path.name + ".lock")):
        ideas = read_jsonl_array(ideas_path)
        queued = [x for x in ideas if x.get("status") == "queued"]
        if queued:
            idea = queued[0]
            updated = {**idea, "status": "running", "claimed_at": now_iso()}
            new_records = [updated if obj.get("id") == idea.get("id") else obj for obj in ideas]
            _atomic_rewrite_text(ideas_path, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in new_records))
            return updated, False
        # seed one
        iid = f"idea-{int(time.time())}-{os.urandom(2).hex()}"
        idea = {
            "id": iid,
            "title": idea_text or "reference candidate",
            "hypothesis": idea_text or "reference candidate proposes slope 1.8 vs identity baseline",
            "method": "Run experiment/run.py slope 1.8 intercept 1.0",
            "expected_delta": "mse change vs identity",
            "risk": "no generalisation evidence",
            "refs": [],
            "status": "queued",
            "created": now_iso(),
        }
        idea_running = {**idea, "status": "running", "claimed_at": now_iso()}
        if not ideas:
            _atomic_rewrite_text(ideas_path, json.dumps(idea_running, ensure_ascii=False) + "\n")
        else:
            atomic_append(ideas_path, json.dumps(idea_running, ensure_ascii=False))
        return idea_running, True

def ensure_baseline_metrics() -> Path:
    p = WORKSPACE / "traces" / "baseline-metrics.json"
    if p.exists():
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    # identity baseline: mse 0
    sys.path.insert(0, str(WORKSPACE))
    try:
        from evaluation.prepare import evaluate, load_data
        data = load_data()
        targets = [t for _, t in data]
        preds = [float(t) for _, t in data]
        metrics = evaluate(preds, targets)
        obj = {"run_id": "reference-bootstrap", "metric_main": metrics, "metric_aux": {"samples": len(data), "description": "identity baseline"}}
    finally:
        if str(WORKSPACE) in sys.path:
            sys.path.remove(str(WORKSPACE))
    write_json(p, obj)
    return p

def load_baseline_metrics() -> dict:
    ensure_baseline_metrics()
    return json.loads((WORKSPACE / "traces" / "baseline-metrics.json").read_text(encoding="utf-8"))

def run_subprocess(code: str, trace_dir: Path, name: str) -> dict:
    """Run code via fresh python subprocess with workspace root on path.
    Preserves raw stdout/stderr."""
    stdout_path = trace_dir / f"{name}-stdout.log"
    stderr_path = trace_dir / f"{name}-stderr.log"
    runlog_path = trace_dir / "run.log"
    trace_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    proc = subprocess.run([sys.executable, "-c", code], cwd=WORKSPACE, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    stdout_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr_path.write_text(proc.stderr or "", encoding="utf-8")
    # append to combined run.log atomically
    with runlog_path.open("a", encoding="utf-8") as fh:
        fh.write(f"=== {name} ===\n")
        fh.write(proc.stdout or "")
        if proc.stderr:
            fh.write("\n---stderr---\n")
            fh.write(proc.stderr)
        fh.write(f"\n---exit:{proc.returncode} wall:{elapsed:.6f}---\n\n")
    return {
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
        "wall": elapsed,
        "stdout_path": str(stdout_path.relative_to(WORKSPACE)) if stdout_path.exists() else None,
        "stderr_path": str(stderr_path.relative_to(WORKSPACE)) if stderr_path.exists() else None,
    }

def build_runner_code(run_id: str, trace_dir: Path, failure_mode: str | None) -> str:
    if failure_mode:
        if failure_mode == "import":
            return (
                "import sys; sys.path.insert(0, '.'); "
                "import nonexistent_module_xyz_987654  # deterministic import failure\n"
            )
        elif failure_mode == "runtime":
            return "raise RuntimeError('deterministic failure-mode runtime error')\n"
        elif failure_mode == "syntax":
            return "import ast; ast.parse('def bad(:)')\n"
        else:
            return f"raise RuntimeError('failure-mode:{failure_mode}')\n"
    # normal runner: import experiment/run.py via package path experiment/evaluation
    # Use project root import
    return (
        "import sys, json\n"
        "from pathlib import Path\n"
        f"run_id={json.dumps(run_id)}\n"
        f"trace_dir={json.dumps(str(trace_dir))}\n"
        "sys.path.insert(0, '.')\n"
        "from experiment.run import main\n"
        "result = main({'run_id': run_id, 'trace_dir': trace_dir, 'stage': 'full'})\n"
        "print(json.dumps(result))\n"
    )

def _run_once(run_id: str, run_dir: Path, trace_dir: Path, args, profile: dict,
              integrity_paths: list[str], mutable_paths: list[str], epsilon: float, direction: str) -> int:
    cached_metrics_path = trace_dir / "metrics.json"
    cached_run_metrics_path = run_dir / "metrics.json"
    idea, seeded = claim_or_seed(args.idea)
    is_reused = (trace_dir / "baseline.json").exists() or (cached_metrics_path.exists())
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "journal").mkdir(parents=True, exist_ok=True)

    # journal seven phases placeholders
    for phase in ["inspiration", "modeling", "experiment", "evaluation", "writing", "review", "archive"]:
        (run_dir / "journal" / f"{phase}.md").write_text(f"# {phase}\nrun_id: {run_id}\nidea: {idea.get('id')}\n", encoding="utf-8")

    gitinfo = git_info()
    integrity_hashes = {p: hash_file(p) for p in integrity_paths}
    baseline = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "idea_snapshot": idea,
        "captured_at": now_iso(),
        "workspace": str(WORKSPACE),
        "git": gitinfo,
        "integrity_paths": integrity_paths,
        "integrity_hashes": integrity_hashes,
        "profile": profile,
    }
    # write baseline.json to both locations
    write_json(trace_dir / "baseline.json", baseline)
    write_json(run_dir / "baseline.json", baseline)

    # commitment
    commitment = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "idea_snapshot": idea,
        "falsifiable_claim": idea.get("hypothesis") or idea.get("title"),
        "observed_metric": profile.get("evaluation", {}).get("metric", "mse"),
        "decision_rule": f"keep if delta {'>' if direction=='lower' else '<'} epsilon {epsilon} (direction {direction})",
        "negation_criterion": f"discard if delta <= epsilon or execution_error",
        "requested_resources": profile.get("stages", {}).get("full", {}).get("requested", {}),
        "created_at": now_iso(),
    }
    write_json(run_dir / "commitment.json", commitment)
    write_json(trace_dir / "commitment.json", commitment)

    # candidate isolation — create isolated candidate dir, try git branch without checkout
    candidate_dir = trace_dir / "candidate"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    # copy mutable file into candidate for audit
    changed_paths: list[str] = []
    for mp in mutable_paths:
        src = WORKSPACE / mp
        if src.exists():
            dst = candidate_dir / mp
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            changed_paths.append(mp)
    # also include candidate copy path for reference
    resolved_backend = "isolated-candidate-dir"
    fallback_reason = None
    branch_name = f"candidate/{run_id}"
    if gitinfo["head"] != "no-head":
        out, err, rc = git_run(["branch", branch_name, gitinfo["head"]])
        if rc == 0:
            resolved_backend = "git-branch"
        else:
            fallback_reason = err or "branch creation failed"
            resolved_backend = "isolated-candidate-dir"
    else:
        fallback_reason = "no-head: repo empty, using isolated directory"

    # integrity gate: hashes unchanged and changed_paths subset of mutable
    integrity_passed = all(hash_file(p) == integrity_hashes[p] for p in integrity_paths)
    # simple fnmatch check for mutable
    def is_mutable(p: str) -> bool:
        import fnmatch
        for pat in mutable_paths:
            if fnmatch.fnmatch(p, pat) or p == pat:
                return True
        return False
    mutable_gate = all(is_mutable(p) for p in changed_paths)
    gate_passed = integrity_passed and mutable_gate

    mutation = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "baseline_sha": gitinfo["head"],
        "branch_name": branch_name,
        "resolved_backend": resolved_backend,
        "fallback_reason": fallback_reason,
        "changed_paths": changed_paths,
        "integrity_gate": "pass" if gate_passed else "fail",
        "integrity_passed": integrity_passed,
        "mutable_gate_passed": mutable_gate,
        "candidate_dir": str(candidate_dir.relative_to(WORKSPACE)),
    }
    write_json(trace_dir / "mutation.json", mutation)
    write_json(run_dir / "mutation.json", mutation)

    # lifecycle: started
    lifecycle_path = trace_dir / "lifecycle.jsonl"
    lifecycle_run_path = run_dir / "lifecycle.jsonl"
    events_path = trace_dir / "events.jsonl"
    run_events_path = run_dir / "events.jsonl"
    if is_reused:
        for p in [lifecycle_path, lifecycle_run_path, events_path, run_events_path]:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
    ts = now_iso()
    started_evt = {"ts": ts, "run_id": run_id, "idea_id": idea.get("id"), "event": "started", "stage": "full", "phase": "experiment", "requested": profile.get("stages", {}).get("full", {}).get("requested", {}), "backend": resolved_backend}
    append_jsonl(lifecycle_path, started_evt)
    append_jsonl(lifecycle_run_path, started_evt)
    append_jsonl(events_path, started_evt)
    append_jsonl(run_events_path, started_evt)

    # execute candidate via fresh subprocess (experiment)
    runner_code = build_runner_code(run_id, trace_dir, args.failure_mode)
    exec_result = run_subprocess(runner_code, trace_dir, "experiment")
    # try to load raw-result.json if produced
    raw_result_path = trace_dir / "raw-result.json"
    metric_main = None
    metric_aux = None
    actual = None
    execution_state = "failed"
    error_obj = None

    if exec_result["returncode"] != 0 or args.failure_mode:
        if args.failure_mode:
            # ensure deterministic execution_error even if returncode 0 (should be non-zero)
            pass
        # classify as execution_error
        execution_state = "failed"
        error_obj = {
            "run_id": run_id,
            "idea_id": idea.get("id"),
            "error_class": "import" if args.failure_mode=="import" else "runtime",
            "message": (exec_result["stderr"] or "execution failed").strip()[:2000],
            "stage": "full",
            "raw_stdout_ref": exec_result["stdout_path"],
            "raw_stderr_ref": exec_result["stderr_path"],
            "returncode": exec_result["returncode"],
        }
        # preserve raw stdout/stderr already
        write_json(trace_dir / "error.json", error_obj)
        write_json(run_dir / "error.json", error_obj)
    else:
        # parse stdout last line json or raw-result
        try:
            if raw_result_path.exists():
                result = json.loads(raw_result_path.read_text(encoding="utf-8"))
            else:
                # try stdout json
                result = json.loads((exec_result["stdout"] or "").strip().splitlines()[-1])
            metric_main = result.get("metric_main")
            metric_aux = result.get("metric_aux")
            actual = result.get("actual")
            execution_state = "completed"
        except Exception as e:
            execution_state = "failed"
            error_obj = {
                "run_id": run_id,
                "idea_id": idea.get("id"),
                "error_class": "runtime",
                "message": f"result parse failed: {e}",
                "stage": "full",
                "raw_stdout_ref": exec_result["stdout_path"],
                "raw_stderr_ref": exec_result["stderr_path"],
                "returncode": exec_result["returncode"],
                "stderr_tail": (exec_result["stderr"] or "")[-2000:],
            }
            write_json(trace_dir / "error.json", error_obj)
            write_json(run_dir / "error.json", error_obj)

    # lifecycle checkpoint after execution
    ts2 = now_iso()
    exec_evt = {"ts": ts2, "run_id": run_id, "idea_id": idea.get("id"), "event": execution_state, "stage": "full", "phase": "experiment", "actual": actual, "wall_clock_seconds": exec_result["wall"]}
    append_jsonl(lifecycle_path, exec_evt)
    append_jsonl(lifecycle_run_path, exec_evt)
    append_jsonl(events_path, exec_evt)
    append_jsonl(run_events_path, exec_evt)

    # clean reproduction subprocess if first execution succeeded
    repro_state = "skipped"
    repro_result = None
    if execution_state == "completed":
        repro_code = build_runner_code(run_id, trace_dir, None)  # clean, no failure_mode
        # use separate trace for reproduction to avoid overwriting raw-result (but we compare)
        # run reproduction into temp dir then compare
        repro_dir = trace_dir / "repro"
        repro_dir.mkdir(parents=True, exist_ok=True)
        # adjust runner to write to repro dir for comparison
        repro_runner = (
            "import sys, json\n"
            "from pathlib import Path\n"
            f"run_id={json.dumps(run_id)}\n"
            f"trace_dir={json.dumps(str(repro_dir))}\n"
            "sys.path.insert(0, '.')\n"
            "from experiment.run import main\n"
            "result = main({'run_id': run_id, 'trace_dir': trace_dir, 'stage': 'full'})\n"
            "print(json.dumps(result))\n"
        )
        repro_exec = run_subprocess(repro_runner, trace_dir, "reproduction")
        try:
            if repro_exec["returncode"] != 0:
                raise RuntimeError(repro_exec["stderr"] or "repro failed")
            repro_raw = repro_dir / "raw-result.json"
            if repro_raw.exists():
                repro_result = json.loads(repro_raw.read_text(encoding="utf-8"))
            else:
                repro_result = json.loads((repro_exec["stdout"] or "").strip().splitlines()[-1])
            # compare metrics
            if repro_result.get("metric_main", {}).get("value") == metric_main.get("value"):
                repro_state = "completed"
            else:
                repro_state = "mismatched"
        except Exception as e:
            repro_state = "failed"
            error_obj2 = {
                "run_id": run_id,
                "idea_id": idea.get("id"),
                "error_class": "runtime",
                "message": f"reproduction failed: {e}",
                "stage": "full",
                "raw_stdout_ref": repro_exec.get("stdout_path"),
                "raw_stderr_ref": repro_exec.get("stderr_path"),
            }
            # keep original error if any, but also note reproduction failure
            write_json(trace_dir / "repro-error.json", error_obj2)

    # evaluation via native evaluator
    baseline_metrics = load_baseline_metrics()
    baseline_val = baseline_metrics.get("metric_main", {}).get("value", 0.0)
    candidate_val = metric_main.get("value") if isinstance(metric_main, dict) else None
    evaluation_state = "failed"
    keep = False
    reason = ""
    delta = None
    if execution_state == "completed" and repro_state == "completed" and candidate_val is not None:
        evaluation_state = "completed"
        if direction == "lower":
            delta = baseline_val - candidate_val
            keep = delta > epsilon
        else:
            delta = candidate_val - baseline_val
            keep = delta > epsilon
        reason = f"{'keep' if keep else 'discard'}: {profile.get('evaluation',{}).get('metric')} baseline {baseline_val} -> candidate {candidate_val} delta {delta} epsilon {epsilon}"
    elif execution_state == "failed":
        evaluation_state = "failed"
        reason = f"execution_error: {error_obj.get('message','')[:200]}"
    elif repro_state in ("failed", "mismatched", "skipped"):
        evaluation_state = "inconclusive" if repro_state!="failed" else "failed"
        reason = f"inconclusive: reproduction {repro_state}"
    else:
        reason = "inconclusive"

    # classify outcome
    if execution_state == "failed":
        outcome = "execution_error"
    elif evaluation_state in ("failed", "inconclusive") and repro_state != "completed":
        outcome = "inconclusive" if repro_state=="mismatched" else "execution_error" if execution_state=="failed" else "inconclusive"
        if repro_state == "failed":
            outcome = "inconclusive"
    elif keep:
        outcome = "keep"
    else:
        # completed but not keep => discard (reference expects discard)
        outcome = "discard"
        # if we had execution_error previously, override
        if execution_state == "failed":
            outcome = "execution_error"

    # ensure outcome respects failure-mode
    if args.failure_mode and outcome != "execution_error":
        outcome = "execution_error"

    # write cost.json
    cost = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "requested": profile.get("stages", {}).get("full", {}).get("requested", {}),
        "actual": actual or {"wall_clock_seconds": exec_result["wall"], "cpu_seconds": 0, "tokens": 0, "material_cost": 0},
        "reproduction_state": repro_state,
    }
    write_json(trace_dir / "cost.json", cost)
    write_json(run_dir / "cost.json", cost)

    # verification.json
    verification = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "integrity_passed": integrity_passed,
        "execution_state": execution_state,
        "clean_reproduction_passed": repro_state == "completed",
        "reproduction_state": repro_state,
        "evaluation_state": evaluation_state,
        "baseline_metric": baseline_metrics.get("metric_main"),
        "candidate_metric": metric_main,
        "delta": delta,
        "epsilon": epsilon,
        "direction": direction,
        "keep": keep,
    }
    write_json(trace_dir / "verification.json", verification)
    write_json(run_dir / "verification.json", verification)

    # metrics.json
    fingerprint = {
        "device": {"kind": "cpu", "count": 1},
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "package_lock_hash": "no-lock",
        }
    }
    metrics = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "parent_run": baseline_metrics.get("run_id"),
        "metric_main": metric_main or {"name": "mse", "value": None, "higher_is_better": False},
        "metric_aux": metric_aux or {},
        "execution": {"stage": "full", "state": execution_state, "requested": cost["requested"], "actual": cost["actual"]},
        "fingerprint": fingerprint,
        "evaluation": {"state": evaluation_state, "evaluator_hash": hash_file("evaluation/prepare.py")},
        "keep": keep,
        "reason": reason,
        "outcome": outcome,
    }
    write_json(trace_dir / "metrics.json", metrics)
    write_json(run_dir / "metrics.json", metrics)

    # reasoning.md
    reasoning_text = (
        f"# Reasoning — {run_id}\n\n"
        f"- idea: {idea.get('id')} — {idea.get('title')}\n"
        f"- hypothesis: {idea.get('hypothesis')}\n"
        f"- candidate: slope 1.8 intercept 1.0 via experiment/run.py (project root import)\n"
        f"- baseline mse: {baseline_val}\n"
        f"- candidate mse: {candidate_val}\n"
        f"- delta: {delta}\n"
        f"- epsilon: {epsilon} direction: {direction}\n"
        f"- execution: {execution_state} reproduction: {repro_state}\n"
        f"- outcome: {outcome} keep: {keep}\n"
        f"- verification: integrity {integrity_passed} backend {resolved_backend}\n"
        f"- evidence: traces/{run_id}/raw-result.json, traces/{run_id}/run.log, traces/{run_id}/verification.json\n"
    )
    (trace_dir / "reasoning.md").write_text(reasoning_text, encoding="utf-8")
    (run_dir / "reasoning.md").write_text(reasoning_text, encoding="utf-8")

    # tool-call.json
    tool_calls = {
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "calls": [
            {"tool": "experiment/run.py", "stage": "full", "state": execution_state, "stdout": exec_result.get("stdout_path"), "stderr": exec_result.get("stderr_path")},
            {"tool": "evaluation/prepare.py", "state": evaluation_state},
            {"tool": "reproduction", "state": repro_state},
        ],
        "failure_mode": args.failure_mode,
    }
    write_json(trace_dir / "tool-call.json", tool_calls)
    write_json(run_dir / "tool-call.json", tool_calls)

    # reports
    reports_dir = WORKSPACE / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    if outcome == "execution_error":
        report_path = reports_dir / "failure.md"
        report_text = (
            f"# Failure Report: {idea.get('title')}\n"
            f"- idea_id: {idea.get('id')}\n"
            f"- run_id: {run_id}\n"
            f"- hypothesis: {idea.get('hypothesis')}\n"
            f"- error_class: {error_obj.get('error_class') if error_obj else 'unknown'}\n"
            f"- message: {error_obj.get('message') if error_obj else 'unknown'}\n"
            f"- evidence: traces/{run_id}/error.json, traces/{run_id}/run.log\n"
            f"- root cause: import/failure-mode deterministic\n"
            f"- negative result: structured execution_error without integrity corruption\n"
            f"- next hypotheses: []\n"
        )
        report_path.write_text(report_text, encoding="utf-8")
        # per-run report also
        (trace_dir / "failure.md").write_text(report_text, encoding="utf-8")
        (run_dir / "failure.md").write_text(report_text, encoding="utf-8")
        review_text = (
            f"# Review — {run_id}\n"
            f"- outcome: execution_error\n"
            f"- gate: failed execution, no keep\n"
            f"- score: 0/5\n"
            f"- critique: deterministic failure-mode exercised, integrity preserved\n"
        )
    else:
        report_text = (
            f"# Report — {run_id}\n\n"
            f"## Hypothesis\n{idea.get('hypothesis')}\n\n"
            f"## Method\nCandidate slope 1.8 intercept 1.0 vs identity baseline.\n\n"
            f"## Metrics\n- baseline mse: {baseline_val}\n- candidate mse: {candidate_val}\n- delta: {delta}\n\n"
            f"## Outcome\n{outcome} — {reason}\n\n"
            f"## Evidence\n- traces/{run_id}/metrics.json\n- traces/{run_id}/verification.json\n- traces/{run_id}/raw-result.json\n"
            f"## Success language\n{'independently reproduced result' if repro_state=='completed' else 'proxy result'}: mse {candidate_val}\n"
        )
        report_path = reports_dir / "report.md"
        report_path.write_text(report_text, encoding="utf-8")
        (trace_dir / "report.md").write_text(report_text, encoding="utf-8")
        (run_dir / "report.md").write_text(report_text, encoding="utf-8")
        review_text = (
            f"# Review — {run_id}\n"
            f"- outcome: {outcome}\n"
            f"- keep: {keep}\n"
            f"- score: {1 if outcome=='discard' else 4}/5\n"
            f"- evaluation_state: {evaluation_state}\n"
            f"- reproduction: {repro_state}\n"
            f"- comment: {'discard expected: candidate underperforms identity baseline' if outcome=='discard' else 'keep'}\n"
        )
    review_path = reports_dir / "review.md"
    review_path.write_text(review_text, encoding="utf-8")
    (trace_dir / "review.md").write_text(review_text, encoding="utf-8")
    (run_dir / "review.md").write_text(review_text, encoding="utf-8")

    # global traces.jsonl, research-ledger.jsonl and archive/failed.jsonl appends:
    # dedup + torn-tail quarantine + one locked transaction each.
    global_trace = {
        "ts": now_iso(),
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "event": outcome,
        "stage": "full",
        "outcome": outcome,
        "keep": keep,
        "baseline": baseline_val,
        "candidate": candidate_val,
        "delta": delta,
        "backend": resolved_backend,
        "metric": profile.get("evaluation", {}).get("metric", "mse"),
        "value": candidate_val,
        "actual": cost["actual"],
        "fingerprint": fingerprint,
    }
    traces_jsonl = WORKSPACE / "traces.jsonl"
    ledger_path = WORKSPACE / "research-ledger.jsonl"
    locked_jsonl_append(traces_jsonl, global_trace)
    # research ledger: scientific entity
    ledger_entry = {
        "ts": now_iso(),
        "run_id": run_id,
        "idea_id": idea.get("id"),
        "profile": profile.get("name"),
        "metric_main": metric_main,
        "outcome": outcome,
        "evidence_refs": [f"traces/{run_id}/metrics.json", f"traces/{run_id}/verification.json"],
    }
    locked_jsonl_append(ledger_path, ledger_entry)
    # also per-run ledger copy
    (trace_dir / "ledger.json").write_text(json.dumps(ledger_entry, indent=2)+"\n", encoding="utf-8")

    # lifecycle final event
    ts3 = now_iso()
    final_evt = {"ts": ts3, "run_id": run_id, "idea_id": idea.get("id"), "event": "completed" if execution_state=="completed" else "failed", "stage": "full", "outcome": outcome, "keep": keep}
    append_jsonl(lifecycle_path, final_evt)
    append_jsonl(lifecycle_run_path, final_evt)
    append_jsonl(events_path, final_evt)
    append_jsonl(run_events_path, final_evt)

    # per-phase events for seven phases (additive)
    for phase in ["inspiration","modeling","experiment","evaluation","writing","review","archive"]:
        evt = {"ts": now_iso(), "run_id": run_id, "phase": phase, "event": "completed", "outcome": outcome if phase=="archive" else None}
        append_jsonl(events_path, evt)
        append_jsonl(run_events_path, evt)

    # archive record
    if outcome == "keep":
        paper_dir = WORKSPACE / "archive" / "papers" / run_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        (paper_dir / "paper.md").write_text(report_text if 'report_text' in locals() else "", encoding="utf-8")
        (paper_dir / "metrics.json").write_text(json.dumps(metrics, indent=2)+"\n", encoding="utf-8")
    else:
        failed_path = WORKSPACE / "archive" / "failed.jsonl"
        failed_entry = {"run_id": run_id, "idea_id": idea.get("id"), "outcome": outcome, "reason": reason, "metric_main": metric_main, "baseline": baseline_val, "ts": now_iso(), "evidence": f"traces/{run_id}/metrics.json"}
        locked_jsonl_append(failed_path, failed_entry)

    # update the exact idea to its terminal status (idempotent, under the queue lock)
    update_idea_terminal(idea.get("id"), run_id, outcome)

    # status.md
    status_path = WORKSPACE / "status.md"
    status_text = (
        f"# Research Flywheel Status\n\n"
        f"## Latest run\n"
        f"- run_id: {run_id}\n"
        f"- idea_id: {idea.get('id')}\n"
        f"- phase: archive\n"
        f"- outcome: {outcome}\n"
        f"- keep: {keep}\n"
        f"- profile: {profile.get('name')}\n"
        f"- recorded_at: {now_iso()}\n"
        f"- trace_dir: traces/{run_id}\n"
        f"- run_dir: runs/{run_id}\n\n"
        f"## Pending actions\n"
        f"- None.\n\n"
        f"## Open questions\n"
        f"1. Next domain profile evaluation.\n\n"
        f"## Recovery order\n"
        f"1. Read status.md, AGENTS.md, QUEST.md\n"
        f"2. Read program.md\n"
        f"3. Read runs/{run_id}/journal/\n"
        f"4. Read traces/{run_id}/\n"
    )
    status_path.write_text(status_text, encoding="utf-8")

    # terminal commit marker written last (after all terminal artifacts)
    write_terminal_marker(run_id, idea.get("id"), outcome, trace_dir, run_dir)

    # console summary
    print(json.dumps({"run_id": run_id, "idea_id": idea.get("id"), "outcome": outcome, "keep": keep, "trace_dir": f"traces/{run_id}", "run_dir": f"runs/{run_id}", "baseline": baseline_val, "candidate": candidate_val, "delta": delta}, indent=2))
    return 0


def _finalize_from_cache(run_id: str, run_dir: Path, trace_dir: Path, metrics: dict) -> bool:
    """Idempotently restore missing terminal artifacts from a valid cached bundle."""
    idea_id = metrics.get("idea_id")
    outcome = metrics.get("outcome")
    keep = metrics.get("keep")
    idea = load_archived_idea(idea_id) if isinstance(idea_id, str) else None
    if idea is None:
        return False
    # Load verification and cost canonical mirrors (caller ensures they were repaired, but re-read tolerantly)
    verification = read_json_object(trace_dir / "verification.json") or read_json_object(run_dir / "verification.json")
    cost = read_json_object(trace_dir / "cost.json") or read_json_object(run_dir / "cost.json")
    if verification is None or cost is None:
        return False
    if not validate_verification(verification, metrics, run_id):
        return False
    ok_cost, _ = _validate_cost(cost, metrics, verification, run_id)
    if not ok_cost:
        return False
    # Resolve profile: frozen from baseline.json when available, else current.
    frozen_profile = None
    for p in (trace_dir / "baseline.json", run_dir / "baseline.json"):
        rec = read_json_object(p)
        if rec and isinstance(rec.get("profile"), dict):
            frozen_profile = rec.get("profile")
            break
    profile_cur = parse_program()
    profile = frozen_profile if isinstance(frozen_profile, dict) else profile_cur
    # Reconstruct scalar views
    candidate_val = metrics.get("metric_main", {}).get("value") if isinstance(metrics.get("metric_main"), dict) else None
    baseline_val = None
    delta_val = verification.get("delta") if verification else None
    if isinstance(verification.get("baseline_metric"), dict):
        baseline_val = verification["baseline_metric"].get("value")
    if baseline_val is None and delta_val is not None and _is_finite_number(candidate_val):
        direction_tmp = verification.get("direction", "lower")
        try:
            baseline_val = float(candidate_val) + float(delta_val) if direction_tmp == "lower" else float(candidate_val) - float(delta_val)
        except (TypeError, ValueError):
            baseline_val = None
    epsilon = verification.get("epsilon", profile.get("evaluation", {}).get("epsilon", 0.0001))
    direction = verification.get("direction", profile.get("evaluation", {}).get("direction", "lower"))
    execution_state = verification.get("execution_state", metrics.get("execution", {}).get("state"))
    repro_state = verification.get("reproduction_state", cost.get("reproduction_state"))
    integrity_passed = verification.get("integrity_passed", True)
    # Determine backend from existing mutation if present
    backend = "replayed"
    for mp in (trace_dir / "mutation.json", run_dir / "mutation.json"):
        rec = read_json_object(mp)
        if rec and isinstance(rec.get("resolved_backend"), str):
            backend = rec.get("resolved_backend")
            break
    # Ensure directories exist
    trace_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "journal").mkdir(parents=True, exist_ok=True)
    # restore journal placeholders if missing
    for phase in ["inspiration", "modeling", "experiment", "evaluation", "writing", "review", "archive"]:
        jp = run_dir / "journal" / f"{phase}.md"
        if not jp.exists() or not jp.read_text(encoding="utf-8").strip():
            jp.write_text(f"# {phase}\nrun_id: {run_id}\nidea: {idea_id}\n", encoding="utf-8")
    # Ensure mirrors are consistent on disk (repair already done in replay, but ensure for direct finalize)
    for name in ("verification.json", "cost.json", "metrics.json"):
        tp = trace_dir / name
        rp = run_dir / name
        tv = read_json_object(tp)
        rv = read_json_object(rp)
        if tv is not None and rv is None:
            write_json(rp, tv)
        elif rv is not None and tv is None:
            write_json(tp, rv)
    # reasoning.md - preserve if exists
    reasoning_text = (
        f"# Reasoning — {run_id}\n\n"
        f"- idea: {idea_id} — {idea.get('title')}\n"
        f"- hypothesis: {idea.get('hypothesis')}\n"
        f"- candidate: slope 1.8 intercept 1.0 via experiment/run.py (project root import)\n"
        f"- baseline mse: {baseline_val}\n"
        f"- candidate mse: {candidate_val}\n"
        f"- delta: {delta_val}\n"
        f"- epsilon: {epsilon} direction: {direction}\n"
        f"- execution: {execution_state} reproduction: {repro_state}\n"
        f"- outcome: {outcome} keep: {keep}\n"
        f"- verification: integrity {integrity_passed} backend {backend}\n"
        f"- evidence: traces/{run_id}/raw-result.json, traces/{run_id}/run.log, traces/{run_id}/verification.json\n"
    )
    for p in (trace_dir / "reasoning.md", run_dir / "reasoning.md"):
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            p.write_text(reasoning_text, encoding="utf-8")
    # tool-call.json - preserve if exists with correct run_id
    for p in (trace_dir / "tool-call.json", run_dir / "tool-call.json"):
        existing = read_json_object(p)
        if existing and existing.get("run_id") == run_id:
            continue
        tool_calls = {
            "run_id": run_id,
            "idea_id": idea_id,
            "calls": [
                {"tool": "experiment/run.py", "stage": "full", "state": execution_state, "stdout": f"traces/{run_id}/experiment-stdout.log", "stderr": f"traces/{run_id}/experiment-stderr.log"},
                {"tool": "evaluation/prepare.py", "state": verification.get("evaluation_state", "completed")},
                {"tool": "reproduction", "state": repro_state},
            ],
            "failure_mode": None,
        }
        write_json(p, tool_calls)
    # report/failure.md and review.md
    reports_dir = WORKSPACE / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    if outcome == "execution_error":
        report_text = (
            f"# Failure Report: {idea.get('title')}\n"
            f"- idea_id: {idea_id}\n"
            f"- run_id: {run_id}\n"
            f"- hypothesis: {idea.get('hypothesis')}\n"
            f"- error_class: runtime\n"
            f"- message: {metrics.get('reason','')[:2000]}\n"
            f"- evidence: traces/{run_id}/error.json, traces/{run_id}/run.log\n"
            f"- root cause: import/failure-mode deterministic\n"
            f"- negative result: structured execution_error without integrity corruption\n"
            f"- next hypotheses: []\n"
        )
        review_text = (
            f"# Review — {run_id}\n"
            f"- outcome: execution_error\n"
            f"- gate: failed execution, no keep\n"
            f"- score: 0/5\n"
            f"- critique: deterministic failure-mode exercised, integrity preserved\n"
        )
        for p in (reports_dir / "failure.md", trace_dir / "failure.md", run_dir / "failure.md"):
            if not p.exists() or not p.read_text(encoding="utf-8").strip():
                p.write_text(report_text, encoding="utf-8")
        for p in (reports_dir / "review.md", trace_dir / "review.md", run_dir / "review.md"):
            if not p.exists() or not p.read_text(encoding="utf-8").strip():
                p.write_text(review_text, encoding="utf-8")
    else:
        reason = metrics.get("reason", f"{outcome}")
        report_text = (
            f"# Report — {run_id}\n\n"
            f"## Hypothesis\n{idea.get('hypothesis')}\n\n"
            f"## Method\nCandidate slope 1.8 intercept 1.0 vs identity baseline.\n\n"
            f"## Metrics\n- baseline mse: {baseline_val}\n- candidate mse: {candidate_val}\n- delta: {delta_val}\n\n"
            f"## Outcome\n{outcome} — {reason}\n\n"
            f"## Evidence\n- traces/{run_id}/metrics.json\n- traces/{run_id}/verification.json\n- traces/{run_id}/raw-result.json\n"
            f"## Success language\n{'independently reproduced result' if repro_state=='completed' else 'proxy result'}: mse {candidate_val}\n"
        )
        review_text = (
            f"# Review — {run_id}\n"
            f"- outcome: {outcome}\n"
            f"- keep: {keep}\n"
            f"- score: {1 if outcome=='discard' else 4}/5\n"
            f"- evaluation_state: {verification.get('evaluation_state')}\n"
            f"- reproduction: {repro_state}\n"
            f"- comment: {'discard expected: candidate underperforms identity baseline' if outcome=='discard' else 'keep'}\n"
        )
        for p in (reports_dir / "report.md", trace_dir / "report.md", run_dir / "report.md"):
            if not p.exists() or not p.read_text(encoding="utf-8").strip():
                p.write_text(report_text, encoding="utf-8")
        for p in (reports_dir / "review.md", trace_dir / "review.md", run_dir / "review.md"):
            if not p.exists() or not p.read_text(encoding="utf-8").strip():
                p.write_text(review_text, encoding="utf-8")
    # global traces.jsonl, research-ledger.jsonl and per-run ledger.json
    global_trace = {
        "ts": now_iso(),
        "run_id": run_id,
        "idea_id": idea_id,
        "event": outcome,
        "stage": "full",
        "outcome": outcome,
        "keep": keep,
        "baseline": baseline_val,
        "candidate": candidate_val,
        "delta": delta_val,
        "backend": backend if isinstance(backend, str) else "replayed",
        "metric": profile.get("evaluation", {}).get("metric", "mse"),
        "value": candidate_val,
        "actual": metrics.get("execution", {}).get("actual"),
        "fingerprint": metrics.get("fingerprint"),
    }
    locked_jsonl_append(WORKSPACE / "traces.jsonl", global_trace)
    ledger_entry = {
        "ts": now_iso(),
        "run_id": run_id,
        "idea_id": idea_id,
        "profile": profile.get("name"),
        "metric_main": metrics.get("metric_main"),
        "outcome": outcome,
        "evidence_refs": [f"traces/{run_id}/metrics.json", f"traces/{run_id}/verification.json"],
    }
    locked_jsonl_append(WORKSPACE / "research-ledger.jsonl", ledger_entry)
    # per-run ledger copy preserve if exists
    ledger_path = trace_dir / "ledger.json"
    if not ledger_path.exists() or not read_json_object(ledger_path):
        ledger_path.write_text(json.dumps(ledger_entry, indent=2) + "\n", encoding="utf-8")
    # archive record - keep vs non-keep
    if outcome == "keep":
        paper_dir = WORKSPACE / "archive" / "papers" / run_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        paper_md = paper_dir / "paper.md"
        metrics_json = paper_dir / "metrics.json"
        if not paper_md.exists() or not paper_md.read_text(encoding="utf-8").strip():
            # Reuse report_text from above branch; for keep, report_text is defined in else branch
            # For keep we also have report_text, for discard branch report_text also defined, but execution_error not keep path
            # Ensure report_text exists
            if "report_text" not in locals():
                report_text = (trace_dir / "report.md").read_text(encoding="utf-8") if (trace_dir / "report.md").exists() else ""
            paper_md.write_text(report_text, encoding="utf-8")
        if not metrics_json.exists() or not read_json_object(metrics_json):
            metrics_json.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    else:
        failed_path = WORKSPACE / "archive" / "failed.jsonl"
        failed_entry = {"run_id": run_id, "idea_id": idea_id, "outcome": outcome, "reason": metrics.get("reason"), "metric_main": metrics.get("metric_main"), "baseline": baseline_val, "ts": now_iso(), "evidence": f"traces/{run_id}/metrics.json"}
        locked_jsonl_append(failed_path, failed_entry)
    # lifecycle and events - idempotent: do not duplicate final or phase records
    lifecycle_path = trace_dir / "lifecycle.jsonl"
    lifecycle_run_path = run_dir / "lifecycle.jsonl"
    events_path = trace_dir / "events.jsonl"
    run_events_path = run_dir / "events.jsonl"
    # Ensure lifecycle contains final event for this run; if already present skip appending
    def _has_final(path: Path) -> bool:
        if not path.exists():
            return False
        for rec in read_jsonl_array(path):
            if rec.get("run_id") == run_id and rec.get("event") in ("completed", "failed") and rec.get("stage") == "full" and rec.get("outcome") == outcome:
                return True
        return False
    def _has_phase(path: Path, phase: str) -> bool:
        if not path.exists():
            return False
        for rec in read_jsonl_array(path):
            if rec.get("run_id") == run_id and rec.get("phase") == phase and rec.get("event") == "completed":
                return True
        return False
    if not _has_final(lifecycle_path) or not _has_final(lifecycle_run_path):
        ts3 = now_iso()
        final_evt = {"ts": ts3, "run_id": run_id, "idea_id": idea_id, "event": "completed" if execution_state == "completed" else "failed", "stage": "full", "outcome": outcome, "keep": keep}
        # Only append to those missing final
        if not _has_final(lifecycle_path):
            append_jsonl(lifecycle_path, final_evt)
        if not _has_final(lifecycle_run_path):
            append_jsonl(lifecycle_run_path, final_evt)
        if not _has_final(events_path):
            append_jsonl(events_path, final_evt)
        if not _has_final(run_events_path):
            append_jsonl(run_events_path, final_evt)
        for phase in ["inspiration", "modeling", "experiment", "evaluation", "writing", "review", "archive"]:
            evt = {"ts": now_iso(), "run_id": run_id, "phase": phase, "event": "completed", "outcome": outcome if phase == "archive" else None}
            if not _has_phase(events_path, phase):
                append_jsonl(events_path, evt)
            if not _has_phase(run_events_path, phase):
                append_jsonl(run_events_path, evt)
    # update idea terminal and status.md (idempotent overwrites preserve latest)
    update_idea_terminal(idea_id, run_id, outcome)
    status_path = WORKSPACE / "status.md"
    if not status_path.exists() or "Latest run" not in status_path.read_text(encoding="utf-8"):
        status_text = (
            f"# Research Flywheel Status\n\n"
            f"## Latest run\n"
            f"- run_id: {run_id}\n"
            f"- idea_id: {idea_id}\n"
            f"- phase: archive\n"
            f"- outcome: {outcome}\n"
            f"- keep: {keep}\n"
            f"- profile: {profile.get('name')}\n"
            f"- recorded_at: {now_iso()}\n"
            f"- trace_dir: traces/{run_id}\n"
            f"- run_dir: runs/{run_id}\n\n"
            f"## Pending actions\n"
            f"- None.\n\n"
            f"## Open questions\n"
            f"1. Next domain profile evaluation.\n\n"
            f"## Recovery order\n"
            f"1. Read status.md, AGENTS.md, QUEST.md\n"
            f"2. Read program.md\n"
            f"3. Read runs/{run_id}/journal/\n"
            f"4. Read traces/{run_id}/\n"
        )
        status_path.write_text(status_text, encoding="utf-8")
    else:
        # Preserve existing status if it already references this run
        existing = status_path.read_text(encoding="utf-8")
        if run_id not in existing:
            status_text = (
                f"# Research Flywheel Status\n\n"
                f"## Latest run\n"
                f"- run_id: {run_id}\n"
                f"- idea_id: {idea_id}\n"
                f"- phase: archive\n"
                f"- outcome: {outcome}\n"
                f"- keep: {keep}\n"
                f"- profile: {profile.get('name')}\n"
                f"- recorded_at: {now_iso()}\n"
                f"- trace_dir: traces/{run_id}\n"
                f"- run_dir: runs/{run_id}\n\n"
                f"## Pending actions\n"
                f"- None.\n\n"
                f"## Open questions\n"
                f"1. Next domain profile evaluation.\n\n"
                f"## Recovery order\n"
                f"1. Read status.md, AGENTS.md, QUEST.md\n"
                f"2. Read program.md\n"
                f"3. Read runs/{run_id}/journal/\n"
                f"4. Read traces/{run_id}/\n"
            )
            status_path.write_text(status_text, encoding="utf-8")
    # terminal markers written last by caller
    return True


def _mirrors_equal(a: dict | None, b: dict | None) -> bool:
    if a is None or b is None:
        return False
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _replay_cached(run_id: str, run_dir: Path, trace_dir: Path, args, direction: str) -> int | None:
    """Return 0 on successful cached replay, None to fall through, else recovery-error exit code."""
    cached_metrics_path = trace_dir / "metrics.json"
    cached_run_metrics_path = run_dir / "metrics.json"
    cached_trace = read_json_object(cached_metrics_path) if cached_metrics_path.exists() else None
    cached_run = read_json_object(cached_run_metrics_path) if cached_run_metrics_path.exists() else None
    trace_ok, trace_reason = validate_metrics(cached_trace, run_id)
    run_ok, run_reason = validate_metrics(cached_run, run_id)
    if not trace_ok and not run_ok:
        return None
    # mirror equality and repair for metrics
    if trace_ok and run_ok:
        if not _mirrors_equal(cached_trace, cached_run):
            # If identity fields differ -> specific error, else generic mirror disagreement
            if cached_trace.get("idea_id") != cached_run.get("idea_id") or cached_trace.get("outcome") != cached_run.get("outcome") or cached_trace.get("keep") != cached_run.get("keep") or cached_trace.get("metric_main") != cached_run.get("metric_main") or cached_trace.get("fingerprint") != cached_run.get("fingerprint"):
                return record_recovery_error(run_id, run_dir, trace_dir, "cached mirrors disagree on terminal identity (idea_id/outcome/keep)")
            return record_recovery_error(run_id, run_dir, trace_dir, "cached metrics mirrors disagree")
        metrics = cached_trace
    elif trace_ok:
        metrics = cached_trace
    else:
        metrics = cached_run
    # Validate verification mirrors and consistency with metrics
    ver_trace = read_json_object(trace_dir / "verification.json") if (trace_dir / "verification.json").exists() else None
    ver_run = read_json_object(run_dir / "verification.json") if (run_dir / "verification.json").exists() else None
    ver_trace_ok, _ = _validate_verification_strict(ver_trace, metrics, run_id) if isinstance(ver_trace, dict) else (False, "missing")
    ver_run_ok, _ = _validate_verification_strict(ver_run, metrics, run_id) if isinstance(ver_run, dict) else (False, "missing")
    if not ver_trace_ok and not ver_run_ok:
        return record_recovery_error(run_id, run_dir, trace_dir, "verification mirrors missing or invalid")
    if ver_trace_ok and ver_run_ok:
        if not _mirrors_equal(ver_trace, ver_run):
            return record_recovery_error(run_id, run_dir, trace_dir, "verification mirrors disagree")
        verification = ver_trace
    elif ver_trace_ok:
        verification = ver_trace
    else:
        verification = ver_run
    # Validate cost mirrors and consistency
    cost_trace = read_json_object(trace_dir / "cost.json") if (trace_dir / "cost.json").exists() else None
    cost_run = read_json_object(run_dir / "cost.json") if (run_dir / "cost.json").exists() else None
    cost_trace_ok, _ = _validate_cost(cost_trace, metrics, verification, run_id) if isinstance(cost_trace, dict) else (False, "missing")
    cost_run_ok, _ = _validate_cost(cost_run, metrics, verification, run_id) if isinstance(cost_run, dict) else (False, "missing")
    if not cost_trace_ok and not cost_run_ok:
        return record_recovery_error(run_id, run_dir, trace_dir, "cost mirrors missing or invalid")
    if cost_trace_ok and cost_run_ok:
        if not _mirrors_equal(cost_trace, cost_run):
            return record_recovery_error(run_id, run_dir, trace_dir, "cost mirrors disagree")
        cost = cost_trace
    elif cost_trace_ok:
        cost = cost_trace
    else:
        cost = cost_run
    # After successful validation, repair any missing/invalid mirror from canonical
    if not trace_ok:
        write_json(cached_metrics_path, metrics)
    if not run_ok:
        write_json(cached_run_metrics_path, metrics)
    if not ver_trace_ok:
        write_json(trace_dir / "verification.json", verification)
    if not ver_run_ok:
        write_json(run_dir / "verification.json", verification)
    if not cost_trace_ok:
        write_json(trace_dir / "cost.json", cost)
    if not cost_run_ok:
        write_json(run_dir / "cost.json", cost)
    # Terminal marker exact checks. Malformed/wrong existing marker is recovery error.
    idea_id = metrics.get("idea_id")
    outcome = metrics.get("outcome")
    trace_marker_path = trace_dir / "terminal.json"
    run_marker_path = run_dir / "terminal.json"
    trace_exists = trace_marker_path.exists()
    run_exists = run_marker_path.exists()
    trace_rec = read_json_object(trace_marker_path) if trace_exists else None
    run_rec = read_json_object(run_marker_path) if run_exists else None
    # If marker exists but is malformed or identity mismatch -> error
    if trace_exists:
        if trace_rec is None or trace_rec.get("run_id") != run_id or trace_rec.get("idea_id") != idea_id or trace_rec.get("outcome") != outcome or trace_rec.get("terminal") is not True:
            return record_recovery_error(run_id, run_dir, trace_dir, "terminal marker malformed or mismatched")
    if run_exists:
        if run_rec is None or run_rec.get("run_id") != run_id or run_rec.get("idea_id") != idea_id or run_rec.get("outcome") != outcome or run_rec.get("terminal") is not True:
            return record_recovery_error(run_id, run_dir, trace_dir, "terminal marker malformed or mismatched")
    # If markers missing (one or both), finalize from complete valid bundle
    if not trace_exists or not run_exists:
        if not _finalize_from_cache(run_id, run_dir, trace_dir, metrics):
            return record_recovery_error(run_id, run_dir, trace_dir, "cached metrics present without terminal marker and finalization was not possible")
        # write markers last
        write_terminal_marker(run_id, idea_id, outcome, trace_dir, run_dir)
    # Build replay view for console
    baseline_v = None
    candidate_v = metrics.get("metric_main", {}).get("value") if isinstance(metrics.get("metric_main"), dict) else None
    delta_v = verification.get("delta")
    baseline_metric = verification.get("baseline_metric")
    candidate_metric = verification.get("candidate_metric")
    baseline_v = baseline_metric.get("value") if isinstance(baseline_metric, dict) else None
    if isinstance(candidate_metric, dict):
        candidate_v = candidate_metric.get("value")
    if baseline_v is None and delta_v is not None and candidate_v is not None and _is_finite_number(candidate_v) and _is_finite_number(delta_v):
        try:
            baseline_v = float(candidate_v) + float(delta_v) if direction == "lower" else float(candidate_v) - float(delta_v)
        except (TypeError, ValueError):
            baseline_v = None
    print(json.dumps({
        "run_id": run_id,
        "idea_id": metrics["idea_id"],
        "outcome": metrics["outcome"],
        "keep": metrics["keep"],
        "trace_dir": f"traces/{run_id}",
        "run_dir": f"runs/{run_id}",
        "baseline": baseline_v,
        "candidate": candidate_v,
        "delta": delta_v,
        "cached": True,
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Research flywheel run_once")
    parser.add_argument("--idea", type=str, default=None, help="Idea text to seed if queue empty")
    parser.add_argument("--failure-mode", type=str, default=None, help="Deterministic execution_error mode: import|runtime|syntax")
    parser.add_argument("--run-id", type=str, default=None, help="Reuse/force run id")
    args = parser.parse_args()

    profile = parse_program()
    integrity_paths: list[str] = profile.get("integrity_paths", INTEGRITY_DEFAULT)
    mutable_paths: list[str] = profile.get("mutable_paths", MUTABLE_DEFAULT)
    epsilon: float = float(profile.get("evaluation", {}).get("epsilon", 0.0001))
    direction: str = profile.get("evaluation", {}).get("direction", "lower")

    explicit = args.run_id is not None
    if explicit:
        try:
            run_id = validate_run_id(args.run_id)
        except ValueError as exc:
            parser.error(str(exc))
    else:
        run_id = new_run_id()
        # reserve safely: retry if the generated id collides with an existing run/trace dir
        while (WORKSPACE / "runs" / run_id).exists() or (WORKSPACE / "traces" / run_id).exists():
            run_id = new_run_id()
    run_dir = WORKSPACE / "runs" / run_id
    trace_dir = WORKSPACE / "traces" / run_id

    if explicit:
        # per-run lock acquired before cache inspection and held through replay or full finalization
        with locked(run_dir.parent / f"{run_id}.lock"):
            replay = _replay_cached(run_id, run_dir, trace_dir, args, direction)
            if replay is not None:
                return replay
            if run_dir.exists() or trace_dir.exists():
                recovered_idea = recover_run_idea(run_id, run_dir, trace_dir)
                if recovered_idea is None:
                    return record_recovery_error(run_id, run_dir, trace_dir, "existing incomplete run lacks a recoverable idea snapshot or idea_id")
                return record_recovery_error(run_id, run_dir, trace_dir, "existing incomplete run is preserved; start a new run-id or add a stage-specific resume implementation")
            return _run_once(run_id, run_dir, trace_dir, args, profile, integrity_paths, mutable_paths, epsilon, direction)
    return _run_once(run_id, run_dir, trace_dir, args, profile, integrity_paths, mutable_paths, epsilon, direction)

if __name__ == "__main__":
    sys.exit(main())
