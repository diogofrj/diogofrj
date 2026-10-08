#!/usr/bin/env python3
"""Generate info-card.svg: a neofetch-style card whose lines fade in one by one.

Static content. Edit ROWS and re-run: python scripts/make_info_card.py
"""
import os
from html import escape

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "info-card.svg")

USER = "diogo"
ROWS = [
    ("Name", "Diogo Fernandes"),
    ("Role", "DevOps / DevSecOps Engineer"),
    ("From", "Rio de Janeiro, Brazil"),
    ("Stack", "Azure · AKS · Kubernetes · Terraform"),
    ("Tooling", "Docker · Ansible · Packer · PowerShell · Bash"),
    ("Azure", "AZ-900/104/140/305/500 · DP-900 · SC-900"),
    ("Other", "LPIC-1/2/3 · Terraform · OCI · VCP-DCV · MCT"),
    ("Learning", "AI agents · MCP servers"),
    ("Path", "Self-taught"),
    ("Hobby", "Ecotourism"),
]

WIDTH, PAD, TITLEBAR_H, LINE_H, VALUE_X = 560, 24, 34, 24, 110
BG, FRAME, KEY, VALUE, PROMPT, MUTED = "#0d1117", "#30363d", "#58a6ff", "#c9d1d9", "#3fb950", "#8b949e"
STAGGER, DURATION = 0.18, 0.4


def main():
    height = TITLEBAR_H + PAD + (len(ROWS) + 1) * LINE_H + PAD // 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13">',
        f'<title>About {escape(USER)}</title>',
        '<style>'
        '@keyframes line{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}'
        f'.l{{animation:line {DURATION}s ease-out both}}'
        '</style>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H // 2}" r="5" fill="{color}"/>')
    out.append(f'<text x="{WIDTH // 2}" y="{TITLEBAR_H // 2 + 4}" fill="{MUTED}" font-size="12" '
               f'text-anchor="middle">{escape(USER)}@github: ~</text>')

    y = TITLEBAR_H + PAD + 10
    out.append(f'<g class="l" style="animation-delay:0s"><text x="{PAD}" y="{y}" fill="{PROMPT}">$ neofetch</text></g>')
    for i, (key, value) in enumerate(ROWS, start=1):
        y += LINE_H
        out.append(
            f'<g class="l" style="animation-delay:{i * STAGGER:.2f}s">'
            f'<text x="{PAD}" y="{y}" fill="{KEY}" font-weight="bold">{escape(key)}</text>'
            f'<text x="{VALUE_X}" y="{y}" fill="{VALUE}">{escape(value)}</text></g>'
        )
    out.append('</svg>')

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out))
    print(f"wrote {os.path.normpath(OUT_PATH)}")


if __name__ == "__main__":
    main()
