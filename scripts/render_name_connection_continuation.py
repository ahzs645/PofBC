#!/usr/bin/env python3
"""Reproduce the frozen follow-up crops and sheets from exact-hash original PDFs."""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/name-links/continuation-2026-11-02'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True, help='Original PDFs named <sourceId>.pdf, with the hashes in the manifest.')
    parser.add_argument('--out', type=Path, required=True, help='A separate output folder; reviewed evidence is never overwritten.')
    args = parser.parse_args()
    if args.out.resolve() == (AREA / 'renders').resolve():
        raise SystemExit('Use a separate output folder to preserve the visual review')
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((AREA / 'render-manifest.json').read_text())
    plans = json.loads((AREA / 'review-plan.json').read_text())
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
    docs, panels, results = {}, {}, []
    for r in manifest['cases']:
        sid = r['sourceId']
        if sid not in docs:
            pdf = args.cache / (sid + '.pdf')
            if hashlib.sha256(pdf.read_bytes()).hexdigest() != r['pdfSha256']:
                raise ValueError('Original source hash differs: ' + sid)
            docs[sid] = fitz.open(pdf)
        p = plans[r['planIndex']]
        e = p['reviewRows'][r['evidenceIndex']]
        crop = args.out / Path(r['crop']).name
        docs[sid][r['physicalPage'] - 1].get_pixmap(dpi=300, alpha=False, clip=fitz.Rect(r['rectPdfPoints'])).save(crop)
        if hashlib.sha256(crop.read_bytes()).hexdigest() != r['cropSha256']:
            raise ValueError('Re-rendered crop differs; inspect the source and renderer version: ' + crop.name)
        im = Image.open(crop).convert('RGB')
        im.thumbnail((1380, 90))
        panel = Image.new('RGB', (1400, 145), 'white')
        draw = ImageDraw.Draw(panel)
        draw.text((8, 2), f'#{p["id"]} {p["kind"]} {e["role"]} | {p["fromName"]} -> {p["toName"]}', font=font, fill='black')
        draw.text((8, 25), f'{sid} p{e["physicalPage"]} | pay {e["row"][2]:,} | expenses {e["row"][3]}', font=font, fill='black')
        panel.paste(im, (8, 49))
        panels[(r['sheet'], r['panelOnSheet'])] = panel
        results.append({'crop': crop.name, 'identical': True})
    receipt = json.loads((AREA / 'visual-review.json').read_text())
    for s in receipt['sheets']:
        number = s['sheet']
        chunk = sorted((at, im) for (sheet, at), im in panels.items() if sheet == number)
        image = Image.new('RGB', (1400, 145 * len(chunk)), (230, 230, 230))
        for at, im in chunk:
            image.paste(im, (0, (at - 1) * 145))
        path = args.out / f'sheet-{number:02d}.png'
        image.save(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != s['sha256']:
            raise ValueError('Re-rendered contact sheet differs: ' + path.name)
    print(f'Identical reproduction: {len(results)} source crops and {len(receipt["sheets"])} contact sheets')


if __name__ == '__main__':
    main()
