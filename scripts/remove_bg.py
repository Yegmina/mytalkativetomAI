from __future__ import annotations

import math
from pathlib import Path

from PIL import Image


def near_white(r: int, g: int, b: int, threshold: int) -> bool:
    return math.sqrt((255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2) <= threshold


def remove_background(src: Path, dest: Path, threshold: int = 18) -> None:
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    pixels = img.load()
    visited = [[False] * h for _ in range(w)]

    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        if visited[x][y]:
            continue
        visited[x][y] = True
        r, g, b, a = pixels[x, y]
        if not near_white(r, g, b, threshold):
            continue
        pixels[x, y] = (r, g, b, 0)
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)


def main() -> None:
    base = Path("C:/work/talkingtom/frontend/public/assets/kit")
    pairs = [
        ("kit_body_neutral.jpg", "kit_body_neutral.png"),
        ("kit_body_happy.jpg", "kit_body_happy.png"),
        ("kit_body_sad.jpg", "kit_body_sad.png"),
        ("kit_body_angry.jpg", "kit_body_angry.png"),
        ("kit_body_tired.jpg", "kit_body_tired.png"),
    ]
    for src_name, out_name in pairs:
        src = base / src_name
        if not src.exists():
            print(f"skip {src_name}")
            continue
        dest = base / out_name
        remove_background(src, dest)
        print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
