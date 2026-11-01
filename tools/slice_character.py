"""Cuts the player walk frames out of the sheets into assets/sprites/player/.

The sheets have different pixel sizes, and the farmer's rows differ in height,
so each row is scaled on its own until the figure is TARGET_HEIGHT tall. That
keeps the character the same size when he turns or switches identity. Requires
Pillow, NumPy and SciPy. Run from the project root:

    python tools/slice_character.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUTPUT = Path("assets/sprites/player")
CANVAS_SIZE = (44, 56)  # Feet sit on the bottom edge of the canvas.
TARGET_HEIGHT = 48
MIN_FIGURE_AREA = 3000  # In sheet pixels. Smaller blobs are not figures.
SAME_ROW_DISTANCE = 100  # Figures whose tops are this close share a row.

# Each output row: (folder, name, sheet, row in the sheet, figures to use).
# Figures count left to right. The farmer's front figures 2, 4 and 5 turn
# sideways, and drog_dealer.jpg's side row never brings the legs together, so
# the Drug Lord's side walk comes from its own sheet.
ROWS = [
    ("farmer", "front", "assets/farmer.jpg", 0, [0, 1, 3]),
    ("farmer", "back", "assets/farmer.jpg", 1, [0, 1, 2, 3, 4, 5]),
    ("farmer", "side", "assets/farmer.jpg", 2, [0, 1, 2, 3, 4, 5, 6]),
    ("drug_lord", "front", "assets/drog_dealer.jpg", 0, [0, 1, 2, 3]),
    ("drug_lord", "back", "assets/drog_dealer.jpg", 1, [0, 1, 2, 3]),
    ("drug_lord", "side", "assets/drog_lord2.jpg", 0, [0, 1, 2, 3, 4, 5]),
]


def foreground_mask(image):
    """Everything except the magenta background and its purple shadow."""
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    return ~((np.abs(r - b) < 40) & (np.minimum(r, b) - g > 40))


def find_rows(image):
    """Returns the sheet's rows, each a left-to-right list of (rgb, mask)."""
    mask = foreground_mask(image)
    # Opening drops JPEG specks so they can't join figures or count as one.
    labels, _ = ndi.label(ndi.binary_opening(mask, np.ones((5, 5))), np.ones((3, 3)))
    found = []
    for index, slices in enumerate(ndi.find_objects(labels), 1):
        if (labels[slices] == index).sum() > MIN_FIGURE_AREA:
            found.append((slices[0].start, slices[1].start, index))
    rows = []
    for top, left, index in sorted(found):
        for row in rows:
            if abs(row[0][0] - top) < SAME_ROW_DISTANCE:
                row.append((top, left, index))
                break
        else:
            rows.append([(top, left, index)])
    return [[_crop(image, mask, labels, f[2]) for f in sorted(row, key=lambda f: f[1])] for row in rows]


def _crop(image, mask, labels, index):
    # Dilating restores the thin edge pixels that the opening removed.
    region = ndi.binary_dilation(labels == index, np.ones((9, 9))) & mask
    ys, xs = np.nonzero(region)
    box = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    return image[box], region[box]


def shrink(rgb, mask, scale):
    """Downscales using each block's median, so JPEG noise doesn't show."""
    height, width = mask.shape
    new_h, new_w = max(1, round(height * scale)), max(1, round(width * scale))
    edges_y = np.linspace(0, height, new_h + 1).astype(int)
    edges_x = np.linspace(0, width, new_w + 1).astype(int)
    out = np.zeros((new_h, new_w, 4), np.uint8)
    for j in range(new_h):
        for i in range(new_w):
            y = slice(edges_y[j], max(edges_y[j + 1], edges_y[j] + 1))
            x = slice(edges_x[i], max(edges_x[i + 1], edges_x[i] + 1))
            block = mask[y, x]
            if block.mean() >= 0.5:
                out[j, i, :3] = np.median(rgb[y, x][block], axis=0)
                out[j, i, 3] = 255
    return out


def to_canvas(pixels):
    """Centers on the figure's mass, so frames don't jitter sideways."""
    canvas_w, canvas_h = CANVAS_SIZE
    opaque = pixels[..., 3] > 0
    rows = np.nonzero(opaque.any(axis=1))[0]
    pixels = pixels[rows.min():rows.max() + 1]
    opaque = opaque[rows.min():rows.max() + 1]
    offset_x = canvas_w // 2 - int(round(np.nonzero(opaque)[1].mean()))
    offset_y = canvas_h - pixels.shape[0]
    canvas = np.zeros((canvas_h, canvas_w, 4), np.uint8)
    for y, x in zip(*np.nonzero(opaque)):
        canvas[y + offset_y, x + offset_x] = pixels[y, x]
    return Image.fromarray(canvas, "RGBA")


def main():
    sheets = {}
    for folder, name, sheet, row, figures in ROWS:
        if sheet not in sheets:
            image = np.asarray(Image.open(sheet).convert("RGB")).astype(int)
            sheets[sheet] = find_rows(image)
        chosen = [sheets[sheet][row][index] for index in figures]
        scale = TARGET_HEIGHT / float(np.median([mask.shape[0] for _, mask in chosen]))
        (OUTPUT / folder).mkdir(parents=True, exist_ok=True)
        for number, (rgb, mask) in enumerate(chosen):
            to_canvas(shrink(rgb, mask, scale)).save(OUTPUT / folder / f"{name}_{number}.png")


if __name__ == "__main__":
    main()
