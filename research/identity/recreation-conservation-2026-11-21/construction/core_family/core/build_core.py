"""Deliberate geometric reconstructions of three 1971-73 BC identity symbols.

No contour extraction is used to make the artwork. Source segmentation is used
only to normalize the separate visual comparison images. Coordinates below are
editable design parameters, with repeated quarters, mirrored volutes, and a
single fish construction reused three times.
"""
from pathlib import Path
import json
import cairosvg
from svgpathtools import parse_path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter

HERE = Path(__file__).resolve().parent
INK = '#000000'

def svg(name,description,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000" viewBox="0 0 1000 1000" role="img" aria-labelledby="title desc">
<title id="title">{name}</title><desc id="desc">{description} Historical reconstruction, November 2026; not an original vector master.</desc>
{body}
</svg>'''

def rounded_path(r):
    k = .552284749831
    a=r*(1-k)
    return f'M {r} 0 H {1000-r} C {1000-a} 0 1000 {a} 1000 {r} V {1000-r} C 1000 {1000-a} {1000-a} 1000 {1000-r} 1000 H {r} C {a} 1000 0 {1000-a} 0 {1000-r} V {r} C 0 {a} {a} 0 {r} 0 Z'

def department():
    # The four outside corners of the negative quadrants are intentionally
    # square. Rounding them would alter a conspicuous feature of the specimen.
    q=parse_path('M 77 77 H 334 C 430 77 481 128 481 220 L 481 341 C 481 360 475 367 459 375 C 415 394 394 416 375 458 C 366 477 358 481 339 481 H 225 C 126 481 77 433 77 336 Z')
    quarters=' '.join(q.rotated(a,complex(500,500)).d() for a in (0,90,180,270))
    circle='M 595 500 A 95 95 0 1 0 405 500 A 95 95 0 1 0 595 500 Z'
    body=f'<g id="four-lobes-and-centre"><path id="compound-field-with-five-openings" fill="{INK}" fill-rule="evenodd" d="{rounded_path(217)} {quarters} {circle}"/></g>'
    return svg('Department of Recreation and Conservation','Four rotationally related negative quadrants and one circular opening in a rounded square.',body)

def parks():
    # A filled, tapering volute rather than a constant-width spiral stroke.
    volute='M 410 947 V 325 C 410 267 365 222 309 222 C 242 222 194 273 194 336 C 194 388 230 427 277 427 C 317 427 347 395 347 357 C 347 323 324 302 296 302 C 278 302 266 316 266 335 C 266 349 277 356 291 351 C 304 347 314 353 314 365 C 314 376 307 382 292 385 C 255 394 222 373 222 337 C 222 295 255 265 299 265 C 354 265 389 305 389 360 C 389 429 340 482 275 482 C 191 482 126 416 126 333 C 126 231 210 150 309 150 C 405 150 484 227 484 324 V 947 Z'
    body=f'''<g id="parks-geometry" fill="{INK}">
<rect id="rounded-frame" x="37" y="37" width="926" height="926" rx="174" fill="none" stroke="{INK}" stroke-width="74"/>
<g id="paired-volutes"><path id="left-volute" d="{volute}"/><path id="right-volute" transform="translate(1000 0) scale(-1 1)" d="{volute}"/></g></g>'''
    return svg('Provincial Parks Branch','Mirrored tapering spiral forms on two upright stems, connected to a rounded square frame.',body)

def fisheries():
    fish='M 145 202 C 167 171 262 132 360 127 C 458 121 560 140 650 166 L 705 171 C 757 130 799 110 835 108 C 809 158 797 201 803 245 C 807 275 819 297 833 311 C 791 310 752 278 704 239 L 650 243 C 559 278 471 298 367 294 C 269 290 177 255 148 225 Q 137 214 145 202 Z'
    # Each fish includes its eye and curved gill. The grid passes continuously
    # through the fish; it is not clipped at their outlines in the source.
    single=f'''<path id="fish-outline" d="{fish}" fill="none" stroke="{INK}" stroke-width="20" stroke-linejoin="round"/>
<path id="gill" d="M 263 178 C 291 202 289 239 251 263" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round"/>
<circle id="eye" cx="217" cy="190" r="10.5" fill="{INK}"/>'''
    body=f'''<defs><g id="fish-master">{single}</g></defs>
<g id="three-fish" fill="{INK}"><use id="upper-fish" xlink:href="#fish-master"/><use id="middle-fish" xlink:href="#fish-master" transform="translate(0 287)"/><use id="lower-fish" xlink:href="#fish-master" transform="translate(0 574)"/></g>
<g id="grid" stroke="{INK}" stroke-width="25"><path id="vertical-divisions" d="M 369 60 V 940 M 650 60 V 940"/><path id="horizontal-divisions" d="M 60 355 H 940 M 60 644 H 940"/></g>
<rect id="rounded-frame" x="37" y="37" width="926" height="926" rx="175" fill="none" stroke="{INK}" stroke-width="74"/>'''
    return svg('Commercial Fisheries / Marine Resources Branch','Three repeated fish crossed by two vertical and two horizontal grid lines in a rounded square. Same symbol carries two branch names.',body)

def compare(name):
    ref=np.array(Image.open(HERE/f'{name}_reference.png').convert('L'))
    rendered=Image.open(HERE/f'{name}.png').convert('RGBA')
    vec=np.array(rendered)[:,:,3]/255
    # Small 1-bit scan holes are print/scan defects, not original design detail.
    src=gaussian_filter((255-ref)/255,.8)>.50
    tgt=vec>.50
    iou=float((src&tgt).sum()/(src|tgt).sum())
    # A tolerance measured in units of the 1000-unit symbol, not source pixels.
    dtgt=distance_transform_edt(~tgt); dsrc=distance_transform_edt(~src)
    tol=7.5
    recall=float((dtgt[src]<=tol).mean());precision=float((dsrc[tgt]<=tol).mean())
    overlay=np.full((1000,1000,3),255,dtype=np.uint8)
    overlay[src]=[235,74,114];overlay[tgt]=[50,160,207];overlay[src&tgt]=[39,49,59]
    Image.fromarray(overlay).save(HERE/f'{name}_overlay.png')
    panel=Image.new('RGB',(1500,565),'#f5f4ef');d=ImageDraw.Draw(panel)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
    for i,(im,label) in enumerate([(Image.fromarray(ref),'Report scan'),(Image.alpha_composite(Image.new('RGBA',(1000,1000),'white'),rendered).convert('RGB'),'Reconstructed vector'),(Image.fromarray(overlay),'Overlay: source pink / vector blue')]):
        panel.paste(im.resize((450,450)),(25+i*500,60));d.text((25+i*500,22),label,font=font,fill='#263c36')
    panel.save(HERE/f'{name}_comparison.png')
    return {'ink_IoU':round(iou,4),'tolerance_units':tol,'source_ink_within_tolerance':round(recall,4),'vector_ink_within_tolerance':round(precision,4),'normalization':'independent bounding box scaling, no deformation; no local warp','native_reference_size':'approximately 212 pixels square','not_a_fidelity_score':True}

if __name__=='__main__':
    metrics={}
    for name,fn in [('department',department),('parks',parks),('fisheries',fisheries)]:
        content=fn();(HERE/f'{name}.svg').write_text(content)
        cairosvg.svg2png(bytestring=content.encode(),write_to=str(HERE/f'{name}.png'),output_width=1000,output_height=1000)
        cairosvg.svg2pdf(bytestring=content.encode(),write_to=str(HERE/f'{name}.pdf'))
        metrics[name]=compare(name)
    (HERE/'metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2))
