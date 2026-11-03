"""Build the site's drawings of the three Noxious Weeds pieces from their supplied PDFs.

The PDFs (Ministry of Forests, Forest Practices Branch; made in 1999 and 2000) are photographs and
illustrations placed as JPEG images, with the copy as live text in fonts the files do not carry:
Univers and Eurostile. So any viewer of the PDFs sets the copy in whatever it has. This build sets
it deliberately, in free faces that are close in width and spirit, and outlines it:

    Univers, Univers Bold         TeX Gyre Heros (the face the site stands in for Helvetica)
    Univers Condensed (and Bold)  TeX Gyre Heros Cn
    Eurostile Condensed (and Bold) Saira Condensed
    Eurostile Bold Extended       Michroma

Each glyph keeps the position the PDF gives it, so lines keep their length and breaks; only the
letter shapes are the substitute's. The fonts embedded in the PDFs (the leaflet's Mekanik headings,
Trebuchet and its bullets) are their own.

For each piece:

1. `pdftocairo -svg` draws the page with that font map. Its images are the PDF's own JPEG streams,
   byte for byte; they are written out as files beside the drawing instead of inside it.
2. Every id is prefixed, since Poppler numbers ids the same way in every file.
3. Each top-level element is given the part it belongs to (`data-part`), by where it sits: the
   parts' regions are below, in the page's own units (points).
4. A part that is a region of a photograph (a plant in the composited landscape, say) gets a
   *highlight*: a copy of the photograph masked to a soft-edged ellipse over the region. The viewer
   shows it only while that part is lit, so when everything else settles back the plant stays
   bright. The copy is the same image, so it adds nothing to download.
5. Coordinates are rounded to a hundredth of a point.

Needs poppler-utils (pdftocairo) and lxml, and the substitute faces, which are fetched into `fonts/`
(left out of git) on the first run:

    python3 build.py P071.pdf P072.pdf P073.pdf
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import svg_bounds as sb  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = REPO / 'src' / 'posters' / 'noxious-weeds'
FONTS = HERE / 'fonts'
SVG = sb.SVG
XLINK = sb.XLINK

FONT_FILES = {
    # The full release, not the site's trimmed stand-in (src/fonts/stand-in), which has no fi and fl
    # ligatures: the copy asks for them, and without them they print as gaps.
    'texgyreheros-regular.otf': 'https://mirrors.ctan.org/fonts/tex-gyre/opentype/texgyreheros-regular.otf',
    'texgyreheros-bold.otf': 'https://mirrors.ctan.org/fonts/tex-gyre/opentype/texgyreheros-bold.otf',
    'texgyreheroscn-regular.otf': 'https://mirrors.ctan.org/fonts/tex-gyre/opentype/texgyreheroscn-regular.otf',
    'texgyreheroscn-bold.otf': 'https://mirrors.ctan.org/fonts/tex-gyre/opentype/texgyreheroscn-bold.otf',
    'Michroma-Regular.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/michroma/Michroma-Regular.ttf',
    'SairaCondensed-Regular.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/sairacondensed/SairaCondensed-Regular.ttf',
    'SairaCondensed-Bold.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/sairacondensed/SairaCondensed-Bold.ttf',
}

# ── The pieces ──────────────────────────────────────────────────────────────────────────────────
#
# `parts` are in the order an element is matched against them: the first whose region holds the
# element's centre takes it. `highlight` is the part of a photograph to keep bright for the part.

SHATTERING = {
    'slug': 'shattering-the-environment',
    'prefix': 'ste',
    'title': 'Shattering the Environment',
    'pages': [1],
    'photos': ['landscape'],  # the composited landscape: a part of its own, and the ground of four
    'parts': {
        'title': {'regions': [(190, 110, 1530, 200)], 'highlight': [(880, 105, 1040, 200)]},
        'thistle': {'regions': [(510, 1690, 800, 1810)], 'highlight': [(350, 235, 590, 1670)]},
        'skeletonweed': {'regions': [(840, 1690, 1110, 1810)], 'highlight': [(770, 105, 1030, 1670)]},
        'knapweed': {'regions': [(1120, 1690, 1400, 1810)], 'highlight': [(1340, 640, 1660, 1460)]},
        'toadflax': {'regions': [(1420, 1690, 1810, 1810)], 'highlight': [(1580, 900, 2260, 1670)]},
        'message': {'regions': [(2100, 300, 2360, 1010)]},
        'website': {'regions': [(2100, 1480, 2380, 1580)]},
        'credits': {'regions': [(2100, 1590, 2320, 1670)]},
        'signature': {'regions': [(1800, 1670, 2150, 1745)]},
        'wordmark': {'regions': [(1840, 1745, 2130, 1850)]},
        'landscape': {'regions': [(0, 0, 2592, 1944)]},  # what is left: the photograph and the cracks
    },
}

EXPLOSION = {
    'slug': 'explosion-in-slow-motion',
    'prefix': 'eis',
    'title': 'Explosion in Slow Motion',
    'pages': [1],
    'photos': ['composite'],
    'parts': {
        'headline': {'regions': [(300, 70, 1290, 190)]},
        # IN SLOW MOTION is drawn as paths, under the photographed EXPLOSION.
        'title': {'regions': [(580, 480, 1070, 670)], 'highlight': [(290, 230, 1300, 700)]},
        # The seeds drifting across the top of the sheet, each its own image.
        'seeds': {'regions': [(370, 130, 490, 230), (1120, 40, 1190, 110), (1300, 600, 1380, 680), (100, 980, 200, 1070),
                              (1370, 1030, 1480, 1150), (845, 920, 950, 1025)]},
        'nodding': {'regions': [(1100, 700, 1330, 930), (820, 1030, 940, 1125)],
                    'highlight': [(300, 640, 1250, 1500)]},
        'spurge': {'regions': [(195, 960, 475, 1290)]},
        'skeletonweed': {'regions': [(1260, 760, 1400, 1135), (1045, 1130, 1280, 1275)]},
        'toadflax': {'regions': [(1330, 1195, 1584, 1560), (1270, 1560, 1510, 1665)]},
        'ragwort': {'regions': [(185, 1350, 312, 1572), (270, 1565, 510, 1710)]},
        'houndstongue': {'regions': [(0, 1625, 250, 2190), (160, 1770, 380, 1875)]},
        'biocontrol': {'regions': [(160, 1876, 290, 2000), (1395, 1865, 1584, 2080)]},
        'marsh': {'regions': [(490, 1755, 690, 1885)], 'highlight': [(570, 1560, 760, 2430)]},
        'gorse': {'regions': [(770, 2015, 920, 2170)], 'highlight': [(690, 1420, 1010, 2150)]},
        'diffuse': {'regions': [(280, 1860, 615, 2215), (300, 2190, 550, 2290)]},
        'spotted': {'regions': [(1165, 1640, 1452, 2090), (1040, 1840, 1230, 2030), (1075, 2085, 1240, 2190)]},
        'control': {'regions': [(30, 2228, 510, 2420), (750, 2365, 920, 2425), (1110, 2240, 1540, 2440)]},
        'signature': {'regions': [(810, 2190, 1140, 2245)]},
        'wordmark': {'regions': [(810, 2245, 1140, 2345)]},
        'action': {'regions': [(0, 2460, 1584, 2592)]},
    },
}

BEWARE = {
    'slug': 'beware-these-alien-invaders',
    'prefix': 'btai',
    'title': 'Beware These Alien Invaders',
    'pages': [1, 2, 3, 4, 5],
    'gap': 36,  # points between the screens as they are stacked
    'photos': [],
    'parts': {
        # Regions on the stacked sheet: screen n starts at (n - 1) × (468 + gap).
        'headline': {'regions': [(285, 85, 660, 112)]},  # before the photograph it is printed across
        'intro': {'regions': [(0, 0, 440, 345)]},
        'invaders': {'regions': [(280, 112, 670, 345)]},
        'start': {'regions': [(240, 365, 440, 450)]},
        'thistle': {'regions': [(60, 504 + 60, 600, 504 + 330)]},
        'gorse': {'regions': [(60, 1008 + 60, 600, 1008 + 330)]},
        'toadflax': {'regions': [(60, 1512 + 60, 600, 1512 + 330)]},
        'houndstongue': {'regions': [(60, 2016 + 60, 600, 2016 + 330)]},
        'navigation': {'regions': [(200, 504 + 360, 480, 504 + 460), (200, 1008 + 360, 480, 1008 + 460),
                                   (200, 1512 + 360, 480, 1512 + 460), (200, 2016 + 360, 480, 2016 + 460)]},
    },
}

PIECES = {'P071': BEWARE, 'P072': SHATTERING, 'P073': EXPLOSION}


# ── Fonts ───────────────────────────────────────────────────────────────────────────────────────

FONTCONFIG = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>{dir}</dir>
  <cachedir>{cache}</cachedir>
  <match target="pattern"><test name="family"><string>Univers</string></test>
    <test name="width" compare="less"><int>100</int></test>
    <edit name="family" mode="assign" binding="strong"><string>TeX Gyre Heros Cn</string></edit></match>
  <match target="pattern"><test name="family"><string>Univers</string></test>
    <edit name="family" mode="assign" binding="strong"><string>TeX Gyre Heros</string></edit></match>
  <match target="pattern"><test name="family"><string>Eurostile</string></test>
    <test name="width" compare="less"><int>100</int></test>
    <edit name="family" mode="assign" binding="strong"><string>Saira Condensed</string></edit></match>
  <match target="pattern"><test name="family"><string>Eurostile</string></test>
    <edit name="family" mode="assign" binding="strong"><string>Michroma</string></edit></match>
  <match target="pattern"><test name="family"><string>Helvetica</string></test>
    <edit name="family" mode="assign" binding="strong"><string>TeX Gyre Heros</string></edit></match>
  <match target="pattern"><test name="family"><string>Syntax</string></test>
    <edit name="family" mode="assign" binding="strong"><string>TeX Gyre Heros</string></edit></match>
</fontconfig>
"""


def font_environment(work):
    FONTS.mkdir(exist_ok=True)
    for name, source in FONT_FILES.items():
        target = FONTS / name
        if target.exists():
            continue
        if isinstance(source, Path):
            shutil.copyfile(source, target)
        else:
            print(f'fetching {name}')
            with urllib.request.urlopen(source) as response:
                target.write_bytes(response.read())
    conf = Path(work) / 'fonts.conf'
    conf.write_text(FONTCONFIG.format(dir=FONTS, cache=Path(work) / 'cache'))
    return {**os.environ, 'FONTCONFIG_FILE': str(conf)}


# ── One page ────────────────────────────────────────────────────────────────────────────────────

def poppler_page(pdf, page, work, env):
    target = Path(work) / f'{Path(pdf).stem}-{page}.svg'
    subprocess.run(['pdftocairo', '-svg', '-f', str(page), '-l', str(page), str(pdf), str(target)], check=True, env=env)
    return sb.load(target)


def prefix_ids(root, prefix):
    renamed = {}
    for element in root.iter():
        if isinstance(element.tag, str) and element.get('id'):
            renamed[element.get('id')] = f"{prefix}-{element.get('id')}"
            element.set('id', renamed[element.get('id')])
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        for key in ('{%s}href' % XLINK, 'href'):
            value = element.get(key)
            if value and value.startswith('#') and value[1:] in renamed:
                element.set(key, '#' + renamed[value[1:]])
        for key in ('clip-path', 'mask', 'fill'):
            value = element.get(key)
            if value and 'url(#' in value:
                element.set(key, re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{renamed.get(m.group(1), m.group(1))})', value))


ROUND = re.compile(r'-?\d+\.\d{3,}')


def rounded(text, places=2):
    return ROUND.sub(lambda m: f'{float(m.group(0)):.{places}f}'.rstrip('0').rstrip('.'), text)


def slim(root):
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        for key in ('d', 'x', 'y', 'width', 'height'):
            if element.get(key):
                element.set(key, rounded(element.get(key)))
        if element.get('transform'):  # a matrix's scale needs more places than a coordinate
            element.set('transform', rounded(element.get('transform'), 5))
        # Poppler writes colours as rgb(%) and an opacity of 1 on everything.
        if element.get('fill-opacity') == '1':
            del element.attrib['fill-opacity']
        for key in ('fill', 'stroke'):
            value = element.get(key)
            m = value and re.fullmatch(r'rgb\(([\d.]+)%, ([\d.]+)%, ([\d.]+)%\)', value)
            if m:
                element.set(key, '#%02x%02x%02x' % tuple(round(float(v) * 2.55) for v in m.groups()))


# ── The piece ───────────────────────────────────────────────────────────────────────────────────

def inside(point, region):
    x, y = point
    return region[0] <= x <= region[2] and region[1] <= y <= region[3]


def build(pdf, piece, work, env):
    slug, prefix = piece['slug'], piece['prefix']
    images_out = OUT / 'images'
    images_out.mkdir(parents=True, exist_ok=True)
    written = {}  # image digest → file name, so a repeated image is one file

    root = etree.Element('{%s}svg' % SVG, nsmap={None: SVG, 'xlink': XLINK})
    defs = etree.SubElement(root, '{%s}defs' % SVG)
    title = etree.SubElement(root, '{%s}title' % SVG)
    title.text = f"{piece['title']} — Ministry of Forests, Forest Practices Branch (rebuilt from the PDF)"
    body = etree.SubElement(root, '{%s}g' % SVG, id=f'{prefix}-poster')
    top = 0.0
    width = 0.0
    papers = []
    counts = {}
    found = {}  # part → [box], one per region it was found in (and per highlight)

    def grow(part, key, box):
        boxes = found.setdefault(part, {})
        old = boxes.get(key)
        boxes[key] = box if old is None else (min(old[0], box[0]), min(old[1], box[1]), max(old[2], box[2]), max(old[3], box[3]))
    for n, page_number in enumerate(piece['pages'], 1):
        page = poppler_page(pdf, page_number, work, env)
        prefix_ids(page.root, f'{prefix}-p{n}' if len(piece['pages']) > 1 else prefix)
        page = sb.Page(page.root)  # re-index the renamed ids
        _, _, w, h = (float(v) for v in page.root.get('viewBox').split())
        width = max(width, w)
        holder = etree.SubElement(body, '{%s}g' % SVG)
        if top:
            holder.set('transform', f'translate(0 {top:g})')
        paper = etree.SubElement(holder, '{%s}rect' % SVG, id=f'{prefix}-paper-{n}', width=f'{w:g}', height=f'{h:g}', fill='#ffffff')
        papers.append(paper.get('id'))
        for d in page.root.findall('{%s}defs' % SVG):
            for child in d:
                defs.append(child)
        photos = list(piece['photos'])
        items = page.items()
        # The page's own white ground is the paper.
        for item in items:
            element = item['element']
            if item['kind'] == 'g' and len(element) == 1 and sb.local(element[0]) == 'path' and element[0].get('fill') == 'rgb(100%, 100%, 100%)':
                continue
            if item['kind'] == 'path' and element.get('fill') == 'rgb(100%, 100%, 100%)' and item['box'] and item['box'][2] - item['box'][0] >= w - 1:
                continue
            holder.append(element)
            box = item['box']
            if box is None:
                continue
            centre = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + top)
            # The photograph that is the ground of the piece is the largest image on it.
            if item['kind'] == 'image' and photos and (box[2] - box[0]) * (box[3] - box[1]) > 0.25 * w * h:
                name = photos.pop(0)
                element.set('data-part', name if name in piece['parts'] else 'ground')
                element.set('id', f'{prefix}-{name}')
                item['photo'] = name
                if name in piece['parts']:
                    grow(name, 'photo', (box[0], box[1] + top, box[2], box[3] + top))
            else:
                for part, spec in piece['parts'].items():
                    hit = next((i for i, r in enumerate(spec['regions']) if inside(centre, r)), None)
                    if hit is not None:
                        element.set('data-part', part)
                        counts[part] = counts.get(part, 0) + 1
                        # A text run's bounds are its glyphs' origins; give it its height back.
                        x0, y0, x1, y1 = box
                        if item['kind'] == 'text':
                            y0 -= 9
                        grow(part, hit, (x0, y0 + top, x1, y1 + top))
                        break
            if item.get('photo'):
                # Highlights of the parts that are regions of this photograph, drawn just above it.
                anchor = element
                for part, spec in piece['parts'].items():
                    for i, (x0, y0, x1, y1) in enumerate(spec.get('highlight', [])):
                        grow(part, f'glow-{i}', (x0, y0, x1, y1))
                        mask_id = f'{prefix}-glow-{part}-{i}'
                        mask = etree.SubElement(defs, '{%s}mask' % SVG, id=mask_id, maskUnits='userSpaceOnUse',
                                                x=f'{x0 - 60:g}', y=f'{y0 - 60:g}', width=f'{x1 - x0 + 120:g}', height=f'{y1 - y0 + 120:g}')
                        etree.SubElement(mask, '{%s}ellipse' % SVG, cx=f'{(x0 + x1) / 2:g}', cy=f'{(y0 + y1) / 2:g}',
                                         rx=f'{(x1 - x0) * 0.62:g}', ry=f'{(y1 - y0) * 0.62:g}', fill=f'url(#{prefix}-soft)')
                        glow = etree.Element('{%s}g' % SVG, {'data-part': part, 'data-highlight': '', 'mask': f'url(#{mask_id})'})
                        copy = etree.SubElement(glow, '{%s}use' % SVG)
                        copy.set('{%s}href' % XLINK, f'#{element.get("id")}')
                        anchor.addnext(glow)
                        anchor = glow
        # Images out of the drawing, into files.
        for image in [e for e in defs.iter('{%s}image' % SVG)]:
            ref = sb.href(image)
            if not ref or not ref.startswith('data:'):
                continue
            mime, data = ref[5:].split(';base64,', 1)
            data = base64.b64decode(data)
            digest = hashlib.sha256(data).hexdigest()
            if digest not in written:
                ext = {'image/jpeg': 'jpg', 'image/png': 'png'}[mime]
                written[digest] = f'{slug}-{len(written) + 1:02d}.{ext}'
                (images_out / written[digest]).write_bytes(data)
            image.set('{%s}href' % XLINK, f'images/{written[digest]}')
        top += h + piece.get('gap', 0)
    height = top - piece.get('gap', 0)
    # The soft edge every highlight shares: full in the middle, fading out to its rim.
    soft = etree.SubElement(defs, '{%s}radialGradient' % SVG, id=f'{prefix}-soft')
    for offset, value in (('0', '#fff'), ('0.62', '#fff'), ('1', '#000')):
        etree.SubElement(soft, '{%s}stop' % SVG, offset=offset, attrib={'stop-color': value})
    root.set('viewBox', f'0 0 {width:g} {height:g}')
    root.set('width', f'{width:g}pt')
    root.set('height', f'{height:g}pt')
    slim(root)
    text = etree.tostring(root, encoding='unicode')
    target = OUT / f'{slug}.svg'
    target.write_text(text)
    # Each part's frame and hotspots, as the viewer takes them: the union of what was found for it,
    # and one box for each region (and highlight) it was found in.
    view = (0, 0, width, height)

    def as_box(b):
        x0, y0 = max(b[0], view[0]), max(b[1], view[1])
        x1, y1 = min(b[2], view[2]), min(b[3], view[3])
        return {'x': round(x0, 1), 'y': round(y0, 1), 'w': round(x1 - x0, 1), 'h': round(y1 - y0, 1)}

    measured = {}
    for part in piece['parts']:
        boxes = list(found.get(part, {}).values())
        if not boxes:
            raise SystemExit(f'{slug}: nothing was found for the part {part!r}')
        union = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        measured[part] = {'box': as_box(union), 'boxes': [as_box(b) for b in boxes]}
    (OUT / f'{slug}.parts.js').write_text(
        f'// Written by artwork/posters/noxious-weeds/build.py: where each part of {piece["title"]} was found\n'
        '// in the drawing (its frame, and one hotspot per region it was found in), in points.\n\n'
        f'export default {json.dumps({"view": as_box(view), "papers": papers, "parts": measured}, indent=1)}\n')
    thumbnail(pdf, piece, env)
    untagged = sum(1 for e in body.iter() if e.getparent() is not None and e.getparent().getparent() is body and not e.get('data-part') and e.get('id') not in papers)
    print(f'{slug}: {len(text) / 1e3:.0f} KB, {len(written)} images ({sum((images_out / f).stat().st_size for f in written.values()) / 1e3:.0f} KB), '
          f'viewBox 0 0 {width:g} {height:g}; untagged {untagged}; ' + ', '.join(f'{k} {v}' for k, v in counts.items()))
    return papers


def thumbnail(pdf, piece, env):
    """The shelf card: the piece drawn by Poppler with the same fonts, 480 pixels on its long side."""
    from PIL import Image
    with tempfile.TemporaryDirectory() as work:
        pages = []
        for page in piece['pages']:
            stem = Path(work) / f'p{page}'
            subprocess.run(['pdftoppm', '-r', '72', '-png', '-singlefile', '-f', str(page), '-l', str(page), str(pdf), str(stem)], check=True, env=env)
            pages.append(Image.open(f'{stem}.png').convert('RGB'))
        gap = piece.get('gap', 0)
        sheet = Image.new('RGB', (max(p.width for p in pages), sum(p.height for p in pages) + gap * (len(pages) - 1)), '#ffffff')
        y = 0
        for page in pages:
            sheet.paste(page, (0, y))
            y += page.height + gap
        sheet.thumbnail((480, 480), Image.LANCZOS)
        sheet.save(OUT / f"{piece['slug']}.thumb.jpg", quality=84, optimize=True, progressive=True)


def main(pdfs):
    with tempfile.TemporaryDirectory() as work:
        env = font_environment(work)
        for pdf in pdfs:
            key = re.search(r'P07\d', Path(pdf).name).group(0)
            build(pdf, PIECES[key], work, env)


if __name__ == '__main__':
    main(sys.argv[1:])
