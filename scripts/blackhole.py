#!/usr/bin/env python3
"""Render assets/blackhole.svg, the animated banner of my GitHub profile.

Standard library only. The RNG is seeded, so running the script again gives the
same file and the diff only changes when the parameters do.

    python scripts/blackhole.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

WIDTH, HEIGHT = 1200, 420
CX, CY = 600.0, 210.0
TILT = -9.0              # disk tilt on screen, in degrees
SHADOW = 62.0            # radius of the shadow
EINSTEIN = SHADOW * 1.9  # lens strength used to bend the stars
ASPECT = 0.085           # ry / rx of the disk, seen almost edge-on
SEED = 1977
OUT = Path(__file__).resolve().parent.parent / "assets" / "blackhole.svg"


def num(x: float) -> str:
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def loop_path(rx: float, ry: float, cy: float = 0.0) -> str:
    # Counter-clockwise from the left edge: front half first, then the back.
    # Paired with pathLength="1000", a dash pattern summing 1000 loops without a seam.
    a = f"A{num(rx)} {num(ry)} 0 1 0"
    return f"M{num(-rx)} {num(cy)}{a} {num(rx)} {num(cy)}{a} {num(-rx)} {num(cy)}"


def dashes(rng: random.Random, density: float) -> str:
    parts: list[float] = []
    while sum(parts) < 1000:
        parts.append(rng.uniform(6, 70) * (0.6 + density))
        parts.append(rng.uniform(2, 45) * (1.4 - density))
    scale = 1000 / sum(parts)
    return ",".join(num(p * scale) for p in parts)


def orbit(rng: random.Random, d: str, width: float, opacity: float, density: float, period: float,
          tilt: float = 0.0) -> str:
    turn = f' transform="rotate({num(tilt)})"' if tilt else ""
    return (
        f'<path class="o" d="{d}"{turn} pathLength="1000" stroke-width="{num(width)}" '
        f'stroke-opacity="{num(opacity)}" stroke-dasharray="{dashes(rng, density)}" '
        f'style="animation-duration:{num(period)}s"/>'
    )


def disk_rings(rng: random.Random) -> list[str]:
    inner, outer, count = SHADOW * 1.3, SHADOW * 6.2, 64
    rings = []
    for i in range(count):
        r = inner + (outer - inner) * (i / (count - 1)) ** 1.7
        glow = (inner / r) ** 1.15
        rings.append(orbit(
            rng,
            # Jitter the thickness and tilt a little so the rings cross each other
            # and the disk reads as gas, not as Saturn.
            loop_path(r, r * ASPECT * rng.uniform(0.7, 1.35)),
            width=rng.uniform(0.4, 1.0) + 2.0 * glow * rng.random(),
            opacity=0.12 + 0.88 * glow * rng.uniform(0.7, 1.0),
            density=min(1.0, 0.25 + glow),
            # Kepler: the period grows with r^1.5, so the inner edge outruns the rest.
            period=6.0 * (r / inner) ** 1.5,
            tilt=rng.uniform(-0.8, 0.8),
        ))
    return rings


def halo_rings(rng: random.Random) -> list[str]:
    # The far side of the disk, bent over and under the shadow by the lens.
    # Outer rings drift upward, which makes the arc thicker on top, like in Interstellar.
    inner, outer, count = SHADOW * 1.02, SHADOW * 1.6, 44
    rings = []
    for i in range(count):
        r = inner + (outer - inner) * i / (count - 1)
        fade = ((outer - r) / (outer - inner)) ** 1.6
        rings.append(orbit(
            rng,
            loop_path(r, r, -(r - SHADOW) * 0.45),
            width=rng.uniform(0.6, 1.8),
            opacity=0.12 + 0.88 * fade * rng.uniform(0.7, 1.0),
            density=rng.uniform(0.6, 1.0),
            period=4.0 * (r / SHADOW) ** 1.5,
        ))
    for r in (SHADOW * 1.08, SHADOW * 1.22, SHADOW * 1.4):
        # Wide, faint strokes underneath: the bloom that smooths the arc.
        rings.append(orbit(rng, loop_path(r, r, -(r - SHADOW) * 0.45), width=rng.uniform(6, 10),
                           opacity=rng.uniform(0.1, 0.16), density=1.0, period=4.0 * (r / SHADOW) ** 1.5))
    return rings


def hot_spots(rng: random.Random) -> list[str]:
    spots = []
    for r in (SHADOW * 1.7, SHADOW * 2.4, SHADOW * 3.3):
        period = 6.0 * (r / (SHADOW * 1.5)) ** 1.5
        spots.append(
            f'<ellipse rx="4" ry="1.2" fill="#fff" opacity=".85">'
            f'<animateMotion dur="{num(period)}s" begin="-{num(rng.uniform(0, period))}s" '
            f'repeatCount="indefinite" rotate="auto" path="{loop_path(r, r * ASPECT)}"/></ellipse>'
        )
    return spots


def lensed_stars(rng: random.Random) -> list[str]:
    """Scatter stars on the sky behind the hole and bend them with a point lens.

    Each star yields two images: the main one pushed outward and a faint one on the
    opposite side, both stretched along the tangent. Near the Einstein radius this
    piles the stars into a thin ring around the shadow.
    """
    stars = []
    for _ in range(520):
        x = rng.uniform(-80, WIDTH + 80)
        y = rng.uniform(-80, HEIGHT + 80)
        size = 0.25 + 1.3 * rng.random() ** 3
        alpha = rng.uniform(0.25, 0.95)
        twinkle = rng.random() < 0.3
        period, delay = rng.uniform(2.5, 7.0), rng.uniform(0, 7.0)

        dx, dy = x - CX, y - CY
        d = max(math.hypot(dx, dy), 1e-3)
        root = math.sqrt(d * d + 4 * EINSTEIN**2)
        u = d / EINSTEIN
        core = (u * u + 2) / (2 * u * math.sqrt(u * u + 4))

        for image, gain in (((d + root) / 2, core + 0.5), ((d - root) / 2, core - 0.5)):
            if abs(image) < SHADOW * 1.04:
                continue
            px, py = CX + dx / d * image, CY + dy / d * image
            if not (0 <= px <= WIDTH and 0 <= py <= HEIGHT):
                continue
            gain = abs(gain)
            stretch = min(abs(image) / d, 6.0)
            squash = max(min(gain / stretch, 1.4), 0.35)
            a = alpha if image > 0 else alpha * min(1.0, gain) ** 0.5
            if a < 0.05:
                continue
            anim = ""
            if twinkle and image > 0:
                anim = f' class="tw" style="animation-duration:{num(period)}s;animation-delay:-{num(delay)}s"'
            if stretch / squash < 1.2:
                stars.append(f'<circle cx="{num(px)}" cy="{num(py)}" r="{num(size)}" opacity="{num(a)}"{anim}/>')
            else:
                angle = math.degrees(math.atan2(dy, dx)) + 90
                stars.append(
                    f'<ellipse cx="{num(px)}" cy="{num(py)}" rx="{num(size * stretch)}" ry="{num(size * squash)}" '
                    f'opacity="{num(a)}" transform="rotate({num(angle)} {num(px)} {num(py)})"{anim}/>'
                )
    return stars


def bright_stars(rng: random.Random) -> list[str]:
    glows = []
    while len(glows) < 7:
        x, y = rng.uniform(20, WIDTH - 20), rng.uniform(16, HEIGHT - 16)
        if math.hypot(x - CX, (y - CY) * 2.2) < SHADOW * 7:
            continue  # keep the area around the disk clean
        r = rng.uniform(5, 9)
        glows.append(
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="url(#star)"/>'
            f'<circle cx="{num(x)}" cy="{num(y)}" r="1.1" fill="#fff"/>'
        )
    return glows


def parts() -> tuple[str, str, str]:
    """The scene as (css, defs, body), so profile.py can place it inside a taller SVG."""
    rng = random.Random(SEED)
    stars = lensed_stars(rng)
    glows = bright_stars(rng)
    disk = "".join(disk_rings(rng) + hot_spots(rng))
    halo = "".join(halo_rings(rng))
    reach = SHADOW * 6.4

    css = """.o{animation:orbit linear infinite}
@keyframes orbit{to{stroke-dashoffset:-1000}}
.tw{animation:twinkle ease-in-out infinite}
@keyframes twinkle{50%{opacity:.12}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}"""
    defs = f"""<clipPath id="back"><rect x="{num(-reach)}" y="{num(-reach)}" width="{num(reach * 2)}" height="{num(reach + 0.5)}"/></clipPath>
<clipPath id="front"><rect x="{num(-reach)}" y="-0.5" width="{num(reach * 2)}" height="{num(reach)}"/></clipPath>
<linearGradient id="doppler" gradientUnits="userSpaceOnUse" x1="{num(-reach)}" y1="0" x2="{num(reach)}" y2="0">
<stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="#ececec"/><stop offset="1" stop-color="#505050"/>
</linearGradient>
<radialGradient id="haze" gradientUnits="userSpaceOnUse" cx="{num(CX)}" cy="{num(CY)}" r="{num(WIDTH * 0.5)}">
<stop offset="0" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="{num(SHADOW * 2.2)}">
<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset=".47" stop-color="#fff" stop-opacity=".55"/>
<stop offset=".58" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<radialGradient id="flare">
<stop offset="0" stop-color="#fff" stop-opacity=".32"/><stop offset=".25" stop-color="#fff" stop-opacity=".08"/>
<stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<radialGradient id="star">
<stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>"""
    body = f"""<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#haze)"/>
<g fill="#fff">{"".join(stars)}{"".join(glows)}</g>
<g transform="translate({num(CX)} {num(CY)}) rotate({num(TILT)})">
<ellipse rx="{num(reach * 0.8)}" ry="{num(SHADOW * 0.7)}" fill="url(#flare)"/>
<circle r="{num(SHADOW * 2.2)}" fill="url(#glow)"/>
<g fill="none" stroke="url(#doppler)" clip-path="url(#back)">{disk}</g>
<g fill="none" stroke="url(#doppler)">{halo}</g>
<circle r="{num(SHADOW)}" fill="#000"/>
<circle r="{num(SHADOW + 3)}" fill="none" stroke="#fff" stroke-width="10" stroke-opacity=".2"/>
<circle r="{num(SHADOW + 1)}" fill="none" stroke="#fff" stroke-width="2.2" stroke-opacity="1"/>
<g fill="none" stroke="url(#doppler)" clip-path="url(#front)">{disk}<path d="{loop_path(SHADOW * 1.6, SHADOW * 1.6 * ASPECT)}" stroke-width="7" stroke-opacity=".22"/></g>
</g>"""
    return css, defs, body


def render() -> str:
    css, defs, body = parts()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Agujero negro</title>
<desc id="desc">Agujero negro animado: disco de acreción girando, anillo de fotones y estrellas deformadas por la lente gravitacional.</desc>
<style>
{css}
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
