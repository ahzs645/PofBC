from pathlib import Path
import json, subprocess
OUT=Path(__file__).resolve().parents[1]/'svg'
OUT.mkdir(exist_ok=True)
INK='#252623'
parts=[]
def path(d,fill='none',sw=1.6,extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{INK if sw else "none"}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def ellipse(cx,cy,rx,ry,fill=INK):
 return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"/>'
# Hand-constructed drawing coordinates. No pixel extraction, contour finding or auto tracing.
# Every figure is built from intentionally selected Bezier geometry and line engraving.
def face(kind='short',pose=0,glasses=False,variant=0):
 p=[]
 long=kind in ['wavy','bob']
 if long:
  p.append(path('M -42 21 C -68 33 -66 61 -61 80 C -73 95 -60 107 -65 119 C -66 137 -51 151 -39 150 L -24 135 L 28 138 C 49 157 68 137 59 122 C 75 113 67 97 64 85 C 70 58 55 27 40 19 Z M -39 34 C -44 49 -42 59 -40 70 C -53 57 -54 75 -47 83 L -39 86 C -32 112 -17 130 5 132 C 26 132 39 109 44 85 C 54 84 58 67 48 65 L 44 67 C 48 49 43 35 33 26 Z',INK,1.0,extra='fill-rule="evenodd"'))
 else:
  p.append(path('M -44 23 C -53 35 -54 56 -46 73 L -36 73 L -27 30 L 29 28 L 39 66 L 50 65 C 56 41 51 21 36 17 Z',INK,1.0))
 # Head, brow and ear contours. Unpainted areas are truly transparent.
 p.append(path('M -39 34 C -44 49 -42 59 -40 70 C -53 57 -54 75 -47 83 L -39 86 C -32 112 -17 130 5 132 C 26 132 39 109 44 85 C 54 84 58 67 48 65 L 44 67 C 48 49 43 35 33 26',sw=2.0))
 p.append(path('M -46 71 C -42 69 -42 77 -44 79 M 48 71 C 53 70 49 80 47 80',sw=1.0))
 if kind=='swept':
  p.append(path('M -43 51 C -27 49 -19 34 -5 33 C 12 33 23 23 34 25 C 40 38 40 44 45 49 L 42 24 L -29 21 Z',INK,1.0))
  p.append(path('M -40 43 C -20 40 -12 27 4 27 M -34 34 C -17 30 -4 21 16 23',sw=1.0))
 elif kind=='wavy':
  p.append(path('M -43 57 C -31 52 -27 37 -21 29 C -12 42 1 37 7 27 C 18 42 31 34 36 24 C 36 36 43 48 47 51',sw=2.4))
  p.append(path('M -54 61 C -61 74 -49 79 -55 89 C -62 100 -53 108 -48 107 M -53 112 C -61 126 -48 137 -41 136 M 57 58 C 65 72 51 79 59 88 C 66 99 54 107 55 118 C 56 131 48 140 39 138',sw=1.5))
 elif kind=='bob':
  p.append(path('M -42 53 C -30 43 -25 28 -14 26 C -6 38 13 36 21 26 C 29 39 38 46 46 50 M -55 58 C -59 83 -51 112 -40 124 M 56 58 C 61 82 51 112 41 120',sw=1.7))
 else:
  p.append(path('M -41 42 C -30 29 -20 33 -10 26 C 8 34 26 29 38 29 L 44 47',sw=1.7))
 # Slightly different brow, eye and nose geometry give a group rather than repeated stamps.
 if pose==1:
  p.append(path('M -27 59 C -17 52 -7 53 -1 56 M 12 54 C 23 49 31 51 36 55',sw=2.3))
  p.append(path('M -26 65 C -18 60 -9 60 -3 64 M 14 61 C 22 56 30 58 35 61',sw=1.7))
  p.extend([ellipse(-11,64,2.7,2),ellipse(27,60,2.6,2)])
  p.append(path('M 8 64 C 7 77 16 80 16 84 C 12 88 5 87 2 85 M 0 89 L -5 88',sw=1.6))
 else:
  p.append(path('M -29 56 C -20 52 -10 52 -3 56 M 11 56 C 20 51 31 51 37 56',sw=2.3))
  p.append(path('M -27 63 C -20 59 -11 59 -5 63 M 13 63 C 21 59 29 59 35 63',sw=1.6))
  p.extend([ellipse(-16,63,2.8,2.1),ellipse(24,63,2.8,2.1)])
  p.append(path('M 6 64 C 2 75 0 79 1 83 C 5 87 12 85 15 83 M -2 84 L -7 85',sw=1.4))
 p.append(path('M -27 72 C -20 75 -14 74 -9 72 M 18 73 C 24 76 31 74 34 72',sw=0.8))
 if variant%3==0:
  p.append(path('M -18 97 C -8 91 -3 91 4 94 C 12 90 21 92 29 96 C 15 111 -4 111 -18 97 Z',sw=1.5))
  p.append(path('M -14 98 C 0 100 15 100 25 97 M -4 116 C 4 119 13 117 17 114',sw=1.0))
 elif variant%3==1:
  p.append(path('M -18 99 C -6 93 5 90 15 93 L 25 97 C 9 104 -7 104 -18 99 M -4 109 C 6 112 14 108 18 106',sw=1.4))
 else:
  p.append(path('M -18 95 C -7 100 11 101 28 94 C 18 111 -6 114 -18 95 Z M -13 98 C -3 102 14 103 23 98 C 15 105 -4 107 -13 98 Z',INK,0.6,extra='fill-rule="evenodd"'))
 p.append(path('M -31 89 C -30 94 -28 99 -24 101 M 33 88 C 34 92 32 97 29 100',sw=0.85))
 if glasses:
  p.append(path('M -36 54 L -3 55 L -6 76 C -17 83 -30 78 -33 73 Z M 12 55 L 42 52 L 39 73 C 31 80 19 80 14 74 Z M -2 58 C 3 56 7 56 12 58 M -37 57 L -46 53 M 42 55 L 49 51',sw=3.0))
 p.append(path('M -21 123 L -24 143 M 25 122 L 30 144 M -16 133 C -4 143 14 142 22 133',sw=1.4))
 for i in range(5):
  p.append(path(f'M {-17+i*3} {129+i*.9} l 5 6',sw=.55))
 if variant%2:
  p.append(path('M -33 78 l 3 8 M -30 78 l 2 5 M 35 78 l -1 6 M 33 100 l -3 8 M -24 106 l 3 5',sw=.65))
 return ''.join(p)

def portrait(spec):
 kind=spec.get('kind','short');v=spec['v'];p=[]
 # Gown and neckline.
 p.append(path('M -24 139 C -39 144 -56 147 -72 154 C -94 168 -107 198 -111 250 M 31 140 C 55 146 70 150 85 164 C 102 183 109 219 112 249',sw=1.8))
 p.append(path('M -25 139 L -54 151 L -30 178 L 2 157 L 32 178 L 61 151 L 30 139',sw=1.5))
 if spec.get('dark',False):
  p.append(path('M -54 151 L -72 156 L -90 177 L -107 239 L -61 250 L -32 178 L 1 163 L 34 181 L 59 249 L 110 248 C 102 207 98 181 79 162 L 61 152 L 33 177 L 2 158 L -30 177 Z',INK,0.8))
  pass # Filled robe regions remain solid ink; no opaque white highlights.
 else:
  p.append(path('M -72 160 C -70 187 -80 208 -78 231 M -64 169 L -63 209 M -54 181 L -59 238 M 72 162 C 71 180 89 210 88 235 M 63 176 L 74 230 M -32 181 C -21 201 -19 226 -18 250 M 34 183 C 25 209 27 226 35 249',sw=1.1))
 p.append(path('M 1 161 L -3 246 M 8 171 L 10 247 M -21 186 L -17 198 M 23 190 L 21 205',sw=1.0))
 # Etched hatching on gown.
 if not spec.get('dark',False):
  for i in range(9):
   yy=193+i*5
   p.append(path(f'M {-103+(i%3)*1.3:.1f} {yy} l 13 -4 M {91-(i%2)*2} {yy+3} l 10 4',sw=.6))
 p.append(face(kind,spec.get('pose',0),spec.get('glasses',False),v))
 # Mortarboard overlaps the hairline.
 if spec.get('hat')=='none':
  return ''.join(p)
 if spec.get('hat','solid')=='solid':
  p.append(path('M -103 -1 L 5 -29 L 108 -1 L 4 24 Z',INK,1.2))
  p.append(path('M -45 18 L -44 39 C -16 30 15 30 43 38 L 45 18 C 21 12 -16 13 -45 18 Z',INK,1.0))
  pass # True solid ink cap; no opaque highlight strokes.
 else:
  p.append(path('M -103 -1 L 5 -29 L 108 -1 L 4 24 Z',sw=1.5))
  p.append(path('M -45 18 L -44 39 C -16 30 15 30 43 38 L 45 18',sw=1.4))
  for i in range(7):
   p.append(path(f'M {-72+i*4} {7+i*2.0} L {40+i*4} {7+i*1.2}',sw=.55))
 # Off-centre crown button and tassel.
 p.append(ellipse(5,5,3,1.5))
 if v%2:
  p.append(path('M 5 5 L 84 12 C 82 25 84 41 81 57 M 81 55 L 75 84 L 87 85 Z',sw=1.2))
  for i in range(4):p.append(path(f'M {79+i*1.4} 59 L {77+i*2.4} 82',sw=.65))
 else:
  p.append(path('M 5 5 L -83 13 C -85 25 -79 46 -84 57 M -84 56 L -91 85 L -78 85 Z',sw=1.2))
  for i in range(4):p.append(path(f'M {-86+i*1.3} 59 L {-89+i*2.6} 82',sw=.65))
 return ''.join(p)

figures=[
 dict(id='rear-left',x=398,y=36,s=.57,rot=-6,kind='bob',v=0,hat='light'),
 dict(id='rear-right',x=469,y=84,s=.56,rot=5,kind='short',v=1,dark=True,hat='light'),
 dict(id='upper-left',x=301,y=163,s=.79,rot=-4,kind='swept',v=2,hat='light'),
 dict(id='upper-centre',x=415,y=194,s=.73,rot=-2,kind='bob',v=3,dark=True),
 dict(id='upper-right',x=535,y=193,s=.80,rot=3,kind='short',v=4),
 dict(id='middle-left',x=156,y=339,s=1.0,rot=-4,kind='bob',v=5,hat='light'),
 dict(id='middle-centre',x=321,y=318,s=.94,rot=-2,kind='bob',v=6,dark=True),
 dict(id='middle-right-glasses',x=503,y=366,s=1.03,rot=3,kind='short',v=7,glasses=True,hat='light'),
 dict(id='foreground-left',x=176,y=568,s=1.21,rot=-5,kind='swept',v=1,pose=1,hat='none'),
 dict(id='foreground-right',x=431,y=554,s=1.25,rot=3,kind='wavy',v=9,dark=True),
]
# Each later figure knocks out underlying ink using vector clip paths. This retains
# transparent paper/negative space without white face patches or bitmap masks.
sil='M -104 5 L 5 -28 L 110 5 L 65 22 L 56 49 C 65 72 59 100 43 121 L 31 139 C 56 145 73 152 86 164 C 103 184 112 223 113 252 L -113 252 C -107 203 -97 172 -73 154 L -24 138 L -37 120 C -61 111 -69 91 -61 66 L -51 31 Z'
def tf(f):return f'translate({f["x"]} {f["y"]}) rotate({f["rot"]}) scale({f["s"]})'
defs=[]
for f in figures:
 sil_f=sil if f.get('hat')!='none' else 'M -42 21 C -58 34 -57 58 -51 70 C -58 85 -49 112 -37 120 L -24 138 C -53 147 -65 149 -73 154 C -97 172 -107 203 -113 252 L 113 252 C 112 223 103 184 86 164 C 73 152 56 145 31 139 L 43 121 C 59 100 65 72 56 49 C 53 29 41 18 25 17 Z'
 defs.append(f'<clipPath id="outside-{f["id"]}" clipPathUnits="userSpaceOnUse"><path clip-rule="evenodd" fill-rule="evenodd" d="M -4000 -4000 H 4000 V 4000 H -4000 Z {sil_f}" transform="{tf(f)}"/></clipPath>')
body=[]
for i,f in enumerate(figures):
 block=f'<g id="figure-{f["id"]}" transform="{tf(f)}">{portrait(f)}</g>'
 for n in figures[i+1:]:block=f'<g clip-path="url(#outside-{n["id"]})">{block}</g>'
 body.append(block)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="900" viewBox="0 0 720 900" role="img" aria-labelledby="title desc"><title id="title">IUS support campaign: ten graduates, interpretive vector redrawing</title><desc id="desc">Original manually constructed Bezier drawing informed by the ten-figure composition on the supplied photographed campaign brochure. This is an interpretive replacement, not a recovered original illustration. Every figure is an editable vector group; no raster data or automatic tracing.</desc><defs>{''.join(defs)}</defs><g id="graduates-illustration">{''.join(body)}</g></svg>'''
(OUT/'ius-graduates-interpretive.svg').write_text(svg)
meta={
 'title':'Ten graduates - interpretive vector redrawing',
 'source':'IMG_7953(1).jpeg',
 'status':'interpretive replacement; not an exact facsimile',
 'evidence':'Photograph shows ten faces in a tapered composition: 2 small rear graduates, 3 upper-middle, 3 lower-middle, 2 large foreground. The lower-middle right figure wears glasses. Mortarboards, tassels and academic gowns are visible.',
 'method':'Manually authored Bezier outlines, solid ink regions, restrained line hatching, and vector clip paths. No image tracing, no raster content, no external fonts.',
 'limitations':['Facial features and fine engraving are newly drawn because photograph resolution does not support recovery.','Mortarboard angles, line hatching and gown folds are interpretations.','Do not describe as the original campaign illustration or original artist artwork.'],
 'viewBox':[0,0,720,900],
 'ink':INK,
 'elements':len(figures),
 'negative_space':'Transparent background; foreground silhouettes clip underlying ink with vector clip paths.',
 'files':['ius-graduates-interpretive.svg','build_graduates.py']
}
(OUT.parent/'source'/'illustration_metadata.json').write_text(json.dumps(meta,indent=2))
print(str(OUT/'ius-graduates-interpretive.svg'))
