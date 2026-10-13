#!/usr/bin/env python3
"""Build the revised emblem from editable vector components and authored geometry.
No font is required. No raster is opened by this build script.
"""
from pathlib import Path
import json,copy,math
import numpy as np
from lxml import etree as E
from custom_lettering import GLYPHS
P=Path(__file__).parent
NS='http://www.w3.org/2000/svg';INK='http://www.inkscape.org/namespaces/inkscape'
def num(v):return f'{float(v):.3f}'.rstrip('0').rstrip('.')
def el(p,t,**attrs):
 n=E.SubElement(p,f'{{{NS}}}{t}')
 for k,v in attrs.items():
  if v is not None:n.set(k.replace('_','-'),str(v))
 return n
def group(p,id,label=None):
 g=el(p,'g',id=id)
 if label:g.set(f'{{{INK}}}label',label)
 return g
def path(p,d,fill='black',**attrs):return el(p,'path',d=d,fill=fill,**attrs)
def xy(p):return ','.join(num(v) for v in p)
def smooth_path(points):
 pts=np.array(points,float)
 if len(pts)==2:return 'L'+xy(pts[1])
 result=''
 for i in range(len(pts)-1):
  prev=pts[max(0,i-1)];a=pts[i];b=pts[i+1];nxt=pts[min(len(pts)-1,i+2)]
  c1=a+(b-prev)/6;c2=b-(nxt-a)/6
  result+=f'C{xy(c1)} {xy(c2)} {xy(b)} '
 return result

def ribbon(points,radii):
    """Construct a round variable-width stroke from analytic vector discs,
    union the overlapping geometry, and refit a compact smooth vector boundary.
    This operates on vector centerline data, never on raster contours.
    """
    import shapely
    pts=np.array(points,float);rr=np.array(radii,float);centers=[];widths=[]
    for i in range(len(pts)-1):
        a=pts[i];b=pts[i+1];prev=pts[max(0,i-1)];nxt=pts[min(len(pts)-1,i+2)]
        c1=a+(b-prev)/6;c2=b-(nxt-a)/6
        n=max(2,int(np.linalg.norm(b-a)/.55)+1)
        for j in range(n):
            t=j/n
            centers.append((1-t)**3*a+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*b)
            widths.append((1-t)*rr[i]+t*rr[i+1])
    centers.append(pts[-1]);widths.append(rr[-1])
    discs=shapely.buffer(shapely.points(np.array(centers)),np.array(widths),quad_segs=8)
    merged=shapely.union_all(discs).simplify(.15,preserve_topology=True)
    polygons=list(merged.geoms) if merged.geom_type=='MultiPolygon' else [merged]
    def closed_curve(coords):
        q=np.asarray(coords,float)[:-1]
        if len(q)<3:return ''
        mids=(q+np.roll(q,-1,axis=0))/2
        d='M'+xy(mids[-1])
        for i in range(len(q)):
            before=q[i]-q[(i-1)%len(q)];after=q[(i+1)%len(q)]-q[i]
            den=np.linalg.norm(before)*np.linalg.norm(after)
            cosine=float(before@after)/den if den else 1
            if cosine>.62:
                d+=f'Q{xy(q[i])} {xy(mids[i])} '
            else:
                d+=f'L{xy(q[i])} L{xy(mids[i])} '
        return d+'Z '
    return ''.join(closed_curve(poly.exterior.coords)+''.join(closed_curve(ring.coords) for ring in poly.interiors) for poly in polygons)

def draw_tree(master):
 tree=group(master,'central-conifer','Reference-specific conifer, trunk and roots');tree.set(f'{{{INK}}}groupmode','layer')
 trunk=group(tree,'upper-main-trunk','Main trunk - narrow, slightly right offset, tapered lower end')
 path(trunk,'M743.5,550.5 C747.8,552.3 749,556.5 749,563.5 L749,610 C749,621 749.5,631.5 752.8,640.7 C754,643.3 755.2,647 756.6,646.7 C759,646.2 759.8,638.1 759.8,631.8 L759.8,578.4 C759.8,569 758.1,561.3 760.8,556.3 L765,550 Z')
 path(trunk,'M754.7,620.2 C754.9,626.8 754.5,632.2 756.5,639.7 C757.4,633.5 756.8,625.5 756.4,620.4 Q755.7,618 754.7,620.2 Z','white')
 crown=group(tree,'crown-branch-system','Crown - curved variable-width branches, source-specific topology')
 crown.set('transform','translate(0.166667 0.166667)')
 graph=json.loads((P/'crown_branch_graph.json').read_text())
 for e in graph['edges']:
  path(crown,ribbon(e['points'],e['radii']),id=f'crown-branch-{e["id"]:03}',**{'data-start-node':e['start_node'],'data-end-node':e['end_node']})
 for i,n in enumerate(graph['nodes']):
  if n['radius']>.3:el(crown,'circle',cx=num(n['x']),cy=num(n['y']),r=num(max(.5,n['radius']-.16)),fill='black',id=f'crown-junction-{i:03}')
 roots=group(tree,'lower-trunk-and-roots','Lower trunk - source notch, asymmetrical bark cuts and root flare')
 path(roots,'M747.3,691.5 C749.5,691.1 752.6,696.6 754.1,701.8 L755.1,704.3 C755.8,698.5 758.8,694.2 760.8,691.9 Q762.9,690.1 762.9,694.3 L762.9,719.2 C763.1,730.8 764.5,743.2 764.8,752 C765.2,761.6 766.9,766.7 773.1,770.2 L784.4,776 C794.4,783.8 802.8,787.7 813.7,793.1 Q816.9,794.8 815.6,797.3 Q814.4,799.2 810.8,798.1 L782.4,790.7 C767.3,786.4 757.8,783.6 747,786.1 L697,798.4 Q692.1,800.2 691.1,796.8 Q690.8,795.3 694.5,792.9 L716.6,780.9 C729.4,774.1 737.3,769.1 740.4,765.1 C744,760.9 744.4,753.4 744.9,745.8 L746.3,720.2 L746.8,699 Z',id='lower-trunk-silhouette')
 path(roots,'M757.1,738.5 L758.4,738.5 Q759,738.5 759,742 L759.6,753.5 L760.1,762.1 Q760.7,768 764.5,771.5 Q767,774 773.2,775.8 Q780,780.1 786.5,787.3 L779.3,783.3 Q771.9,780.3 766,779.8 Q756.4,778.6 751,772.4 Q749.8,770.8 750.1,764.9 L750.3,758.6 Q750.2,753.6 750.7,753.3 L751.4,753.9 Q752.7,767.3 754.5,768.6 Q756.3,770.5 756.9,766.4 L756.7,747.2 L756.6,739.2 Q756.6,738.1 757.1,738.5 Z','white',id='root-main-bark-cut')
 path(roots,'M757.1,722.1 Q758.2,722 758.3,724.3 L758,729.9 Q756.8,730.9 757,728.1 Z','white',id='root-upper-bark-cut')
 path(roots,'M751.2,748 Q752.8,747.6 752.8,749.6 L751.8,752.3 Q750.8,752.6 750.8,750.2 Z','white',id='root-left-stem-cut')
 path(roots,'M745.8,771.2 Q744.2,774.8 738.4,777.1 L740.3,775.1 Z','white',id='left-root-crescent')
 path(roots,'M730.5,786.3 Q736.6,783 740.7,780.5 Q742.8,780 743,779.7 L745.2,781.7 Q742.1,783.7 737.4,784.2 Z','white',id='left-root-cut')
 path(roots,'M718.8,786.4 L724.8,783.8 L721.8,786 Z','white',id='left-root-tip-highlight')
 fitted=P/'tree_root_refinements.json'
 if fitted.exists():
  for ident,d in json.loads(fitted.read_text()).items():
   n=roots.xpath(f'//*[@id="{ident}"]')
   if n:n[0].set('d',d)
 return tree

def draw_lettering(master):
 g=group(master,'lettering','Source-fitted reusable vector capitals; no font dependency');g.set(f'{{{INK}}}groupmode','layer')
 rows=json.loads((P/'letter_placements.json').read_text());groups={}
 for i,r in enumerate(rows):
  word=r['word']
  if word not in groups:
   groups[word]=group(g,word,word.upper().replace('-',' '));groups[word].set('aria-label',word.upper().replace('-',' '))
  ch=r['character'];d,w=GLYPHS[ch];h=r['glyph_height']
  q=group(groups[word],f'{word}-letter-{i+1:02d}',ch)
  q.set('transform',f'translate({num(r["cx"]+.5)} {num(r["cy"]+.5)}) rotate({num(r["angle"])}) scale({num(r["sx"])} {num(r["sy"])}) translate({num(-w/2)} {num(-h/2)})')
  o=r['weight_offset']
  path(q,d,fill_rule='evenodd',stroke='black' if o>=0 else 'white',stroke_width=num(abs(o)*2),stroke_linejoin='round')
 return g

def draw_exterior(master):
 allg=group(master,'exterior-engraving','Exterior engraving - source-specific curved ink geometry')
 allg.set(f'{{{INK}}}groupmode','layer')
 allg.set('transform','translate(0.25 0.25)')
 axes={
 'left-tall-spray':[(454,507),(400,313),(352,135)],
 'left-inner-spray':[(519,473),(512,356),(520,250)],
 'left-upper-side-spray':[(507,496),(331,430),(159,369)],
 'left-lower-side-spray':[(500,490),(329,489),(177,553)],
 'right-tall-spray':[(1041,480),(1089,281),(1137,127)],
 'right-inner-spray':[(1003,483),(983,349),(954,250)],
 'right-upper-side-spray':[(1000,489),(1162,398),(1374,379)],
 'right-lower-side-spray':[(1007,488),(1169,527),(1360,572)]}
 samples={}
 for name,vs in axes.items():
  a,b,c=np.array(vs,float);t=np.linspace(0,1,90)[:,None]
  samples[name]=(1-t)**2*a+2*(1-t)*t*b+t*t*c
 subgroups={}
 for side in ['left','right']:
  sg=group(allg,f'{side}-exterior',side.title()+' exterior components')
  for name in [f'{side}-cone',f'{side}-lower-stem']+[k for k in axes if k.startswith(side)]:
   subgroups[name]=group(sg,name,name.replace('-',' ').title())
 def classification(p,side):
  x,y=p
  reflected=x if side=='left' else 1500-x
  if y>740 and reflected>414:return side+'-lower-stem'
  if y>635 or (y>547 and reflected>400-(y-575)*1.8):return side+'-cone'
  choices={k:np.linalg.norm(v-[x,y],axis=1).min() for k,v in samples.items() if k.startswith(side)}
  return min(choices,key=choices.get)
 for side in ['left','right']:
  gr=json.loads((P/f'{side}_exterior_graph.json').read_text())
  for e in gr['edges']:
   pts=np.array(e['points'],float);rr=np.array(e['radii'],float)
   g=subgroups[classification(pts.mean(axis=0),side)]
   if np.ptp(rr)<.42:
    path(g,'M'+xy(pts[0])+smooth_path(pts),'none',stroke='black',stroke_width=num(2*np.median(rr)),stroke_linecap='round',stroke_linejoin='round',id=f'{side}-ink-curve-{e["id"]:04}')
   else:
    path(g,ribbon(pts,rr),id=f'{side}-variable-ink-{e["id"]:04}')
  for i,n in enumerate(gr['nodes']):
   if not n.get('used'):continue
   g=subgroups[classification([n['x'],n['y']],side)]
   el(g,'circle',cx=num(n['x']),cy=num(n['y']),r=num(max(.45,n['radius']-.18)),fill='black',id=f'{side}-ink-junction-{i:04}')
 return allg


def build():
 master=E.Element(f'{{{NS}}}svg',nsmap={None:NS,'inkscape':INK})
 master.set('version','1.1');master.set('width','1536');master.set('height','1024');master.set('viewBox','0 0 1536 1024')
 el(master,'title').text='British Columbia Forest Service - Lands Department - revised source-specific vector reconstruction'
 el(master,'desc').text='Reference-specific variable-width curved ink geometry, separately rebuilt main trunk and roots, measured oval, and individually positioned reusable capital outlines. No embedded raster or font dependencies. This is a reconstruction, not an authenticated historical production master.'
 draw_exterior(master)
 ov=json.loads((P/'oval_geometry.json').read_text())
 ov['cx']+=.5;ov['cy']+=.5
 seal=group(master,'oval-seal','Measured oval field and border');seal.set(f'{{{INK}}}groupmode','layer')
 el(seal,'ellipse',id='oval-field',cx=num(ov['cx']),cy=num(ov['cy']),rx=num(ov['rx']),ry=num(ov['ry']),fill='white',stroke='black',stroke_width=num(ov['stroke_width']),transform=f'rotate({num(ov["rotation_degrees"])} {num(ov["cx"])} {num(ov["cy"])})')
 draw_tree(master);draw_lettering(master)
 return master

def save(root,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 E.ElementTree(root).write(str(path),pretty_print=True,xml_declaration=True,encoding='utf-8')

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=P.parent/'svg/bcfs-lands-department-v2-editable.svg')
 parser.add_argument('--preview',type=Path,help='Optional PNG preview; requires CairoSVG')
 args=parser.parse_args()
 try:
  svg=build();save(svg,args.output)
  if args.preview:
   import cairosvg
   args.preview.parent.mkdir(parents=True,exist_ok=True)
   cairosvg.svg2png(url=str(args.output),write_to=str(args.preview),background_color='white')
  print(f'Created {args.output}')
 except Exception as exc:
  raise SystemExit(f'Build failed: {exc}')
