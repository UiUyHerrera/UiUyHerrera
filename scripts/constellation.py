#!/usr/bin/env python3
"""Render assets/constellation.svg: my stack drawn as a star chart.

Each constellation is a language and its stars are the tools I use with it.
Tools that belong to two of them are where the constellations meet.

    python scripts/constellation.py
"""

from __future__ import annotations

import random
from pathlib import Path

from blackhole import num

WIDTH, HEIGHT = 1200, 400
SEED = 404
OUT = Path(__file__).resolve().parent.parent / "assets" / "stack-map.svg"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# key: (label, x, y, size, label side)
STARS = {
    # Languages: the bright hubs every tool hangs from
    "typescript": ("typescript", 56, 38, 3.4, "r"),
    "javascript": ("javascript", 560, 34, 3.4, "r"),
    "python": ("python", 1080, 40, 3.4, "l"),
    "sql": ("sql", 548, 382, 3.4, "r"),
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
    # More languages, hooked to the tools they meet in my projects
    "java": ("java", 300, 360, 2.0, "r"),
    "csharp": ("c#", 380, 210, 2.0, "r"),
    "cpp": ("c++", 720, 40, 2.0, "r"),
    "luau": ("luau", 690, 210, 2.2, "r"),
    "php": ("php", 1000, 370, 2.0, "r"),
}

EDGES = [
    ("typescript", "zod"), ("typescript", "express"),
    ("javascript", "figma"), ("javascript", "webext"), ("javascript", "cpp"),
    ("python", "tkinter"), ("python", "psutil"),
    ("sql", "sqlite"), ("sql", "mysql"), ("sql", "postgres"),
    ("zod", "express"), ("express", "node"), ("node", "prisma"), ("prisma", "vitest"),
    ("node", "figma"), ("figma", "webext"),
    ("sqlite", "postgres"), ("postgres", "mysql"),
    ("ytdlp", "tkinter"), ("tkinter", "psutil"), ("psutil", "pytest"), ("pytest", "flask"), ("flask", "sqlalchemy"),
    # Where the constellations touch.
    ("prisma", "postgres"), ("sqlalchemy", "postgres"),
    ("webext", "ytdlp"),  # a browser extension that hands the download to a local Python program
    ("figma", "luau"),    # the Figma plugin feeds the Studio plugin
    ("php", "mysql"), ("java", "sqlite"), ("csharp", "node"), ("cpp", "webext"),
]



DESC = "Star chart of my stack, one constellation per language. TypeScript: Node.js, Express, Prisma, Zod and Vitest. JavaScript: Node.js, the Figma plugin API and WebExtensions. Python: Flask, SQLAlchemy, pytest, Tkinter, psutil and yt-dlp. SQL: PostgreSQL, MySQL and SQLite. Java, C#, C++, Luau and PHP are linked to the tools they meet."

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
        f'<circle class="gl" cx="{x}" cy="{y}" r="{num(size * 5)}" fill="url(#chalo)" '
        f'style="animation-duration:{num(rng.uniform(3, 6))}s;animation-delay:-{num(rng.uniform(0, 6))}s"/>'
        f'<circle cx="{x}" cy="{y}" r="{num(size)}" fill="#fff"/>'
    )


def stars(rng: random.Random) -> str:
    out = []
    for label, x, y, size, side in STARS.values():
        dx, dy, anchor = OFFSETS[side]
        out.append(star(rng, x, y, size) + f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{label}</text>')
    return "".join(out)



def parts(background: bool = True) -> tuple[str, str, str]:
    """The chart as (css, defs, body), so profile.py can place it inside a taller SVG."""
    rng = random.Random(SEED)
    css = """.p{animation:pulse linear infinite}
@keyframes pulse{to{stroke-dashoffset:-200}}
.gl{animation:glint ease-in-out infinite}
@keyframes glint{50%{opacity:.35}}"""
    defs = ('<radialGradient id="chalo"><stop offset="0" stop-color="#fff" stop-opacity=".35"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    sky_dots = sky(rng)
    back = (f'<g fill="none" stroke="#fff" stroke-opacity=".05" stroke-dasharray="2 6">{grid()}</g>'
            f'<g fill="#fff">{sky_dots}</g>') if background else ""
    body = f"""{back}
{edges(rng)}
<g font-family="{FONT}" font-size="15" fill="#d6d6d6">{stars(rng)}</g>"""
    return css, defs, body


def render() -> str:
    css, defs, body = parts()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Stack</title>
<desc id="desc">{DESC}</desc>
<style>
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="16"/></clipPath>
{defs}
</defs>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="#000"/>
{body}
</g>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"{OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
