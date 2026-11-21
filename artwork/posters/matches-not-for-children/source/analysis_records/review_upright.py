#!/usr/bin/env python3
"""Render/evaluate upright_reserve.py without changing any other component."""
from pathlib import Path
import importlib.util
import json
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NS = {'s': 'http://www.w3.org/2000/svg'}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(path):
    subprocess.run(['inkscape', str(path), '--export-type=png',
                    '--export-filename=' + str(path.with_suffix('.png')),
                    '--export-width=1000'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    u = module('upright', HERE / 'upright_reserve.py')
    a = module('analysis', HERE / 'analyze_edges.py')
    (HERE / 'upright_reserve.svg').write_text(u.svg())
    master = ET.parse(HERE / 'prior/BCFS_Matches_Reconstructed.svg')
    master.getroot().find('.//s:path[@id="right-upright-reserve"]', NS).set('d', u.UPRIGHT_PATH)
    composite = HERE / 'upright-v3-composite.svg'
    master.write(composite, encoding='utf-8', xml_declaration=True)
    render(composite)
    render(HERE / 'upright_reserve.svg')
    g = master.getroot().find('.//s:g[@id="paper-reserves"]', NS)
    root = ET.Element('{http://www.w3.org/2000/svg}svg',
                      {'width': '1000', 'height': '1400', 'viewBox': '0 0 1000 1400'})
    root.append(g)
    union = HERE / 'upright-v3-union.svg'
    ET.ElementTree(root).write(union, encoding='utf-8', xml_declaration=True)
    render(union)

    ref = np.asarray(Image.open(ROOT / 'work/revision2/reference-reserve-mask-root.png')) > 127
    old = np.asarray(Image.open(ROOT / 'work/revision2/revised-reserve-mask.png')) > 127
    new = np.asarray(Image.open(union.with_suffix('.png')).convert('RGBA'))[:, :, 3] > 127
    yy, xx = np.indices(ref.shape)
    valid = (((xx-914.5)/74)**2 + ((yy-1217.5)/90)**2 > 1) & (yy < 1250) & (xx > 140) & (xx < 925) & (yy > 30)
    regions = {'Upright support': [750, 165, 890, 1245],
               'Upper shoulder': [750, 165, 890, 420],
               'Below diagonal head': [750, 495, 890, 642],
               'Middle head and shoulder': [750, 630, 890, 745],
               'Narrow right notch': [760, 830, 880, 970],
               'Left return and lower cap': [750, 990, 875, 1245]}
    metrics = {name: {'bounds': box, 'v2': a.measures(ref, old, valid, box),
                     'v3': a.measures(ref, new, valid, box)} for name, box in regions.items()}
    report = {'method': 'Same fixed Revision 2 reference mask, 1000x1400 registration and seal exclusion. Other four V2 contours retained.',
              'regions': metrics}
    (HERE / 'upright_metrics.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(metrics['Upright support'], indent=2))

    photo = Image.open(ROOT / 'work/reference-rectified.png').convert('RGB')
    old_image = Image.open(HERE / 'prior/BCFS_Matches_Preview.png').convert('RGB').resize((1000, 1400), Image.Resampling.LANCZOS)
    current = Image.open(composite.with_suffix('.png')).convert('RGB')
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
    bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 21)
    for name, box in [('upper', (755, 165, 905, 520)),
                      ('middle', (745, 570, 885, 895)),
                      ('lower', (745, 960, 875, 1245))]:
        w, h = (box[2]-box[0])*3, (box[3]-box[1])*3
        board = Image.new('RGB', (3*w+80, h+100), '#f3f3ee')
        draw = ImageDraw.Draw(board)
        for i, (label, im) in enumerate([('PHOTO', photo), ('V2', old_image), ('V3', current)]):
            x = 20+i*(w+20)
            draw.text((x, 17), label, font=bold, fill='#1c2928')
            board.paste(im.crop(box).resize((w, h), Image.Resampling.BICUBIC), (x, 55))
        draw.text((20, h+65), 'Same crop and registration; enlargement is 3×.', font=font, fill='#445c57')
        board.save(HERE / f'upright-{name}-comparison.png')

    for name, mask in [('v2', old), ('v3', new)]:
        a.overlay(ref, mask, np.asarray(photo), valid).crop((740, 160, 910, 1245)).resize(
            (510, 3255), Image.Resampling.NEAREST).save(HERE / f'upright-{name}-overlay.png')
    old_overlay = Image.open(HERE / 'upright-v2-overlay.png')
    new_overlay = Image.open(HERE / 'upright-v3-overlay.png')
    for name, ys in [('top', (0, 1080)), ('middle', (1080, 2130)), ('bottom', (2130, 3255))]:
        h = ys[1] - ys[0]
        board = Image.new('RGB', (1060, h+60), '#f3f3ee')
        draw = ImageDraw.Draw(board)
        draw.text((20, 15), 'V2 · magenta excess / teal missing', font=font, fill='#15232a')
        draw.text((550, 15), 'V3 · same reference mask', font=font, fill='#15232a')
        board.paste(old_overlay.crop((0, ys[0], 510, ys[1])), (10, 50))
        board.paste(new_overlay.crop((0, ys[0], 510, ys[1])), (540, 50))
        board.save(HERE / f'upright-overlay-{name}.png')


if __name__ == '__main__':
    main()
