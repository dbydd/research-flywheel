#!/usr/bin/env python
"""experiment/build_corpus.py — 四域语料构建（spec §3, run ssd-spectral-restore-001）。

产出:
  experiment/corpus/src/<domain>.full.txt   每个域的完整源文本（含 provenance 头注释之外的纯文本）
  experiment/corpus/src/<domain>.sources.json 该域的来源清单（URL/标题/revid/文件路径/字节区间/许可）
  experiment/corpus/<domain>__<i>.txt       切好的序列文件（i ∈ {0,1}: 0=fit, 1=held-out）
  experiment/corpus/MANIFEST.json           域名/来源/许可/字节区间/token 数/sha256/split 归属

tokenization 口径（spec §3 规则 4）: Qwen2 tokenizer, add_special_tokens=False, 不套 chat template;
序列 i = 全文 token 流的 [512*i, 512*(i+1)) 切片的解码文本；提取脚本再编码并取前 512 个 token。
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

UA = {"User-Agent": "onlyne-swarm-bench/1.0 (research flywheel; ssd-spectral-restore-001)"}


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))


# ---------------- wiki_en ----------------

WIKI_EN_TITLES = ["Sparse matrix", "Low-rank approximation", "State-space representation",
                  "Singular value decomposition", "Attention (machine learning)",
                  "Mamba (deep learning)"]


def fetch_wiki_en():
    sources, chunks = [], []
    for title in WIKI_EN_TITLES:
        url = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts%7Crevisions"
               "&explaintext=1&redirects=1&rvprop=ids&format=json&formatversion=2&titles="
               + urllib.parse.quote(title))
        data = json.loads(http_get(url))
        page = data["query"]["pages"][0]
        extract = page.get("extract", "")
        revid = page["revisions"][0]["revid"]
        # 只要导语（第一个 == 小节标题之前），保证是百科正文散文
        lead = extract.split("\n==")[0].strip()
        chunks.append(lead)
        sources.append({
            "title": page["title"], "requested_title": title, "revid": revid,
            "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page['title'].replace(' ', '_'))}",
            "license": "CC BY-SA 4.0", "chars_used": len(lead),
            "byte_range": [0, len(lead.encode("utf-8"))],
        })
        print(f"  wiki_en: {page['title']} revid={revid} lead_chars={len(lead)}")
    text = "\n\n".join(chunks)
    return text, {"api": "en.wikipedia.org/w/api.php prop=extracts explaintext", "articles": sources,
                  "license": "CC BY-SA 4.0"}


# ---------------- code_py ----------------

STDLIB_CANDIDATES = [
    Path("/opt/homebrew/Cellar/python@3.12/3.12.14/Frameworks/Python.framework/Versions/3.12/lib/python3.12/fnmatch.py"),
    Path.home() / ".local/share/uv/python/cpython-3.12-macos-aarch64-none/lib/python3.12/fnmatch.py",
    Path("/opt/homebrew/Cellar/python@3.11/3.11.16/Frameworks/Python.framework/Versions/3.11/lib/python3.11/fnmatch.py"),
]


def pick_stdlib_files():
    import sysconfig
    base = Path(sysconfig.get_paths()["stdlib"])
    names = ["fnmatch.py", "filecmp.py", "stat.py", "textwrap.py"]
    out = []
    for n in names:
        p = base / n
        if p.exists():
            out.append(p)
    if not out:  # 兜底：候选清单
        for p in STDLIB_CANDIDATES:
            if p.exists():
                out.append(p)
                break
    return out


def fetch_code_py():
    files = pick_stdlib_files()[:3]
    chunks, sources = [], []
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        chunks.append(t)
        sources.append({"path": str(p), "bytes": len(t.encode("utf-8")),
                        "byte_range": [0, len(t.encode("utf-8"))],
                        "license": "PSF/APACHE-2.0 (CPython stdlib)"})
        print(f"  code_py: {p} bytes={len(t)}")
    return "\n\n".join(chunks), {"mode": "local CPython stdlib", "files": sources,
                                 "license": "PSF/APACHE-2.0"}


# ---------------- math_tex ----------------

MATH_SOURCE_FILES = [
    "obsidian/draft/Mamba与Transformer的秩差距-学习笔记-2026-09-08.md",
    "runs/ssd-spectral-restore-001/spec.md",
    "runs/ssd-spectral-restore-001/derivation.md",
]


def extract_tex_blocks(md_text: str):
    """取 $$...$$ 显示块与其紧邻上文句子，作为「LaTeX 公式与推导散文」。"""
    blocks = []
    for m in re.finditer(r"\$\$(.+?)\$\$", md_text, flags=re.S):
        block = m.group(1).strip()
        if len(block) < 8:
            continue
        # 紧邻上文：块起点前最后一个非空行（散文句）
        before = md_text[: m.start()].rstrip().split("\n")
        prose = before[-1].strip() if before and before[-1].strip() else ""
        prose = re.sub(r"^[>\-\d\.\s\*\#]+", "", prose)[:300]
        blocks.append((prose + "\n" + block, m.start(), m.end()))
    return blocks


def fetch_math_tex():
    chunks, sources = [], []
    for rel in MATH_SOURCE_FILES:
        p = ROOT / rel
        if not p.exists():
            print(f"  math_tex: MISS {rel}")
            continue
        md = p.read_text(encoding="utf-8")
        picked = extract_tex_blocks(md)
        text = "\n\n".join(b[0] for b in picked)
        chunks.append(text)
        sources.append({"path": rel, "blocks": len(picked),
                        "byte_range": [picked[0][1], picked[-1][2]] if picked else [0, 0],
                        "license": "自有内容（本工作区产出）"})
        print(f"  math_tex: {rel} blocks={len(picked)} chars={len(text)}")
    return "\n\n".join(chunks), {"mode": "本仓库自产 LaTeX 块", "files": sources,
                                 "license": "proprietary-self"}


# ---------------- zh_prose ----------------

ANALECTS_CHAPTERS = [
    "論語/學而第一", "論語/爲政第二", "論語/八佾第三", "論語/里仁第四", "論語/公冶長第五",
    "論語/雍也第六", "論語/述而第七", "論語/泰伯第八", "論語/子罕第九", "論語/鄉黨第十",
    "論語/先進第十一", "論語/顏淵第十二", "論語/子路第十三", "論語/憲問第十四", "論語/衛靈公第十五",
    "論語/季氏第十六", "論語/陽貨第十七", "論語/微子第十八", "論語/子張第十九", "論語/堯曰第二十",
]


def clean_wikitext(c: str) -> str:
    c = re.sub(r"\{\{[^{}]*\}\}", "", c, flags=re.S)          # 去模板
    c = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", c)         # [[a|b]] -> b
    c = re.sub(r"\[\[([^\]]+)\]\]", r"\1", c)                  # [[a]] -> a
    c = re.sub(r"'''?'", "", c)
    c = re.sub(r"^\*+", "", c, flags=re.M)                      # 列表星号
    c = re.sub(r"\n{2,}", "\n", c)
    keep = []
    for line in c.split("\n"):
        line = line.strip()
        if not line or line.startswith(("|", "{", "}", "#", "<!--", "==")):
            continue
        if re.search(r"[\u4e00-\u9fff]", line):
            keep.append(line)
    return "\n".join(keep)


def fetch_zh_prose():
    chunks, sources = [] , []
    for title in ANALECTS_CHAPTERS:
        url = "https://zh.wikisource.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "prop": "revisions", "titles": title,
            "rvprop": "content|ids", "rvslots": "main", "redirects": 1,
            "format": "json", "formatversion": 2})
        try:
            data = json.loads(http_get(url))
            page = data["query"]["pages"][0]
            rev = page["revisions"][0]
            raw = rev["slots"]["main"]["content"]
        except Exception as e:  # 单章失败不阻断；清单里记录
            print(f"  zh_prose: FAIL {title}: {e}")
            continue
        text = clean_wikitext(raw)
        if len(text) < 50:
            continue
        chunks.append(text)
        sources.append({"title": page["title"], "chapter": title, "revid": rev["revid"],
                        "url": "https://zh.wikisource.org/wiki/" + urllib.parse.quote(page["title"]),
                        "chars_used": len(text),
                        "byte_range": [0, len(text.encode("utf-8"))]})
        print(f"  zh_prose: {title} revid={rev.get('revid')} chars={len(text)}")
    return "\n".join(chunks), {"mode": "zh.wikisource《論語》20 章全文（公版古籍）",
                               "chapters": sources, "license": "public domain"}


FETCHERS = {"wiki_en": fetch_wiki_en, "code_py": fetch_code_py,
            "math_tex": fetch_math_tex, "zh_prose": fetch_zh_prose}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights-path", default=str(Path.home() / ".cache/huggingface/hub/qwen25-0.5b-bf16-dl"),
                    help="用于切分的 tokenizer 所在模型目录")
    ap.add_argument("--domains", default="wiki_en,code_py,math_tex,zh_prose")
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--out-dir", default=str(ROOT / "experiment" / "corpus"))
    ap.add_argument("--no-network", action="store_true", help="复用 corpus/src 下已有全文")
    args = ap.parse_args()

    out = Path(args.out_dir)
    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)

    from mlx_lm import load
    print(f"loading tokenizer from {args.weights_path}")
    model, tokenizer = load(str(Path(args.weights_path).expanduser()))
    del model

    manifest = {"seq_len": args.seq_len, "tokenizer": {"source": str(args.weights_path),
                "class": type(tokenizer).__name__, "chat_template_applied": False,
                "add_special_tokens": False},
                "split_rule": "seq_index 0 = fit, 1 = held-out（全文 token 流顺序切片）",
                "domains": {}}
    mf_path = out / "MANIFEST.json"
    if mf_path.exists():  # 增量更新：只重写本次处理的域
        try:
            prev = json.loads(mf_path.read_text())
            manifest["domains"] = dict(prev.get("domains", {}))
        except Exception:
            pass

    ok = True
    for dom in [d.strip() for d in args.domains.split(",") if d.strip()]:
        full_path = src / f"{dom}.full.txt"
        prov_path = src / f"{dom}.sources.json"
        if args.no_network and full_path.exists():
            text = full_path.read_text(encoding="utf-8")
            prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
        else:
            print(f"[{dom}] fetching")
            text, prov = FETCHERS[dom]()
        if not text or len(text) < 100:
            print(f"[{dom}] ERROR: empty text")
            ok = False
            continue
        full_path.write_text(text, encoding="utf-8")
        prov_path.write_text(json.dumps(prov, ensure_ascii=False, indent=1), encoding="utf-8")
        ids = tokenizer.encode(text, add_special_tokens=False)
        n_tokens = len(ids)
        seqs = []
        for i in (0, 1):
            sl = ids[args.seq_len * i: args.seq_len * (i + 1)]
            if len(sl) < args.seq_len:
                seqs.append({"seq_index": i, "status": "dropped_insufficient_tokens",
                             "tokens_available": len(sl)})
                continue
            seg_text = tokenizer.decode(sl)
            f = out / f"{dom}__{i}.txt"
            f.write_text(seg_text, encoding="utf-8")
            re_ids = tokenizer.encode(seg_text, add_special_tokens=False)
            seqs.append({"seq_index": i, "split": "fit" if i == 0 else "heldout",
                         "file": str(f.relative_to(ROOT)), "tokens": args.seq_len,
                         "reencode_tokens": len(re_ids),
                         "sha256": sha256_text(seg_text)})
        manifest["domains"][dom] = {
            "source_meta": prov, "full_text_file": str(full_path.relative_to(ROOT)),
            "full_text_chars": len(text), "full_text_sha256": sha256_text(text),
            "total_tokens": n_tokens, "sequences": seqs}
        print(f"[{dom}] chars={len(text)} tokens={n_tokens} seqs={[s['seq_index'] for s in seqs if s['seq_index'] is not None]}")

    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"MANIFEST -> {out/'MANIFEST.json'}")
    ok = ok and all(
        len([s for s in d["sequences"] if s.get("split")]) == 2
        for d in manifest["domains"].values())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
