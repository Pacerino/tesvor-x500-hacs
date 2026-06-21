"""Render Tesvor X500 path points into a PNG map image.

The X500 is a gyro/bump-navigation robot (no LIDAR), so the firmware only
reports a trail of path points: (x, y, type). We render that trail as a
coverage path with the dock and current robot position highlighted, similar
in spirit to a Dreame map camera but without room segmentation.
"""

from __future__ import annotations

import io

from PIL import Image, ImageDraw

from .const import MAP_IMAGE_SIZE, MAP_PADDING

# Colors (RGBA)
COLOR_BG = (18, 22, 28, 255)
COLOR_PATH = (110, 180, 255, 255)
COLOR_PATH_EDGE = (90, 220, 160, 255)
COLOR_DOCK = (255, 200, 60, 255)
COLOR_ROBOT = (255, 80, 80, 255)
COLOR_GRID = (40, 48, 58, 255)

# point type hints (best-effort; firmware "type" semantics are partial)
TYPE_EDGE = 1


def render_png(points: list[tuple[int, int, int]]) -> bytes:
    """Render the given path points to PNG bytes."""
    size = MAP_IMAGE_SIZE
    img = Image.new("RGBA", (size, size), COLOR_BG)
    draw = ImageDraw.Draw(img)

    _draw_grid(draw, size)

    if len(points) < 2:
        return _to_bytes(img)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)
    usable = size - 2 * MAP_PADDING
    scale = min(usable / span_x, usable / span_y)

    # Center the path within the image.
    off_x = (size - span_x * scale) / 2
    off_y = (size - span_y * scale) / 2

    def project(x: int, y: int) -> tuple[float, float]:
        px = off_x + (x - min_x) * scale
        # Flip Y so the map reads top-down naturally.
        py = size - (off_y + (y - min_y) * scale)
        return px, py

    # Draw the continuous path as connected segments.
    prev = None
    for x, y, kind in points:
        cur = project(x, y)
        if prev is not None:
            color = COLOR_PATH_EDGE if kind == TYPE_EDGE else COLOR_PATH
            draw.line([prev, cur], fill=color, width=3)
        prev = cur

    # Dock = first point; robot = last point.
    fx, fy = project(*points[0][:2])
    lx, ly = project(*points[-1][:2])
    _dot(draw, fx, fy, 8, COLOR_DOCK)
    _dot(draw, lx, ly, 9, COLOR_ROBOT)

    return _to_bytes(img)


def _draw_grid(draw: ImageDraw.ImageDraw, size: int, step: int = 50) -> None:
    for i in range(0, size, step):
        draw.line([(i, 0), (i, size)], fill=COLOR_GRID, width=1)
        draw.line([(0, i), (size, i)], fill=COLOR_GRID, width=1)


def _dot(
    draw: ImageDraw.ImageDraw, x: float, y: float, r: float, color
) -> None:
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def _to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
