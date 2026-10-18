#!/usr/bin/env python3
"""Render assets/profile.svg: the black hole and my introduction over a galaxy.

GitHub doesn't let a README set a background, so the header is one SVG with a
continuous sky behind the black hole, my name and the intro text.

    python scripts/profile.py
"""

from __future__ import annotations

import html
import math
import random
from pathlib import Path

import blackhole
import constellation  # noqa: F401  (shares the font)
from blackhole import num

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "profile.svg"
WIDTH = 1200
MARGIN = 96
FONT = constellation.FONT
CHAR = 0.6  # width of a monospace character, in ems; used to wrap text by hand
SEED = 2026

NAME = "Luciano Herrera"
ROLE = "Junior full stack developer  ·  Canelones, Uruguay"

INTRO = [
    "I study Computer Engineering at FING (Universidad de la República), and before that I finished the IT "
    "track at UTU. I lean towards the backend: APIs in Node with TypeScript and PostgreSQL, and web apps in "
    "Python with Flask. I've also worked in tech support and on automating reports.",
    "I'm looking for my first developer job, in Montevideo, Canelones or remote.",
    "The black hole above is drawn by a plain Python script. Each ring of the disk spins at the speed "
    "Kepler's third law gives it, and the stars go through a gravitational lens before they're drawn.",
]


def wrap(text: str, size: float, width: float) -> list[str]:
    limit = int(width / (size * CHAR))
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > limit:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + [line] if line else lines


def text(x: float, y: float, value: str, size: float, color: str, **attrs: str) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" fill="{color}"{extra}>{html.escape(value)}</text>'


def paragraph(y: float, value: str, size: float = 17, color: str = "#d4d4d4", lead: float = 1.65) -> tuple[str, float]:
    out = []
    for line in wrap(value, size, WIDTH - 2 * MARGIN):
        out.append(text(MARGIN, y, line, size, color))
        y += size * lead
    return "".join(out), y


def galaxy(rng: random.Random, height: float, start: float) -> str:
    """A faint Milky Way: a diagonal band of tiny stars and nebula glow, plus a scattered field."""
    x0, y0, x1, y1 = WIDTH + 150, start - 50, -150, height - 150
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    clouds, dots = [], []
    angle = math.degrees(math.atan2(uy, ux))
    for i in range(7):
        t = (i + 0.5) / 7
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        clouds.append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rng.uniform(260, 380))}" ry="{num(rng.uniform(70, 120))}" '
                      f'fill="url(#nebula)" opacity="{num(rng.uniform(0.5, 1))}" transform="rotate({num(angle)} {num(cx)} {num(cy)})"/>')
    for i in range(1500):
        t = rng.random()
        spread = rng.gauss(0, 95)
        x = x0 + (x1 - x0) * t - uy * spread
        y = y0 + (y1 - y0) * t + ux * spread
        if 0 <= x <= WIDTH and start <= y <= height:
            dots.append((x, y, 0.2 + rng.random() ** 4 * 1.1, rng.uniform(0.15, 0.7)))
    for _ in range(420):
        dots.append((rng.uniform(0, WIDTH), rng.uniform(start, height), 0.25 + rng.random() ** 3 * 1.2, rng.uniform(0.2, 0.8)))
    stars = []
    for x, y, r, a in dots:
        twinkle = ""
        if rng.random() < 0.12:
            twinkle = (f' class="tw" style="animation-duration:{num(rng.uniform(2.5, 7))}s;'
                       f'animation-delay:-{num(rng.uniform(0, 7))}s"')
        stars.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" opacity="{num(a)}"{twinkle}/>')
    return f'<g>{"".join(clouds)}</g><g fill="#fff">{"".join(stars)}</g>'


def render() -> str:
    rng = random.Random(SEED)
    bh_css, bh_defs, bh_body = blackhole.parts()
    body, y = [], blackhole.HEIGHT + 30
    body.append(text(MARGIN, y, NAME, 46, "#ffffff", font_weight="bold", letter_spacing="1"))
    y += 40
    body.append(text(MARGIN, y, ROLE, 18, "#a8a8a8", letter_spacing="1"))
    y += 52
    for value in INTRO:
        block, y = paragraph(y, value, size=20, color="#ececec", lead=1.6)
        body.append(block)
        y += 16
    height = y + 30

    summary = f"{NAME}. {ROLE}. " + " ".join(INTRO)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {num(height)}" width="{WIDTH}" height="{num(height)}" role="img" aria-labelledby="title desc">
<title id="title">{NAME}</title>
<desc id="desc">{html.escape(summary)}</desc>
<style>
{bh_css}
</style>
<defs>
<clipPath id="frame"><rect width="{WIDTH}" height="{num(height)}" rx="16"/></clipPath>
<radialGradient id="nebula"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
{bh_defs}
</defs>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{num(height)}" fill="#000"/>
{galaxy(rng, height, blackhole.HEIGHT - 40)}
{bh_body}
<g font-family="{FONT}">{"".join(body)}</g>
</g>
</svg>
"""


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"{OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
