#!/usr/bin/env python3
"""Regenerate the finalized outlined inscription from explicit master curves.

Requires FontTools only. It does not need a font installation, raster source,
image tracing, optimisation or access to any external file.
"""
from pathlib import Path
import json,math
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'round-inscription-parameters.json').read_text())
F=P['reference_frame'];k=F['reference_to_final_scale'];cx,cy=F['center'];fx,fy=F['final_center']
paths=[]
for item in sorted(P['placements'],key=lambda x:x['text_index']):
    master=P['masters'][item['character']]
    x0,y0,x1,y1=master['bounds'];mx=(x0+x1)/2;my=(y0+y1)/2
    sx,sy=item['scale_x'],item['scale_y'];th=math.radians(item['angle_degrees']);sn,cs=math.sin(th),math.cos(th)
    a,b,c,d=sx*cs,sx*sn,sy*sn,-sy*cs;tx,ty=item['center_xy']
    e=tx-a*mx-c*my;f=ty-b*mx-d*my
    matrix=(k*a,k*b,k*c,k*d,fx+k*(e-cx),fy+k*(f-cy))
    pen=SVGPathPen(None);parse_path(master['path'],TransformPen(pen,matrix))
    paths.append(f'<path id="letter-{item["text_index"]:02d}" data-character="{item["character"]}" d="{pen.getCommands()}"/>')
svg=['<?xml version="1.0" encoding="UTF-8"?>','<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500">',
     '<title>British Columbia Steamship Company (1975) Ltd. - finalized circular lettering</title>',
     '<desc>Outlined Roman serif construction with custom C, S, s, y, 5 and 7. Corrected optical size and placement. No raster tracing or font dependencies.</desc>',
     '<g id="circular-lettering" fill="#000000">',*paths,'</g>','</svg>']
(HERE/'round-inscription.svg').write_text('\n'.join(svg)+'\n')
print('Finalized circular inscription regenerated from explicit master curves.')
