---
globs: ["archive/*.jsonl", "archive/**", "inspiration.md"]
description: Idea pool and archive append discipline
---

# Archive Discipline

- `archive/ideas.jsonl` is append-only through the lock helpers. Idea records carry: id, title, hypothesis, method, expected_delta, risk, refs, score, status (`queued`|`running`|`discard`|`failure`), created. A record missing hypothesis/method/expected_delta is invalid — discard it at generation time, never repair it in place.
- `archive/failed.jsonl` is the dead-hypothesis ledger. `idea-generator` deduplicates against it before proposing. Before deleting anything from the pool, the record must already exist in `failed.jsonl` or in an archived paper.
- `inspiration.md` is a view, not a ledger: it mirrors the newest queued ideas for the human. The pool file is the truth; regenerate the view freely.
- Delete a candidate branch (`omp/task/*`, `candidate/*`) only after its terminal archive record exists. The branch is disposable; the evidence envelope is not.
