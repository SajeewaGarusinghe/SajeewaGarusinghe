"""Prep a photo so ascii-image-converter can actually see the face.

GUIDE.md asks for a plain background and high contrast. This photo has neither:
the tiled wall (L~124-175) is *brighter* than the skin (L~85), so a naive
conversion draws the bathroom and erases the subject.

Fix: split on a luminance cutoff. Everything above it (wall, shirt) is crushed
to white -> becomes empty space in the ASCII. Everything below it (skin, hair,
sunglasses, beard) is stretched across the full range -> becomes the strokes.

    python scripts/prep_photo.py assets/unnamed.webp assets/face.png --cutoff 112
"""

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


def prep(
    src: Path,
    dst: Path,
    cutoff: int,
    floor: int,
    blur: float,
    gamma: float,
    box: str,
) -> None:
    im = Image.open(src).convert("L")

    if box:
        im = im.crop(tuple(int(v) for v in box.split(",")))

    # knock down tile grout / skin texture before thresholding, or it turns to noise
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))

    span = max(cutoff - floor, 1)
    lut = []
    for v in range(256):
        if v >= cutoff:
            lut.append(255)  # background + shirt -> white -> empty
        else:
            # stretch [floor, cutoff) across [0, 245]; gamma > 1 drags the
            # midtones (skin) darker so the face gets real density, not dots
            t = max(v - floor, 0) / span
            lut.append(int((t**gamma) * 245))
    im = im.point(lut)

    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst)
    print(f"{src.name} -> {dst}  cutoff={cutoff} gamma={gamma} blur={blur} box={box or 'full'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--cutoff", type=int, default=112, help="above this -> white")
    ap.add_argument("--floor", type=int, default=8, help="below this -> black")
    ap.add_argument("--blur", type=float, default=1.5)
    ap.add_argument("--gamma", type=float, default=1.8, help=">1 darkens midtones")
    ap.add_argument("--box", default="", help="crop box x0,y0,x1,y1")
    a = ap.parse_args()
    prep(a.src, a.dst, a.cutoff, a.floor, a.blur, a.gamma, a.box)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
