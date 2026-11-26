"""Preserve the Clinton covers' native illustrated marks and outlined PDF glyphs."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET

import pymupdf


SCRIPT = Path(__file__).resolve()
PUBLIC = SCRIPT.parents[4] / "public/identity-recovered/municipalities/clinton"
SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", XLINK)

# Zero-based children in the foreground group of each cover's PyMuPDF SVG.
# Their surrounding captions, cover illustrations and photographs are excluded.
JOBS = {
    "walking-tour-2021.pdf": {
        "sha256": "6bd536e17b13fcba9705a8e67c0e0ae06ac6d2d791a63b0df612f0017f04572b",
        "pieces": (
            ("walking-tour-2021-colour.svg", "Village of Clinton, two-colour signature", (92, 130, 313, 210), (range(72, 80), range(101, 117))),
            ("walking-tour-2021-title-lockup.svg", "Village of Clinton, Historic Walking Tour", (92, 130, 313, 231), (range(72, 117),)),
            ("walking-tour-2021-slogan.svg", "Clinton, Where History Meets Adventure", (266, 516, 357, 591), (range(9, 60),)),
        ),
    },
    "community-profile-2022.pdf": {
        "sha256": "d748c15cb3593087423f0c9e7cd59cc1115b6dbb30c82eebc37abba9c2d1be01",
        "pieces": (
            ("community-profile-2022-investment.svg", "Village of Clinton, Ready for Investment", (405, 680, 591, 767), (range(7, 51),)),
        ),
    },
}


def referenced_ids(elements):
    for outer in elements:
        for item in outer.iter():
            for name, value in item.attrib.items():
                if name == f"{{{XLINK}}}href" and value.startswith("#"):
                    yield value[1:]
                yield from re.findall(r"url\(#([^)]*)\)", value)


def write_piece(page, filename, title, bounds, selections):
    definitions, foreground = page
    elements = [foreground[index] for selection in selections for index in selection]
    defs_by_id = {item.get("id"): item for item in definitions if item.get("id")}
    pending = list(referenced_ids(elements))
    needed = set()
    while pending:
        name = pending.pop()
        if name not in needed:
            needed.add(name)
            pending.extend(referenced_ids([defs_by_id[name]]))

    left, top, right, bottom = bounds
    width, height = right - left, bottom - top
    root = ET.Element(f"{{{SVG}}}svg", {
        "viewBox": f"{left} {top} {width} {height}", "width": str(width * 4), "height": str(height * 4),
    })
    ET.SubElement(root, f"{{{SVG}}}title").text = title
    defs = ET.SubElement(root, f"{{{SVG}}}defs")
    defs.extend(deepcopy(item) for item in definitions if item.get("id") in needed)
    root.extend(deepcopy(elements))
    for item in root.iter():
        if item.tag in (f"{{{SVG}}}image", f"{{{SVG}}}text"):
            raise ValueError(f"Unexpected bitmap or live text in {filename}")
        item.attrib.pop("data-text", None)
    data = ET.tostring(root, encoding="utf-8") + b"\n"
    (PUBLIC / filename).write_bytes(data)
    print(filename, len(data), sha256(data).hexdigest())


def main(source_directory):
    for filename, job in JOBS.items():
        data = (source_directory / filename).read_bytes()
        if sha256(data).hexdigest() != job["sha256"]:
            raise ValueError(f"Source PDF changed: {filename}")
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            page = ET.fromstring(doc[0].get_svg_image(text_as_path=True))
        for piece in job["pieces"]:
            write_piece(page, *piece)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
