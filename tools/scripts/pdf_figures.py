#!/usr/bin/env python3
"""Render each captioned figure of a PDF into a standalone PNG.

Usage: pdf_figures.py <in.pdf> <outdir> <slug> [--dpi 200] [--max N] [--only 1,2,5]

Figures are located from their "Figure N:" caption. The figure band runs from the
last run-in paragraph above the caption down to the caption's last line: LaTeXML
figures carry their labels as loose text, so the surrounding prose is what bounds
the band, not the drawing clusters alone.
"""
import argparse
import os

import pymupdf

MARGIN = 6.0
HEADER = 45.0
FOOTER = 745.0
MIN_X0 = 60.0
MAX_X1 = 552.0


def page_rects(page):
    """(text, image, drawing) rectangles of one page, in the printable column."""
    text = [pymupdf.Rect(b[:4]) for b in page.get_text("blocks") if b[6] == 0]
    imgs = []
    for info in page.get_images(full=True):
        try:
            imgs.append(page.get_image_bbox(info))
        except Exception:
            pass
    rects = text + imgs + list(page.cluster_drawings())
    keep = lambda r: r.x1 > MIN_X0 and r.x0 < MAX_X1 and r.height < 700
    return [r for r in text if keep(r)], [r for r in imgs if keep(r)], [r for r in page.cluster_drawings() if keep(r)]


def is_prose(rect) -> bool:
    """A run-in paragraph rather than a figure label or a caption."""
    return rect.height > 40 and rect.width > 300


def figure_rect(page, caption):
    text, imgs, drawings = page_rects(page)
    all_rects = text + imgs + drawings
    above = [r for r in all_rects if r.y1 <= caption.y0 + 3 and r.y1 > HEADER and r.y0 < FOOTER]
    prose = [r for r in text if r.y1 <= caption.y0 + 3 and r.y1 > HEADER and r.y0 < FOOTER and is_prose(r)]
    top = max([r.y1 for r in prose], default=HEADER)

    rect = pymupdf.Rect(caption)
    band = pymupdf.Rect(0, top + 1, page.rect.width, caption.y1 + 3)
    contents = [r for r in above if r.y1 > top + 1 and r.intersects(band)]
    if not contents:
        return None
    for r in contents:
        rect |= r & band
    rect = pymupdf.Rect(rect.x0 - MARGIN, rect.y0 - MARGIN, rect.x1 + MARGIN, rect.y1 + MARGIN)
    return rect & page.rect


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("slug")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--max", type=int, default=99)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    only = {int(x) for x in args.only.split(",") if x.strip()} if args.only else None

    found = {}
    for pno, page in enumerate(doc):
        for n in range(1, 60):
            if n in found or n > args.max:
                continue
            hits = page.search_for(f"Figure {n}:")
            if hits:
                found[n] = (pno, hits[0])

    os.makedirs(args.outdir, exist_ok=True)
    written = 0
    for n in sorted(found):
        if only and n not in only:
            continue
        pno, cap = found[n]
        page = doc[pno]
        rect = figure_rect(page, cap)
        if rect is None or rect.width < 40 or rect.height < 20:
            print(f"fig{n}: SKIP (no region) page {pno + 1}")
            continue
        pix = page.get_pixmap(clip=rect, dpi=args.dpi)
        out = f"{args.outdir}/{args.slug}-fig{n}.png"
        pix.save(out)
        written += 1
        print(f"fig{n}: page {pno + 1} rect=({rect.x0:.0f},{rect.y0:.0f},{rect.x1:.0f},{rect.y1:.0f}) {pix.width}x{pix.height}")
    print(f"total {written} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
