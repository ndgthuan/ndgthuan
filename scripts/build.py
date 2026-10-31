"""Rebuild the profile SVGs (header, pipeline, telemetry, quote) and the auto-updated README sections.

Runs daily from .github/workflows/readme.yml. Needs a token in GH_TOKEN or GITHUB_TOKEN.
"""

import base64
import datetime as dt
import json
import os
import re
import urllib.request
from html import escape
from pathlib import Path

USER = "ndgthuan"
USER_ID = 179018304
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
JOINED = dt.date(2024, 8, 21)  # GitHub account creation date
HIDDEN_REPOS = {USER, "todo"}  # never listed under RECENTLY PUSHED

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', monospace"

# Dusk palette, taken from the avatar: night-blue sky, sunset orange, leaf green.
NIGHT = "#0d1520"
PANEL = "#142131"
LINE = "#24364a"
TEXT = "#eef3f7"
MUTED = "#8ea3b8"
PEACH = "#f6b56b"
CORAL = "#ec8466"
SKY = "#5fb3e0"
LEAF = "#8cc265"

# ---------------------------------------------------------------- data


def graphql(query, **variables):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch():
    data = graphql(
        """
        query($login: String!) {
          user(login: $login) {
            followers { totalCount }
            contributionsCollection { contributionCalendar { totalContributions } }
            repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                         orderBy: {field: PUSHED_AT, direction: DESC}) {
              totalCount
              nodes {
                name description url pushedAt isFork stargazerCount
                primaryLanguage { name }
                languages(first: 10) { edges { size node { name color } } }
              }
            }
          }
        }
        """,
        login=USER,
    )["user"]
    repos = data["repositories"]["nodes"]
    langs = {}
    for r in repos:
        if r["isFork"]:
            continue
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            size, color = langs.get(name, (0, e["node"]["color"]))
            langs[name] = (size + e["size"], color or MUTED)
    return {
        "repos": data["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": data["followers"]["totalCount"],
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "languages": sorted(langs.items(), key=lambda kv: -kv[1][0]),
        "recent": [r for r in repos if not r["isFork"] and r["name"] not in HIDDEN_REPOS][:6],
    }


def avatar_data_uri():
    url = f"https://avatars.githubusercontent.com/u/{USER_ID}?v=4&s=240"
    with urllib.request.urlopen(url) as resp:
        kind = resp.headers.get_content_type()
        return f"data:{kind};base64,{base64.b64encode(resp.read()).decode()}"


def days_since(start, today):
    return (today - start).days


# ---------------------------------------------------------------- header


def header_svg(avatar):
    w, h = 1000, 320
    stars = [(70, 40), (160, 22), (240, 70), (330, 30), (420, 58), (520, 18), (610, 48), (930, 30), (880, 80), (700, 26)]
    star_els = "\n".join(
        f'<circle cx="{x}" cy="{y}" r="{1.2 + (i % 3) * 0.5}" fill="#fff" class="tw" style="animation-delay:{(i * 0.37) % 3:.2f}s"/>'
        for i, (x, y) in enumerate(stars)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>
  .tw {{ animation: tw 3s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .25 }} 50% {{ opacity: 1 }} }}
  .c1 {{ animation: drift 38s linear infinite; }}
  .c2 {{ animation: drift 55s linear infinite; animation-delay: -20s; }}
  @keyframes drift {{ from {{ transform: translateX(-260px) }} to {{ transform: translateX(1100px) }} }}
  .orbit {{ transform-origin: 800px 160px; animation: spin 40s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg) }} }}
  .sun {{ animation: glow 6s ease-in-out infinite; }}
  @keyframes glow {{ 0%,100% {{ opacity: .85 }} 50% {{ opacity: 1 }} }}
  .fade {{ animation: up .9s ease-out both; }}
  @keyframes up {{ from {{ opacity: 0; transform: translateY(8px) }} to {{ opacity: 1; transform: none }} }}
</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0b1726"/>
    <stop offset=".45" stop-color="#1f4a6e"/>
    <stop offset=".78" stop-color="#d9835a"/>
    <stop offset="1" stop-color="#f6c07a"/>
  </linearGradient>
  <radialGradient id="sunG">
    <stop offset="0" stop-color="#ffe2a8"/>
    <stop offset=".5" stop-color="#f6b56b" stop-opacity=".7"/>
    <stop offset="1" stop-color="#f6b56b" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  <clipPath id="av"><circle cx="800" cy="160" r="92"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  {star_els}
  <circle class="sun" cx="560" cy="300" r="170" fill="url(#sunG)"/>
  <g class="c1" opacity=".35"><ellipse cx="0" cy="120" rx="90" ry="12" fill="#ffd9c2"/><ellipse cx="40" cy="110" rx="50" ry="10" fill="#ffd9c2"/></g>
  <g class="c2" opacity=".25"><ellipse cx="0" cy="190" rx="120" ry="10" fill="#ffd9c2"/></g>
  <path d="M0 250 L90 205 L170 240 L260 190 L360 236 L460 200 L560 246 L660 214 L760 248 L860 210 L1000 240 L1000 320 L0 320 Z" fill="#24435e" opacity=".85"/>
  <path d="M0 280 L120 248 L230 274 L340 240 L470 282 L590 252 L720 284 L850 256 L1000 280 L1000 320 L0 320 Z" fill="#142a3d"/>
  <rect y="306" width="{w}" height="14" fill="#0d1520"/>

  <g class="fade" font-family="{SANS}">
    <text x="56" y="88" font-family="{MONO}" font-size="13" fill="{PEACH}" letter-spacing="2">~/ndgthuan  ·  README.md</text>
    <text x="54" y="148" font-size="50" font-weight="800" fill="#fff" letter-spacing="1">Nguyễn Dương</text>
    <text x="54" y="200" font-size="50" font-weight="800" fill="#fff" letter-spacing="1">Gia Thuận</text>
    <text x="56" y="236" font-size="17" font-style="italic" fill="#ffe7d6">Data &amp; AI engineer in training. From raw data to models people can trust.</text>
  </g>

  <g class="orbit" fill="none" stroke="#ffe2c4" stroke-opacity=".55">
    <circle cx="800" cy="160" r="112" stroke-dasharray="3 9" stroke-width="2"/>
    <circle cx="912" cy="160" r="4" fill="{PEACH}" stroke="none"/>
    <circle cx="688" cy="160" r="3" fill="#fff" stroke="none"/>
  </g>
  <circle cx="800" cy="160" r="100" fill="{PEACH}" opacity=".25"/>
  <image href="{avatar}" x="708" y="68" width="184" height="184" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>
  <circle cx="800" cy="160" r="92" fill="none" stroke="#fff" stroke-width="4"/>
</g>
</svg>
"""


# ---------------------------------------------------------------- pipeline

STAGES = [
    ("SOURCES", "CSV · REST APIs · OLTP", ["e-commerce: olist", "formats: csv / json"], PEACH),
    ("INGEST", "PYTHON · KAFKA", ["extract + validate", "load as-is to bronze"], CORAL),
    ("WAREHOUSE", "SQL SERVER · T-SQL", ["bronze > silver > gold", "dimensional modeling"], SKY),
    ("SERVE", "BI · ML · LLM APPS", ["dashboards & KPIs", "features for AI models"], LEAF),
]


def pipeline_svg():
    w, h = 1000, 250
    card_w, card_h, gap, top = 196, 150, 50, 66
    left = (w - (4 * card_w + 3 * gap)) // 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}">',
        "<style>",
        ".flow { stroke-dasharray: 4 10; animation: flow 1.2s linear infinite; }",
        "@keyframes flow { to { stroke-dashoffset: -14 } }",
        ".pulse { animation: pulse 2.4s ease-in-out infinite; }",
        "@keyframes pulse { 0%,100% { opacity: .35 } 50% { opacity: 1 } }",
        "</style>",
        f'<rect width="{w}" height="{h}" rx="16" fill="{NIGHT}" stroke="{LINE}"/>',
        f'<text x="28" y="36" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">DATA_PIPELINE // HOW_I_BUILD</text>',
        f'<circle cx="{w - 128}" cy="32" r="4" fill="#3fd68c" class="pulse"/>',
        f'<text x="{w - 116}" y="36" font-family="{MONO}" font-size="12" letter-spacing="2" fill="#3fd68c">RUNNING</text>',
    ]
    for i, (title, sub, lines, color) in enumerate(STAGES):
        x = left + i * (card_w + gap)
        parts += [
            f'<rect x="{x}" y="{top}" width="{card_w}" height="{card_h}" rx="12" fill="{PANEL}" stroke="{color}" stroke-opacity=".7"/>',
            f'<rect x="{x}" y="{top}" width="{card_w}" height="4" rx="2" fill="{color}"/>',
            f'<text x="{x + 18}" y="{top + 34}" font-family="{MONO}" font-size="11" fill="{color}">0{i + 1}</text>',
            f'<text x="{x + 18}" y="{top + 58}" font-size="17" font-weight="800" fill="{TEXT}" letter-spacing="1">{title}</text>',
            f'<text x="{x + 18}" y="{top + 78}" font-family="{MONO}" font-size="10.5" font-weight="bold" fill="{color}">{escape(sub)}</text>',
            f'<rect x="{x + 18}" y="{top + 90}" width="{card_w - 36}" height="3" rx="1.5" fill="{LINE}"/>',
            f'<rect x="{x + 18}" y="{top + 90}" width="{(card_w - 36) * (i + 1) // 4}" height="3" rx="1.5" fill="{color}"/>',
        ]
        for j, line in enumerate(lines):
            parts.append(f'<text x="{x + 18}" y="{top + 114 + j * 17}" font-family="{MONO}" font-size="11" fill="{MUTED}">{escape(line)}</text>')
        if i < len(STAGES) - 1:
            x1, x2, y = x + card_w + 4, x + card_w + gap - 4, top + card_h // 2
            parts += [
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2" class="flow"/>',
                f'<path d="M{x2 - 6} {y - 5} L{x2} {y} L{x2 - 6} {y + 5}" fill="none" stroke="{color}" stroke-width="2"/>',
            ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- telemetry


def telemetry_svg(stats, today):
    w, h = 1000, 230
    tiles = [
        ("CONTRIBUTIONS", f"{stats['contributions']:,}", "past 12 months", PEACH),
        ("PUBLIC REPOS", f"{stats['repos']}", "and counting", CORAL),
        ("STARS EARNED", f"{stats['stars']}", "thank you", SKY),
        ("DAYS ON GITHUB", f"{days_since(JOINED, today):,}", f"since {JOINED:%b %Y}", LEAF),
    ]
    tile_w, gap, left, top = 220, 20, 30, 56
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}">',
        f'<rect width="{w}" height="{h}" rx="16" fill="{NIGHT}" stroke="{LINE}"/>',
        f'<text x="28" y="36" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">GITHUB_TELEMETRY // UPDATED {today:%Y-%m-%d}</text>',
    ]
    for i, (label, value, note, color) in enumerate(tiles):
        x = left + i * (tile_w + gap)
        parts += [
            f'<rect x="{x}" y="{top}" width="{tile_w}" height="92" rx="12" fill="{PANEL}"/>',
            f'<rect x="{x}" y="{top + 16}" width="3" height="60" rx="1.5" fill="{color}"/>',
            f'<text x="{x + 20}" y="{top + 28}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTED}">{label}</text>',
            f'<text x="{x + 20}" y="{top + 62}" font-size="30" font-weight="800" fill="{TEXT}">{value}</text>',
            f'<text x="{x + 20}" y="{top + 80}" font-family="{MONO}" font-size="10.5" fill="{color}">{escape(note)}</text>',
        ]

    # language bar, by bytes across all public non-fork repos
    langs = stats["languages"][:6]
    total = sum(size for _, (size, _) in langs) or 1
    bar_x, bar_y, bar_w = 30, 172, w - 60
    parts.append(f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>')
    parts.append('<g clip-path="url(#bar)">')
    x = bar_x
    for name, (size, color) in langs:
        seg = bar_w * size / total
        parts.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{seg + 0.5:.1f}" height="10" fill="{color}"/>')
        x += seg
    parts.append("</g>")
    x = bar_x
    for name, (size, color) in langs:
        label = f"{name} {100 * size / total:.1f}%"
        parts += [
            f'<circle cx="{x + 5}" cy="{bar_y + 30}" r="5" fill="{color}"/>',
            f'<text x="{x + 15}" y="{bar_y + 34}" font-family="{MONO}" font-size="11.5" fill="{TEXT}">{escape(label)}</text>',
        ]
        x += 22 + len(label) * 7.2
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- quote

QUOTES = [
    ("Software is eating the world,", "but AI is going to eat software.", "Jensen Huang, 2017"),
    ("Greatness comes from character. Character isn't formed out", "of smart people, it's formed out of people who suffered.", "Jensen Huang, Stanford GSB, 2024"),
    ("Whatever it is, run after it like we did.", "Run, don't walk.", "Jensen Huang, NTU commencement, 2023"),
]


def quote_svg():
    """Cycles through QUOTES with a cross-fade; each one stays up for `hold` seconds."""
    w, h, hold = 1000, 210, 6
    total = hold * len(QUOTES)
    show = 100 / len(QUOTES)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}">',
        "<style>",
        f".q {{ opacity: 0; animation: q {total}s infinite; }}",
        f"@keyframes q {{ 0% {{ opacity: 0 }} {show * .08:.1f}% {{ opacity: 1 }} {show * .92:.1f}% {{ opacity: 1 }} {show:.1f}%, 100% {{ opacity: 0 }} }}",
        "</style>",
        f'<rect width="{w}" height="{h}" rx="16" fill="{NIGHT}" stroke="{LINE}"/>',
        f'<rect x="0" y="0" width="5" height="{h}" rx="2" fill="{PEACH}"/>',
        f'<text x="40" y="104" font-family="Georgia, serif" font-size="96" fill="{PEACH}" opacity=".35">&#8220;</text>',
        f'<text x="{w - 40}" y="{h - 4}" text-anchor="end" font-family="Georgia, serif" font-size="96" fill="{PEACH}" opacity=".35">&#8221;</text>',
    ]
    for i, (line1, line2, source) in enumerate(QUOTES):
        parts += [
            f'<g class="q" style="animation-delay:{i * hold}s">',
            f'<text x="{w // 2}" y="88" text-anchor="middle" font-size="23" font-weight="700" fill="{TEXT}">{escape(line1)}</text>',
            f'<text x="{w // 2}" y="124" text-anchor="middle" font-size="23" font-weight="700" fill="{TEXT}">{escape(line2)}</text>',
            f'<text x="{w // 2}" y="162" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{PEACH}">'
            f'<tspan fill="{CORAL}">&#8212;&#8212;  </tspan>{escape(source)}<tspan fill="{CORAL}">  &#8212;&#8212;</tspan></text>',
            "</g>",
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- readme


def replace_block(text, name, content):
    pattern = re.compile(rf"(<!-- {name} starts -->).*?(<!-- {name} ends -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def recent_block(repos):
    lines = []
    for r in repos:
        date = r["pushedAt"][:10]
        lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else ""
        desc = r["description"] or ""
        if len(desc) > 55:
            desc = desc[:52].rstrip() + "..."
        desc = f" &mdash; {escape(desc)}" if desc else ""
        meta = f" <sub>`{lang}` {date}</sub>" if lang else f" <sub>{date}</sub>"
        lines.append(f"- [**{r['name']}**]({r['url']}){desc}{meta}")
    return "\n".join(lines)


def main():
    today = dt.date.today()
    stats = fetch()
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header_svg(avatar_data_uri()), encoding="utf-8")
    (ASSETS / "pipeline.svg").write_text(pipeline_svg(), encoding="utf-8")
    (ASSETS / "telemetry.svg").write_text(telemetry_svg(stats, today), encoding="utf-8")
    (ASSETS / "quote.svg").write_text(quote_svg(), encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = replace_block(text, "recent_repos", recent_block(stats["recent"]))
    readme.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
