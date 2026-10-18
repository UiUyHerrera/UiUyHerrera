#!/usr/bin/env python3
"""Render assets/constellation.svg: my stack drawn as a star chart.

Each project is a constellation and each star is a tool it uses. Tools shared by
more than one project are where the constellations meet.

    python scripts/constellation.py
"""

from __future__ import annotations

import random
from pathlib import Path

from blackhole import num

WIDTH, HEIGHT = 1200, 400
SEED = 404
OUT = Path(__file__).resolve().parent.parent / "assets" / "constellation.svg"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# key: (label, x, y, size, label side)
STARS = {
    "ts": ("typescript", 90, 84, 2.4, "t"),
    "node": ("node.js", 190, 176, 3.2, "l"),
    "express": ("express", 300, 112, 2.2, "t"),
    "prisma": ("prisma", 296, 258, 2.0, "r"),
    "vitest": ("vitest", 140, 306, 1.6, "b"),
    "docker": ("docker", 410, 340, 1.8, "b"),
    "postgres": ("postgresql", 580, 312, 2.8, "b"),
    "figma": ("figma", 430, 52, 1.8, "l"),
    "js": ("javascript", 560, 150, 3.0, "b"),
    "luau": ("luau", 690, 64, 2.2, "t"),
    "python": ("python", 900, 210, 3.4, "l"),
    "ytdlp": ("yt-dlp", 1040, 150, 1.8, "r"),
    "ffmpeg": ("ffmpeg", 1110, 232, 1.8, "b"),
    "flask": ("flask", 990, 318, 2.2, "r"),
    "sqlalchemy": ("sqlalchemy", 790, 318, 1.8, "b"),
    "pytest": ("pytest", 1110, 360, 1.8, "r"),
}

EDGES = [
    ("ts", "node"), ("node", "express"), ("node", "prisma"), ("prisma", "postgres"),
    ("node", "vitest"), ("docker", "postgres"), ("docker", "node"),
    ("figma", "js"), ("js", "luau"), ("node", "js"),
    ("js", "python"),        # mpeasy: the extension talks to a local Python host
    ("python", "ytdlp"), ("python", "ffmpeg"),
    ("python", "flask"), ("flask", "sqlalchemy"), ("sqlalchemy", "postgres"), ("flask", "pytest"),
]

NAMES = [
    ("ecommerce-rest-api", 40, 384),
    ("figmatoroblox", 500, 30),
    ("mpeasy", 700, 196),
    ("reservini", 860, 390),
]

OFFSETS = {"t": (0, -14, "middle"), "b": (0, 22, "middle"), "l": (-12, 4, "end"), "r": (12, 4, "start")}


def sky(rng: random.Random) -> str:
    dots = []
    for _ in range(160):
        x, y = rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)
        dots.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(0.2 + rng.random() ** 3)}" '
                    f'opacity="{num(rng.uniform(0.15, 0.6))}"/>')
    return "".join(dots)


def grid() -> str:
    # Declination-style arcs, like the ones printed on old star charts.
    arcs = []
    for i in range(5):
        r = 900 + i * 110
        arcs.append(f'<circle cx="600" cy="{num(HEIGHT + r - 40 - i * 70)}" r="{r}"/>')
    return "".join(arcs)


def edges(rng: random.Random) -> str:
    lines, pulses = [], []
    for a, b in EDGES:
        _, x1, y1, _, _ = STARS[a]
        _, x2, y2, _, _ = STARS[b]
        d = f"M{x1} {y1}L{x2} {y2}"
        lines.append(f'<path d="{d}"/>')
        # A short dash runs along every line; the 3/197 pattern leaves a pause between runs.
        pulses.append(
            f'<path class="p" d="{d}" pathLength="100" stroke-dasharray="3 197" '
            f'style="animation-duration:{num(rng.uniform(4, 8))}s;animation-delay:-{num(rng.uniform(0, 8))}s"/>'
        )
    return (f'<g stroke="#fff" stroke-opacity=".22" stroke-width="1">{"".join(lines)}</g>'
            f'<g stroke="#fff" stroke-width="1.6" stroke-linecap="round" fill="none">{"".join(pulses)}</g>')


def stars(rng: random.Random) -> str:
    out = []
    for label, x, y, size, side in STARS.values():
        dx, dy, anchor = OFFSETS[side]
        out.append(
            f'<circle class="tw" cx="{x}" cy="{y}" r="{num(size * 5)}" fill="url(#halo)" '
            f'style="animation-duration:{num(rng.uniform(3, 6))}s;animation-delay:-{num(rng.uniform(0, 6))}s"/>'
            f'<circle cx="{x}" cy="{y}" r="{num(size)}" fill="#fff"/>'
            f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{label}</text>'
        )
    return "".join(out)


def render() -> str:
    rng = random.Random(SEED)
    names = "".join(f'<text x="{x}" y="{y}">{name}</text>' for name, x, y in NAMES)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Stack</title>
<desc id="desc">Mapa estelar de mi stack. TypeScript, Node.js, Express, Prisma, Vitest y Docker en ecommerce-rest-api; Figma, JavaScript, Node.js y Luau en FigmaToRoblox; JavaScript, Python, yt-dlp y ffmpeg en mpeasy; Python, Flask, SQLAlchemy y pytest en reservini; PostgreSQL compartido entre los dos backends.</desc>
<style>
.p{{animation:pulse linear infinite}}
@keyframes pulse{{to{{stroke-dashoffset:-200}}}}
.tw{{animation:twinkle ease-in-out infinite}}
@keyframes twinkle{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="16"/></clipPath>
<radialGradient id="halo"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="#000"/>
<g fill="none" stroke="#fff" stroke-opacity=".05" stroke-dasharray="2 6">{grid()}</g>
<g fill="#fff">{sky(rng)}</g>
{edges(rng)}
<g font-family="{FONT}" font-size="15" fill="#d6d6d6">{stars(rng)}</g>
<g font-family="{FONT}" font-size="11" letter-spacing="3" fill="#8a8a8a">{names}</g>
</g>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"{OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
