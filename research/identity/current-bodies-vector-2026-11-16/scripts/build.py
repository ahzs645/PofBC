"""Build every SVG of this package and its review images.

    python -I research/identity/current-bodies-vector-2026-11-16/scripts/build.py DOWNLOADS

DOWNLOADS is a folder holding the official PDFs listed in SOURCES below under the given file
names (download them from the URLs in ../source-register.json). Each PDF's SHA-256 is checked
before use. The two SVG sources (LDB Wholesale Operations logo, SFU PowerPoint template image) are
kept in ../source/. The rebuilt (reconstructed) marks are made by rebuild/bceid.py and
rebuild/compass_build.py and are not touched here.

Writes the SVGs into public/identity-*/<body>/ and review images into ../review/.
"""
import hashlib, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PKG)))
sys.path.insert(0, HERE)
from pdfvec import extract
from svgcomponent import isolate
import pymupdf
from PIL import Image

SOURCES = {
    'wave2.pdf': '54e7f7f482ef2aaeb3f9c1256e2bff3ef1be3724fc8069ae1136139538161302',
    'bylaw-2026.pdf': 'cbe564eaaf42ac1c6a0374e21a15726305aba8b2f56d907deb95e02eb12f65e6',
    'rac-ck-2024.pdf': 'cd31464fd8c0e0f0abfcd3b30deb508155ee7d7e83c940b4c299eee5feaee582',
    'community-2025.pdf': 'd809b776d2d71b14fc5734160c32288fbf050a60864f1f3bf3d9cc317f63dcf1',
    'aspire-2019.pdf': '559d6a4556e2d023d544b4f1c68bf2f0b8221e04a796643dddba1634ff2c0239',
    'sust-toolkit-2026.pdf': '9734d020204522500dde470081c210b997d98e91cb63f41f96c3299a6bcb5080',
    'BCIB_Building-Opportunity-Here-report-F25-26.pdf': '6acd3419e553e60287caf1fb0654ec9d3536c7c54dc2768993e342e93c73de8d',
}

# (output file under public/, source pdf, page, clip rectangle in PDF points, review background)
PDF_JOBS = [
    ('identity-expanded/bc-pension-corporation/wave-2-strategic-plan-2024-colour.svg', 'wave2.pdf', 1, (50, 128, 232, 164), '#ffffff'),
    ('identity-expanded/etsi-bc/bylaws-2026-full-name-colour.svg', 'bylaw-2026.pdf', 1, (60, 58, 360, 140), '#ffffff'),
    ('identity-expanded/etsi-bc/rac-terms-2024-full-name-reversed.svg', 'rac-ck-2024.pdf', 1, (60, 58, 360, 140), '#006892'),
    ('identity-expanded/metro-vancouver-transit-police/report-to-community-2025-reversed.svg', 'community-2025.pdf', 1, (430, 685, 568, 756), '#00578a'),
    ('identity-expanded/e-comm/aspire-strategic-plan-2019-colour.svg', 'aspire-2019.pdf', 1, (55, 66, 220, 108), '#ffffff'),
    ('identity-expanded/sub-vancouver-convention-centre/sustainability-toolkit-2026-reversed.svg', 'sust-toolkit-2026.pdf', 16, (30, 665, 230, 732), '#18295c'),
    ('identity-collected/bc-infrastructure-benefits/bcib-2026-short-reversed-source-vector.svg', 'BCIB_Building-Opportunity-Here-report-F25-26.pdf', 1, (52, 92, 200, 125), '#232a4a'),
]
SVG_JOBS = [
    # LDB lockup: the right-hand part of the LDB Wholesale Operations logo (BC logo, rule, name)
    ('identity-expanded/liquor-distribution-branch/ldb-wholesale-site-ldb-lockup.svg', 'ldb-wholesale-operations-logo.svg', (294.5, 95, 540, 160), '#ffffff'),
]
COPY_JOBS = [
    # SFU horizontal logo: the SVG embedded in the official PowerPoint template, unchanged
    ('identity-expanded/simon-fraser-university/powerpoint-template-horizontal-colour.svg', 'sfu-powerpoint-template-image4.svg', '#ffffff'),
]


def render(svg, png, width, bg):
    subprocess.run(['node', os.path.join(HERE, 'render.cjs'), svg, png, str(width), bg], check=True)


def review_pair(src_png, svg, out, bg):
    """Side by side: the source page region (left) and the extracted SVG (right)."""
    tmp = out + '.tmp.png'
    a = Image.open(src_png).convert('RGB')
    render(svg, tmp, a.width, bg)
    b = Image.open(tmp).convert('RGB'); os.remove(tmp)
    h = max(a.height, b.height)
    sheet = Image.new('RGB', (a.width + b.width + 24, h + 16), '#808080')
    sheet.paste(a, (8, 8)); sheet.paste(b, (a.width + 16, 8))
    sheet.thumbnail((1200, 600))
    sheet.save(out, 'WEBP', quality=80)


def main(downloads):
    records = []
    for name, sha in SOURCES.items():
        got = hashlib.sha256(open(os.path.join(downloads, name), 'rb').read()).hexdigest()
        if got != sha:
            sys.exit(f'{name}: SHA-256 {got} is not the checked source {sha}')
    for out, pdf, page, rect, bg in PDF_JOBS:
        dest = os.path.join(ROOT, 'public', out)
        info = extract(os.path.join(downloads, pdf), page, rect, dest)
        assert info['images'] == 0 and info['texts'] == 0 and info['uses'] == 0, info
        crop = os.path.join(PKG, 'review', 'src.png')
        pymupdf.open(os.path.join(downloads, pdf))[page - 1].get_pixmap(clip=pymupdf.Rect(rect), dpi=300).save(crop)
        review_pair(crop, dest, os.path.join(PKG, 'review', os.path.basename(out).replace('.svg', '.webp')), bg)
        os.remove(crop)
        info['out'] = out; info['source'] = pdf
        records.append(info)
    for out, src, rect, bg in SVG_JOBS:
        dest = os.path.join(ROOT, 'public', out)
        info = isolate(os.path.join(PKG, 'source', src), rect, dest)
        assert info['images'] == 0 and info['texts'] == 0, info
        crop = os.path.join(PKG, 'review', 'src.png')
        render(os.path.join(PKG, 'source', src), crop, 1100, bg)
        review_pair(crop, dest, os.path.join(PKG, 'review', os.path.basename(out).replace('.svg', '.webp')), bg)
        os.remove(crop)
        info['out'] = out; info['source'] = src
        records.append(info)
    for out, src, bg in COPY_JOBS:
        dest = os.path.join(ROOT, 'public', out)
        shutil.copyfile(os.path.join(PKG, 'source', src), dest)
        data = open(dest, 'rb').read()
        tmp = os.path.join(PKG, 'review', os.path.basename(out).replace('.svg', '.webp'))
        render(dest, tmp + '.png', 900, bg); Image.open(tmp + '.png').save(tmp, 'WEBP', quality=80); os.remove(tmp + '.png')
        records.append(dict(out=out, source=src, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    json.dump(records, open(os.path.join(PKG, 'extraction-metadata.json'), 'w'), indent=1)
    print(json.dumps([{k: r[k] for k in ('out', 'bytes', 'sha256')} for r in records], indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
