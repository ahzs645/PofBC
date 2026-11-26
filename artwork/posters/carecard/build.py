"""Build the CareCard ad from the registered reference, transcription and catalogue SVGs.
Requires Pillow, numpy, opencv-python-headless, vtracer and fonttools.
"""
import base64
import json
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

import cv2
import numpy as np
import vtracer
from PIL import Image, ImageDraw, ImageFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'src/posters/carecard'
SCAN = Image.open(OUT / 'reference.webp').convert('L')
GRAY = np.asarray(SCAN)
SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XLINK)


def element(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{SVG}}}{tag}', {k: str(v) for k, v in attrs.items()})


page = ET.Element(f'{{{SVG}}}svg', viewBox='0 0 891 1215', width='11in', height='15in')
element(page, 'title').text = 'BC’s New CareCard.'
element(page, 'desc').text = 'Reconstruction of the 1989 Ministry of Health advertisement. Black ink on paper.'
defs = element(page, 'defs')
element(page, 'rect', id='paper', width=891, height=1215, fill='white')
element(page, 'rect', x=6, y=8, width=873, height=1194, stroke='#444444', fill='none')


def trace(parent, box, label, threshold, speckle=3):
    """Fit curves to the ink boundary at 3× scale, keeping the counters in the letters."""
    x, y, right, bottom = box
    patch = cv2.resize(GRAY[y:bottom, x:right], None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    mask = np.where(patch < threshold, 0, 255).astype('uint8')
    encoded = cv2.imencode('.png', mask)[1].tobytes()
    traced = ET.fromstring(vtracer.convert_raw_image_to_svg(
        encoded, 'png', colormode='binary', mode='spline', filter_speckle=speckle,
        corner_threshold=55, length_threshold=4, path_precision=2))
    group = element(parent, 'g', transform=f'translate({x} {y}) scale(0.33333333)', **{'aria-label': label})
    for path in traced:
        path.attrib.pop('fill', None)
        group.append(path)


headline = element(page, 'g', id='headline', fill='#161616')
trace(headline, (18, 148, 867, 385), 'BC’s New CareCard.', 130, 8)
trace(element(page, 'g', id='slogan', fill='#161616'),
      (36, 1036, 836, 1107), 'Carry it in good health.', 126, 7)

# Match the relative ink densities of the newspaper illustrations on white stock.
catalogue_paints = {}
TONES = {
    '#f7f7fb': '#f4f4f4', '#bcbcbc': '#eeeeee', '#f7f3f5': '#f1f1f1',
    '#848cc6': '#aaaaaa', '#6d7dbe': '#b4b4b4', '#ed3629': '#444444',
    '#ee3924': '#626262', '#fbef12': '#dadada', '#a89668': '#adadad',
    '#b2a173': '#b9b9b9', '#9e8a45': '#616161', '#d7d9db': '#eeeeee',
    '#191918': '#262626', '#20201c': '#272727'
}


def place_card(variant, x, y, width):
    card = ET.parse(ROOT / f'public/cards/carecard/{variant}-card.svg').getroot()
    _, _, native_width, native_height = map(float, card.get('viewBox').split())
    height = width * native_height / native_width
    group = element(page, 'g', id=f'{variant}-card')
    for offset, tone in [(8, 229), (7, 216), (6, 197), (5, 174), (4, 148), (3, 121), (2, 101)]:
        element(group, 'rect', x=x+offset*.72, y=y+offset, width=width, height=f'{height:.3f}',
                rx=10, fill='#'+f'{tone:02x}'*3)
    card.set('x', str(x))
    card.set('y', str(y))
    card.set('width', str(width))
    card.set('height', str(height))
    # Suppress the blur on the faint repeat so it remains vector in a print export.
    # Use the printed sample inscription on the poster, with the templates' digit paths.
    def field(name):
        return card.find(f'.//*[@id="{name}"]')

    number = field('sample-number')
    number.set('aria-label', '9121 428 303')
    number.set('transform', 'translate(52 92) scale(0.99 1.22)')
    for use, digit in zip(number, '9121428303', strict=True):
        use.set(f'{{{XLINK}}}href', '#digit-' + digit)
    field('number-label').attrib.update(x='53', y='89')
    field('sample-name').attrib.update(x='29', y='148', **{'font-family': 'Arial Narrow, sans-serif',
                                      'font-weight': 'bold', 'letter-spacing': '1.7'})
    field('sample-name').text = 'STEPHANIE MICHAELS'
    field('date-label').attrib.update(x='130', y='130')
    field('birth-date').attrib.update(x='167', y='137')
    field('birth-date').text = '03/02/17'
    for x0, label, value in [(29, 'EFFECTIVE', '07/89'), (81, 'EXPIRES END OF', '12/93'),
                             (148, 'GROUP AND DEPENDENT NO.', '80868599-00')]:
        element(card, 'text', x=x0, y=115, fill='#191918',
                **{'font-family':'Arial Narrow, sans-serif','font-size':'5.2','font-weight':'bold'}).text = label
        element(card, 'text', x=x0, y=124, fill='#20201c',
                **{'font-family':'monospace','font-size':'9.3','letter-spacing':'0.6'}).text = value
    element(card, 'text', x=31, y=136, fill='#20201c',
            **{'font-family':'monospace','font-size':'7.5'}).text = 'UNIT   61'
    number_label = field('number-label')
    for node in card.iter():
        node.attrib.pop('filter', None)
        for key, value in list(node.attrib.items()):
            if key == 'id':
                node.set(key, f'{variant}-{value}')
            elif value in TONES:
                catalogue_paints[node, key] = value
                gray = TONES[value]
                if variant == 'gold' and value in ('#20201c', '#191918') and node is not number_label:
                    gray = '#e8e8e8'
                node.set(key, gray)
            elif value.startswith('url(#'):
                node.set(key, value.replace('url(#', f'url(#{variant}-'))
            elif key.endswith('href') and value.startswith('#'):
                node.set(key, f'#{variant}-{value[1:]}')
    group.append(card)
    element(group, 'rect', x=x, y=y, width=width, height=f'{height:.3f}', rx=10,
            fill='none', stroke='#555555', **{'stroke-width': 1.3})


place_card('standard', 309.5, 402, 273)
place_card('gold', 578.5, 509.5, 272)

# The line breaks and readings are transcribed from the supplied newspaper image.
# Each pair of y cuts encloses one printed line in the column.
left = element(page, 'g', id='minister-message', fill='#212121')
centre = element(page, 'g', id='standard-copy', fill='#212121')
right = element(page, 'g', id='seniors-copy', fill='#212121')
FONTS = Path('/System/Library/Fonts/Supplemental')
fonts = {key: TTFont(FONTS / name) for key, name in [
    ('roman', 'Times New Roman.ttf'), ('italic', 'Times New Roman Italic.ttf'),
    ('heavy', 'Arial Black.ttf'), ('sans', 'Arial.ttf'), ('bold', 'Arial Bold.ttf')]}
defined = set()


def register_letters(caption, face, line, boxes, uses, sx, sy, lo, top):
    """Fit spacing to scanned glyphs while keeping the line's common baseline and scale."""
    font = ImageFont.truetype(fonts[face].reader.file.name, 160)
    source = np.clip((212-line.astype('float32'))/155, 0, 1)
    costs, previous, candidates = None, [], []
    for char, box in zip(caption.replace(' ', ''), boxes, strict=True):
        left, bottom, right, upper = box
        origin = (left-lo)*sx
        w = max(1, round((right-left)*sx))
        h = max(1, round((upper-bottom)*sy))
        y = max(0, min(line.shape[0]-h, round((top-upper)*sy)))
        ink = Image.new('L',(256,256))
        ImageDraw.Draw(ink).text((16,0),char,font=font,fill=255,anchor='lt')
        template = np.asarray(ink.crop(ink.getbbox()).resize((w,h), Image.Resampling.LANCZOS)).astype('float32')/255
        offsets = np.arange(-10,11)
        starts = np.clip(round(origin)+offsets, 0, line.shape[1]-w)
        match = cv2.matchTemplate(source[y:y+h],template,cv2.TM_SQDIFF)[0]
        score = match[starts]/max(float(template.sum()),1) + 0.001*offsets**2
        if costs is not None:
            # Penalize abrupt changes of tracking and preserve the letters' reading order.
            shift = (starts[:,None]-candidates[-1][None,:])-(origin-last_origin)
            transitions = costs[None,:] + .045*shift**2
            transitions[starts[:,None] <= candidates[-1][None,:]] = np.inf
            best = transitions.argmin(axis=1)
            score += transitions[np.arange(len(best)),best]
            previous.append(best)
        candidates.append(starts)
        costs, last_origin = score, origin
    choice = int(costs.argmin())
    for i in reversed(range(len(uses))):
        original = float(uses[i].get('x'))
        delta = candidates[i][choice]-(boxes[i][0]-lo)*sx
        uses[i].set('x', f'{original+delta/sx:.2f}')
        if i:
            choice = previous[i-1][choice]


def lines(parent, face, x1, x2, cuts, copy):
    """Set clean, portable vector letters in the measured ink box of each line."""
    font = fonts[face]
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    readings = copy.strip().splitlines()
    assert len(readings) == len(cuts) - 1
    for caption, y1, y2 in zip(readings, cuts, cuts[1:]):
        ys, xs = np.where(GRAY[y1:y2, x1:x2] < 147)
        x = x1 + xs.min()
        y = y1 + ys.min()
        w, h = np.ptp(xs) + 1, np.ptp(ys) + 1
        group = element(parent, 'g', **{'aria-label': caption})
        advance, boxes = 0, []
        for char in caption:
            glyph = glyphs[cmap[ord(char)]]
            bounds = BoundsPen(glyphs)
            glyph.draw(bounds)
            if bounds.bounds:
                lo, bottom, hi, top = bounds.bounds
                boxes.append((lo + advance, bottom, hi + advance, top))
                ident = f'type-{face}-{ord(char)}'
                if ident not in defined:
                    pen = SVGPathPen(glyphs)
                    glyph.draw(pen)
                    element(defs, 'path', id=ident, d=pen.getCommands())
                    defined.add(ident)
                element(group, 'use', href='#'+ident, x=advance)
            advance += glyph.width
        lo, bottom = min(b[0] for b in boxes), min(b[1] for b in boxes)
        hi, top = max(b[2] for b in boxes), max(b[3] for b in boxes)
        sx, sy = w/(hi-lo), h/(top-bottom)
        register_letters(caption, face, GRAY[y:y+h,x:x+w], boxes, list(group), sx, sy, lo, top)
        group.set('transform', f'translate({x} {y}) scale({sx:.8f} {-sy:.8f}) translate({-lo} {-top})')


lines(left, 'italic', 40, 295, [462, 490, 516], """
A Message from
the Minister of Health""")
lines(left, 'roman', 41, 298, [520,537,558,576,598,621,639,657,680,702,718,741,760,779,798,818], """
As a member of British Columbia’s
Medical Services Plan, you enjoy the
benefits of one of the world’s finest
health care systems.
As good as our system is, we are
always working to make it better—
and that is the reason for British
Columbia’s new CareCard.
The CareCard will play an important
role in health care into the 1990’s
and beyond. It will help to stream-
line the running of our health care
system, resulting in more efficient
record-keeping and better service
to the public.""")
lines(left, 'roman', 163, 294, [820,840,859,878,896,917,936,956,973], """
By practicing a
healthy lifestyle
and using our
health care
system wisely,
we can all help
manage health
care costs.""")
portrait = SCAN.crop((46, 822, 158, 970))
portrait.save(OUT / 'peter-dueck.png')
element(left, 'image', id='portrait', x=46, y=822, width=112, height=148,
        href='data:image/png;base64,'+base64.b64encode((OUT/'peter-dueck.png').read_bytes()).decode())
# Rejoin the faint upper loop of the printed signature with a hairline curve.
element(left, 'path', d='M44 989 C53 974 77 970 87 980 C98 993 79 1009 53 1028 '
        'M37 1001 C35 1026 48 1035 67 1029 C90 1022 100 1010 74 1007',
        stroke='#777777', fill='none', **{'stroke-width':'.7'})
trace(left, (38,1017,110,1033), 'Signature flourish', 155, 1)
lines(left, 'italic', 110, 299, [977,994,1008,1027], """
Honourable Peter A. Dueck
Minister of Health and
Minister Responsible for Seniors""")
lines(centre, 'heavy', 319, 554, [594,612,628,646], """
Another Step Forward For
British Columbia’s Quality
Health Care System""")
lines(centre, 'roman', 302, 568, [646,666,683,702,719,739,757,775,793,812,830,850], """
The CareCard is a new, personalized
identity card for members of B.C.’s
Medical Services Plan. It replaces
the current MSP card and Seniors’
Pharmacare card with a durable plastic
card...one which bears your signature
and Personal Health Number. If you now
belong to MSP, you’ll receive a CareCard
within the next few months. It’s all part
of our ongoing effort to improve the
operation of our health care system.""")
lines(centre, 'heavy', 305, 565, [853,877], 'A CareCard for each individual')
lines(centre, 'roman', 303, 568, [878,896,915,934,952,969,988,1006,1025], """
Every MSP subscriber under 65 years
of age will be mailed an individual
CareCard, as well as a separate card for
each dependent. Except for young
children, everyone should sign his or
her own card...and carry it when
visiting a physician or other health care
provider.""")
lines(right, 'heavy', 598, 816, [698,718,736], """
A special Gold CareCard
for Seniors""")
lines(right, 'roman', 575, 852, [738,756,774,792,808,827,845,862,879,898,915,933,950], """
B.C. residents 65 years and over
will receive a special Gold CareCard,
which replaces both the MSP and the
Seniors’ Pharmacare cards. As a Senior,
this will be the only card you need
when visiting a physician, pharmacist
or other health care provider. The
Gold CareCard is a more convenient
way to enjoy our comprehensive health
care system and the various discounts
available to Seniors throughout
British Columbia.""")
issuer = element(page, 'g', id='issuer', fill='#202020')
# Ask the generator for its actual paths and official colour arrangement.
flag_markup = subprocess.check_output(['node', '--input-type=module', '-e',
    "import {flagMarkup} from './src/flag/flagLayout.js'; "
    "console.log(flagMarkup({x:577,y:971,width:65},'official'))"], cwd=ROOT, text=True)
flag = ET.fromstring(flag_markup)
issuer.append(flag)
flag_tones = {'#10069f':'#111111', '#ef3340':'#131313', '#ffd100':'#fdfdfd'}
for path in flag:
    catalogue_paints[path, 'fill'] = path.get('fill')
    path.set('fill', flag_tones[path.get('fill')])
lines(issuer, 'bold', 648, 758, [980,996,1009], """
Province of
British Columbia""")
lines(issuer, 'sans', 648, 760, [1009,1026], 'Ministry of Health')

# Reuse the raccoon ad's warm paper and ink endpoints. Give each source paint
# a distinct value so the viewer can restore the catalogue colours with its normal swap control.
ink = np.array([61, 55, 47])
paper = np.array([233, 205, 173])
swaps = {'colour': {}, 'grayscale': {}}
for node in page.iter():
    for key in ('fill', 'stroke'):
        value = node.get(key)
        if value == 'white':
            value = '#ffffff'
        if not value or not value.startswith('#'):
            continue
        tone = int(value[1:3], 16) / 255
        # Near-solid headline ink matches the companion newspaper poster.
        if value == '#161616':
            tone = 0
        mixed = np.rint(ink + (paper-ink)*tone).astype(int)
        sepia = '#' + ''.join(f'{v:02x}' for v in mixed)
        colour = catalogue_paints.get((node, key), value)
        while sepia in swaps['colour'] and (swaps['colour'][sepia], swaps['grayscale'][sepia]) != (colour, value):
            mixed[2] += 1
            sepia = '#' + ''.join(f'{v:02x}' for v in mixed)
        swaps['colour'][sepia] = colour
        swaps['grayscale'][sepia] = value
        node.set(key, sepia)
ET.ElementTree(page).write(OUT/'new-carecard.svg', encoding='utf-8')
(OUT/'paints.json').write_text(json.dumps({k:list(v.items()) for k,v in swaps.items()}, indent=2)+'\n')
