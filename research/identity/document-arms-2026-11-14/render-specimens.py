"""Render source pages and documented detail regions; never redraw or clean the scans.

Run with the workspace Python environment (PyMuPDF). Original PDFs are retained
beside the outputs. Coordinates are PDF points, measured from the top left.
"""
from pathlib import Path
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / "reference"
SOURCES = {
    "oic-1121-1978.pdf": {
        "url": "https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978",
        "publisher": "Queen's Printer of British Columbia / BC Laws",
        "documentDate": "1978-05-04",
    },
    "oic-832-1978.pdf": {
        "url": "https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978",
        "publisher": "Queen's Printer of British Columbia / BC Laws",
        "documentDate": "1978-04-06",
    },
    "mining-bc-1954.pdf": {
        "url": "https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf",
        "publisher": "British Columbia Department of Mines; Don McDiarmid, Queen's Printer",
        "documentDate": "1954",
    },
}
SPECIMENS = [
    ("oic-1121-heading", "oic-1121-1978.pdf", 1, [275, 0, 495, 110]),
    ("oic-1121-grant", "oic-1121-1978.pdf", 4, [110, 5, 505, 153]),
    ("oic-832-heading", "oic-832-1978.pdf", 1, [280, 10, 490, 120]),
    ("mining-1954-cover", "mining-bc-1954.pdf", 1, [130, 500, 405, 615]),
    ("mining-1954-title", "mining-bc-1954.pdf", 2, [130, 510, 405, 620]),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = {
        "reviewed": "2026-11-14",
        "purpose": "Reference specimens only. These pixels never enter exported study artwork.",
        "rendering": {
            "tool": "PyMuPDF", "version": fitz.VersionBind,
            "pageDpi": 110, "detailDpi": 216,
            "treatment": "PDF page rendering and rectangular detail clips only; no cleanup, recolouring, tracing or generated detail.",
        },
        "sources": [], "specimens": [],
    }
    for filename, metadata in SOURCES.items():
        path = REFERENCE / filename
        with fitz.open(path) as document:
            manifest["sources"].append({
                "file": "reference/" + filename, **metadata,
                "sha256": digest(path), "bytes": path.stat().st_size,
                "pages": len(document),
            })
    image_path = REFERENCE / "1906-arms.jpg"
    manifest["sources"].append({
        "file": "reference/1906-arms.jpg",
        "url": "https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/1906-arms.jpg",
        "contextUrl": "https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms",
        "publisher": "Province of British Columbia", "dimensions": [200, 186],
        "sha256": digest(image_path), "bytes": image_path.stat().st_size,
        "dateNote": "1906 describes the design, not an established creation date for this digital illustration.",
    })
    for name, filename, page_number, clip in SPECIMENS:
        with fitz.open(REFERENCE / filename) as document:
            page = document[page_number - 1]
            page_path = REFERENCE / f"{name}-page.png"
            detail_path = REFERENCE / f"{name}-detail.png"
            page.get_pixmap(dpi=110, alpha=False).save(page_path)
            page.get_pixmap(dpi=216, clip=fitz.Rect(clip), alpha=False).save(detail_path)
            manifest["specimens"].append({
                "id": name, "source": "reference/" + filename,
                "page": page_number, "pageSizePoints": list(page.rect),
                "detailClipPoints": clip,
                "pageImage": {"file": "reference/" + page_path.name, "sha256": digest(page_path)},
                "detailImage": {"file": "reference/" + detail_path.name, "sha256": digest(detail_path)},
            })
    (ROOT / "source-register.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Rendered {len(SPECIMENS)} documented specimens from {len(SOURCES)} retained PDFs.")

if __name__ == "__main__":
    main()
