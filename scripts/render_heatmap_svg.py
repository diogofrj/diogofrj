#!/usr/bin/env python3
"""Render data/contributions.json as contrib-heatmap.svg.

53x7 rounded boxes that slide in once on load (CSS keyframes, no loop).
GitHub strips scripts from READMEs but plays animations inside SVGs
embedded with <img>, so all motion lives in the SVG.
"""
import datetime
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # GitHub levels 0-4
CELL, GAP = 12, 3
STEP = CELL + GAP
PAD = 22
LABEL_W = 30
TITLEBAR_H = 34
MONTHS_H = 22
FOOTER_H = 62

BG, FRAME, MUTED, TEXT = "#0d1117", "#30363d", "#8b949e", "#c9d1d9"
COL_DELAY, ROW_DELAY, DURATION = 0.018, 0.04, 0.4


def build_grid(days):
    """Columns of 7 cells (Sunday first), padded with None at the edges."""
    grid, col = [], []
    for d in days:
        weekday = (datetime.date.fromisoformat(d["date"]).weekday() + 1) % 7
        if not col:
            col = [None] * weekday
        col.append(d)
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        grid.append(col + [None] * (7 - len(col)))
    return grid


def month_labels(grid):
    labels, last = [], None
    for ci, col in enumerate(grid):
        first = next(c for c in col if c)
        month = datetime.date.fromisoformat(first["date"]).month
        if month != last:
            labels.append((ci, datetime.date(2000, month, 1).strftime("%b")))
            last = month
    if len(labels) > 1 and labels[1][0] - labels[0][0] < 3:
        labels.pop(0)  # partial first month would overlap the next label
    return labels


def render(data):
    grid = build_grid(data["days"])
    gx0 = PAD + LABEL_W
    gy0 = TITLEBAR_H + MONTHS_H
    width = gx0 + len(grid) * STEP - GAP + PAD
    height = gy0 + 7 * STEP - GAP + FOOTER_H
    user = escape(data["username"])

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<title>GitHub contribution graph for {user}</title>',
        '<style>'
        '@keyframes cell{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}'
        f'.c{{animation:cell {DURATION}s cubic-bezier(.2,.8,.2,1) both}}'
        '</style>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{width}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H // 2}" r="5" fill="{color}"/>')
    out.append(f'<text x="{width // 2}" y="{TITLEBAR_H // 2 + 4}" fill="{MUTED}" font-size="12" '
               f'text-anchor="middle">{user}@github: ~/contributions --graph</text>')

    for ci, name in month_labels(grid):
        out.append(f'<text x="{gx0 + ci * STEP}" y="{TITLEBAR_H + 15}" fill="{MUTED}" font-size="10">{name}</text>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{PAD}" y="{gy0 + row * STEP + 10}" fill="{MUTED}" font-size="9">{name}</text>')

    for ci, col in enumerate(grid):
        for ri, cell in enumerate(col):
            if not cell:
                continue
            color = PALETTE[min(cell["level"], len(PALETTE) - 1)]
            delay = ci * COL_DELAY + ri * ROW_DELAY
            out.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" '
                       f'x="{gx0 + ci * STEP}" y="{gy0 + ri * STEP}" width="{CELL}" height="{CELL}" '
                       f'rx="2" fill="{color}"/>')

    fy = gy0 + 7 * STEP - GAP + 24
    out.append(f'<text x="{PAD}" y="{fy}" fill="{TEXT}" font-size="12">'
               f'{data["total_contributions"]:,} contributions in the last year</text>')
    out.append(f'<text x="{PAD}" y="{fy + 18}" fill="{MUTED}" font-size="11">'
               f'{data["active_days"]} active days · longest streak {data["longest_streak"]} days</text>')

    lx = width - PAD - 140
    out.append(f'<text x="{lx}" y="{fy + 1}" fill="{MUTED}" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        out.append(f'<rect x="{lx + 34 + i * STEP}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    out.append(f'<text x="{lx + 34 + 5 * STEP + 2}" y="{fy + 1}" fill="{MUTED}" font-size="10">More</text>')

    out.append('</svg>')
    return "\n".join(out)


def main():
    with open(IN_PATH) as f:
        data = json.load(f)
    svg = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {os.path.normpath(OUT_PATH)} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
