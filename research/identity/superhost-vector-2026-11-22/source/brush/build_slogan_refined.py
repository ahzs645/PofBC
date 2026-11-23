#!/usr/bin/env python3
"""Recreate the refined slogan from reusable pen skeletons and saved placements.

Usage: python3 build_slogan_refined.py [--output Slogan_Refined.svg]
Requires svgpathtools. No raster reference is read by this generator.
"""
from pathlib import Path
import argparse,json,math
from svgpathtools import parse_path
from curve_fitting import simplify

HERE=Path(__file__).resolve().parent
def ribbon(d,width):
    p=parse_path(d);a=[];b=[]
    for j,seg in enumerate(p):
        n=max(12,int(seg.length()/.4))
        for k in range(n+1):
            t=k/n;z=seg.point(t);v=seg.derivative(t)
            if abs(v)<1e-8:continue
            normal=complex(-v.imag,v.real)/abs(v)
            angle=math.atan2(v.imag,v.real)
            half=(1.15+1.15*abs(math.sin(angle+.2)))*(width/3.7)
            if j==0 and t<.1:half*=.72+2.8*t
            if j==len(p)-1 and t>.9:half*=1-2.8*(t-.9)
            a.append(z+normal*half);b.append(z-normal*half)
    q=a+b[::-1]
    polygon='M'+' L'.join(f'{z.real:.3f} {z.imag:.3f}' for z in q)+' Z'
    return simplify(polygon,.075)[0]

def build(output):
    data=json.loads((HERE/'brush-skeletons-refined.json').read_text())
    rows=[]
    for i,glyph in enumerate(data['fitted']):
        c=glyph['glyph'];width=data['nib_widths'].get(c,data['nib_widths']['other'])
        paths=''.join('<path d="'+ribbon(d,width)+'"/>' for d in data['glyphs'][c])
        rows.append(f'<g id="slogan-letter-{i}-{c}" data-letter="{c}" transform="{glyph["transform"]}">'+paths+'</g>')
    body='<g id="superhost-slogan" data-text="Expect the most" data-method="shared pen skeletons, mathematical nib sweep, constrained letter registration; no raster-contour tracing" fill="#000000">'+''.join(rows)+'</g>'
    output.write_text(body)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'Slogan_Refined.svg')
    args=parser.parse_args();build(args.output);print(args.output)
