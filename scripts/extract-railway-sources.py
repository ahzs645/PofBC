#!/usr/bin/env python3
"""Reproduce the registered railway crops from the three exact source files.

Requires PyMuPDF and Pillow. Downloads are deliberately separate from extraction.
Use --check to render in memory and verify the committed crop checksums.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "research/identity/railway-history-2026-11-12/source-register.json"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cariboo", required=True, type=Path)
    parser.add_argument("--pnra-image", required=True, type=Path)
    parser.add_argument("--canadian-rail", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "public")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    register = json.loads(REGISTER.read_text())
    paths = {
        "cariboo": args.cariboo,
        "pnra": args.pnra_image,
        "canadianRail547": args.canadian_rail,
    }
    for key, path in paths.items():
        if sha256(path.read_bytes()) != register["inputs"][key]["sha256"]:
            raise ValueError(f"Source checksum differs: {key} ({path})")

    output_root = args.output_root.resolve()
    count = 0
    with fitz.open(paths["cariboo"]) as cariboo, fitz.open(paths["canadianRail547"]) as canadian:
        pdfs = {"cariboo": cariboo, "canadianRail547": canadian}
        for asset in register["assets"] + register["contextAssets"]:
            provenance = asset["verification"]
            key = provenance["inputKey"]
            if key == "pnra":
                with Image.open(paths[key]) as original:
                    if list(original.size) != provenance["sourcePixelSize"]:
                        raise ValueError("Archive image dimensions differ")
                    crop = original.crop(provenance["cropBboxSourcePixels"])
                    buffer = io.BytesIO()
                    crop.save(buffer, format="PNG")
                    data = buffer.getvalue()
                    size = list(crop.size)
            else:
                page = pdfs[key][provenance["sourcePdfPage"] - 1]
                rect = fitz.Rect(provenance["cropBboxPdfPoints"])
                if not page.rect.contains(rect):
                    raise ValueError(f"Crop outside source page: {asset['id']}")
                scale = provenance["renderDpi"] / 72
                pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=rect, alpha=False)
                data = pixmap.tobytes("png")
                size = [pixmap.width, pixmap.height]
            if size != provenance["pixelSize"] or sha256(data) != asset["sha256"]:
                raise ValueError(f"Rendered crop differs: {asset['id']}; check renderer versions")
            destination = (output_root / asset["file"]).resolve()
            if not destination.is_relative_to(output_root):
                raise ValueError(f"Invalid output path: {asset['file']}")
            if args.check:
                if not destination.exists() or sha256(destination.read_bytes()) != asset["sha256"]:
                    raise ValueError(f"Committed crop differs: {asset['file']}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            count += 1
    print(f"{'Verified' if args.check else 'Wrote'} {count} source crops; all dimensions and SHA-256 checksums match")


if __name__ == "__main__":
    main()
