"""Make the viewer's loading preview of Wildlife Trees from a render of the site's copy.

The poster is one green ink on white paper, so the preview stores only how much ink each pixel
holds, in four tones (paper, a light and a dark tint, full ink), as a 2-bit PNG: about 190 KB at
1000 pixels wide, where a JPEG of the same picture is over 400 KB, since the fine hatching is the
hardest thing there is for JPEG to compress. At the size the whole poster is first shown it cannot
be told from the drawing; it is only a stand-in until the drawing arrives.

Needs Pillow and numpy:

    python3 preview.py /tmp/wildlife-trees-2000.png ../../../src/posters/wildlife-trees/preview.png
"""
import sys

import numpy
from PIL import Image

INK = numpy.array([0x32, 0x6C, 0x59])
PAPER = numpy.array([0xFF, 0xFF, 0xFF])
TONES = numpy.array([0, 1 / 3, 2 / 3, 1])
WIDTH = 1000


def main(source, target):
    render = numpy.asarray(Image.open(source).convert('RGB')).astype(float)
    # Ink is read from the red channel, where the green ink and the paper are furthest apart.
    ink = numpy.clip((255 - render[..., 0]) / (255 - INK[0]), 0, 1)
    grey = Image.fromarray((ink * 255).round().astype('uint8'), 'L')
    grey = grey.resize((WIDTH, round(WIDTH * grey.height / grey.width)), Image.LANCZOS)
    level = numpy.asarray(grey).astype(float) / 255
    index = numpy.abs(level[..., None] - TONES).argmin(-1).astype('uint8')
    palette = [round(c) for tone in TONES for c in PAPER + (INK - PAPER) * tone]
    out = Image.fromarray(index, 'P')
    out.putpalette(palette + [0] * (768 - len(palette)))
    out.save(target, optimize=True, bits=2)
    print(f'{out.width} × {out.height} → {target}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
