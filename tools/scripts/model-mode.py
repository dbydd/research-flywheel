#!/usr/bin/env python3
"""按预设切换各 role 的模型与思考等级。

用法（仓根或任意位置皆可）：
  python3 tools/scripts/model-mode.py            # 显示当前档位与可选预设
  python3 tools/scripts/model-mode.py fast       # 应用预设
预设表：tools/scripts/model-modes.json，每 role 一行 [model, thinking]。
双写模板（templates/<role>）与活 ws（ws/<role>），regen 与下次起会话都拿得到。
生效边界：只影响之后新起的 role session；在飞的会话不热改。
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_ROOT = ROOT / ".onlyne" / "templates"
WS_ROOT = ROOT / ".onlyne" / "ws"
PRESETS = ROOT / "tools" / "scripts" / "model-modes.json"


def settings_paths(role):
    for base in (TEMPLATE_ROOT, WS_ROOT):
        p = base / role / ".pi" / "settings.json"
        if p.is_file():
            yield p


def current_mode():
    mode = {}
    for role in sorted(p.parent.parent.name for p in TEMPLATE_ROOT.glob("*/.pi/settings.json")):
        p = TEMPLATE_ROOT / role / ".pi" / "settings.json"
        try:
            d = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        mode[role] = (d.get("defaultModel", "?"), d.get("defaultThinkingLevel", "?"))
    return mode


def apply(name):
    presets = json.loads(PRESETS.read_text())
    if name not in presets:
        sys.exit(f"未知预设 {name!r}，可选：{', '.join(sorted(presets))}")
    want = presets[name]
    cur = current_mode()
    changed = 0
    for role, (model, thinking) in sorted(want.items()):
        if role not in cur:
            print(f"跳过 {role}：模板里没有这个 role")
            continue
        old = cur[role]
        for p in settings_paths(role):
            d = json.loads(p.read_text())
            if d.get("defaultModel") == model and d.get("defaultThinkingLevel") == thinking:
                continue
            d["defaultModel"] = model
            d["defaultThinkingLevel"] = thinking
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
            changed += 1
        mark = "→" if old != (model, thinking) else "="
        print(f"{role:10s} {old[0]}/{old[1]} {mark} {model}/{thinking}")
    print(f"预设 {name} 已应用（改写 {changed} 个文件；新会话生效）")


def main():
    if len(sys.argv) > 1:
        apply(sys.argv[1])
    else:
        presets = json.loads(PRESETS.read_text())
        cur = current_mode()
        print("当前（模板值）：")
        for role, (m, t) in sorted(cur.items()):
            print(f"  {role:10s} {m}/{t}")
        print("可选预设：", ", ".join(sorted(presets)))


if __name__ == "__main__":
    main()
