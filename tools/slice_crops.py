"""Cuts crop growth stages out of assets/crops.jpg into assets/sprites/crops/.

The sheet is 480x268 pixel art upscaled to 2752x1536, on an opaque background
with baked-in grid lines and shadows. This restores the native resolution and
removes those. Requires Pillow, NumPy and SciPy. Run from the project root:

    python tools/slice_crops.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SOURCE = Path("assets/crops.jpg")
OUTPUT = Path("assets/sprites/crops")
NATIVE_SIZE = (480, 268)
CANVAS_SIZE = (40, 48)  # The base of the plant sits on the bottom edge.
MIN_FIGURE_PIXELS = 40
# Shadow, background and grid colors all lie along this line in RGB space.
SHADOW_RGB = np.array([33, 35, 44], float)
GRID_RGB = np.array([107, 115, 126], float)
BACKGROUND_TOLERANCE = 11
# Background color, which also shows through gaps enclosed by leaves.
BACKGROUND_RGB = np.array([64, 68, 79], float)
ENCLOSED_TOLERANCE = 14

# Native pixels: (top, bottom). Starts below the column titles.
TOMATO_ROW = (43, 88)
ROW_LEFT = 82
ROW_RIGHT = 480
# The ripe stage shows three joined plants. Keep the leftmost, as native x range.
TOMATO_RIPE_X = (387, 412)


def to_native(path):
    image = np.asarray(Image.open(path).convert("RGB")).astype(float)
    height, width, _ = image.shape
    native_w, native_h = NATIVE_SIZE
    scale_x, scale_y = width / native_w, height / native_h
    native = np.zeros((native_h, native_w, 3), np.uint8)
    for j in range(native_h):
        for i in range(native_w):
            # The median of each block's center ignores blur at its edges.
            x0 = int(i * scale_x + 1.5)
            x1 = max(int((i + 1) * scale_x - 1.5), x0 + 1)
            y0 = int(j * scale_y + 1.5)
            y1 = max(int((j + 1) * scale_y - 1.5), y0 + 1)
            native[j, i] = np.median(image[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    return native


def background_like(rgb):
    axis = GRID_RGB - SHADOW_RGB
    t = np.clip(((rgb - SHADOW_RGB) @ axis) / (axis @ axis), 0, 1)
    closest = SHADOW_RGB + t[..., None] * axis
    return np.linalg.norm(rgb - closest, axis=2) < BACKGROUND_TOLERANCE


def find_figures(native, row):
    band = native[row[0]:row[1], ROW_LEFT:ROW_RIGHT]
    labels, _ = ndi.label(background_like(band))
    edge = np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    figures, _ = ndi.label(~np.isin(labels, np.unique(edge[edge > 0])), np.ones((3, 3)))
    found = []
    for index, slices in enumerate(ndi.find_objects(figures), 1):
        mask = figures[slices] == index
        if mask.sum() >= MIN_FIGURE_PIXELS:
            gaps = np.linalg.norm(band[slices].astype(float) - BACKGROUND_RGB, axis=2) < ENCLOSED_TOLERANCE
            mask = mask & ~gaps
            found.append((slices[1].start + ROW_LEFT, band[slices], mask))
    found.sort(key=lambda item: item[0])
    return found


def largest_part(mask):
    labels, count = ndi.label(mask)
    sizes = ndi.sum(mask, labels, range(1, count + 1))
    return labels == int(np.argmax(sizes)) + 1


def to_canvas(rgb, mask):
    canvas_w, canvas_h = CANVAS_SIZE
    canvas = np.zeros((canvas_h, canvas_w, 4), np.uint8)
    rows = np.nonzero(mask.any(axis=1))[0]
    bottom = rows[-1]
    offset_x = canvas_w // 2 - int(round(np.nonzero(mask)[1].mean()))
    offset_y = canvas_h - 1 - bottom
    for y, x in zip(*np.nonzero(mask)):
        canvas[y + offset_y, x + offset_x] = (*rgb[y, x], 255)
    return Image.fromarray(canvas, "RGBA")


def main():
    native = to_native(SOURCE)
    figures = find_figures(native, TOMATO_ROW)
    if len(figures) != 4:
        raise SystemExit(f"Expected 4 tomato stages, found {len(figures)}")
    folder = OUTPUT / "tomato"
    folder.mkdir(parents=True, exist_ok=True)
    for stage, (left, rgb, mask) in enumerate(figures, 1):
        if stage == 4:
            first, last = (x - left for x in TOMATO_RIPE_X)
            rgb, mask = rgb[:, first:last], largest_part(mask[:, first:last])
        to_canvas(rgb, mask).save(folder / f"stage_{stage}.png")


if __name__ == "__main__":
    main()
