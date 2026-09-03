#!/usr/bin/env bash
# new-worker.sh — supervisor 侧一键拉起全新 worker
# 用法: ./scripts/new-worker.sh <workspace> <iter> "<task_input>"
# 依赖: herdr (HERDR_ENV=1) 时走 herdr，否则提示用 subagent
set -euo pipefail
WS="${1:?workspace path required}"
ITER="${2:?iter number required (e.g. 1)}"
TASK_INPUT="${3:-}"
ITER_PAD=$(printf "%03d" "$ITER")
QUEST=$(head -n 5 "$WS/QUEST.md" 2>/dev/null | tr '\n' ' ' | cut -c1-200)

PROMPT="你是 harness-worker #${ITER_PAD}，工作区在 ${WS}。
任务：${QUEST}
本次输入：${TASK_INPUT}
约定：上下文以磁盘文件为准（AGENTS.md / .agents/skills/ / .pi/），产物写到 runs/${ITER_PAD}/output/，可复用逻辑标注 TOOL_CANDIDATE，结束追加 DONE/BLOCKED/FAILED 到 runs/${ITER_PAD}/worker.log。
禁止：改 AGENTS.md / .pi/ / .agents/skills/，执行 herdr server stop。
开始吧。"

if [[ "${HERDR_ENV:-}" == "1" ]]; then
  # 选方向：简单用 right，可按需改 down
  NEW_PANE=$(herdr pane split --current --direction right --cwd "$PWD" --no-focus | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['result']['pane']['pane_id'])")
  echo "pane: $NEW_PANE"
  herdr agent start "harness-worker-${ITER_PAD}" --kind pi --pane "$NEW_PANE" -- --cwd "$WS"
  herdr agent prompt "harness-worker-${ITER_PAD}" --wait --timeout 600000 "$PROMPT"
else
  echo "Not in herdr (HERDR_ENV!=1). Launch worker via subagent with this prompt:"
  echo "---"
  echo "$PROMPT"
fi
