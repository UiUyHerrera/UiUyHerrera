#!/usr/bin/env python3
"""Render assets/profile.svg: the whole profile as one tall image over a galaxy.

GitHub doesn't let a README set a background, so the black hole, the text, the
projects and the stack are drawn into a single SVG with one continuous sky.
The README keeps the links underneath, because nothing inside an image is
clickable.

    python scripts/profile.py
"""

from __future__ import annotations

import base64
import html
import math
import random
from pathlib import Path

import blackhole
import constellation
from blackhole import num

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "profile.svg"
ICONS = ROOT / "assets" / "icons"
WIDTH = 1200
MARGIN = 96
FONT = constellation.FONT
CHAR = 0.6  # width of a monospace character, in ems; used to wrap text by hand
SEED = 2026

INTRO = [
    "Soy Luciano, de Canelones. Estudio Ingeniería en Computación en la FING y antes hice el Bachillerato "
    "en Informática de UTU. Me tira más el backend que el frontend: APIs en Node con TypeScript y PostgreSQL, "
    "y apps web en Python con Flask. También trabajé en soporte técnico y automatizando reportes.",
    "Busco mi primer trabajo como desarrollador, en Montevideo, Canelones o remoto.",
    "El agujero negro de arriba y todo este perfil los dibuja un script en Python puro. Cada anillo del disco "
    "gira a la velocidad que le toca por la tercera ley de Kepler, y las estrellas pasan por una lente "
    "gravitacional antes de dibujarse.",
]

PROJECTS = [
    ("FigmaToRoblox", "JavaScript · Node.js · Luau",
     "Puente entre Figma y Roblox Studio. Diseñás una pantalla en Figma, copiás un código de seis letras y en "
     "Studio aparece como UI nativa de Roblox, con botones, paneles, pestañas y animaciones."),
    ("Reservini", "Python · Flask · SQLAlchemy · PostgreSQL",
     "Reservas para negocios chicos. El dueño carga sus servicios y horarios, comparte un link y los clientes "
     "reservan solos. No deja tomar dos veces la misma hora, manda confirmación y recordatorio por mail, y los "
     "tests corren en GitHub Actions."),
    ("ecommerce-rest-api", "TypeScript · Express · Prisma · PostgreSQL",
     "API de una tienda: registro con JWT, roles, productos con stock y pedidos que se arman dentro de una "
     "transacción, sin vender dos veces la última unidad. Documentada con OpenAPI y probada contra PostgreSQL."),
    ("mpeasy", "JavaScript · Python",
     "Extensión de navegador para bajar audio y video. Le pasa cada pedido por native messaging a un programa "
     "local en Python que usa yt-dlp y ffmpeg, y cada versión sale sola como release."),
    ("AimGearZ", "Shopify · Liquid",
     "Mi tienda de periféricos gaming en Chile. Programé el tema entero: catálogo, buscador, carrito y las "
     "secciones propias."),
]

STACK = [
    ("Frontend", ["html", "css", "js", "ts"]),
    ("Backend", ["ts", "py", "java", "cs", "php", "cpp", "lua"]),
    ("Frameworks y bases de datos", ["nodejs", "express", "flask", "prisma", "postgres", "mysql", "sqlite"]),
    ("Herramientas", ["git", "github", "githubactions", "docker", "vitest", "npm", "vercel", "figma"]),
]

CONTACT = "linkedin.com/in/luciano-herrera-b71212416  ·  bu3luciano@gmail.com  ·  Canelones, Uruguay"


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


def heading(y: float, value: str) -> tuple[str, float]:
    rule = f'<path d="M{MARGIN + len(value) * 15 * CHAR * 1.4 + 18} {num(y - 5)}H{WIDTH - MARGIN}" stroke="#fff" stroke-opacity=".14"/>'
    return text(MARGIN, y, value.upper(), 15, "#9a9a9a", letter_spacing="6") + rule, y + 44


def icon(name: str, x: float, y: float, size: float) -> str:
    data = base64.b64encode((ICONS / f"{name}.svg").read_bytes()).decode()
    return f'<image x="{num(x)}" y="{num(y)}" width="{num(size)}" height="{num(size)}" href="data:image/svg+xml;base64,{data}"/>'


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
    st_css, st_defs, st_body = constellation.parts(background=False)
    body, y = [], blackhole.HEIGHT + 40

    for value in INTRO:
        block, y = paragraph(y, value)
        body.append(block)
        y += 14

    y += 30
    block, y = heading(y, "Proyectos")
    body.append(block)
    for name, tech, about in PROJECTS:
        body.append(text(MARGIN, y, name, 22, "#ffffff", font_weight="bold"))
        body.append(text(MARGIN + len(name) * 22 * CHAR + 20, y, tech, 14, "#8a8a8a"))
        block, y = paragraph(y + 32, about, size=16, color="#bdbdbd")
        body.append(block)
        y += 26

    y += 20
    block, y = heading(y, "Stack")
    body.append(block)
    body.append(f'<g transform="translate(0 {num(y - 30)})">{st_body}</g>')
    y += constellation.HEIGHT - 10
    block, y = paragraph(y, "Cada constelación es un lenguaje y sus estrellas son lo que uso con él.", size=15, color="#8a8a8a")
    body.append(block)
    y += 18

    for label, names in STACK:
        body.append(text(MARGIN, y, label, 15, "#d4d4d4", font_weight="bold"))
        y += 16
        body.append("".join(icon(n, MARGIN + i * 62, y, 52) for i, n in enumerate(names)))
        y += 52 + 38

    y += 10
    body.append(f'<path d="M{MARGIN} {num(y)}H{WIDTH - MARGIN}" stroke="#fff" stroke-opacity=".14"/>')
    y += 40
    body.append(text(WIDTH / 2, y, CONTACT, 14, "#9a9a9a", text_anchor="middle"))
    height = y + 56

    summary = " ".join(INTRO) + " Proyectos: " + " ".join(f"{n} ({t}): {a}" for n, t, a in PROJECTS)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {num(height)}" width="{WIDTH}" height="{num(height)}" role="img" aria-labelledby="title desc">
<title id="title">Luciano Herrera</title>
<desc id="desc">{html.escape(summary)}</desc>
<style>
{bh_css}
{st_css}
</style>
<defs>
<clipPath id="frame"><rect width="{WIDTH}" height="{num(height)}" rx="16"/></clipPath>
<radialGradient id="nebula"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000"/></linearGradient>
{bh_defs}
{st_defs}
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
