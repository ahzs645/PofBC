#!/usr/bin/env python3
"""Build an illustrated reference catalogue from catalogue.json.

Usage:
    python build_catalogue.py /path/to/catalogue.json
    python build_catalogue.py /path/to/catalogue.json --compact
    python build_catalogue.py /path/to/catalogue.json --output /path/to/review.pdf

Requires ReportLab and Pillow. Images are embedded as supplied, fitted to the
available rectangle without cropping, recolouring, sharpening, or retouching.
Section-grouped pagination is the default. --compact packs up to four records
per page in their existing order and prints section labels on mixed pages.

Input fields:
  title, subtitle, createdOn,
  sources: [{id, title, url, credit?}],
  entries: [{id, title, section, dateLabel, classification, description,
             datingNote, imagePath, sources: [source_id], sourcePages?, credit?}]
imagePath is resolved relative to the JSON file. A null/empty path produces an
explicit "No image supplied" panel; a missing named file is an input error.
An optional top-level readingKey can replace the default (100 words maximum).
All supplied strings are treated as plain text, not ReportLab markup.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


PAGE_W, PAGE_H = landscape(A4)
MARGIN = 27.0
GAP = 13.0
FOOTER_TOP = 27.0
BODY_BOTTOM = 37.0
BODY_W = PAGE_W - 2 * MARGIN

INK = colors.HexColor("#17394F")
TEXT = colors.HexColor("#273742")
MUTED = colors.HexColor("#60717A")
LINK = colors.HexColor("#1F5F7A")
PAPER = colors.HexColor("#F4F2EB")
WHITE = colors.HexColor("#FFFFFF")
RULE = colors.HexColor("#DADFD9")
KEY_BG = colors.HexColor("#E9EDE8")

READING_KEY = (
    "Dates distinguish a design, an object and a surviving publication; dating "
    "notes explain the evidence. Drawing families are descriptive groupings. "
    "Reference images retain their original appearance, including SAMPLE "
    "watermarks. Linked source IDs identify the evidence; the source index "
    "provides titles and credits."
)

FONTS = {
    "regular": "Helvetica",
    "bold": "Helvetica-Bold",
    "italic": "Helvetica-Oblique",
    "serif": "Times-Roman",
}


class CatalogueError(ValueError):
    pass


class LayoutError(CatalogueError):
    pass


def clean(value: object) -> str:
    """Keep inventory wording while normalising line breaks and dash glyphs."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise CatalogueError(f"Expected a text value, got {type(value).__name__}")
    value = value.translate(str.maketrans({"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u00a0": " "}))
    return re.sub(r"\s+", " ", value).strip()


def plain(value: object) -> str:
    return escape(clean(value), quote=True)


def register_fonts() -> None:
    """Embed widely available fonts; permit a portable built-in-font fallback."""
    roots = [Path("/usr/share/fonts/truetype/dejavu"), Path(__file__).parent / "fonts"]
    names = {"regular": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf", "italic": "DejaVuSans-Oblique.ttf", "serif": "DejaVuSerif.ttf"}
    for root in roots:
        if all((root / filename).is_file() for filename in names.values()):
            for key, filename in names.items():
                font_name = f"Catalogue-{key}"
                pdfmetrics.registerFont(TTFont(font_name, str(root / filename)))
                FONTS[key] = font_name
            pdfmetrics.registerFontFamily("Catalogue-regular", normal=FONTS["regular"], bold=FONTS["bold"], italic=FONTS["italic"], boldItalic=FONTS["bold"])
            return


def paragraph(text: str, *, size: float = 9.1, leading: float | None = None,
              font: str = "regular", colour=TEXT, markup: bool = False) -> Paragraph:
    style = ParagraphStyle(
        "catalogue", fontName=FONTS[font], fontSize=size,
        leading=leading or size * 1.3, textColor=colour, alignment=TA_LEFT,
        spaceBefore=0, spaceAfter=0, allowWidows=0, allowOrphans=0,
        splitLongWords=1, borderPadding=0,
    )
    return Paragraph(text if markup else plain(text), style)


def measured(p: Paragraph, width: float) -> float:
    return p.wrap(width, PAGE_H * 5)[1]


def draw_p(c: canvas.Canvas, p: Paragraph, x: float, top: float, width: float) -> float:
    height = measured(p, width)
    p.drawOn(c, x, top - height)
    return top - height


def safe_url(value: object) -> str:
    url = clean(value)
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CatalogueError(f"Source URL must be an absolute HTTP(S) URL: {url!r}")
    return url


def source_anchor(source: dict, label: str | None = None) -> str:
    return f'<link href="{escape(source["url"], quote=True)}" color="#1F5F7A"><u>{plain(label or source["id"])}</u></link>'


def load_inventory(path: Path) -> tuple[dict, list[dict], OrderedDict[str, dict]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CatalogueError(f"Cannot read inventory {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CatalogueError("The inventory root must be an object")
    data["title"] = clean(data.get("title")) or "British Columbia: coat of arms"
    data["subtitle"] = clean(data.get("subtitle"))
    data["createdOn"] = clean(data.get("createdOn")) or date.today().isoformat()
    data["readingKey"] = clean(data.get("readingKey")) or READING_KEY
    if len(data["readingKey"].split()) > 100:
        raise CatalogueError("readingKey must contain no more than 100 words")
    sources: OrderedDict[str, dict] = OrderedDict()
    for raw in data.get("sources", []):
        source = dict(raw)
        for field in ("id", "title", "credit"):
            source[field] = clean(source.get(field))
        if not source["id"] or source["id"] in sources:
            raise CatalogueError(f"Missing or duplicate source id: {source['id']!r}")
        source["url"] = safe_url(source.get("url"))
        sources[source["id"]] = source
    entries: list[dict] = []
    seen: set[str] = set()
    for number, raw in enumerate(data.get("entries", []), 1):
        entry = dict(raw)
        for field in ("id", "title", "section", "dateLabel", "classification", "description", "datingNote", "sourcePages", "credit"):
            entry[field] = clean(entry.get(field))
        entry["id"] = entry["id"] or f"record-{number}"
        if entry["id"] in seen:
            raise CatalogueError(f"Duplicate entry id: {entry['id']}")
        seen.add(entry["id"])
        entry["section"] = entry["section"] or "Specimens"
        entry["title"] = entry["title"] or entry["id"]
        entry["number"] = number
        ids = entry.get("sources", [])
        if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
            raise CatalogueError(f"Entry {entry['id']} must have a list of source IDs")
        unknown = [item for item in ids if item not in sources]
        if unknown:
            raise CatalogueError(f"Entry {entry['id']} refers to unknown sources: {unknown}")
        entry["sources"] = ids
        image_path = clean(entry.get("imagePath"))
        entry["image"] = None
        entry["ratio"] = 1.0
        if image_path:
            image = (path.parent / image_path).resolve()
            if not image.is_file():
                raise CatalogueError(f"Image for {entry['id']} does not exist: {image}")
            try:
                with Image.open(image) as im:
                    width, height = im.size
                    im.verify()
            except Exception as exc:
                raise CatalogueError(f"Cannot read image for {entry['id']}: {image}: {exc}") from exc
            if width <= 0 or height <= 0:
                raise CatalogueError(f"Empty image for {entry['id']}: {image}")
            entry["image"] = image
            entry["ratio"] = width / height
        entries.append(entry)
    if not entries:
        raise CatalogueError("The inventory has no entries")
    return data, entries, sources


def initial_pages(entries: list[dict], compact: bool) -> list[list[dict]]:
    if compact:
        return [entries[pos:pos + 4] for pos in range(0, len(entries), 4)]
    grouped: OrderedDict[str, list[dict]] = OrderedDict()
    for entry in entries:
        grouped.setdefault(entry["section"], []).append(entry)
    return [group[pos:pos + 4] for group in grouped.values() for pos in range(0, len(group), 4)]


def section_label(entries: list[dict]) -> str:
    return " / ".join(dict.fromkeys(entry["section"] for entry in entries))


def page_header(c: canvas.Canvas | None, data: dict, entries: list[dict], *, first: bool) -> float:
    top = PAGE_H - MARGIN
    title = paragraph(data["title"], size=19.3, leading=23.0, font="serif", colour=INK)
    subtitle = paragraph(data["subtitle"], size=8.5, leading=10.8, colour=MUTED)
    if c:
        top = draw_p(c, title, MARGIN, top, BODY_W)
    else:
        top -= measured(title, BODY_W)
    if data["subtitle"]:
        top -= 5
        if c:
            top = draw_p(c, subtitle, MARGIN, top, BODY_W)
        else:
            top -= measured(subtitle, BODY_W)
    if first:
        top -= 7
        key = paragraph('<b>READING KEY</b>  ' + plain(data["readingKey"]), size=7.5, leading=9.6, colour=MUTED, markup=True)
        key_h = measured(key, BODY_W - 18)
        if c:
            c.setFillColor(KEY_BG)
            c.roundRect(MARGIN, top - key_h - 12, BODY_W, key_h + 12, 4, fill=1, stroke=0)
            draw_p(c, key, MARGIN + 9, top - 6, BODY_W - 18)
        top -= key_h + 12
    top -= 10
    section = paragraph(section_label(entries), size=9.2, leading=11.4, font="bold", colour=INK)
    count_text = f"{entries[0]['number']:02d}-{entries[-1]['number']:02d} / {data['entryCount']:02d}"
    label_width = BODY_W - 88
    section_h = measured(section, label_width)
    if c:
        draw_p(c, section, MARGIN, top, label_width)
        c.setFillColor(MUTED)
        c.setFont(FONTS["regular"], 8.0)
        c.drawRightString(PAGE_W - MARGIN, top - 8.5, count_text)
    return top - section_h - 10


def card_rects(count: int, top: float) -> list[tuple[float, float, float, float]]:
    height = top - BODY_BOTTOM
    half_w = (BODY_W - GAP) / 2
    if count == 1:
        return [(MARGIN, BODY_BOTTOM, BODY_W, height)]
    if count == 2:
        return [(MARGIN + col * (half_w + GAP), BODY_BOTTOM, half_w, height) for col in range(2)]
    half_h = (height - GAP) / 2
    top_y = BODY_BOTTOM + half_h + GAP
    if count == 3:
        return [(MARGIN, top_y, half_w, half_h), (MARGIN + half_w + GAP, top_y, half_w, half_h), (MARGIN, BODY_BOTTOM, BODY_W, half_h)]
    return [(MARGIN + col * (half_w + GAP), top_y if row == 0 else BODY_BOTTOM, half_w, half_h) for row in range(2) for col in range(2)]


@dataclass
class CardLayout:
    entry: dict
    rect: tuple[float, float, float, float]
    heading: list[tuple[Paragraph, float]]
    footer: list[tuple[Paragraph, float]]
    body: list[tuple[Paragraph, float]]
    body_x: float
    body_top: float
    body_width: float
    image_box: tuple[float, float, float, float]


def make_card_layout(entry: dict, rect: tuple[float, float, float, float], sources: dict,
                     mixed: bool) -> CardLayout:
    x, y, width, height = rect
    pad = 12.0 if width < 500 else 16.0
    inner = width - 2 * pad
    top = y + height - pad
    heading = []
    eyebrow = entry["dateLabel"] or "Date not established"
    if mixed:
        eyebrow += "  |  " + entry["section"]
    date_p = paragraph(eyebrow, size=7.3 if mixed else 8.0, leading=9.3, font="bold", colour=LINK)
    heading.append((date_p, top))
    top -= measured(date_p, inner) + 4
    title_p = paragraph(entry["title"], size=12.0 if width < 500 else 15.2, leading=14.3 if width < 500 else 18.2, font="serif", colour=INK)
    heading.append((title_p, top))
    top -= measured(title_p, inner) + 4
    if entry["classification"]:
        class_p = paragraph(entry["classification"], size=7.25, leading=9.0, colour=MUTED)
        heading.append((class_p, top))
        top -= measured(class_p, inner) + 6
    else:
        top -= 3

    footer_parts = []
    source_html = "Sources: " + "  /  ".join(source_anchor(sources[sid]) for sid in entry["sources"]) if entry["sources"] else "Source not supplied"
    if entry["sourcePages"]:
        source_html += "  |  " + plain(entry["sourcePages"])
    footer_parts.append(paragraph(source_html, size=7.2, leading=9.1, colour=MUTED, markup=True))
    if entry["credit"]:
        footer_parts.append(paragraph(entry["credit"], size=6.9, leading=8.8, colour=MUTED))
    footer_height = sum(measured(p, inner) for p in footer_parts) + 2 * max(0, len(footer_parts) - 1)
    footer_top = y + pad + footer_height
    footer = []
    ftop = footer_top
    for p in footer_parts:
        footer.append((p, ftop))
        ftop -= measured(p, inner) + 2
    body_bottom = footer_top + 9
    available = top - body_bottom
    if available < 60:
        raise LayoutError(f"Headings/credits leave too little image space for {entry['id']}")

    tall = height > 300 and width < 500
    landscape_image = entry["ratio"] >= 2.2 and width < 500
    stacked = tall or landscape_image
    base_size = 10.3 if height > 300 else (9.5 if width > 500 else 9.0)
    text_width = inner if stacked else inner * (0.38 if width > 500 and height > 300 else 0.47)
    body = []
    text_height = 0.0
    chosen_size = base_size
    for size in (base_size, max(8.6, base_size - 0.4), 8.2):
        parts = []
        if entry["description"]:
            parts.append(paragraph(entry["description"], size=size, leading=size * 1.29, colour=TEXT))
        if entry["datingNote"]:
            parts.append(paragraph('<b>Dating.</b> ' + plain(entry["datingNote"]), size=size - 0.3, leading=(size - 0.3) * 1.28, colour=MUTED, markup=True))
        text_height = sum(measured(p, text_width) for p in parts) + 5 * max(0, len(parts) - 1)
        image_min = min(95.0, available * 0.42) if tall else 44.0
        fits = text_height <= available if not stacked else text_height + image_min + 8 <= available
        if fits:
            chosen_size = size
            break
    else:
        raise LayoutError(f"Caption for {entry['id']} needs a larger card; shorten description or use grouped pagination")

    if stacked:
        image_height = available - text_height - (8 if text_height else 0)
        image_box = (x + pad, top - image_height, inner, image_height)
        text_top = top - image_height - 8
        body_x = x + pad
    else:
        image_width = inner - text_width - 12
        image_box = (x + pad, body_bottom, image_width, available)
        body_x = x + pad + image_width + 12
        text_top = top
    if image_box[3] < 42:
        raise LayoutError(f"Image panel for {entry['id']} would be too short")
    for p in parts:
        body.append((p, text_top))
        text_top -= measured(p, text_width) + 5
    if text_top + 5 < body_bottom - 0.5:
        raise LayoutError(f"Text would overflow the card for {entry['id']}")
    return CardLayout(entry, rect, heading, footer, body, body_x, top, text_width, image_box)


def fit_pages(data: dict, initial: list[list[dict]], sources: dict) -> list[list[dict]]:
    """Enlarge cards instead of clipping long evidence captions."""
    pending = list(initial)
    pages = []
    while pending:
        entries = pending.pop(0)
        top = page_header(None, data, entries, first=not pages)
        mixed = len({e["section"] for e in entries}) > 1
        try:
            for entry, rect in zip(entries, card_rects(len(entries), top)):
                make_card_layout(entry, rect, sources, mixed)
        except LayoutError:
            if len(entries) == 1:
                raise
            split = 2 if len(entries) >= 3 else 1
            pending = [entries[:split], entries[split:]] + pending
            continue
        pages.append(entries)
    return pages


def draw_image(c: canvas.Canvas, entry: dict, box: tuple[float, float, float, float]) -> None:
    x, y, width, height = box
    c.setFillColor(WHITE)
    c.rect(x, y, width, height, fill=1, stroke=0)
    if entry["image"]:
        # ReportLab retains the source image; only its placement/scale changes.
        c.drawImage(str(entry["image"]), x + 2, y + 2, width=width - 4, height=height - 4,
                    preserveAspectRatio=True, anchor="c", mask="auto", anchorAtXY=False)
    else:
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.rect(x + 2, y + 2, width - 4, height - 4, fill=0, stroke=1)
        p = paragraph("No image supplied", size=8.5, colour=MUTED)
        ph = measured(p, width - 20)
        draw_p(c, p, x + 10, y + height / 2 + ph / 2, width - 20)


def draw_card(c: canvas.Canvas, layout: CardLayout) -> None:
    x, y, width, height = layout.rect
    pad = 12.0 if width < 500 else 16.0
    c.setFillColor(WHITE)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.55)
    c.roundRect(x, y, width, height, 4.0, stroke=1, fill=1)
    c.setFillColor(LINK)
    c.roundRect(x, y + height - 31, 2.3, 20, 1, fill=1, stroke=0)
    for p, top in layout.heading:
        draw_p(c, p, x + pad, top, width - 2 * pad)
    draw_image(c, layout.entry, layout.image_box)
    for p, top in layout.body:
        draw_p(c, p, layout.body_x, top, layout.body_width)
    for p, top in layout.footer:
        draw_p(c, p, x + pad, top, width - 2 * pad)


def page_base(c: canvas.Canvas, data: dict, page: int, total: int) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MARGIN, FOOTER_TOP, PAGE_W - MARGIN, FOOTER_TOP)
    c.setFont(FONTS["regular"], 7.3)
    c.setFillColor(MUTED)
    c.drawString(MARGIN, 14.5, f"REFERENCE CATALOGUE  |  Prepared {data['createdOn']}")
    c.drawRightString(PAGE_W - MARGIN, 14.5, f"{page:02d} / {total:02d}")


def index_item(source: dict, width: float) -> tuple[list[Paragraph], float]:
    heading = paragraph(f'<b>{plain(source["id"])}</b>  {plain(source["title"] or source["id"])}', size=8.7, leading=10.6, colour=INK, markup=True)
    host = urlsplit(source["url"]).netloc.removeprefix("www.")
    url_p = paragraph(source_anchor(source, host + " | Open source"), size=7.5, leading=9.4, colour=LINK, markup=True)
    parts = [heading, url_p]
    if source["credit"]:
        parts.append(paragraph(source["credit"], size=7.2, leading=9.0, colour=MUTED))
    height = sum(measured(p, width) for p in parts) + 3 * (len(parts) - 1) + 10
    return parts, height


def index_pages(sources: dict) -> list[list[tuple[dict, int, float]]]:
    column_width = (BODY_W - 2 * 22) / 3
    top = PAGE_H - 91
    bottom = BODY_BOTTOM + 3
    pages: list[list[tuple[dict, int, float]]] = []
    current = []
    col = 0
    y = top
    for source in sources.values():
        _, height = index_item(source, column_width)
        if height > top - bottom:
            raise LayoutError(f"Source index entry {source['id']} is too long for one column")
        if y - height < bottom:
            col += 1
            y = top
        if col == 3:
            pages.append(current)
            current = []
            col = 0
        current.append((source, col, y))
        y -= height
    if current:
        pages.append(current)
    return pages


def build(input_path: Path, output: Path, compact: bool) -> dict:
    register_fonts()
    data, entries, sources = load_inventory(input_path)
    data["entryCount"] = len(entries)
    pages = fit_pages(data, initial_pages(entries, compact), sources)
    source_pages = index_pages(sources)
    total = len(pages) + len(source_pages)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".building")
    c = canvas.Canvas(str(temporary), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(data["title"])
    c.setAuthor("PofBC research catalogue")
    c.setSubject(data["subtitle"] or "Illustrated reference catalogue with linked primary sources")
    c.setCreator("build_catalogue.py / ReportLab")
    seen_sections = set()
    for page_number, records in enumerate(pages, 1):
        page_base(c, data, page_number, total)
        top = page_header(c, data, records, first=page_number == 1)
        mixed = len({record["section"] for record in records}) > 1
        for record in records:
            section = record["section"]
            if section not in seen_sections:
                bookmark = "section-" + hashlib.sha1(section.encode()).hexdigest()[:12]
                c.bookmarkPage(bookmark)
                c.addOutlineEntry(section, bookmark, level=0)
                seen_sections.add(section)
        for record, rect in zip(records, card_rects(len(records), top)):
            draw_card(c, make_card_layout(record, rect, sources, mixed))
        c.showPage()
    for index_no, items in enumerate(source_pages, 1):
        number = len(pages) + index_no
        page_base(c, data, number, total)
        if index_no == 1:
            c.bookmarkPage("source-index")
            c.addOutlineEntry("Source index", "source-index", level=0)
        heading = "Source index" + (f" / {index_no}" if len(source_pages) > 1 else "")
        draw_p(c, paragraph(heading, size=21, leading=25, font="serif", colour=INK), MARGIN, PAGE_H - MARGIN, BODY_W)
        note = "Source IDs match the clickable references on each card. Titles, links and credits are reproduced from the inventory."
        draw_p(c, paragraph(note, size=8.5, leading=11, colour=MUTED), MARGIN, PAGE_H - 60, BODY_W)
        column_width = (BODY_W - 2 * 22) / 3
        for source, column, top in items:
            x = MARGIN + column * (column_width + 22)
            parts, _ = index_item(source, column_width)
            for p in parts:
                top = draw_p(c, p, x, top, column_width) - 3
        c.showPage()
    c.save()
    temporary.replace(output)
    return {"output": str(output), "entries": len(entries), "sources": len(sources), "specimenPages": len(pages), "sourceIndexPages": len(source_pages), "pages": total, "pagination": "compact" if compact else "section-grouped"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inventory", type=Path, help="Path to catalogue.json")
    parser.add_argument("--output", type=Path, help="Output PDF (default: catalogue.pdf beside the inventory)")
    parser.add_argument("--compact", action="store_true", help="Pack entries in their existing order, up to four per page; identify mixed sections on cards")
    args = parser.parse_args()
    inventory = args.inventory.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else inventory.with_name("catalogue.pdf")
    try:
        print(json.dumps(build(inventory, output, args.compact), indent=2))
    except (CatalogueError, OSError) as exc:
        print(f"Catalogue error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
