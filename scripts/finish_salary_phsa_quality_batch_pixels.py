#!/usr/bin/env python3
"""Independent actual-PDF pixel replay; never opens a salary candidate file."""
import argparse
import collections
import hashlib
import io
import json
from pathlib import Path

import fitz
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run(images, views, pdf):
    manifest = json.loads(images.read_text())
    packet = json.loads(views.read_text())
    assert packet["originalImageManifest"] == pin(images)
    assert digest(pdf.read_bytes()) == manifest["sourceSha256"]
    assert (packet["sourceId"], packet["sourceSha256"]) == (manifest["sourceId"], manifest["sourceSha256"])
    originals = {r["sequence"]: r for r in manifest["rows"]}
    assert len(originals) == len(manifest["rows"]) == len(packet["rows"])
    groups = collections.defaultdict(list)
    for row in packet["rows"]:
        original = originals[row["sequence"]]
        assert all(row[k] == value for k, value in original.items())
        groups[row["physicalPage"]].append(row)
    pages, field_count = [], 0
    with fitz.open(pdf) as document:
        for number, rows in sorted(groups.items()):
            png = document[number - 1].get_pixmap(dpi=300, alpha=False).tobytes("png")
            source = Image.open(io.BytesIO(png)).convert("RGB")
            assert digest(png) == rows[0]["actualSourceImageSha256"]
            for row in rows:
                actual_source = Path(row["actualSourceImagePath"])
                assert digest(actual_source.read_bytes()) == row["actualSourceImageSha256"] == digest(png)
                full = Path(row["cropPath"])
                assert digest(full.read_bytes()) == row["cropSha256"]
                expected = source.crop(row["cropRectOriginal300DpiPixels"])
                assert ImageChops.difference(expected, Image.open(full).convert("RGB")).getbbox() is None
                assert [v["field"] for v in row["sourceNativeTargetViews"]] == row["reviewTargetFields"]
                for view in row["sourceNativeTargetViews"]:
                    path = Path(view["path"])
                    assert digest(path.read_bytes()) == view["sha256"]
                    expected = source.crop(view["originalPdf300DpiPixelBox"])
                    actual = Image.open(path).convert("RGB")
                    assert expected.size == actual.size
                    assert ImageChops.difference(expected, actual).getbbox() is None
                    field_count += 1
                for entry in ({"path": row["pageEvidencePath"], "sha256": row["pageEvidenceSha256"]}, row["rawPageEvidence"]):
                    assert digest((ROOT / entry["path"]).read_bytes()) == entry["sha256"]
            pages.append({"physicalPage": number, "independentActual300PngSha256": digest(png), "rowCrops": len(rows)})
    by_sequence = {r["sequence"]: r for r in packet["rows"]}
    for sheet in packet["contactSheets"]:
        path = Path(sheet["path"])
        assert digest(path.read_bytes()) == sheet["sha256"]
        image = Image.open(path).convert("RGB")
        y = 0
        for seq in sheet["sequences"]:
            view = next(v for v in by_sequence[seq]["sourceNativeTargetViews"] if v["field"] == sheet["field"])
            crop = Image.open(view["path"]).convert("RGB")
            body = image.crop((0, y + 38, crop.width, y + 38 + crop.height))
            assert ImageChops.difference(crop, body).getbbox() is None
            y += crop.height + 38
        assert y == image.height
    return {"reviewer": "/root/recovery_review", "script": pin(Path(__file__).resolve()),
            "sourceId": manifest["sourceId"], "sourceSha256": manifest["sourceSha256"], "batch": manifest["batch"],
            "sourceOnlyImages": pin(images), "sourceOnlyViews": pin(views), "originalPdfCachePath": str(pdf),
            "physicalPagesIndependentlyRendered": len(pages), "originalRowCropsVerified": len(originals),
            "sourceNativeFieldViewsVerified": field_count, "contactSheetSourceBodiesVerified": len(packet["contactSheets"]),
            "pages": pages, "allActualSourcePngCropViewAndSheetSourcePixelsExact": True,
            "method": "Independently render the original PDF with MuPDF at300dpi, verify complete sourcePNG hashes and every fullrow/field/sheetbody against unaltered original pixels. Verify raw/page evidence hashes. No candidate file opened.",
            "limits": ["Mechanical source fidelity validates pixel provenance, not the correctness of personal glyph transcription.",
                       "Only the packet's requested fields are reviewed; no whole-source acceptance is implied."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--views", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    value = run(args.images.resolve(), args.views.resolve(), args.pdf.resolve())
    with args.out.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({k: value[k] for k in ("batch", "physicalPagesIndependentlyRendered", "originalRowCropsVerified", "sourceNativeFieldViewsVerified", "contactSheetSourceBodiesVerified")}))
