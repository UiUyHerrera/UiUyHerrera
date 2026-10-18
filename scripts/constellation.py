#!/usr/bin/env python3
"""Render assets/constellation.svg: my stack drawn as a star chart.

Each constellation is a language and its stars are the tools I use with it.
Tools that belong to two of them are where the constellations meet, and the
lone named stars are languages I use without a stack worth drawing.

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
    # TypeScript
    "zod": ("zod", 70, 176, 1.8, "l"),
    "express": ("express", 160, 92, 2.2, "t"),
    "node": ("node.js", 300, 156, 3.2, "b"),
    "prisma": ("prisma", 200, 246, 2.2, "r"),
    "vitest": ("vitest", 92, 318, 1.8, "b"),
    # JavaScript
    "figma": ("figma api", 450, 74, 2.0, "t"),
    "webext": ("webextensions", 612, 128, 2.2, "b"),
    # SQL
    "sqlite": ("sqlite", 418, 340, 1.8, "b"),
    "postgres": ("postgresql", 548, 296, 2.8, "t"),
    "mysql": ("mysql", 672, 344, 2.0, "b"),
    # Python
    "ytdlp": ("yt-dlp", 826, 112, 1.8, "t"),
    "tkinter": ("tkinter", 966, 86, 2.0, "t"),
    "psutil": ("psutil", 1106, 150, 1.8, "r"),
    "pytest": ("pytest", 1074, 288, 2.0, "r"),
    "flask": ("flask", 930, 236, 2.4, "b"),
    "sqlalchemy": ("sqlalchemy", 776, 252, 2.0, "b"),
}

EDGES = [
    ("zod", "express"), ("express", "node"), ("node", "prisma"), ("prisma", "vitest"),
    ("node", "figma"), ("figma", "webext"),
    ("sqlite", "postgres"), ("postgres", "mysql"),
    ("ytdlp", "tkinter"), ("tkinter", "psutil"), ("psutil", "pytest"), ("pytest", "flask"), ("flask", "sqlalchemy"),
    # Where the constellations touch.
    ("prisma", "postgres"), ("sqlalchemy", "postgres"),
    ("webext", "ytdlp"),  # a browser extension that hands the download to a local Python program
]

# Constellation names, written where each one sits on the chart.
NAMES = [("TYPESCRIPT", 40, 40), ("JAVASCRIPT", 500, 28), ("SQL", 530, 390), ("PYTHON", 1080, 36)]

# Languages drawn as single named stars.
LONE = [("JAVA", 300, 360), ("C#", 380, 210), ("C++", 720, 40), ("LUAU", 690, 210), ("PHP", 1000, 370)]

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


def star(rng: random.Random, x: float, y: float, size: float) -> str:
    return (
        f'<circle class="tw" cx="{x}" cy="{y}" r="{num(size * 5)}" fill="url(#halo)" '
        f'style="animation-duration:{num(rng.uniform(3, 6))}s;animation-delay:-{num(rng.uniform(0, 6))}s"/>'
        f'<circle cx="{x}" cy="{y}" r="{num(size)}" fill="#fff"/>'
    )


def stars(rng: random.Random) -> str:
    out = []
    for label, x, y, size, side in STARS.values():
        dx, dy, anchor = OFFSETS[side]
        out.append(star(rng, x, y, size) + f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{label}</text>')
    return "".join(out)


def lone_stars(rng: random.Random) -> str:
    return "".join(star(rng, x, y, 2.0) + f'<text x="{x + 12}" y="{y + 4}">{name}</text>' for name, x, y in LONE)


def render() -> str:
    rng = random.Random(SEED)
    names = "".join(f'<text x="{x}" y="{y}">{name}</text>' for name, x, y in NAMES)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Stack</title>
<desc id="desc">Mapa estelar de mi stack, con una constelación por lenguaje. TypeScript: Node.js, Express, Prisma, Zod y Vitest. JavaScript: Node.js, la API de plugins de Figma y WebExtensions. Python: Flask, SQLAlchemy, pytest, Tkinter, psutil y yt-dlp. SQL: PostgreSQL, MySQL y SQLite. Estrellas sueltas: Java, C#, C++, Luau y PHP.</desc>
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
<g font-family="{FONT}" font-size="12" letter-spacing="3" fill="#c4c4c4">{lone_stars(rng)}</g>
<g font-family="{FONT}" font-size="14" letter-spacing="4" fill="#b4b4b4">{names}</g>
</g>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"{OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
