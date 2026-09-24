#!/usr/bin/env python3
"""Convert a MathJax-rendered web article into a plain markdown extraction.

Usage: weblog_to_md.py <in.html> <out.md> [--title "..."] [--selector "#PostContent"]

WordPress/MathJax pages carry the original LaTeX in <script type="math/tex"> next to
the rendered MathML. This script keeps the LaTeX, drops the rendered frames, unwraps
the layout markup, and lets pandoc lay out the prose, headings, quotes and tables.
"""
import argparse
import re
import subprocess

from bs4 import BeautifulSoup

PLACEHOLDER = "@@MATHFMT{}@@"


def clean(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "svg", "noscript", "iframe"]):
        if tag.name == "script" and (tag.get("type") or "").startswith("math/tex"):
            continue
        tag.decompose()

    maths: list[str] = []
    for script in soup.find_all("script"):
        kind = script.get("type") or ""
        if not kind.startswith("math/tex"):
            continue
        tex = script.get_text().strip()
        tex = re.sub(r"^\\begin\{(equation|align|gather|multline)\*?\}", "", tex)
        tex = re.sub(r"\\end\{(equation|align|gather|multline)\*?\}$", "", tex)
        tex = tex.strip()
        display = "mode=display" in kind
        idx = len(maths)
        maths.append(f"$$\n{tex}\n$$" if display else f"${tex}$")
        script.replace_with(soup.new_string(PLACEHOLDER.format(idx)))

    for tag in soup.find_all(class_=lambda c: c and any("MathJax" in x for x in ([c] if isinstance(c, str) else c))):
        if tag.name in ("span", "div"):
            tag.decompose()

    for tag in soup.find_all(["div", "span", "font", "center"]):
        tag.unwrap()

    for a in soup.find_all("a"):
        kids = [c for c in a.children if getattr(c, "name", None) or str(c).strip()]
        if len(kids) == 1 and getattr(kids[0], "name", None) == "img":
            a.unwrap()
            continue
        if not a.get("href"):
            a.unwrap()
            continue
        a.attrs = {k: v for k, v in a.attrs.items() if k == "href"}
    for tag in soup.find_all(True):
        for attr in ("class", "id", "style", "title", "width", "height", "alt", "align"):
            tag.attrs.pop(attr, None)
    for img in soup.find_all("img"):
        img["alt"] = "image"

    return str(soup), maths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--title", default=None)
    ap.add_argument("--selector", default="#PostContent")
    ap.add_argument("--rewrite", action="append", default=[], metavar="SRC=PATH",
                    help="rewrite an embedded media reference to the archived copy")
    args = ap.parse_args()

    with open(args.src, encoding="utf-8") as fh:
        page = fh.read()

    soup = BeautifulSoup(page, "lxml")
    node = soup.select_one(args.selector)
    if node is None:
        print(f"selector {args.selector} not found")
        return 1

    cleaned, maths = clean(str(node))
    proc = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars", "--wrap=none"],
        input=cleaned,
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout
    for idx, tex in enumerate(maths):
        out = out.replace(f"<p>{PLACEHOLDER.format(idx)}</p>", tex)
        out = out.replace(PLACEHOLDER.format(idx), tex)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    out = re.sub(r"\s*\[\\#\]\(#[^)]*\)", "", out)
    for pair in args.rewrite:
        src, path = pair.split("=", 1)
        out = out.replace(src, path)
    if args.title:
        out = f"# {args.title}\n\n" + out.lstrip("\n")

    with open(args.dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"wrote {args.dst}: {len(out)} chars, {out.count(chr(10))} lines, {len(maths)} math elements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
