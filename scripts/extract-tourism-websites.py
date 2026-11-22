#!/usr/bin/env python3
"""Reproduce the tourism website specimens from their recorded source files.

Usage:
    python scripts/extract-tourism-websites.py --source-dir /path/to/sources

The source directory must contain visitor-services-playbook-2022.pdf and
supernaturalbc-launch-2025.jpg. The WorldHost browser capture is preserved in
public/tourism/websites/source-pages/ because a direct PDF download was not
available during acquisition. The script never replaces missing evidence with
reconstructed artwork and rejects a different edition of a source file.

Requires PyMuPDF (fitz) and Pillow. No network access is used.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import fitz
from PIL import Image


EXPECTED_INPUTS = {
    "visitor-services-playbook-2022.pdf": "c0f528ff8b330015070c28285a1163ddcb4f29dd3c080d5d2cc10745b8916919",
    "supernaturalbc-launch-2025.jpg": "c23d1cbe2024f77e084b7787890167afc83336fa4c75e312bf017cecc5968200",
    "worldhost-page47-browser.jpg": "82f3fb19b12c81bac5d663b925fea1906369177b794e5d37408a6ee9d4a1a7fa",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_input(path, expected_name):
    if not path.is_file():
        raise FileNotFoundError(f"Required source file is missing: {path}")
    actual = sha256(path)
    if actual != EXPECTED_INPUTS[expected_name]:
        raise ValueError(f"Source version differs from the inspected edition: {path.name} ({actual})")


def asset_details(root, path):
    with Image.open(path) as image:
        width, height = image.size
    return {
        "path": str(path.relative_to(root)),
        "file": str(path.relative_to(root / "public")),
        "format": path.suffix[1:],
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "dimensionUnit": "pixel",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = root / "public/tourism/websites"
    output.mkdir(parents=True, exist_ok=True)
    source_pages = output / "source-pages"
    source_pages.mkdir(exist_ok=True)
    pdf_path = args.source_dir / "visitor-services-playbook-2022.pdf"
    launch_path = args.source_dir / "supernaturalbc-launch-2025.jpg"
    capture_path = args.source_dir / "worldhost-page47-browser.jpg"
    if not capture_path.is_file():
        capture_path = source_pages / "worldhost-page47-browser.jpg"
    for path, name in [(pdf_path, pdf_path.name), (launch_path, launch_path.name), (capture_path, capture_path.name)]:
        check_input(path, name)

    # Preserve the published JPEG without colour changes or another lossy encode.
    launch_output = output / "supernaturalbc-launch-2025.jpg"
    if launch_path.resolve() != launch_output.resolve():
        shutil.copyfile(launch_path, launch_output)

    # This is the guide's original embedded screenshot, not a page rasterization.
    with fitz.open(pdf_path) as pdf:
        if len(pdf) != 25:
            raise ValueError("Expected the inspected 25-page July 2022 playbook")
        page = pdf[12]
        if "HelloBC" not in page.get_text() or 102 not in [entry[0] for entry in page.get_images(full=True)]:
            raise ValueError("The inspected HelloBC image is not present on PDF page 13")
        screenshot = fitz.Pixmap(pdf, 102)
        mask = fitz.Pixmap(pdf, 101)
        screenshot = fitz.Pixmap(screenshot, mask)
        screenshot.save(output / "hellobc-listing-2022.png")

    capture_output = source_pages / "worldhost-page47-browser.jpg"
    if capture_path.resolve() != capture_output.resolve():
        shutil.copyfile(capture_path, capture_output)
    with Image.open(capture_path) as capture:
        if capture.size != (1363, 936):
            raise ValueError("WorldHost capture dimensions differ from the recorded viewport")
        # Includes the entire published figure and its grey side margins.
        capture.crop((479, 361, 1126, 839)).save(output / "worldhost-website-2014.png")

    sources = [
        {
            "id": "tourism-digital-plan-2014",
            "title": "Online Reputation Management, second edition, September 2014",
            "publisher": "Destination BC Corp.",
            "date": "2014-09",
            "dateMeaning": "Publication edition; the reproduced website's capture date is not specified.",
            "url": "https://www.destinationbc.ca/content/uploads/2018/08/TBEGuide_ORM2014_SEPT29_LINKED-compressed.pdf",
            "sourceFilename": "TBEGuide_ORM2014_SEPT29_LINKED-compressed.pdf",
            "pageCount": 70,
            "sourceType": "Official guide viewed in a browser PDF viewer",
            "sourceSha256": None,
            "acquisitionNote": "The PDF rendered successfully, but a direct PDF download was unavailable. A complete visible figure was captured at 125% viewer zoom; the full viewport capture is retained for replay and inspection.",
            "captureFile": "public/tourism/websites/source-pages/worldhost-page47-browser.jpg",
            "captureSha256": sha256(capture_output),
        },
        {
            "id": "tourism-listings-2022",
            "title": "Visitor Services Digital and Social Media Playbook, July 2022",
            "publisher": "Destination BC",
            "date": "2022-07",
            "dateMeaning": "Month printed on the guide's cover; the reproduced website's capture date is not specified.",
            "url": "https://www.destinationbc.ca/content/uploads/2022/07/Visitor-Services-Digital-and-Social-Media-Playbook.pdf",
            "relatedWebUrl": "https://www.destinationbc.ca/news/new-visitor-services-digital-and-social-media-playbook/",
            "announcementDate": "2022-07-15",
            "sourceFilename": pdf_path.name,
            "pageCount": 25,
            "sha256": sha256(pdf_path),
            "sourceType": "Official PDF downloaded through the publisher's link",
        },
        {
            "id": "supernaturalbc-launch-2025",
            "title": "Introducing SupernaturalBC.com: Discover Our New Digital Home",
            "publisher": "Destination BC",
            "date": "2025-10-10",
            "dateMeaning": "Article publication date; the article identifies the website launch as 10 September 2025.",
            "url": "https://www.destinationbc.ca/news/introducing-supernaturalbc-com-discover-our-new-digital-home/",
            "imageUrl": "https://www.destinationbc.ca/content/uploads/2025/10/Supernatural-BC-1180x700.jpg",
            "imageUrlObservation": "Verified as the displayed image element's currentSrc; its thumbnail src attribute differs.",
            "websiteLaunchDate": "2025-09-10",
            "sourceType": "Original image downloaded from the official announcement",
            "sha256": sha256(launch_path),
        },
    ]

    assets = [
        {
            "id": "worldhost-website-2014",
            "title": "WorldHost Training Services website, reproduced in September 2014",
            **asset_details(root, output / "worldhost-website-2014.png"),
            "kind": "source-crop",
            "sourceId": "tourism-digital-plan-2014",
            "sourcePage": 47,
            "printedPage": 46,
            "date": "2014-09",
            "dateMeaning": "Publication date, not website launch or screenshot capture date.",
            "evidenceType": "official-published-website-screenshot",
            "evidenceStatus": "visual-specimen",
            "alt": "WorldHost Training Services website with orange navigation, a hospitality photograph and customer-service training panels, reproduced in a 2014 Destination BC guide.",
            "caption": "WorldHost website reproduced in Destination BC's September 2014 guide, printed page 46 (PDF page 47). The website capture date is not stated.",
            "label": "WorldHost · published 2014",
            "extractionMethod": "Lossless rectangular crop of a JPEG browser capture of the original PDF's complete website figure.",
            "captureFile": "public/tourism/websites/source-pages/worldhost-page47-browser.jpg",
            "captureSha256": sha256(capture_output),
            "sourceBoundsPixels": [479, 361, 1126, 839],
            "sourceViewportPixels": [1363, 936],
            "viewerZoomPercent": 125,
            "extractionNotes": "The printed figure's grey side margins are preserved. No sharpening, upscaling, redrawing, colour correction or generated detail.",
            "displayBackground": "white",
        },
        {
            "id": "hellobc-listing-2022",
            "title": "HelloBC Squamish Adventure Centre listing, reproduced in July 2022",
            **asset_details(root, output / "hellobc-listing-2022.png"),
            "kind": "embedded-source-image",
            "sourceId": "tourism-listings-2022",
            "sourcePage": 13,
            "printedPage": 12,
            "date": "2022-07",
            "dateMeaning": "Publication month, not website launch or screenshot capture date.",
            "evidenceType": "official-published-website-screenshot",
            "evidenceStatus": "visual-specimen",
            "alt": "HelloBC listing for the Squamish Adventure Centre, with a visitor-centre photograph, rating, social links, contact buttons and description, reproduced in a July 2022 guide.",
            "caption": "Original embedded screenshot from Destination BC's July 2022 playbook, printed page 12 (PDF page 13). The guide credits the Squamish Visitor Centre HelloBC listing.",
            "label": "HelloBC listing · published 2022",
            "sourceSha256": sha256(pdf_path),
            "sourceImageXref": 102,
            "sourceMaskXref": 101,
            "sourceBoundsPoints": [295.3536376953125, 368.091796875, 592.0159912109375, 521.537841796875],
            "extractionMethod": "Extracted the original embedded RGB bitmap and restored its PDF soft mask; saved to PNG at native dimensions.",
            "extractionNotes": "No page crop, upscaling, sharpening, redrawing or generated detail.",
            "displayBackground": "white",
        },
        {
            "id": "supernaturalbc-launch-2025",
            "title": "SupernaturalBC.com launch image published in October 2025",
            **asset_details(root, launch_output),
            "kind": "original-published-image",
            "sourceId": "supernaturalbc-launch-2025",
            "date": "2025-10-10",
            "dateMeaning": "Article publication date; website launch dated separately to 10 September 2025.",
            "evidenceType": "official-published-website-image",
            "evidenceStatus": "visual-specimen",
            "alt": "SupernaturalBC.com launch image showing the Let The Outside In homepage and six destination brands on a desktop monitor.",
            "caption": "Website image published by Destination BC on 10 October 2025; the new site launched on 10 September 2025. This is the publisher's monitor mockup, not a later live-site capture.",
            "label": "SupernaturalBC · launch image 2025",
            "sourceImageUrl": "https://www.destinationbc.ca/content/uploads/2025/10/Supernatural-BC-1180x700.jpg",
            "extractionMethod": "Downloaded the displayed original image from the official article and preserved its bytes.",
            "extractionNotes": "No cropping, resizing, colour correction, recompression or generated detail.",
            "displayBackground": "white",
        },
    ]
    manifest = {
        "schemaVersion": 1,
        "title": "Published tourism website specimens and extraction provenance",
        "acquisitionDate": "2026-11-21",
        "acquisitionDateTimeZone": "America/Vancouver",
        "notes": [
            "All images depict published source material. None is a reconstructed website interface.",
            "Publication dates are distinct from screenshot dates, website launches and the 2013 asset-transfer date.",
            "A website specimen does not establish that every related registered domain operated a separate website.",
            "Original rights remain with the relevant owners. The asset-transfer order is not an open reuse licence.",
        ],
        "sources": sources,
        "assets": assets,
    }
    manifest_path = root / "research/identity/tourism-asset-transfer-2013/website-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(assets)} inspected website specimens and {manifest_path.relative_to(root)}")


if __name__ == "__main__":
    main()
