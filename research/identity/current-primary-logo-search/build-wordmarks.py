"""Build the native Wholesale extract and the independently fitted Stores reconstruction."""
import argparse
from pathlib import Path
import fitz

def xy(p):
    return f"{p.x:.5f} {p.y:.5f}"

def path_from(shape):
    out = []
    end = None
    for item in shape['items']:
        kind = item[0]
        if kind == 're':
            r, orient = item[1:]
            points = [r.tl, r.tr, r.br, r.bl] if orient == 1 else [r.tl, r.bl, r.br, r.tr]
            out.append('M'+' L'.join(xy(p) for p in points)+' Z')
            end = None
        elif kind in ('c', 'l'):
            if end is None or abs(end - item[1]) > .001:
                out.append('M'+xy(item[1]))
            end = item[-1]
            out.append(kind.upper()+' '.join(xy(p) for p in item[2:]))
        else:
            raise ValueError(f'Unexpected PDF geometry: {kind}')
    return ' '.join(out)

def svg(title, desc, vb, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{title}</title>\n<desc id="desc">{desc}</desc>\n{body}\n</svg>\n')

def path(d, transform=None):
    return f'<path d="{d}"' + (f' transform="{transform}"' if transform else '') + '/>'

def fit(shape, box):
    x, y, w, h = box
    r = shape['rect']
    sx, sy = w/r.width, h/r.height
    return path(path_from(shape),f'matrix({sx:.8f} 0 0 {sy:.8f} {x-r.x0*sx:.6f} {y-r.y0*sy:.6f})')

def build(source, out):
    doc = fitz.open(source)
    region = fitz.Rect(80,135,329,155)
    p = doc[1]
    assert not p.get_text(clip=region).strip()
    assert not any(fitz.Rect(im['bbox']).intersects(region) for im in p.get_image_info())
    shapes = [s for s in p.get_drawings() if region.contains(s['rect'])]
    assert len(shapes) == 20 and all(s['type']=='f' and not s['even_odd'] for s in shapes)
    def group(color, geometry):
        return f'<g fill="{color}">\n'+'\n'.join(geometry)+'\n</g>'
    (out/'wholesale-report-green.svg').write_text(svg('BC Cannabis Wholesale',
        'Issuer artwork extracted from the Liquor Distribution Branch Q1 2022 report, PDF page 2. Native glyph and underline paths; no bitmap or font dependency.',
        '79 135 251 21',group('#005432',[path(path_from(s)) for s in shapes])))
    # Retail is a different design. Align each letter to the independently measured
    # retail specimen. Share letter outlines only for the glyphs actually present in the
    # sibling publisher's vector. The A, R, T and taper are new drawn geometry, not pixels.
    letters = [(0,0,2,68,75),(1,72,1,72,77),(2,176,1,71,77),
               (4,349,2,81,75),(5,446,2,81,75),
               (7,630,2,68,75),(8,710,2,23,75),
               (9,745,1,56,77),(15,835,0,43,78),(12,946,0,81,78),
               (14,1106,1,44,75),(15,1158,0,42,78)]
    retail = [fit(shapes[i],tuple(box)) for i,*box in letters]
    a = 'M251 77 L283 2 H308 L341 77 H319 L312.5 61 H280 L273.5 77 Z M285 48 H307.5 L296 20 Z'
    retail += [path(a),path(a, 'translate(282 0)'),path('M883 1 H946 V11 H920 V77 H909 V11 H883 Z'),
               path('M1040 1 H1062 C1075 1 1084 8 1084 21 C1084 31 1080 37 1071 40 C1079 45 1084 54 1090 64 L1098 77 H1086 L1073 57 C1067 48 1062 44 1055 44 H1051 V77 H1040 Z M1051 10 V34 H1059 C1069 34 1073.5 29 1073.5 21.5 C1073.5 14 1068 10 1059 10 Z'),
               path('M0 103.5 C232 102 392 99 601 99 C807 99 990 102 1200 103.5 C963 105 818 108 601 108 C385 108 209 105 0 103.5 Z')]
    (out/'stores-wordmark-rebuilt.svg').write_text(svg('BC Cannabis Stores',
        'Reconstruction from the published Stores raster, using matched lettering geometry from the sibling Wholesale report where applicable and hand-built A, T, R and tapered rule. Not an official Stores master.',
        '-2 -2 1204 112',group('#1b5732',retail)))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('wholesale_pdf',type=Path)
    p.add_argument('output_dir',type=Path)
    args=p.parse_args()
    build(args.wholesale_pdf,args.output_dir)
