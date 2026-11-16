import sys,json; sys.path.insert(0,'.')
from textpath import text_d
from compose import tight_bbox, svg_doc
from sf_symbol import build
FONT='../sf/classico/classico/opentype/URWClassico-Regular.otf'
caps=json.load(open('fit_sfcaps_classico.json'))
region=open('sf_region.d').read()
def make(sym_col, txt_col, reg_col, out, title, desc):
    body=[f'<path d="{d}" fill="{sym_col}"/>' for d in build()]
    for t,r in caps.items():
        # set at size 100, horizontal scale sx (expanded) and uniform s, baked into the outline coordinates
        d,_=text_d(FONT,t,100,r['tracking'])
        import re
        def tf(m):
            x,y=float(m.group(1)),float(m.group(2)); return f'{x*r["s"]*r["sx"]+r["tx"]:.2f} {y*r["s"]+r["ty"]:.2f}'
        d=re.sub(r'(-?[\d.]+) (-?[\d.]+)',tf,d)
        body.append(f'<path d="{d}" fill="{txt_col}"/>')
    body.append(f'<path d="{region}" fill="{reg_col}"/>')
    B='\n'.join('  '+x for x in body)
    vb=tight_bbox(B,(0,0,1943,990),scale=1)
    vb=(max(vb[0]-1,0),max(vb[1]-1,0),vb[2]+1,vb[3]+1)
    open(out,'w').write(svg_doc(B,vb,title,desc))
    return vb
if __name__=='__main__':
    print(make('#000000','#000000','#000000','out-sfhr-mono.svg',
      'Simon Fraser Health Region — S symbol, name and region script, monochrome (vector reconstruction)',
      'Reconstruction fitted to the January 2001 Continuum running-header bitmap. S symbol: straight block edges placed at measured positions, curved edges as fitted Bezier chains. '
      'Name: URW Classico (Optima design) expanded horizontally to match, converted to outlines; original typeface not verified. Hand-lettered region: outline fitted to the bitmap contour.'))
