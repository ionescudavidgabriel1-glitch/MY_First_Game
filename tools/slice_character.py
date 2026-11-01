"""Cuts player frames out of assets/character.png into assets/sprites/player/.

The sheet is 480x268 pixel art upscaled to 2752x1536, on an opaque background
with baked-in grid lines and shadows. This restores the native resolution and
removes those. Requires Pillow, NumPy and SciPy. Run from the project root:

    python tools/slice_character.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SOURCE = Path("assets/character.png")
OUTPUT = Path("assets/sprites/player")
NATIVE_SIZE = (480, 268)
CANVAS_SIZE = (44, 56)  # Feet sit on the bottom edge of the canvas.

# Shadow, background and grid colors all lie along this line in RGB space.
SHADOW_RGB = np.array([33, 35, 44], float)
GRID_RGB = np.array([107, 115, 126], float)
BACKGROUND_TOLERANCE = 11

# Rows of the sheet, in native pixels: (top, bottom). Figures start at x = 78.
SURFACE_ROW = (33, 86)
UNDERGROUND_ROW = (153, 208)
LEFT_MARGIN = 78

# The side-view gas mask matches the grid color and its outline has gaps, so
# background removal can't tell them apart. These native pixels are forced to
# stay, as y: (first x, last x).
PROTECTED_SPANS = {
    168: (398, 413), 169: (398, 414), 170: (398, 414), 171: (401, 414),
    172: (401, 414), 173: (400, 413), 174: (400, 408),
}
FEET_ROWS = 8

# Output name -> index of the figure in its row, counted left to right.
SURFACE_FRAMES = {
    "front_0": 0, "front_1": 6,
    "back_0": 1, "back_1": 4,
    "side_0": 8, "side_1": 5, "side_2": 2, "side_3": 7,
}
UNDERGROUND_FRAMES = {"front_0": 4, "back_0": 6, "side_0": 7, "side_idle": 8}


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
    """Returns (rgb, mask) per figure, left to right, in row-sized crops."""
    band = native[row[0]:row[1], LEFT_MARGIN:]
    removable = background_like(band)
    for y, (first, last) in PROTECTED_SPANS.items():
        if row[0] <= y < row[1]:
            removable[y - row[0], first - LEFT_MARGIN:last + 1 - LEFT_MARGIN] = False
    labels, _ = ndi.label(removable)
    # Only background connected to the band's edge is removed, so colors
    # enclosed by a dark outline survive even if they match the background.
    edge = np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    outside = np.isin(labels, np.unique(edge[edge > 0]))
    figures, _ = ndi.label(~outside, np.ones((3, 3)))
    found = []
    for index, slices in enumerate(ndi.find_objects(figures), 1):
        mask = figures[slices] == index
        if mask.sum() >= 150:
            found.append((slices[1].start, band[slices], mask))
    found.sort(key=lambda item: item[0])
    return [(rgb, mask) for _, rgb, mask in found]


def repair_edges(mask):
    """Fills pinholes and drops stray pixels left by the background removal."""
    mask = mask.copy()
    # Grid lines touch the boots. They are thin, so opening removes them.
    mask[-FEET_ROWS:] = ndi.binary_opening(mask, np.ones((2, 2)))[-FEET_ROWS:]
    kernel = np.ones((3, 3), int)
    kernel[1, 1] = 0
    for _ in range(2):
        neighbours = ndi.convolve(mask.astype(int), kernel, mode="constant")
        mask = (mask & (neighbours >= 2)) | (~mask & (neighbours >= 6))
    # Side-by-side connectivity only, so specks touching at a corner are dropped.
    labels, count = ndi.label(mask)
    if count > 1:
        sizes = ndi.sum(mask, labels, range(1, count + 1))
        mask = labels == int(np.argmax(sizes)) + 1
    return mask


def to_canvas(rgb, mask):
    """Centers on the figure's mass, so frames don't jitter sideways."""
    canvas_w, canvas_h = CANVAS_SIZE
    canvas = np.zeros((canvas_h, canvas_w, 4), np.uint8)
    offset_x = canvas_w // 2 - int(round(np.nonzero(mask)[1].mean()))
    offset_y = canvas_h - mask.shape[0]
    for y, x in zip(*np.nonzero(mask)):
        canvas[y + offset_y, x + offset_x] = (*rgb[y, x], 255)
    return Image.fromarray(canvas, "RGBA")


def export(native, row, frames, folder):
    figures = find_figures(native, row)
    (OUTPUT / folder).mkdir(parents=True, exist_ok=True)
    for name, index in frames.items():
        rgb, mask = figures[index]
        to_canvas(rgb, repair_edges(mask)).save(OUTPUT / folder / f"{name}.png")


def main():
    native = to_native(SOURCE)
    export(native, SURFACE_ROW, SURFACE_FRAMES, "farmer")
    export(native, UNDERGROUND_ROW, UNDERGROUND_FRAMES, "drug_lord")


if __name__ == "__main__":
    main()
