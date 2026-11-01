"""Cuts ground tiles out of assets/word/ground_tiles.jpg into one tile sheet.

Each tile on the sheet has its own dark edge, which shows as a grid when it
repeats. This trims the edges and patches the joins, so tiles repeat cleanly.
Requires Pillow, NumPy and SciPy. Run from the project root:

    python tools/slice_ground.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SOURCE = Path("assets/word/ground_tiles.jpg")
OUTPUT = Path("assets/sprites/ground/ground_tiles.png")
TILE_SIZE = 32
MIN_TILE_AREA = 50000  # In sheet pixels. Smaller blobs are not tiles.
TRIM = 0.13  # Share of each side that is cut away.
PATCH_WIDTH = 3.5  # How far from a join the patching reaches, in tile pixels.

# Tiles to export, left to right in the output. Index counts along the sheet's
# rows: 0 grass, 1 flower grass, 2 lush grass, 3 dirt, 4 dry soil, 5 wet soil,
# 6 sand, 7 cobblestone.
TILES = [0, 1]


def find_tiles(image):
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    background = (np.abs(r - b) < 50) & (np.minimum(r, b) - g > 60)
    labels, _ = ndi.label(ndi.binary_opening(~background, np.ones((9, 9))))
    tiles = [
        slices for index, slices in enumerate(ndi.find_objects(labels), 1)
        if (labels[slices] == index).sum() > MIN_TILE_AREA
    ]
    middle = image.shape[0] / 2
    tiles.sort(key=lambda s: (s[0].start > middle, s[1].start))
    return [image[slices] for slices in tiles]


def shrink(image):
    """Downscales using each block's median, so JPEG noise doesn't show."""
    height, width, _ = image.shape
    edges_y = np.linspace(0, height, TILE_SIZE + 1).astype(int)
    edges_x = np.linspace(0, width, TILE_SIZE + 1).astype(int)
    out = np.zeros((TILE_SIZE, TILE_SIZE, 3), np.uint8)
    for j in range(TILE_SIZE):
        for i in range(TILE_SIZE):
            block = image[edges_y[j]:edges_y[j + 1], edges_x[i]:edges_x[i + 1]]
            out[j, i] = np.median(block.reshape(-1, 3), axis=0)
    return out


def remove_joins(tile):
    """Moves the joins to the tile's center, then scatters other pixels over
    them. Scattering instead of blending keeps the art's own colors."""
    rng = np.random.default_rng(1)
    middle = TILE_SIZE / 2 - 0.5
    shifted = np.roll(tile, (TILE_SIZE // 2, TILE_SIZE // 2), (0, 1))
    distance_x = np.abs(np.arange(TILE_SIZE) - middle)[None, :]
    distance_y = np.abs(np.arange(TILE_SIZE) - middle)[:, None]
    chance = np.clip(1 - np.minimum(distance_x, distance_y) / PATCH_WIDTH, 0, 1)
    replace = rng.random((TILE_SIZE, TILE_SIZE)) < chance
    shifted[replace] = tile[::-1, ::-1][replace]
    return shifted


def main():
    image = np.asarray(Image.open(SOURCE).convert("RGB")).astype(int)
    found = find_tiles(image)
    if len(found) != 8:
        raise SystemExit(f"Expected 8 tiles, found {len(found)}")
    sheet = Image.new("RGB", (TILE_SIZE * len(TILES), TILE_SIZE))
    for column, index in enumerate(TILES):
        tile = found[index]
        height, width, _ = tile.shape
        cut = int(min(height, width) * TRIM)
        finished = remove_joins(shrink(tile[cut:height - cut, cut:width - cut]))
        sheet.paste(Image.fromarray(finished, "RGB"), (column * TILE_SIZE, 0))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT)


if __name__ == "__main__":
    main()
