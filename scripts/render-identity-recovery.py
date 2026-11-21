#!/usr/bin/env python3
"""Render source-artwork proof sheets; these are not application screenshots.

Requires Pillow and the repository's installed @resvg/resvg-js. Originals are
never changed. Raster specimens are shown at no more than their native size.
"""
import json
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'research/identity/missing-recovery-2026-11-20'
OUTPUT = DIRECTORY / 'review'
OUTPUT.mkdir(parents=True, exist_ok=True)
manifest = json.loads((DIRECTORY / 'assets-manifest.json').read_text())
rows = [(body, asset) for body in sorted(manifest['bodies'], key=lambda body: (body['id'].startswith('municipality-'), body['shortName'])) for asset in body['assets']]
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font = ImageFont.truetype(font_path, 18)
small = ImageFont.truetype(font_path, 14)
heading = ImageFont.truetype(font_path, 26)
CELL_WIDTH, CELL_HEIGHT, COLUMNS, ROWS = 390, 280, 4, 5


def wrapped(draw, text, max_width):
    lines = ['']
    for word in text.split():
        candidate = (lines[-1] + ' ' + word).strip()
        if lines[-1] and draw.textlength(candidate, font=font) > max_width:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


with tempfile.TemporaryDirectory(prefix='identity-proof-') as temporary:
    temporary = Path(temporary)
    vectors = [{'source': str(ROOT / 'public' / asset['file']), 'output': str(temporary / (asset['id'] + '.png'))}
               for _, asset in rows if asset['isVector']]
    renderer = """import fs from 'node:fs'; import { Resvg } from '@resvg/resvg-js';
const files = JSON.parse(fs.readFileSync(0, 'utf8'));
for (const file of files) fs.writeFileSync(file.output, new Resvg(fs.readFileSync(file.source), { fitTo: { mode: 'width', value: 1000 } }).render().asPng());"""
    subprocess.run(['node', '--input-type=module', '-e', renderer], cwd=ROOT, input=json.dumps(vectors), text=True, check=True)
    pages = []
    per_page = COLUMNS * ROWS
    for offset in range(0, len(rows), per_page):
        group = rows[offset:offset + per_page]
        row_count = (len(group) + COLUMNS - 1) // COLUMNS
        canvas = Image.new('RGB', (CELL_WIDTH * COLUMNS, row_count * CELL_HEIGHT + 100), '#f0f0eb')
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 13), 'Recovered identity artwork', font=heading, fill='#163149')
        draw.text((16, 52), f'Source proof sheet {len(pages) + 1} · observed 20 November 2026 · original colours and lettering · raster thumbnails are not enlarged', font=small, fill='#45525b')
        for index, (body, asset) in enumerate(group):
            x = index % COLUMNS * CELL_WIDTH
            y = index // COLUMNS * CELL_HEIGHT + 90
            plate = '#172c43' if asset.get('darkBackground') else '#ffffff'
            draw.rectangle((x + 10, y, x + CELL_WIDTH - 10, y + 194), fill=plate)
            path = temporary / (asset['id'] + '.png') if asset['isVector'] else ROOT / 'public' / asset['file']
            image = Image.open(path).convert('RGBA')
            image.thumbnail((CELL_WIDTH - 48, 168), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (CELL_WIDTH - image.width) // 2, y + (194 - image.height) // 2), image)
            lines = wrapped(draw, body['shortName'], CELL_WIDTH - 28)
            for line_index, line in enumerate(lines[:2]):
                draw.text((x + 12, y + 204 + line_index * 21), line, font=font, fill='#163149')
            dimensions = asset.get('dimensions', {})
            size = f" · {dimensions['width']} × {dimensions['height']}" if dimensions.get('width') and not asset['isVector'] else ''
            draw.text((x + 12, y + 251), asset['format'].upper() + (' · native vector' if asset['isVector'] else ' · raster') + size, font=small, fill='#45525b')
        name = f'artwork-{len(pages) + 1:02}.jpg'
        canvas.save(OUTPUT / name, quality=90, optimize=True)
        pages.append({'file': 'review/' + name, 'assets': [asset['id'] for _, asset in group]})
    (OUTPUT / 'index.json').write_text(json.dumps({'note': 'Artwork proof sheets, not browser screenshots. Raster specimens are not enlarged.', 'pages': pages}, indent=2) + '\n')
    print(f'Rendered {len(rows)} accepted artwork files across {len(pages)} proof sheets.')
