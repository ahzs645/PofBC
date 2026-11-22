from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE=Path(__file__).resolve().parent
# Deliberately constructed from a rounded enclosure, shared stems, three bowls,
# a C curve, and M diagonals. No contour extraction or tracing is used.
def svg():
 return '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000" role="img" aria-labelledby="title desc">
<title id="title">British Columbia Provincial Museum — BCPM monogram</title>
<desc id="desc">Geometric reconstruction of the interlocking BCPM mark in the Department of Recreation and Conservation annual reports. Custom Bézier letterforms and shared strokes; no fonts or raster images.</desc>
<g id="museum-mark" fill="none" stroke="#000000" stroke-linecap="butt" stroke-linejoin="round">
  <g id="shared-letter-stems" stroke-width="64">
    <path id="bp-left-stem" d="M 146,70 V 966"/>
    <path id="pm-centre-stem" d="M 464,480 V 966"/>
    <path id="cm-right-stem" d="M 852,401 V 966"/>
  </g>
  <g id="m-diagonals" stroke-width="58" stroke-linejoin="miter">
    <path d="M 490,488 L 655,915 L 845,430"/>
  </g>
  <g id="b-and-p-bowls" stroke-width="59">
    <path id="b-upper-bowl" d="M 146,97 H 351 C 429,97 466,132 466,198 C 466,264 429,291 352,291 H 146"/>
    <path id="b-lower-bowl" d="M 146,291 H 349 C 434,291 477,333 477,398 C 477,468 432,506 351,506 H 146"/>
    <path id="p-bowl" d="M 146,506 H 345 C 426,506 464,546 464,606 C 464,672 426,700 345,700 H 146"/>
  </g>
  <g id="c-curve" fill="#000000" stroke="none">
    <path d="M 882,196 H 817 C 805,142 766,116 693,116 C 578,116 518,181 518,306 C 518,436 572,485 682,485 C 766,485 809,455 820,401 H 884 C 866,494 808,542 682,542 C 521,542 453,468 453,306 C 453,141 533,53 693,53 C 798,53 865,101 882,196 Z"/>
  </g>
  <path id="shared-bcpm-junction" d="M474,450 H509 V499 H474Z" fill="#000000" stroke="none"/>
  <g id="rounded-enclosure" stroke-width="68">
    <rect x="34" y="34" width="932" height="932" rx="181"/>
  </g>
</g>
</svg>'''

s=svg();(BASE/'museum.svg').write_text(s)
cairosvg.svg2png(bytestring=s.encode(),write_to=str(BASE/'museum.png'),output_width=1000,output_height=1000)
cairosvg.svg2pdf(bytestring=s.encode(),write_to=str(BASE/'museum.pdf'))
# Reference shown at 1000x1000 for visual registration; original screenshot crop 200x200.
src=Image.open(BASE/'source_crop.png').convert('RGB')
vec=Image.open(BASE/'museum.png').convert('RGBA')
w=Image.new('RGBA',(1000,1000),'white');w.alpha_composite(vec); clean=w.convert('RGB')
board=Image.new('RGB',(2040,1080),'#f4f3ed');board.paste(src,(0,60));board.paste(clean,(1040,60));d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23);d.text((20,18),'SOURCE: 1971 report, museum divider (208 x 210 px)',fill='black',font=font);d.text((1060,18),'RECONSTRUCTION: custom geometric letterforms',fill='black',font=font);board.save(BASE/'comparison.png')
# False colour overlap: source cyan, reconstruction red; matching silhouettes dark.
a=np.asarray(src).astype(float);gray=a.mean(axis=2)
# Single global threshold serves only QA. It does not generate paths.
ref=np.clip((215-gray)/75,0,1)
v=np.asarray(vec)[:,:,3].astype(float)/255
ov=np.empty((1000,1000,3),dtype=np.uint8)
ov[:,:,0]=255*(1-.75*ref)
ov[:,:,1]=255*(1-.85*v)
ov[:,:,2]=255*(1-.85*v)
Image.fromarray(ov).save(BASE/'overlay.png')
