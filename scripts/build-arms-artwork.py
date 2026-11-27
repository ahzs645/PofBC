#!/usr/bin/env python3
"""Build the Coats of Arms view's artwork from the 16 November 2026 arms acquisition.

Reads research/identity/arms-acquisition-2026-11-16/ (catalogue.json, holders.json and the original
files under assets/) and writes:

  src/arms/artwork/<asset id>.webp   one display copy per artwork record, never upscaled
  src/arms/artwork/<asset id>.svg    the original itself, for each record that is an SVG, so the
                                     view draws vector artwork as vector (the WebP stays its
                                     fallback and thumbnail)
  src/arms/artwork.json              the holders, their artwork and the credits the view shows

The originals stay where they are, unchanged; the display copies are only downsampled (SVGs are
rendered in Chromium). Run it again after the acquisition
changes:

    python3 scripts/build-arms-artwork.py
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'research/identity/arms-acquisition-2026-11-16'
OUT_DIR = ROOT / 'src/arms/artwork'
INDEX = ROOT / 'src/arms/artwork.json'

# Long edge of the display copy. Letters patent are pages of text, so they keep more detail.
EDGE = 720
EDGE_DOCUMENT = 1100
QUALITY = 82

# SVGs are rendered in Chromium (Playwright), as a browser would draw them; resvg panics on the
# Province's official SAMPLE vectors. One browser renders the whole batch.
RENDER_SVGS = r"""
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
// Playwright is installed globally, where require() finds it and import does not.
const { chromium } = createRequire(`${process.cwd()}/`)('playwright')
const jobs = JSON.parse(readFileSync(process.argv.at(-1), 'utf8'))
const browser = await chromium.launch()
const page = await browser.newPage()
for (const { svg, out, edge } of jobs) {
  const text = readFileSync(svg, 'utf8')
  const doc = new DOMParserLite(text)
  const [width, height] = doc.size()
  const scale = edge / Math.max(width, height)
  const w = Math.round(width * scale), h = Math.round(height * scale)
  await page.setViewportSize({ width: w, height: h })
  const src = 'data:image/svg+xml;base64,' + Buffer.from(text).toString('base64')
  await page.setContent(`<style>html,body{margin:0;background:transparent}img{display:block;width:${w}px;height:${h}px}</style><img src="${src}">`)
  await page.waitForFunction(() => document.querySelector('img').complete)
  await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } })
}
await browser.close()

// The root element's size: its viewBox, else its width and height.
function DOMParserLite (text) {
  const root = text.match(/<svg\b[^>]*>/s)[0]
  const attr = (name) => root.match(new RegExp(`\\s${name}\\s*=\\s*["']([^"']+)["']`))?.[1]
  return {
    size () {
      const box = attr('viewBox')?.trim().split(/[\s,]+/).map(Number)
      if (box?.length === 4 && box[2] > 0 && box[3] > 0) return [box[2], box[3]]
      return [parseFloat(attr('width')), parseFloat(attr('height'))]
    }
  }
}
"""


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace('’', '').replace("'", '')).strip('-')


def render_svgs(assets):
    """Render every SVG to a PNG in one Chromium session; returns {asset id: PNG path}."""
    tmp = Path(tempfile.mkdtemp())
    jobs = [{'svg': str(SOURCE / 'assets' / asset['file']), 'out': str(tmp / f"{asset['id']}.png"), 'edge': edge_for(asset)}
            for asset in assets if asset['format'] == 'SVG']
    (tmp / 'jobs.json').write_text(json.dumps(jobs))
    subprocess.run(['node', '--input-type=module', '-e', RENDER_SVGS, str(tmp / 'jobs.json')], check=True, cwd=ROOT)
    return {Path(job['out']).stem: Path(job['out']) for job in jobs}


def edge_for(asset):
    return EDGE_DOCUMENT if asset['kind'] == 'letters-patent' else EDGE


def display_copy(asset, out, rendered):
    edge = edge_for(asset)
    original = SOURCE / 'assets' / asset['file']
    if asset['format'] == 'SVG':
        image = Image.open(rendered[asset['id']])
        image.load()
    else:
        image = Image.open(original)
        image.load()
        if image.mode == 'P':
            image = image.convert('RGBA')
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        image.thumbnail((edge, edge), Image.LANCZOS)
    if image.mode == 'RGBA' and image.getextrema()[3][0] == 255:
        image = image.convert('RGB')
    image.save(out, 'WEBP', quality=QUALITY, method=6)
    return image.size


UNSAFE_SVG = re.compile(r'<(?:\w+:)?(?:script|foreignObject|iframe|object|embed)\b|\son\w+\s*=|javascript\s*:|@import\b', re.I)
EXTERNAL_REF = re.compile(r'(?:xlink:)?href\s*=\s*["\'](?!#)([^"\']+)', re.I)


def vector_copy(asset):
    """The original SVG, copied unchanged beside its display copy, once checked to draw only itself."""
    if asset['format'] != 'SVG':
        return None
    text = (SOURCE / 'assets' / asset['file']).read_text(encoding='utf-8')
    if UNSAFE_SVG.search(text):
        sys.exit(f"{asset['id']}: active content in {asset['file']}")
    if EXTERNAL_REF.search(text) or re.search(r'url\(\s*["\']?(?!#)', text):
        sys.exit(f"{asset['id']}: external reference in {asset['file']}")
    name = f"{asset['id']}.svg"
    (OUT_DIR / name).write_text(text, encoding='utf-8')
    return name


def main():
    catalogue = json.loads((SOURCE / 'catalogue.json').read_text())
    holders = json.loads((SOURCE / 'holders.json').read_text())
    assets = {asset['id']: asset for asset in catalogue['assets']}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered = render_svgs(catalogue['assets'])

    artwork = {}
    for asset in catalogue['assets']:
        name = f"{asset['id']}.webp"
        size = display_copy(asset, OUT_DIR / name, rendered)
        artwork[asset['id']] = {
            'title': asset['title'],
            'kind': asset['kind'],
            'date': asset['dateLabel'],
            'historical': bool(asset['historical']),
            'author': asset['author'],
            'licence': asset['licence'],
            'licenceUrl': asset.get('licenceUrl'),
            'rights': asset.get('rights'),
            'page': asset['sourcePage'],
            'original': asset['file'],
            'alternates': [alt['file'] for alt in asset.get('alternateFiles') or []],
            'format': asset['format'],
            'vector': bool(asset['isVector']),
            'notes': asset.get('notes'),
            'image': name,
            'vectorImage': vector_copy(asset),
            'size': list(size),
            # The catalogue specimen this file is another copy of (see the acquisition README).
            **({'sameAs': asset['sameAs']} if asset.get('sameAs') else {})
        }

    by_file = {asset['file']: asset_id for asset_id, asset in assets.items()}
    out_holders = []
    ids = set()
    for holder in holders:
        # Municipal holders are numbered by register project in the acquisition; the site names them.
        holder_id = slug(holder['name']) if holder['group'] == 'municipal' else holder['id']
        if holder_id in ids:
            sys.exit(f'duplicate holder id {holder_id}')
        ids.add(holder_id)
        image = holder.get('image') or {}
        primary = by_file.get(image.get('publicFile'))
        entry = {
            'id': holder_id,
            'name': holder['name'],
            'group': holder['group'],
            'registerUrls': [record['url'] for record in holder.get('records', [])],
            'primary': primary,
            'primaryAlt': image.get('alt') if primary else None,
            'artwork': [asset['id'] for asset in holder['artwork']]
        }
        out_holders.append(entry)

    additional = []
    for holder in catalogue.get('additionalHolders', []):
        additional.append({key: holder.get(key) for key in ('id', 'name', 'group', 'year', 'registered', 'grantedLabel', 'granted', 'motto', 'description', 'note', 'sources')})

    unused = sorted(path.name for path in [*OUT_DIR.glob('*.webp'), *OUT_DIR.glob('*.svg')]
                    if path.stem not in artwork or (path.suffix == '.svg' and not artwork[path.stem]['vectorImage']))
    for name in unused:
        (OUT_DIR / name).unlink()

    INDEX.write_text(json.dumps({
        'retrieved': catalogue['retrievedOn'],
        'source': 'research/identity/arms-acquisition-2026-11-16',
        'holders': out_holders,
        'additionalHolders': additional,
        'artwork': artwork
    }, ensure_ascii=False, indent=1) + '\n')
    total = sum(path.stat().st_size for path in OUT_DIR.glob('*.webp'))
    print(f'{len(artwork)} artwork records, {len(out_holders)} holders, {total / 1e6:.1f} MB of display copies → {INDEX.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
