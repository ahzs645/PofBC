"""Recover the eight page 3 specimens from the Province's Bear Smart brochure.

Run from the repository with Python, PyMuPDF, pikepdf, and pdftocairo installed.
Pass the verified source PDF followed by the root output directory (normally public).
"""
import argparse
from hashlib import sha256
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

import pikepdf
import pymupdf

SOURCE_SHA256 = "903b02d29e96d3b4bb0db4fcaec1b170c9f6ed0c94fc71bb7ac34ea668ecb169"
NARAMATA_STRATEGY_SHA256 = "7e675689be92f48c6843de64ea8eb77691551bbf322cd9d08f74dfb3c3de8dd4"
# Figure IDs are from page 3's tagged PDF content. The rectangles contain the complete marks.
SPECIMENS = {
    "identity-recovered/municipalities/lions-bay/bear-smart-stacked.png": (188, (460, 292, 584, 351), 5),
    "identity-recovered/municipalities/port-alberni/bear-smart-serif.svg": (189, (220, 299, 315, 348), None),
    "identity-municipal/kamloops/bear-smart-black-tagline.svg": (190, (459, 212, 582, 281), None),
    "identity-collected/tourism-partners/discover-naramata-illustrated-badge.png": (191, (336, 204, 455, 291), 493 / 118.258),
    "identity-recovered/municipalities/whistler/bear-smart-stacked.svg": (192, (220, 210, 323, 285), None),
    "identity-municipal/coquitlam/bear-smart-blue-green.svg": (193, (338, 330, 440, 359), None),
    "identity-recovered/municipalities/new-denver/bear-smart-wooden-oval.png": (194, (278, 131, 389, 195), 150 / 110.984),
    "identity-recovered/municipalities/squamish/bear-smart-tagline.svg": (195, (411, 134, 522, 190), None),
}


def figure_ops(ops, figure_id):
    for index, instruction in enumerate(ops):
        if (str(instruction.operator) == "BDC" and str(instruction.operands[0]) == "/Figure"
                and instruction.operands[1].get("/MCID") == figure_id):
            break
    else:
        raise ValueError(f"Missing figure {figure_id}")

    instructions = []
    nesting = 1
    graphics_depth = 0
    for instruction in ops[index + 1:]:
        operator = str(instruction.operator)
        if operator == "BDC":
            nesting += 1
            continue
        if operator == "EMC":
            nesting -= 1
            if not nesting:
                break
            continue
        # InDesign opens or closes some figure-local graphics states outside the tag.
        if operator == "Q" and not graphics_depth:
            continue
        graphics_depth += (operator == "q") - (operator == "Q")
        instructions.append(instruction)
    instructions.extend(pikepdf.ContentStreamInstruction([], pikepdf.Operator("Q")) for _ in range(graphics_depth))
    return instructions


def export_figure(page, ops, bounds, target, raster_scale=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as temporary, pikepdf.new() as pdf:
        isolated = Path(temporary) / "isolated.pdf"
        pdf.pages.append(page)
        logo = pdf.pages[0]
        if "/Annots" in logo.obj:
            del logo.obj["/Annots"]
        logo.Contents = pdf.make_stream(pikepdf.unparse_content_stream(ops))
        top = float(logo.MediaBox[3])
        x0, y0, x1, y1 = bounds
        crop = pikepdf.Array([x0, top - y1, x1, top - y0])
        logo.MediaBox = crop
        logo.CropBox = crop
        logo.remove_unreferenced_resources()
        pdf.save(isolated)
        if raster_scale is not None:
            with pymupdf.open(isolated) as raster_pdf:
                matrix = pymupdf.Matrix(raster_scale, raster_scale)
                raster_pdf[0].get_pixmap(matrix=matrix, alpha=True).save(target)
            return
        run(["pdftocairo", "-svg", str(isolated), str(target)], check=True)
        tree = ElementTree.parse(target)
        if list(tree.iterfind(".//{*}image")) or not list(tree.iterfind(".//{*}path")):
            raise ValueError(f"Expected vector-only logo in {target}")


def extract(source, output):
    if sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("The source PDF differs from the reviewed provincial brochure")
    with pikepdf.open(source) as brochure:
        page = brochure.pages[2]
        ops = pikepdf.parse_content_stream(page)
        for filename, (figure_id, bounds, raster_scale) in SPECIMENS.items():
            export_figure(page, figure_ops(ops, figure_id), bounds, output / filename, raster_scale)


def extract_naramata_strategy(source, output):
    if sha256(source.read_bytes()).hexdigest() != NARAMATA_STRATEGY_SHA256:
        raise ValueError("The source PDF differs from the reviewed Discover Naramata strategic plan")
    with pikepdf.open(source) as strategy:
        page = strategy.pages[0]
        # The outlined logo is the final, balanced drawing group on the cover.
        ops = pikepdf.parse_content_stream(page)[113:]
        target = output / "identity-collected/tourism-partners/discover-naramata-strategy-wordmark.svg"
        export_figure(page, ops, (289, 293, 569, 379), target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--naramata-strategy", type=Path)
    arguments = parser.parse_args()
    extract(arguments.source, arguments.output)
    if arguments.naramata_strategy:
        extract_naramata_strategy(arguments.naramata_strategy, arguments.output)
