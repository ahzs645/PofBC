"""Render and crop report specimens without retouching the surviving print."""
import json
import subprocess
from functools import cache
from io import BytesIO
from pathlib import Path

from PIL import Image

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[2]
PUBLIC = ROOT / 'public/initiatives/bear-aware-1997'
REPORT = PACKAGE / 'source/1997-final-report.pdf'

# Coordinates are pixels on a 400-pixel-long proof of each report page.
PAGES = {
    27: (306, 400), 28: (305, 400), 29: (306, 400),
    33: (400, 306), 34: (304, 400), 35: (306, 400),
    36: (304, 400), 46: (400, 305), 47: (306, 400), 48: (304, 400),
}
COMPOSITIONS = [
    (27, None), (28, (65, 52, 283, 348)), (29, (61, 49, 282, 348)),
    (34, (41, 10, 169, 165)), (34, (175, 13, 303, 168)),
    (34, (39, 192, 165, 346)), (34, (176, 197, 301, 346)),
    (35, (34, 7, 161, 158)), (35, (169, 7, 297, 158)),
    (35, (34, 189, 161, 343)), (35, (169, 188, 297, 341)),
    (36, (41, 19, 168, 172)), (36, (173, 21, 301, 175)),
    (47, (26, 6, 171, 127)), (47, (168, 7, 306, 126)),
    (47, (26, 141, 171, 262)), (47, (168, 141, 306, 261)),
    (47, (26, 276, 171, 398)), (47, (168, 276, 306, 398)),
    (48, (22, 6, 170, 128)), (48, (164, 6, 304, 128)),
    (48, (22, 142, 169, 264)), (48, (165, 140, 304, 264)),
    (48, (22, 278, 168, 397)), (48, (165, 278, 304, 397)),
    (46, None), (33, None)
]
COMPONENTS = {
    'be-bear-aware-paw-lockup': (28, (228, 56, 281, 109)),
    'bear-paw': (27, (125, 218, 225, 308)),
    'walking-bear': (34, (49, 18, 84, 43)),
    'friends-mt-revelstoke-glacier': (27, (14, 318, 83, 386)),
    'columbia-basin-stacked': (27, (250, 282, 303, 388)),
    'columbia-basin-symbol': (27, (252, 282, 300, 366)),
    'columbia-basin-horizontal': (34, (46, 131, 111, 159)),
    'columbia-basin-wordmark': (47, (36, 88, 96, 126)),
    'bc-hydro-historic': (27, (158, 381, 223, 399)),
    'bc-environment-historic': (27, (224, 381, 305, 399)),
}


@cache
def render(page):
    data = subprocess.check_output([
        'pdftoppm', '-f', str(page), '-l', str(page), '-scale-to', '1800', '-png', str(REPORT)
    ])
    with Image.open(BytesIO(data)) as source:
        return source.transpose(Image.Transpose.ROTATE_180) if page == 46 else source.copy()


def extract(name, page, crop):
    image = render(page)
    if crop:
        width, height = PAGES[page]
        left, top, right, bottom = crop
        image = image.crop((
            round(left * image.width / width), round(top * image.height / height),
            round(right * image.width / width), round(bottom * image.height / height)
        ))
    file = f'scans/{name}.png'
    image.save(PUBLIC / file, optimize=True)
    return {'scan': file, 'scanWidth': image.width, 'scanHeight': image.height, 'page': page}


def main():
    (PUBLIC / 'scans').mkdir(parents=True, exist_ok=True)
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    compositions = [
        {**record, **extract(Path(record['file']).stem, page, crop)}
        for record, (page, crop) in zip(manifest, COMPOSITIONS, strict=True)
    ]
    components = [
        {'file': f'components/{name}.svg', **extract(name, page, crop)}
        for name, (page, crop) in COMPONENTS.items()
    ]
    output = ROOT / 'src/initiatives/bearAwareSpecimens.json'
    output.write_text(json.dumps({'compositions': compositions, 'components': components}, indent=2) + '\n')


if __name__ == '__main__':
    main()
