"""Turn a cleaned ASCII portrait into a self-contained, animated SVG.

Each ASCII line becomes one <tspan>, wrapped in a single <text> container with
xml:space="preserve" so leading spaces survive. GitHub renders the SVG through
its image proxy, which keeps internal CSS animation working (no external refs).

    python scripts/ascii_to_svg.py assets/portrait.txt assets/portrait.svg
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

FONT_SIZE = 11
LINE_HEIGHT = 11  # equal to font size: ASCII art wants tight, uniform rows
CHAR_WIDTH = FONT_SIZE * 0.6  # monospace advance width
PAD = 16
FG = "#00ff41"  # phosphor green
BG = "#0d1117"  # github dark canvas
REVEAL_PER_LINE = 0.045  # seconds between line reveals (scanline effect)


def build(lines: list[str]) -> str:
    cols = max((len(l) for l in lines), default=0)
    width = int(cols * CHAR_WIDTH + PAD * 2)
    height = int(len(lines) * LINE_HEIGHT + PAD * 2)

    spans = []
    for i, line in enumerate(lines):
        delay = round(i * REVEAL_PER_LINE, 3)
        dy = PAD + FONT_SIZE if i == 0 else LINE_HEIGHT
        spans.append(
            f'<tspan x="{PAD}" dy="{dy}" style="animation-delay:{delay}s">'
            f"{escape(line)}</tspan>"
        )

    total = round(len(lines) * REVEAL_PER_LINE, 3)
    tspans = "\n      ".join(spans)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait of Sajeewa Garusinghe">
  <style>
    .bg {{ fill: {BG}; }}
    text {{
      font-family: "SFMono-Regular", "Consolas", "Liberation Mono", Menlo, monospace;
      font-size: {FONT_SIZE}px;
      fill: {FG};
    }}
    tspan {{
      opacity: 0;
      animation: reveal 0.35s ease-out forwards;
    }}
    @keyframes reveal {{
      from {{ opacity: 0; }}
      to   {{ opacity: 0.92; }}
    }}
    .cursor {{
      fill: {FG};
      animation: blink 1s step-end infinite {total}s;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      tspan {{ opacity: 0.92; animation: none; }}
      .cursor {{ animation: none; }}
    }}
  </style>
  <rect class="bg" width="100%" height="100%" rx="6"/>
  <text xml:space="preserve">
      {tspans}
  </text>
  <rect class="cursor" x="{PAD}" y="{height - PAD - FONT_SIZE + 2}"
        width="{CHAR_WIDTH:.1f}" height="{FONT_SIZE}"/>
</svg>
"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    lines = src.read_text(encoding="utf-8").rstrip("\n").split("\n")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(build(lines), encoding="utf-8")

    print(f"{src} -> {dst}  ({len(lines)} lines, {max(len(l) for l in lines)} cols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
