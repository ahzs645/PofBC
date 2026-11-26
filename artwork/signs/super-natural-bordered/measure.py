"""Register the drawing to the original camera image and compare native photo pixels."""
from base64 import b64decode
from io import BytesIO
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / "src/signs/tourism"
NAME = "super-natural-bordered"
SIZE = (814, 440)
# Top left, top right, bottom right, bottom left. Extend the straight edges
# through the rounded corners and the bicycle at the lower left.
CORNERS = [(60.68, 47.92), (212.16, 60.79), (227.02, 142.59), (71.32, 135.74)]
BOARD = [(0, 0), (814, 0), (814, 440), (0, 440)]
# Boundaries between photographed characters, measured in board coordinates.
# The first and last cut enclose the line. Word spaces are included.
ROWS = {
    "Super, Natural": (35, 160, [79, 144, 197, 248, 293, 334, 374, 464, 513, 549, 602, 645, 697, 741]),
    "British Columbia": (178, 281, [32, 104, 149, 181, 219, 250, 292, 360, 443, 488, 519, 572, 650, 699, 729, 789]),
    "welcomes you": (289, 402, [121, 191, 234, 265, 307, 356, 431, 476, 531, 592, 637, 694]),
}


def homography(src, dst):
    rows, rhs = [], []
    for (x, y), (u, v) in zip(src, dst):
        rows.extend([[x, y, 1, 0, 0, 0, -u*x, -u*y],
                     [0, 0, 0, x, y, 1, -v*x, -v*y]])
        rhs.extend([u, v])
    return np.append(np.linalg.solve(rows, rhs), 1).reshape(3, 3)


def transform(image, size, mapping):
    coefficients = (mapping / mapping[2, 2]).ravel()[:8]
    return image.transform(size, Image.Transform.PERSPECTIVE, coefficients, Image.Resampling.BICUBIC)


def render_ink():
    # Rasterize the delivered outlines as a group and individually. Keeping the
    # typed letters separate avoids assigning their ink to a neighbour when the
    # natural font advances place them across the photographed letter boundaries.
    svg = ET.parse(ASSETS / (NAME + ".svg")).getroot()
    layers = svg.findall("{*}g")
    ink = ET.Element(svg.tag, svg.attrib)
    ink.extend(layers)
    drawings = [ET.tostring(ink, encoding="unicode")]
    labels = []
    for layer in layers:
        label = layer.get("aria-label")
        for path in layer.findall("{*}path"):
            letter = ET.Element(svg.tag, svg.attrib)
            group = ET.SubElement(letter, layer.tag, layer.attrib)
            group.append(path)
            drawings.append(ET.tostring(letter, encoding="unicode"))
            labels.append(label)
    render = """
      import { readFileSync } from 'node:fs'
      import { Resvg } from '@resvg/resvg-js'
      const drawings = JSON.parse(readFileSync(0, 'utf8'))
      const pngs = drawings.map(svg => new Resvg(svg).render().asPng().toString('base64'))
      process.stdout.write(JSON.stringify(pngs))
    """
    output = subprocess.check_output(["node", "--input-type=module", "-e", render],
                                     input=json.dumps(drawings).encode(), cwd=ROOT)
    masks = [Image.open(BytesIO(b64decode(png))).getchannel("A") for png in json.loads(output)]
    return masks[0], list(zip(labels, masks[1:], strict=True))


def project_ink(photo, camera_to_board):
    ink, letters = render_ink()
    supersample = 6
    display_size = (photo.width * supersample, photo.height * supersample)
    mapping = camera_to_board @ np.diag([1/supersample, 1/supersample, 1])
    projected = transform(ink, display_size, mapping)
    centres = {label: [] for label in ROWS}
    for label, letter in letters:
        coverage = transform(letter, display_size, mapping).resize(photo.size, Image.Resampling.BOX)
        y, x = np.nonzero(np.asarray(coverage) >= 128)
        centres[label].append((x.mean(), y.mean()))
    backdrop = photo.resize(display_size, Image.Resampling.BICUBIC)
    overlay = Image.composite(Image.new("RGB", display_size, "#fc27a1"), backdrop, projected)
    # Average the projected ink coverage over each *original* photo pixel.
    native = np.asarray(projected.resize(photo.size, Image.Resampling.BOX)) >= 128
    return overlay, native, centres


def measure(photo, vector_ink, centres, camera_to_board, threshold):
    photo_ink = np.asarray(photo)[:, :, 0] < threshold
    y, x = np.indices(photo_ink.shape)
    # Pillow coordinates put the centre of the first pixel at (0.5, 0.5).
    pixels = np.array([x.ravel() + .5, y.ravel() + .5, np.ones(x.size)])
    mapped = camera_to_board @ pixels
    u, v = (mapped[:2] / mapped[2]).reshape(2, *x.shape)
    scores = {}
    errors = []
    shared = union = 0
    for label, (top, bottom, cuts) in ROWS.items():
        region = (v >= top) & (v < bottom) & (u >= cuts[0]) & (u < cuts[-1])
        region &= ~((v >= 385) & (u < 539))  # bicycle and small marks below the greeting
        overlap = np.count_nonzero(region & photo_ink & vector_ink)
        either = np.count_nonzero(region & (photo_ink | vector_ink))
        scores[label] = round(100 * overlap / either, 1)
        shared += overlap
        union += either
        # Compare centre-to-centre spacing along the baseline in the camera image.
        ends = np.linalg.solve(camera_to_board, [[cuts[0], cuts[-1]], [bottom, bottom], [1, 1]])
        line = np.diff(ends[:2] / ends[2], axis=1).ravel()
        along = (x * line[0] + y * line[1]) / np.linalg.norm(line)
        offsets = []
        for left, right, centre in zip(cuts[:-1], cuts[1:], centres[label], strict=True):
            cell = region & (u >= left) & (u < right)
            offsets.append(np.dot(centre, line) / np.linalg.norm(line) - along[cell & photo_ink].mean())
        errors.extend(abs(np.diff(offsets)))
    scores["All lettering"] = round(100 * shared / union, 1)
    return scores, {"pairs": len(errors), "meanAbsoluteErrorPixels": round(float(np.mean(errors)), 2)}


if __name__ == "__main__":
    photo = Image.open(HERE / "source.png").convert("RGB")
    board_to_camera = homography(BOARD, CORNERS)
    camera_to_board = np.linalg.inv(board_to_camera)
    transform(photo, SIZE, board_to_camera).save(ASSETS / (NAME + ".reference.png"))
    overlay, native, centres = project_ink(photo, camera_to_board)
    overlay = overlay.resize((photo.width * 3, photo.height * 3), Image.Resampling.LANCZOS)
    overlay.save(ASSETS / (NAME + ".overlap.png"), optimize=True)
    scores, spacing = measure(photo, native, centres, camera_to_board, 86)
    metrics = {"iouPercent": scores, "spacing": spacing, "redThreshold": 86, "thresholdSensitivity": {
        cutoff: measure(photo, native, centres, camera_to_board, cutoff)[0]["All lettering"] for cutoff in (80, 92)
    }}
    (ASSETS / (NAME + ".metrics.json")).write_text(json.dumps(metrics, indent=2) + "\n")
