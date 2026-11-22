"""Geometric reconstructions of the three handbook category emblems.

The ram is a hand-drawn Bezier construction; crab limbs/claws and flower petals
use repeated/mirrored components. References remain independent photographs.
"""
from pathlib import Path
import json,io
from PIL import Image,ImageDraw,ImageFont
import cairosvg,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];(P/'svg').mkdir(exist_ok=True);(P/'png').mkdir(exist_ok=True)
INK='#163c36'
FRAME='<rect x="35" y="35" width="930" height="930" rx="160" fill="none" stroke="currentColor" stroke-width="70"/>'
def wrap(name,inner):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000"><title>{name}</title><desc>Geometric historical reconstruction from photographed Provincial Museum handbook covers. Fine detail is source-limited. No raster or font embedded.</desc><g color="{INK}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{FRAME}{inner}</g></svg>'

# Ram: reference-view construction measured from the photographed no.29 emblem.
ram='''<g transform="translate(-36.363636 -90) scale(1.818182 2)">
<g stroke-width="6">
  <path d="M133 214 C133 176 154 151 191 128 C223 108 258 94 297 94 C351 84 402 104 442 142 C488 187 512 250 512 315 C515 375 494 424 454 458 C415 492 367 507 310 506 C249 507 205 487 171 454 C147 430 134 398 133 365 C133 347 138 333 149 328 C162 323 173 335 181 351 C196 376 224 391 256 395 C288 401 320 398 344 382 C364 370 375 348 373 326 C371 304 360 287 344 276"/>
  <path d="M45 281 C67 266 106 268 119 236 C123 214 135 201 151 201 C180 199 207 220 218 254 L259 274 L267 244 C278 232 307 228 344 223 C345 242 338 266 322 280 L315 307"/>
  <path d="M272 270 C291 282 312 274 326 252"/>
  <path d="M149 296 C166 287 188 285 207 282 C207 299 199 310 185 312 C176 311 168 305 168 297"/>
  <path d="M47 425 L87 428 C106 430 115 440 119 459 L130 518"/>
  <path d="M439 472 L464 517"/>
  <path d="M297 96 C276 109 261 120 261 143 C260 172 267 201 279 232"/>
  <path d="M442 143 C408 140 393 150 378 174 C361 199 354 215 344 223"/>
  <path d="M509 258 C479 251 453 265 423 280 L371 303"/>
  <path d="M505 372 C480 395 456 391 425 376 L371 355"/>
  <path d="M444 468 C419 481 398 474 384 448 L347 390"/>
  <path d="M304 505 L303 401"/>
  <path d="M214 482 L253 397"/>
  <path d="M163 442 L215 383"/>
  <path d="M141 398 L183 365"/>
  <path d="M134 359 L167 347"/>
</g></g>'''

# Crab: one claw/arm and four leg components reflected about the body centre.
half='''<g stroke-width="5.5">
<path d="M313 104 C341 88 381 94 411 113 C438 130 442 152 425 168 C402 179 366 158 344 144 C328 133 320 119 313 104 Z"/>
<path d="M316 105 C333 107 350 118 363 126 L372 127 L380 136 L389 136 L397 145 L416 150"/>
<path d="M427 169 C452 173 470 194 466 213 C462 224 452 232 439 238 C423 226 417 213 421 197 C422 184 424 177 427 169 Z"/>
<path d="M443 225 C450 241 430 267 408 281 L384 268 C396 248 417 231 443 225 Z"/>
<path d="M390 323 L474 362 L484 380 L467 388 L377 343 Z"/>
<path d="M377 343 L459 401 L465 423 L448 433 L364 365 Z"/>
<path d="M355 361 L412 425 L426 464 L409 475 L391 438 L336 378 Z"/>
<path d="M331 377 L366 432 L371 491 L352 494 L345 443 L314 384 Z"/>
</g>'''
crab=f'''<g transform="translate(-71.84466 -79.207921) scale(1.941748 1.980198)">
{half}<g transform="translate(584 0) scale(-1 1)">{half}</g>
<path stroke-width="6" d="M176 300 L236 249 C260 246 278 246 292 247 C310 246 328 247 349 251 L408 300 C389 323 365 343 341 356 C316 369 268 369 243 356 C216 342 191 323 176 300 Z"/>
<path stroke-width="9" d="M266 246 L266 222 M318 246 L318 222"/>
<circle cx="266" cy="218" r="8" fill="currentColor" stroke="none"/><circle cx="318" cy="218" r="8" fill="currentColor" stroke="none"/>
</g>'''

# Flower: five radial petals with repeated vein construction. The photos show a
# five-lobed flower; the idealized repetition avoids copying scan distortion.
petal='''<path stroke-width="15" d="M303.095 243.975 C299 169 378 105 475 113 C585 100 702 152 696.905 243.975"/>
<path stroke-width="13" d="M500 515 C438 457 354 354 303.095 243.975"/>
<path stroke-width="10" d="M500 515 C475 428 466 315 469 207 M500 515 C519 426 532 304 531 191"/>'''
flower=''.join(f'<g transform="rotate({a} 500 515)">{petal}</g>' for a in [0,72,144,216,288])+'<circle cx="500" cy="515" r="15" fill="currentColor" stroke="none"/>'

definitions=[('Ram_Head','Ram-head handbook category emblem',ram,'abe_32246743715.jpg',[677,225,757,306],'No.29, The Birds: Diving Birds and Tube-nosed Swimmers; ram head is used as a series/category emblem, not an image of the book subject.'),('Crab','Crab handbook category emblem',crab,'abe_32246733201.jpg',[670,221,745,298],'No.23, Some Common Marine Fishes; repeated limb and claw geometry inferred from the photographed outline.'),('Flower','Flower handbook category emblem',flower,'abe_32246744624.jpg',[713,199,795,282],'No.16, The Orchids; five-petal form and veins corroborated by the edible-plants cover photo. Exact small vein positions remain uncertain.')]
records=[]
for slug,title,inner,src,box,note in definitions:
 svg=wrap(title,inner);dest=P/'svg'/f'{slug}.svg';dest.write_text(svg)
 pic=cairosvg.svg2png(bytestring=svg.encode(),output_width=1000,output_height=1000);(P/'png'/f'{slug}.png').write_bytes(pic)
 ref=Image.open(ROOT/'variant_research/handbooks'/src).crop(box).convert('RGB');ref.save(P/f'{slug}_native_reference.png')
 # Only an overall square rectification is used; no local warp.
 ref=ref.resize((1000,1000),Image.Resampling.BICUBIC);ref.save(P/f'{slug}_registered_reference.png')
 vec=Image.open(io.BytesIO(pic)).convert('RGBA');alpha=vec.getchannel('A').point(lambda x:round(x*.5));pink=Image.new('RGB',(1000,1000),'#c43583');ov=ref.copy();ov.paste(pink,(0,0),alpha);ov.save(P/f'{slug}_overlay.png')
 records.append({'name':title,'slug':slug,'svg':f'svg/{slug}.svg','reference_file':src,'native_crop':box,'registration':'Frame crop normalized to1000square; no local warp. Photograph colours are not calibrated.','construction':'Hand-drawn cubic paths; shared/mirrored components where appropriate. No bitmap trace.','status':'Source-limited historical reconstruction; small internal details approximate.','note':note})

(P/'subject_emblems.json').write_text(json.dumps(records,indent=2))
W,H=1800,2180;sheet=Image.new('RGB',(W,H),'#f4f1e8');d=ImageDraw.Draw(sheet);ff='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
d.text((38,28),'Provincial Museum handbook category marks',font=ImageFont.truetype(fb,39),fill=INK)
d.text((38,85),'Source photograph / geometric reconstruction / overlay. Small line details remain approximate.',font=ImageFont.truetype(ff,24),fill='#52675e')
for i,r in enumerate(records):
 y=145+i*660;d.text((38,y),r['name'],font=ImageFont.truetype(fb,30),fill=INK)
 for j,(label,f) in enumerate([('Photographed source',P/f'{r["slug"]}_registered_reference.png'),('Reconstruction',P/'png'/f'{r["slug"]}.png'),('Overlay',P/f'{r["slug"]}_overlay.png')]):
  x=40+j*590;d.text((x,y+48),label,font=ImageFont.truetype(ff,22),fill='#52675e');a=Image.open(f).convert('RGBA').resize((540,540),Image.Resampling.LANCZOS);sheet.paste(a,(x,y+88),a)
sheet.save(P/'Handbook_Subject_Emblems_Review.png')
print('Created3subjectemblems and review sheet.')
