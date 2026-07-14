"""Photo -> ASCII -> cleaned ASCII -> animated SVG, in one shot.

The portrait currently in the README was built with:

    python scripts/build_portrait.py assets/profile.jpeg \
        --width 80 --crop 45,60,785,880 --negative

--negative matters: the photo has a white backdrop, and the converter maps
*bright* pixels to dense glyphs. Without it the backdrop renders as a solid
wall of '%' and the face disappears into it. Inverted, the backdrop falls away
to empty space and the hair/brows/beard/shirt become the strokes.

--crop trims the frame to head-and-shoulders; uncropped, the black t-shirt
eats nine rows as a solid slab.

Steps (per GUIDE.md):
  1. ascii-image-converter <img> --width N      -> raw ASCII
  2. clean: strip blank edges, dedent to a common left margin, cap at 60 lines
  3. ascii_to_svg.py                            -> assets/portrait.svg

Pass --width several times to eyeball a few sizes before committing:
    python scripts/build_portrait.py face.png --width 60 --width 90 --width 120
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MAX_LINES = 60  # the guide's ceiling: beyond this the face stops reading


def find_converter() -> str:
    exe = shutil.which("ascii-image-converter") or shutil.which(
        "ascii-image-converter.exe"
    )
    if exe:
        return exe
    local = ROOT / "tools" / "ascii-image-converter.exe"
    if local.exists():
        return str(local)
    sys.exit(
        "ascii-image-converter not found. Download it from\n"
        "  https://github.com/TheZoraiz/ascii-image-converter/releases\n"
        f"and drop the .exe in {ROOT / 'tools'} (or put it on PATH)."
    )


def to_ascii(exe: str, image: Path, width: int, extra: list[str]) -> str:
    out = subprocess.run(
        [exe, str(image), "--width", str(width), *extra],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout


def clean(raw: str, max_lines: int = MAX_LINES) -> list[str]:
    lines = [l.rstrip() for l in raw.replace("\r\n", "\n").split("\n")]

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    body = [l for l in lines if l.strip()]
    if not body:
        sys.exit("converter produced no ASCII -- is the image readable?")

    # every line starts at the same position
    indent = min(len(l) - len(l.lstrip()) for l in body)
    lines = [l[indent:] if l.strip() else "" for l in lines]

    if len(lines) > max_lines:
        sys.exit(
            f"{len(lines)} lines > {max_lines} cap -- rerun with a smaller --width"
        )
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--width", type=int, action="append", default=None)
    ap.add_argument("--tag", default="", help="name suffix, e.g. --tag complex")
    ap.add_argument("--crop", default="", help="crop box x0,y0,x1,y1 before converting")
    ap.add_argument("--max-lines", type=int, default=MAX_LINES)
    # anything else (--complex, -n, -m '...') is forwarded to the converter
    args, extra = ap.parse_known_args()
    extra = [a for a in extra if a != "--"]

    if not args.image.exists():
        sys.exit(f"no such image: {args.image}")

    widths = args.width or [90]
    exe = find_converter()
    ASSETS.mkdir(exist_ok=True)

    image = args.image
    if args.crop:
        from PIL import Image  # only needed on the crop path

        cropped = ASSETS / "face.png"
        Image.open(image).crop(
            tuple(int(v) for v in args.crop.split(","))
        ).save(cropped)
        print(f"cropped {image.name} -> {cropped.name}")
        image = cropped

    for w in widths:
        lines = clean(to_ascii(exe, image, w, extra), args.max_lines)
        suffix = (f"-{args.tag}" if args.tag else "") + (
            "" if len(widths) == 1 else f"-{w}"
        )
        txt = ASSETS / f"portrait{suffix}.txt"
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"w={w:>3}  {len(lines)} lines x {max(len(l) for l in lines)} cols  -> {txt}")

        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "ascii_to_svg.py"),
                str(txt),
                str(ASSETS / f"portrait{suffix}.svg"),
            ],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
