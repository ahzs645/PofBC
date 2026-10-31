"""Rebuild sticker lettering from outlined font glyphs and constructed geometric capitals.
Source pixels are used only to measure placement, not to trace contours.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
import math, json
import subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parent
font=TTFont('/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
gs=font.getGlyphSet(); cmap=font.getBestCmap()
# Measured printed-ink bounds, arranged in reading order. Each outline is fitted
# independently, preserving the original graphic's irregular letter spacing.
upper=[('BRITISHCOLUMBIA',[(117,157,143,192),(150,157,175,192),(183,157,187,192),(193,157,218,192),(224,157,228,192),(235,157,261,193),(268,157,294,192),(314,157,342,193),(346,156,376,193),(383,157,404,192),(408,157,433,193),(441,157,472,192),(480,157,506,192),(514,157,518,192),(524,157,552,192)]),('FERRIES',[(876,157,897,192),(903,157,926,192),(932,157,958,192),(965,157,990,193),(998,157,1002,192),(1012,157,1035,192),(1038,157,1065,193)])]
parts=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 1305 1206">','<g id="lettering" aria-label="British Columbia Ferries — Queen of Sidney">','<g id="top-lettering" fill="#101513" aria-label="British Columbia Ferries">']
for wi,(word,bounds) in enumerate(upper):
 for i,(ch,(x0,y0,x1,y1)) in enumerate(zip(word,bounds)):
  glyph=gs[cmap[ord(ch)]];bp=BoundsPen(gs);glyph.draw(bp);a,b,c,d=bp.bounds
  x0-=.35; y0-=.35;x1+=.35;y1+=.35
  sx=(x1-x0)/(c-a);sy=-(y1-y0)/(d-b)
  p=SVGPathPen(gs); glyph.draw(TransformPen(p,(sx,0,0,sy,x0-a*sx,y0-d*sy)))
  parts.append(f'<path id="header-{wi+1}-{i+1:02d}-{ch}" aria-label="{ch}" d="{p.getCommands()}"/>')
parts.append('</g>')
# Hand-constructed rounded grotesk capitals. Dimensions and counters are explicit;
# no autotraced perimeter or external font dependency is used for the name ribbon.
paths={
'O':(36,64,'M18 0 C6 0 0 7 0 19 L0 45 C0 57 6 64 18 64 C30 64 36 57 36 45 L36 19 C36 7 30 0 18 0 Z M18 11 C22.5 11 24 14.5 24 20 L24 44 C24 50 22 53 18 53 C14 53 12 50 12 44 L12 20 C12 14.5 13.5 11 18 11 Z'),
'Q':(39,70,'M18 0 C6 0 0 7 0 19 L0 46.5 C0 58.5 6 65.5 18 65.5 C21 65.5 23.7 65.1 26 64 L34.5 69.7 Q35.2 70.3 35.9 69.1 L39 61 Q39.3 60.2 38.3 59.7 L32.5 57.8 C35 54 36 50.6 36 45.5 L36 19 C36 7 30 0 18 0 Z M18 11 C22.5 11 24 14.5 24 20 L24 46 C24 52 22 55 18 55 C14 55 12 52 12 46 L12 20 C12 14.5 13.5 11 18 11 Z'),
'U':(36,64,'M1.2 0 L10.8 0 Q12 0 12 1.3 L12 44 C12 50.5 13.6 53 18 53 C22.4 53 24 50.5 24 44 L24 1.3 Q24 0 25.2 0 L34.8 0 Q36 0 36 1.3 L36 44 C36 57 30 64 18 64 C6 64 0 57 0 44 L0 1.3 Q0 0 1.2 0 Z'),
'E':(32,62,'M1.4 0 L30.6 0 Q32 0 32 1.4 L32 9.5 Q32 11 30.6 11 L12 11 L12 25.5 L25.9 25.5 Q27 25.5 27 26.8 L27 34.6 Q27 36 25.9 36 L12 36 L12 51 L30.6 51 Q32 51 32 52.4 L32 60.6 Q32 62 30.6 62 L1.4 62 Q0 62 0 60.6 L0 1.4 Q0 0 1.4 0 Z'),
'N':(39,62,'M1.5 0 L11.3 0 Q12.5 0 13 1.2 L27 35.5 L27 1.5 Q27 0 28.4 0 L37.5 0 Q39 0 39 1.5 L39 60.5 Q39 62 37.5 62 L27.8 62 Q26.5 62 26 60.8 L12 26.3 L12 60.5 Q12 62 10.5 62 L1.5 62 Q0 62 0 60.5 L0 1.5 Q0 0 1.5 0 Z'),
'F':(32,62,'M1.4 0 L30.6 0 Q32 0 32 1.4 L32 9.4 Q32 11 30.6 11 L12 11 L12 25.5 L25.2 25.5 Q26.6 25.5 26.6 26.9 L26.6 34.8 Q26.6 36.2 25.2 36.2 L12 36.2 L12 60.6 Q12 62 10.6 62 L1.4 62 Q0 62 0 60.6 L0 1.4 Q0 0 1.4 0 Z'),
'S':(39,66,'M38 17 Q38 18.2 36.8 18.3 L27.2 19 Q26 19.1 25.9 17.8 C25.5 12.9 23.1 10.5 19.1 10.5 C14.8 10.5 12.3 13.1 12.3 17.3 C12.3 21.3 15.4 24.1 21.4 28.1 L26.7 31.7 C34.2 36.6 39 41.5 39 49.6 C39 59.9 32.3 66 19.8 66 C7.4 66 0.8 59.3 0 48.6 Q-.1 47.5 1.3 47.3 L10.9 46.7 Q12 46.6 12.1 48 C12.7 53.1 15.2 55.8 19.9 55.8 C24.3 55.8 26.8 53.2 26.8 49.3 C26.8 45.2 23.9 42.5 18.3 38.8 L12 34.5 C4.9 29.8 1 24.7 1 17.4 C1 6.6 8.1 0 19 0 C30.3 0 36.8 6.1 38 17 Z'),
'I':(12,62,'M1.4 0 L10.6 0 Q12 0 12 1.4 L12 60.6 Q12 62 10.6 62 L1.4 62 Q0 62 0 60.6 L0 1.4 Q0 0 1.4 0 Z'),
'D':(36,62,'M1.3 0 L16 0 C29.8 0 36 7.8 36 21.6 L36 40.4 C36 54.2 29.8 62 16 62 L1.3 62 Q0 62 0 60.7 L0 1.3 Q0 0 1.3 0 Z M12 11 L12 51 L16 51 C22 51 24 47.5 24 40 L24 22 C24 14.5 22 11 16 11 Z'),
'Y':(40,62,'M1.2 0 L11.3 0 Q12.3 0 12.7 1.2 L20.1 24.6 L27.5 1.2 Q27.9 0 28.9 0 L38.8 0 Q40.5 0 39.8 1.6 L26 36.9 L26 60.6 Q26 62 24.6 62 L15.4 62 Q14 62 14 60.6 L14 36.9 L.2 1.6 Q-.5 0 1.2 0 Z')
}
# Rotation, fitted width/height, and original-canvas centers.
layout=[('Q',41,39.50,68.08,365.94,932.67),('U',33,35.44,63.39,404.4,963.51),('E',28,31.42,61.26,444.25,987.1),('E',22,31.77,61.21,481.84,1005.92),('N',17,38.7,60.86,525.67,1021.94),('O',5,36.16,64.19,612.86,1039.86),('F',-1,31.01,60.87,660.99,1040.49),('S',-17,38.47,65.22,759.99,1030.96),('I',-20,12.14,61.17,797.58,1020.61),('D',-24,36.04,61.64,832.64,1006.32),('N',-31,37.76,61.93,876.63,983.72),('E',-38,31.42,62.23,916.91,958.24),('Y',-43,38.94,62.47,951.98,928.96)]
parts.append('<g id="ribbon-lettering" fill="#fffdf7" fill-rule="evenodd" aria-label="Queen of Sidney">')
for i,(ch,ang,w,h,cx,cy) in enumerate(layout):
 fw,fh,d=paths[ch];w+=.3;h+=.3
 parts.append(f'<g id="name-{i+1:02d}-{ch}" aria-label="{ch}" transform="translate({cx} {cy}) rotate({ang}) scale({w/fw:.8f} {h/fh:.8f}) translate({-fw/2} {-fh/2})"><path d="{d}"/></g>')
parts+=['</g>','</g>','</svg>']
s='\n'.join(parts);(ROOT/'lettering.svg').write_text(s)
subprocess.run(['inkscape',str(ROOT/'lettering.svg'),'--export-width=1305','--export-height=1206','--export-filename='+str(ROOT.parent/'qa/lettering.png')],check=True,capture_output=True)
source_path=ROOT.parent/'reference'/'original-reference.png'
if not source_path.exists(): source_path=ROOT.parent.parent/'upload'/'Vintage Queen of Sidney Ferry Sticker(2).png'
source=Image.open(source_path).convert('RGBA');vec=Image.open(ROOT.parent/'qa/lettering.png')
# Bright green edges show lettering reconstruction without hiding printed originals.
from PIL import ImageFilter
mask=vec.getchannel('A');edge=Image.blend(mask.filter(ImageFilter.MaxFilter(3)),mask.filter(ImageFilter.MinFilter(3)),0)
import numpy as np
alpha=np.maximum(np.array(mask.filter(ImageFilter.MaxFilter(3)),dtype=int)-np.array(mask.filter(ImageFilter.MinFilter(3)),dtype=int),0).astype('uint8')
edge=Image.new('RGBA',source.size,(0,255,130,0));edge.putalpha(Image.fromarray(alpha))
source=Image.alpha_composite(source,edge);source.crop((315,885,990,1080)).resize((1350,390)).save(ROOT.parent/'qa/lettering-overlay.png')
(ROOT/'lettering-notes.json').write_text(json.dumps({'upper':'Nimbus Sans Regular, outlined, independently fitted to source printed-glyph bounds','lower':'Constructed rounded grotesk capitals; explicit Bézier / line geometry; individually positioned and rotated','source_canvas':[1305,1206],'lower_layout':[dict(zip(['letter','degrees','width','height','center_x','center_y'],a)) for a in layout],'fidelity_limit':'Letter contours are clean reconstructions; small print wear and source irregularities are intentionally omitted.'},indent=2))
print('Wrote',ROOT/'lettering.svg')
