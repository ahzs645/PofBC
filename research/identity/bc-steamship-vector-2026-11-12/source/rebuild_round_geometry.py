#!/usr/bin/env python3
"""Construct regularized circular logo geometry from a sparse analytic model.

The generator never opens a raster. Dimensions were measured separately against
user-supplied reference artwork and rounded where appropriate. Rings are true
circles; paired facets are mirrored; repeated wave arcs share ellipse parameters.
No automated contour trace, image, font, external resource, clipping mask or
pixel-by-pixel path is included.
"""
from pathlib import Path
import math,json
HERE=Path(__file__).resolve().parent
REF_CX=620.5355002322681
REF_CY=621.8197600642902
REF_OUTER_R=591.6864505385126
K=688/REF_OUTER_R
P={
 'reference_frame':{'cx':REF_CX,'cy':REF_CY,'outer_radius':REF_OUTER_R,'reference_to_final_scale':K,'final_center':[750,750]},
 'rings':{'outer_border_outer':591.6864505385126,'outer_border_inner':567.118891407537,'emblem_outer':414.0247560249769,'emblem_inner':392.02935658558016},
 'upper_envelope':{'cy':624.0,'r':367.0},
 'stem_half_width':52.0,
 'fan_inner_half_width':88.75,
 'fan_baseline':539.0,
 'upper_triangle':{'outer_offset':211.0,'inner_tip_y':449.0},
 'diagonal_ray':{'outer_upper_offset':237.0,'outer_lower_offset':276.0,'inner_upper_y':494.0,'inner_lower_offset':124.5},
 'lower_triangle':{'outer_offset':301.0,'inner_base_offset':171.5},
 'bar':{'cy':617.5,'r':367.0,'top':571.0,'bottom':664.0},
 'first_wave':{'cy':651.4,'rx':128.55,'ry':116.35,'center_offset':233.2,'top':687.5,'lobe_count':3},
 'second_wave':{'cy':763.52,'rx':168.29,'ry':107.51,'center_offset':156.63,'top':785.0,'lobe_count':2},
 'bottom_cap':{'cy':665.14412558,'r':330.63676502,'top':888.0},
 'bottom_dot':{'cy':1114.1777275880563,'r':20.514999682404362},
}

def f(x):return f'{x:.8f}'.rstrip('0').rstrip('.')
def pt(x,y):return f'{f(x)} {f(y-REF_CY)}'
def arc(rx,ry,x,y,sweep=0):return f'A {f(rx)} {f(ry)} 0 0 {sweep} {pt(x,y)}'
def circle(r,cy=REF_CY):
 y=cy-REF_CY
 return f'M 0 {f(y-r)} A {f(r)} {f(r)} 0 1 1 0 {f(y+r)} A {f(r)} {f(r)} 0 1 1 0 {f(y-r)} Z'
def ey(x):return P['upper_envelope']['cy']-math.sqrt(P['upper_envelope']['r']**2-x*x)
def ex(y):return -math.sqrt(P['upper_envelope']['r']**2-(y-P['upper_envelope']['cy'])**2)

def wave(w):
 centers=[-w['center_offset'],0,w['center_offset']] if w['lobe_count']==3 else [-w['center_offset'],w['center_offset']]
 rx,ry,cy,top=w['rx'],w['ry'],w['cy'],w['top']
 half=rx*math.sqrt(1-((top-cy)/ry)**2)
 x0,x1=centers[0]-half,centers[-1]+half
 joints=[]
 for left,right in zip(centers,centers[1:]):
  x=(left+right)/2
  y=cy+ry*math.sqrt(1-((right-left)/(2*rx))**2)
  if y<=top:raise ValueError('Non-positive wave bridge')
  joints.append((x,y))
 out=[f'M {pt(x0,top)} H {f(x1)}']
 for i in range(len(centers)-1,-1,-1):
  end=joints[i-1] if i else (x0,top)
  out.append(arc(rx,ry,*end,1))
 return ' '.join(out)+' Z'

def geometries():
 e=P['upper_envelope'];r=e['r'];xi=-P['fan_inner_half_width'];base=P['fan_baseline'];h=P['stem_half_width'];b=P['bar']
 dt=math.sqrt(b['r']**2-(b['top']-b['cy'])**2);db=math.sqrt(b['r']**2-(b['bottom']-b['cy'])**2)
 stem=f'M {pt(-h,ey(-h))} {arc(r,r,h,ey(h),1)} V {f(b["top"]-REF_CY)} H {f(dt)} {arc(b["r"],b["r"],db,b["bottom"],1)} H {f(-db)} {arc(b["r"],b["r"],-dt,b["top"],1)} H {f(-h)} Z'
 a=-P['upper_triangle']['outer_offset'];t=P['upper_triangle']
 upper=f'M {pt(xi,ey(xi))} {arc(r,r,a,ey(a))} L {pt(xi,t["inner_tip_y"])} Z'
 q=P['diagonal_ray'];a=-q['outer_upper_offset'];b=-q['outer_lower_offset']
 diagonal=f'M {pt(a,ey(a))} {arc(r,r,b,ey(b))} L {pt(-q["inner_lower_offset"],base)} H {f(xi)} V {f(q["inner_upper_y"]-REF_CY)} Z'
 q=P['lower_triangle'];a=-q['outer_offset']
 lower=f'M {pt(a,ey(a))} {arc(r,r,ex(base),base)} H {f(-q["inner_base_offset"])} Z'
 q=P['bottom_cap'];dx=math.sqrt(q['r']**2-(q['top']-q['cy'])**2)
 cap=f'M {pt(-dx,q["top"])} H {f(dx)} {arc(q["r"],q["r"],-dx,q["top"],1)} Z'
 return {'stem-and-bar':stem,'upper-facet':upper,'diagonal-facet':diagonal,'lower-facet':lower,'three-wave-band':wave(P['first_wave']),'two-wave-band':wave(P['second_wave']),'bottom-segment':cap}
G=geometries()
def body(color='#000000'):
 r=P['rings'];out=[f'<g id="round-geometry" fill="{color}" transform="translate(750 750) scale({K:.14f})">']
 out.append(f'<path id="round-outer-border" fill-rule="evenodd" d="{circle(r["outer_border_outer"])} {circle(r["outer_border_inner"])}"/>')
 out.append(f'<path id="emblem-ring" fill-rule="evenodd" d="{circle(r["emblem_outer"])} {circle(r["emblem_inner"])}"/>')
 out.append(f'<path id="central-stem-and-bar" d="{G["stem-and-bar"]}"/>')
 for side in ['left','right']:
  out.append(f'<g id="{side}-facets"'+(' transform="scale(-1 1)"' if side=='right' else '')+'>')
  for kind in ['upper-facet','diagonal-facet','lower-facet']:out.append(f'<path id="{side}-{kind}" d="{G[kind]}"/>')
  out.append('</g>')
 for kind in ['three-wave-band','two-wave-band','bottom-segment']:out.append(f'<path id="{kind}" d="{G[kind]}"/>')
 out.append(f'<path id="round-bottom-dot" d="{circle(P["bottom_dot"]["r"],P["bottom_dot"]["cy"])}"/>')
 out.append('</g>')
 return '\n'.join(out)
def document(color='#000000'):
 return '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500">\n<title>BC Steamship Company - corrected circular geometry</title>\n<desc>Thirteen sparse constructed filled paths. Two true circular rings, mirrored straight fan facets, shared analytic wave ellipses, circular bottom segment and separator dot. No image, text, tracing, mask or external dependency. The minor source asymmetries are deliberately normalized.</desc>\n'+body(color)+'\n</svg>\n'
if __name__=='__main__':
 for name,c in [('round-geometry.svg','#000000'),('round-geometry-white.svg','#ffffff')]: (HERE/name).write_text(document(c))
 (HERE/'geometry-parameters.json').write_text(json.dumps(P,indent=2)+'\n')
 final={
  'reference_to_final':{'scale':K,'source_center':[REF_CX,REF_CY],'target_center':[750,750],'translation':[750-K*REF_CX,750-K*REF_CY]},
  'final_radii':{key:val*K for key,val in P['rings'].items()},
  'final_ring_widths':{'outer_border':(P['rings']['outer_border_outer']-P['rings']['outer_border_inner'])*K,'emblem':(P['rings']['emblem_outer']-P['rings']['emblem_inner'])*K},
  'centerline_ratio':((P['rings']['outer_border_outer']+P['rings']['outer_border_inner'])/(P['rings']['emblem_outer']+P['rings']['emblem_inner'])),
  'final_dot':{'cx':750,'cy':750+(P['bottom_dot']['cy']-REF_CY)*K,'radius':P['bottom_dot']['r']*K},
  'filled_path_count':13,'raster_images':0,'fonts':0,
  'regularization':'Shared concentric exact circles and a common bilateral axis; source ellipse and small centre offsets deliberately normalized. No warp applied to the reference image.',
 }
 (HERE/'final-geometry-metrics.json').write_text(json.dumps(final,indent=2)+'\n')
 print(json.dumps(final,indent=2))
