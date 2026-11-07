"""Build only the BC Place reconstruction's gallery display copies.

Run after build-collected-marks.mjs. The source SVGs use simple geometric paths,
so PyMuPDF can provide the pixels needed to measure bounds and choose display
colours. The shared display builder edits only the SVG viewBox and flat colours;
the downloads retain their original geometry, colours and checksums.

Dependencies: PyMuPDF, numpy, scipy, Pillow, and Node.
Run: python3 scripts/build-bc-place-display.py
"""

import json
import sys
from pathlib import Path

import fitz

import build_collected_display as display


def rasterize(jobs):
    """Render this reconstruction's simple SVGs without browser automation."""
    results = []
    for job in jobs:
        height = round(min(job["height"], job["maxWidth"] / job["aspect"]))
        width = round(height * job["aspect"])
        fitz.TOOLS.set_aa_level(8 if job.get("antialias", True) else 0)
        try:
            with fitz.open(stream=Path(job["src"]).read_bytes(), filetype="svg") as document:
                page = document[0]
                matrix = fitz.Matrix(width / page.rect.width, height / page.rect.height)
                pixmap = page.get_pixmap(matrix=matrix, alpha=True)
                pixmap.save(job["out"])
        finally:
            fitz.TOOLS.set_aa_level(8)
        results.append({"out": job["out"], "width": pixmap.width, "height": pixmap.height})
    return results


def main():
    register = json.loads((display.ROOT / "research/identity/bc-place-reconstruction-2026-11-03/source-register.json").read_text())
    ids = [asset["id"] for asset in register["assets"] if asset.get("isVector")]
    if not ids:
        raise SystemExit("The BC Place reconstruction register contains no vector assets")
    display.rasterize = rasterize
    sys.argv = [sys.argv[0], *ids]
    display.main()


if __name__ == "__main__":
    main()
