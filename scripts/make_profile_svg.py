"""Render the whole profile card -- ASCII portrait + neofetch panel -- as one SVG.

Emits dark.svg and light.svg. README.md is then just a <picture> that swaps
between them on prefers-color-scheme, so the profile renders identically
everywhere and never depends on GitHub's code-block font.

    python scripts/make_profile_svg.py

The ASCII is drawn at a 9px line step, then squashed with scale(SX, SY):
character cells are ~2:1 tall, so an un-squashed portrait looks stretched.
"""

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASCII_SRC = ROOT / "assets" / "portrait.txt"

W, H = 1180, 566
FS = 15  # font size
STEP = 9  # ascii line step, pre-scale
SX, SY = 0.42, 0.86  # squash the ascii into human proportions
PANEL_X = 500  # right column starts here
PANEL_TOP = 42
PANEL_STEP = 21

THEMES = {
    "dark": {
        "bg": "#000000",
        "ascii": "#00FF41",
        "key": "#5EEAD4",
        "value": "#E5E7EB",
        "dim": "#5f6b7a",
        "accent": "#39ff14",
    },
    "light": {
        "bg": "#FFFFFF",
        "ascii": "#14532D",
        "key": "#0F766E",
        "value": "#1F2937",
        "dim": "#94A3B8",
        "accent": "#166534",
    },
}

# (key, value) -- key None renders a bare line, ("", "") a blank spacer
ROWS = [
    ("@", "sajeewa@alibaba"),
    ("-", "-" * 46),
    ("Subject", "Sajeewa Garusinghe"),
    ("Role", "Senior Software Engineer"),
    ("Company", "Alibaba Group"),
    ("Division", "Alibaba Cloud · Daraz Financial Services (Koko)"),
    ("Origin", "Colombo, Sri Lanka"),
    ("Status", "Building • Scaling • Shipping"),
    ("", ""),
    ("Core", "Java, Python, JavaScript, SQL"),
    ("Backend", "Spring Boot 3, Node.js, Microservices"),
    ("Frontend", "React, HTML/CSS"),
    ("Streaming", "Apache Kafka"),
    ("Data", "PostgreSQL, MySQL, Spanner, BigQuery, Redis"),
    ("Cloud", "AWS, GCP, Azure, Alibaba Cloud"),
    ("DevOps", "Docker, Kubernetes, Jenkins, Git"),
    ("Observability", "OpenTelemetry, Grafana Tempo"),
    ("Security", "OAuth 2.0 / OIDC, JWT, RBAC"),
    ("ToolChain", "IntelliJ, VS Code, Postman, Maven, Gradle"),
    ("", ""),
    ("Education", "MSc Advanced Software Eng — Westminster"),
    ("", "BSc (Hons) Electrical Eng — Moratuwa"),
    ("Contact", "linkedin.com/in/spgarusinghe"),
]

KEYW = 15  # key column width, in characters, before the dot leader


def panel(theme: dict) -> str:
    out = []
    y = PANEL_TOP
    for key, val in ROWS:
        if key == "" and val == "":
            y += PANEL_STEP
            continue
        if key == "@":
            out.append(
                f'<text x="{PANEL_X}" y="{y}" fill="{theme["accent"]}" '
                f'font-weight="bold">{escape(val)}</text>'
            )
        elif key == "-":
            out.append(
                f'<text x="{PANEL_X}" y="{y}" fill="{theme["dim"]}">{escape(val)}</text>'
            )
        elif key == "":  # continuation line, indented under the value column
            pad = " " * (KEYW + 2)
            out.append(
                f'<text x="{PANEL_X}" y="{y}" fill="{theme["value"]}" '
                f'xml:space="preserve">{escape(pad + val)}</text>'
            )
        else:
            leader = "." * max(KEYW - len(key), 1)
            out.append(
                f'<text x="{PANEL_X}" y="{y}" xml:space="preserve">'
                f'<tspan fill="{theme["key"]}" font-weight="bold">{escape(key)}</tspan>'
                f'<tspan fill="{theme["dim"]}"> {leader} </tspan>'
                f'<tspan fill="{theme["value"]}">{escape(val)}</tspan>'
                f"</text>"
            )
        y += PANEL_STEP
    return "\n  ".join(out)


def ascii_block(lines: list[str], theme: dict) -> str:
    spans = [
        f'<tspan x="0" y="{i * STEP}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    ]
    return (
        f'<g transform="translate(24,26) scale({SX},{SY})">\n'
        f'    <text fill="{theme["ascii"]}" xml:space="preserve">\n      '
        + "\n      ".join(spans)
        + "\n    </text>\n  </g>"
    )


def build(theme_name: str, lines: list[str]) -> str:
    t = THEMES[theme_name]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img"
     aria-label="Sajeewa Garusinghe — Senior Software Engineer at Alibaba Group">
  <style>
    text, tspan {{
      font-family: "ConsolasFallback", Consolas, "SFMono-Regular", Menlo, monospace;
      font-size: {FS}px;
      white-space: pre;
    }}
    .cursor {{ animation: blink 1.1s step-end infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .cursor {{ animation: none; }} }}
  </style>
  <rect width="{W}" height="{H}" fill="{t["bg"]}" rx="15"/>
  {ascii_block(lines, t)}
  {panel(t)}
  <text x="{PANEL_X}" y="{H - 22}" fill="{t["dim"]}">sajeewa@alibaba:~$ <tspan
        class="cursor" fill="{t["accent"]}">█</tspan></text>
</svg>
"""


def main() -> int:
    lines = ASCII_SRC.read_text(encoding="utf-8").rstrip("\n").split("\n")
    for name in THEMES:
        dst = ROOT / f"{name}.svg"
        dst.write_text(build(name, lines), encoding="utf-8")
        print(f"{dst.name}  ({len(lines)} ascii rows, {max(map(len, lines))} cols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
