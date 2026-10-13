#!/usr/bin/env python3
"""Export the vector master with Inkscape and validate SVG/PDF structure."""
from pathlib import Path
import json
import shutil
import subprocess
from lxml import etree as E
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SVG_NS='http://www.w3.org/2000/svg'

def main() -> None:
    executable=shutil.which('inkscape')
    if executable is None:
        raise SystemExit('Inkscape was not found on PATH; install it to run this export script.')
    master=ROOT/'forest-service-poster.svg'
    if not master.is_file():
        raise SystemExit('Missing forest-service-poster.svg. Run rebuild_poster.py first.')
    for extension,extra in [('pdf',[]),('png',['--export-dpi=300'])]:
        subprocess.run([executable,str(master),f'--export-type={extension}',
                        f'--export-filename={master.with_suffix("."+extension)}',*extra],check=True)
    report={}
    for p in sorted(ROOT.glob('*.svg')):
        t=E.parse(str(p))
        data={
            'vector_paths':len(t.findall('.//{%s}path'%SVG_NS)),
            'raster_image_elements':len(t.findall('.//{%s}image'%SVG_NS)),
            'live_text_elements':len(t.findall('.//{%s}text'%SVG_NS)),
            'external_image_references':len(t.xpath('//*[@href or @*[local-name()="href"]]')),
        }
        if data['raster_image_elements'] or data['external_image_references']:
            raise ValueError(f'Unexpected image or external reference in {p.name}')
        if p.name=='forest-service-poster.svg' and data['live_text_elements']:
            raise ValueError('The primary master must have outlined lettering.')
        report[p.name]=data
    with fitz.open(ROOT/'forest-service-poster.pdf') as pdf:
        data={
            'pages':len(pdf),
            'embedded_images':sum(len(p.get_images(full=True)) for p in pdf),
            'font_resources':sum(len(p.get_fonts(full=True)) for p in pdf),
            'page_mm':[round(pdf[0].rect.width/72*25.4,2),round(pdf[0].rect.height/72*25.4,2)],
        }
        if data['embedded_images'] or data['font_resources']:
            raise ValueError('The PDF unexpectedly contains images or font resources.')
        report['forest-service-poster.pdf']=data
    with Image.open(ROOT/'forest-service-poster.png') as im:
        report['forest-service-poster.png']={'pixels':list(im.size),'dpi':list(im.info.get('dpi',[])),
                                            'format':'raster preview of vector master'}
    (ROOT/'vector-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
