"""Export the same three viewer editions to fixed-size print PDFs. Requires Chrome,
Playwright, pikepdf and Pillow. Pass the output CMYK profile as the first argument.
"""
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

import pikepdf as pdf
from PIL import Image, ImageCms
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / 'src/posters/carecard'
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', NS[1:-1])
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
profile = Path(sys.argv[1])
output = ImageCms.getOpenProfile(str(profile))
transform = ImageCms.buildTransform(ImageCms.createProfile('sRGB'), output, 'RGB', 'CMYK',
                                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                    flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)


@lru_cache(None)
def process_colour(rgb):
    if rgb[0] == rgb[1] == rgb[2]:
        return (0, 0, 0, round(1-rgb[0]/255, 5))
    sample = Image.new('RGB', (1, 1), rgb)
    return tuple(round(n/255, 5) for n in ImageCms.applyTransform(sample, transform).getpixel((0, 0)))


def expand_pattern(svg):
    """Chromium rasterizes SVG tiling patterns on paper. Place their vector motif directly."""
    pattern = svg.find(f'.//{NS}pattern')
    repeat = svg.find(f'.//{NS}rect[@fill="url(#standard-ground-repeat)"]')
    parent = next(g for g in svg.iter() if repeat in list(g))
    group = ET.Element(NS+'g', transform=pattern.get('patternTransform'),
                       fill=pattern.find(NS+'g').get('fill'))
    parent.insert(list(parent).index(repeat), group)
    parent.remove(repeat)
    w, h = float(pattern.get('width')), float(pattern.get('height'))
    for row in range(-1, math.ceil(154 / (h * .277769)) + 1):
        for col in range(-1, math.ceil(244 / (w * .287206)) + 1):
            for dx, dy in [(3.45314, 2.69056), (-16.337, 24.67527)]:
                ET.SubElement(group, NS+'use', href='#standard-ground-word',
                              transform=f'translate({col*w+dx} {row*h+dy}) scale(.12802913 .12370456)')


def separate(source, target, gray):
    with pdf.open(source) as doc:
        page = doc.pages[0]
        operators = []
        for args, op in pdf.parse_content_stream(page):
            name = str(op)
            if name in ('rg','RG'):
                rgb = tuple(round(float(v)*255) for v in args)
                values = [round(rgb[0]/255, 5)] if gray else process_colour(rgb)
                name = ('g' if gray else 'k') if name == 'rg' else ('G' if gray else 'K')
                args, op = values, pdf.Operator(name)
            operators.append((args, op))
        page.Contents = doc.make_stream(pdf.unparse_content_stream(operators))
        # Place the photographic halftone on the black plate at its native resolution.
        images = list(page.images.values())
        assert len(images) == 1 and tuple(int(images[0][k]) for k in ('/Width','/Height')) == (112,148)
        image = images[0]
        image.write(Image.open(ART/'peter-dueck.png').convert('L').tobytes())
        image.ColorSpace = pdf.Name.DeviceGray
        assert '/Pattern' not in page.Resources
        if not gray:
            icc = doc.make_stream(profile.read_bytes())
            icc.N = 4
            desc = ImageCms.getProfileDescription(output).strip()
            doc.Root.OutputIntents = [pdf.Dictionary(Type=pdf.Name.OutputIntent, S=pdf.Name.GTS_PDFX,
                OutputConditionIdentifier=desc, Info=desc, DestOutputProfile=icc)]
        doc.docinfo['/Title'] = 'BC’s New CareCard · ' + target.stem.split('-')[-1].title()
        doc.save(target, compress_streams=True)


swaps = json.loads((ART/'paints.json').read_text())
with TemporaryDirectory() as work, sync_playwright() as pw:
    browser = pw.chromium.launch(channel='chrome')
    tab = browser.new_page()
    for mode in ['sepia','colour','grayscale']:
        svg = ET.parse(ART/'new-carecard.svg').getroot()
        paints = dict(swaps.get(mode, []))
        for node in svg.iter():
            for key in ('fill','stroke'):
                if node.get(key) in paints:
                    node.set(key, paints[node.get(key)])
        expand_pattern(svg)
        tab.set_content('<style>@page{size:11in 15in;margin:0}body{margin:0}svg{display:block}</style>'
                        + ET.tostring(svg, encoding='unicode'))
        intermediate = Path(work)/'chrome.pdf'
        tab.pdf(path=intermediate, prefer_css_page_size=True, print_background=True)
        separate(intermediate, HERE/f'carecard-{mode}.pdf', gray=mode=='grayscale')
    browser.close()
