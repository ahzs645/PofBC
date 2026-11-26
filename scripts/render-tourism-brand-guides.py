#!/usr/bin/env python3
"""Build the Tourism readers from the two publisher PDFs with PyMuPDF and Pillow."""
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata

import pymupdf
from PIL import Image

OUTPUT = Path(__file__).resolve().parents[1] / 'public/tourism/guides'
EDITIONS = {
    'a7100fd6221199d889282ca6428d63d672a8d8d0e0472fb4b2a1343e7346a2a0': 'our-brand-2021',
    '38fb70c62864e6a7dd4650a3b919a088dc82bd9c5aaa081a25dbdad689fa6c60': 'rainforest-to-rockies-2024',
}


def render(path):
    edition = EDITIONS.get(hashlib.sha256(path.read_bytes()).hexdigest())
    if not edition:
        raise ValueError(f'Unrecognized edition: {path}')
    target = OUTPUT / edition
    target.mkdir(parents=True, exist_ok=True)
    text = []
    with pymupdf.open(path) as document:
        for page_number, page in enumerate(document, 1):
            scale = 1680 / page.rect.width
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            image = Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)
            image.save(target / f'{page_number}.webp', quality=83, method=4)
            # Retain the publisher's block order; join line breaks within a paragraph.
            blocks = [' '.join(unicodedata.normalize('NFKC', block[4]).split())
                      for block in page.get_text('blocks') if block[6] == 0]
            text.append([block for block in blocks if block and block != str(page_number)])
    (target / 'text.json').write_text(json.dumps(text, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path, nargs='+')
    for filename in parser.parse_args().pdf:
        render(filename)
