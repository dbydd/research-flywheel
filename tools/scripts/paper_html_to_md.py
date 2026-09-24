#!/usr/bin/env python3
"""Convert an arXiv LaTeXML HTML article into a plain markdown extraction.

Usage: paper_html_to_md.py <article.html> <out.md> [--title "..."]

LaTeXML renders every figure as inline SVG (hundreds of KB of vector paths) and
every display equation as a layout table. This script drops the vector payloads,
rebuilds display equations from the LaTeX that LaTeXML keeps in `alttext`, strips
the wrapper markup, and lets pandoc lay out the remaining prose, lists and tables.
"""
import re
import subprocess
import sys

from bs4 import BeautifulSoup

PLACEHOLDER = "@@EQFMT{}@@"


def equation_tex(table) -> str:
    """Rebuild one display equation (or equation group) as LaTeX."""
    rows = []
    tag = None
    for row in table.find_all("tr"):
        parts = [m.get("alttext", "") for m in row.find_all("math")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        if len(parts) == 2 and parts[1].lstrip().startswith("\\displaystyle"):
            rows.append(f"{parts[0]} & {parts[1].lstrip()}")
        else:
            rows.append(" ".join(parts))
        num = row.find("span", class_=lambda c: c and "ltx_tag_equation" in c)
        if num:
            text = num.get_text(strip=True)
            m = re.match(r"\(([^)]+)\)", text)
            if m:
                tag = m.group(1)
    if not rows:
        return ""
    body = " \\\\ ".join(rows) if len(rows) > 1 else rows[0]
    if len(rows) > 1:
        body = f"\\begin{{aligned}} {body} \\end{{aligned}}"
    if tag:
        body = f"{body} \\tag{{{tag}}}"
    return f"$$\n{body}\n$$"


def clean(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "svg", "img", "picture", "nav", "noscript"]):
        tag.decompose()

    equations: list[str] = []
    for table in soup.find_all("table"):
        classes = " ".join(table.get("class") or [])
        if "ltx_equation" not in classes and "ltx_equationgroup" not in classes:
            continue
        tex = equation_tex(table)
        if not tex:
            table.decompose()
            continue
        idx = len(equations)
        equations.append(tex)
        table.replace_with(soup.new_string(f"\n\n{PLACEHOLDER.format(idx)}\n\n"))

    # LaTeXML wraps every paragraph in ltx_* divs and every word in spans.
    # Lists, paragraphs and captions keep their tags so pandoc can lay them out.
    for tag in soup.find_all(["div", "span", "section", "figure", "figcaption", "cite"]):
        tag.unwrap()

    for a in soup.find_all("a"):
        if not a.get("href"):
            a.unwrap()
            continue
        a.attrs = {k: v for k, v in a.attrs.items() if k == "href"}
    for tag in soup.find_all(True):
        for attr in ("class", "id", "style", "title", "width", "height", "alt", "display"):
            tag.attrs.pop(attr, None)

    return str(soup), equations


def drop_empty_tables(md: str) -> str:
    """LaTeXML emits layout tables with no content; drop those blocks entirely."""
    lines = md.split("\n")
    out: list[str] = []
    block: list[str] = []

    def flush() -> None:
        if not block:
            return
        cells = [c.strip() for line in block for c in line.strip().strip("|").split("|")]
        cells = [c for c in cells if c and set(c) - set("-: ")]
        if cells:
            out.extend(block)
        block.clear()

    for line in lines:
        if line.startswith("|"):
            block.append(line)
            continue
        flush()
        out.append(line)
    flush()
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    title = None
    if "--title" in sys.argv:
        title = sys.argv[sys.argv.index("--title") + 1]

    with open(src, encoding="utf-8") as fh:
        article = fh.read()
    i, j = article.find("<article"), article.find("</article>")
    if i >= 0 and j > i:
        article = article[i : j + len("</article>")]

    cleaned, equations = clean(article)
    proc = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars", "--wrap=none"],
        input=cleaned,
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout

    out = re.sub(r"\A#\s*.*?\n", "", out, count=1)
    for idx, tex in enumerate(equations):
        out = out.replace(PLACEHOLDER.format(idx), tex)
    out = drop_empty_tables(out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    if title:
        out = f"# {title}\n\n" + out.lstrip("\n")

    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"wrote {dst}: {len(out)} chars, {out.count(chr(10))} lines, {len(equations)} display equations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
