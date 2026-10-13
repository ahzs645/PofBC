#!/usr/bin/env python3
"""Rebuild the badge from deliberately placed vector geometry, not raster contours.

Requirements: Python 3.10+, lxml, fonttools; DejaVu Sans Bold for the small caption.
Run: python rebuild_badge.py --output ../dont-gamble-with-fire.svg
All distributed artwork already has outlined lettering and needs no installed font.
"""
from pathlib import Path
import argparse
import math
from lxml import etree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=Path('dont-gamble-with-fire.svg'))
parser.add_argument('--caption-font', type=Path,
                    default=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
args = parser.parse_args()
if not args.caption_font.is_file():
    parser.error('Caption font not found. Supply --caption-font with a local DejaVuSans-Bold.ttf file.')
args.output.parent.mkdir(parents=True, exist_ok=True)
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
BLUE='#01375D'
CREAM='#F1D8AC'
nsmap={None:SVG,'inkscape':INK}
root=ET.Element('{%s}svg'%SVG, nsmap=nsmap, width='1233',height='1233',viewBox='0 0 1233 1233',version='1.1')
root.set('role','img')
root.set('aria-labelledby','title description')
ET.SubElement(root,'{%s}title'%SVG,id='title').text='Don’t gamble with FIRE — B. C. Forest Service'
ET.SubElement(root,'{%s}desc'%SVG,id='description').text=('Clean two-colour vector reconstruction from the supplied historic badge image. '
'Circular border, two dice with separate faces and elliptical pips, manually redrawn headline lettering, '
'and individually outlined curved caption. No embedded bitmap, clipping mask, or autotraced contour.')
art=ET.SubElement(root,'{%s}g'%SVG,id='badge',transform='translate(0 4)')

def g(parent,id,label=None,layer=False,**attrs):
    ob=ET.SubElement(parent,'{%s}g'%SVG,id=id,**{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if label: ob.set('{%s}label'%INK,label)
    if layer: ob.set('{%s}groupmode'%INK,'layer')
    return ob

def el(parent,tag,id=None,**attrs):
    if id: attrs['id']=id
    return ET.SubElement(parent,'{%s}%s'%(SVG,tag),**{k.replace('_','-'):str(v) for k,v in attrs.items()})

def path(parent,id,d,**attrs): return el(parent,'path',id,d=' '.join(d.split()),**attrs)

field=g(art,'field','01 · Circular field and border',True)
el(field,'circle','cream-border',cx=616.5,cy=612.5,r=592.5,fill=CREAM)
el(field,'circle','blue-field',cx=616.5,cy=612.5,r=570,fill=BLUE)

headline=g(art,'headline','02 · Custom headline lettering',True,fill=CREAM,fill_rule='evenodd')
dont=g(headline,'word-dont','don’t — individual letters')
path(dont,'dont-d','''
M435 87 L476 75 L479 231 L445 239 L444 230
C435 236 424 237 413 234 C389 230 373 207 373 177
C373 145 396 117 424 118 L436 119 Z
M433 156 C421 153 413 163 414 178 C415 193 424 200 434 197
C440 195 441 190 439 181 L437 160 C436 158 434 156 433 156 Z''')
path(dont,'dont-o','''
M545 122 C577 122 603 145 603 181 C603 217 578 242 546 243
C512 245 484 221 484 186 C484 151 510 124 545 122 Z
M545 159 C534 159 525 170 525 186 C525 201 533 210 544 211
C555 211 563 200 563 185 C563 172 556 159 545 159 Z''')
path(dont,'dont-n','''
M614 125 L651 124 L651 140 C660 133 672 129 683 134
C704 140 716 160 716 192 L716 243 L678 242 L678 194
C678 177 674 171 665 171 C653 171 649 184 649 200 L649 237 L615 238 Z''')
path(dont,'dont-apostrophe','''
M704 81 Q717 77 725 80 C738 87 733 112 720 128
L718 108 L704 110 L700 88 Q700 83 704 81 Z''')
path(dont,'dont-t','''
M760 90 L800 91 L799 131 L818 131 L814 165 L798 165
L797 235 L761 237 L758 165 L746 165 L743 132 L758 132 Z''')

gamble=g(headline,'word-gamble','gamble! — individual letters')
path(gamble,'gamble-g','''
M302 280 L340 284 L348 391 C351 419 345 434 329 445
C311 456 288 456 271 445 C260 439 254 429 250 419
L285 410 C289 420 296 424 303 421 C309 419 311 412 309 400
C295 406 279 404 265 398 C245 387 236 369 236 348
C236 317 258 290 287 291 L302 293 Z
M295 331 C284 330 277 338 277 350 C277 362 285 370 295 369
C302 368 306 363 304 356 L302 333 Q300 331 295 331 Z''')
path(gamble,'gamble-a','''
M351 335 C355 306 374 289 402 288 C439 286 459 309 460 349
L463 408 L426 409 L424 402 C413 409 398 411 383 409
C365 407 354 395 354 380 C354 357 378 343 414 342
C414 329 410 321 402 321 C394 321 390 327 389 335 Z
M408 366 C401 366 395 369 396 375 C397 383 405 385 413 380
C419 377 420 371 415 368 C413 367 410 366 408 366 Z''')
path(gamble,'gamble-m','''
M470 288 L508 288 L508 300 C524 289 544 292 554 309
C570 294 592 297 606 308 C620 320 626 336 626 361
L626 413 L586 411 L586 358 C586 346 583 339 576 339
C568 339 565 347 565 359 L565 406 L528 409 L528 356
C528 342 524 335 517 335 C508 335 504 345 504 361 L504 407 L470 406 Z''')
path(gamble,'gamble-b','''
M631 250 L673 249 L672 302 C683 296 697 295 711 300
C730 309 740 329 740 350 C740 377 728 399 710 408
C698 413 683 413 670 408 L669 420 L636 415 Z
M684 334 C675 334 669 345 669 357 C669 369 675 378 684 378
C693 378 699 368 699 356 C699 344 693 334 684 334 Z''')
path(gamble,'gamble-l','M739 244 L780 250 L782 409 L747 410 Z')
path(gamble,'gamble-e','''
M900 356 L829 356 C832 373 847 377 861 364 L893 377
C884 395 868 403 850 404 C814 406 790 382 789 348
C788 310 810 283 842 282 C876 280 899 305 900 339 Z
M831 329 L861 329 C858 311 837 311 831 329 Z''')
path(gamble,'gamble-exclamation','M987 256 L1030 283 L957 384 L932 380 Z')
el(gamble,'ellipse','gamble-exclamation-dot',cx=936.5,cy=407.5,rx=18.5,ry=18)

dice=g(art,'dice','03 · Dice — editable faces and pips',True)
back=g(dice,'rear-die','Rear die',fill=CREAM,stroke=BLUE,stroke_width=3.4,stroke_linejoin='round',stroke_linecap='round')
path(back,'rear-die-shell','''
M590 469 L680 424 Q689 419 707 420 L877 427
Q900 428 906 457 L912 607 Q913 621 904 633
L846 709 Q832 730 821 714 Q812 734 794 733
L592 734 Q577 732 576 710 L571 523 Q567 491 590 469 Z''')
path(back,'rear-die-front-face','''
M607 485 L805 491 C813 493 816 507 816 528
L816 701 Q816 730 794 733 L592 734 Q577 732 576 710
L571 523 Q570 493 607 485 Z''')
path(back,'rear-die-right-face','''
M827 485 L876 445 C895 438 904 441 906 457
L912 607 Q913 621 904 633 L846 709 Q832 730 821 714
Q817 708 816 701 L816 528 Q816 500 827 485 Z''')
path(back,'rear-die-top-face','''
M601 468 L680 424 Q689 419 707 420 L866 426
C883 426 890 432 876 445 L827 485 Q820 491 805 491
L607 485 C592 485 585 479 601 468 Z''')
pips=g(back,'rear-die-pips','Rear die — pips 1 / 5 / 4',fill=BLUE,stroke='none')
el(pips,'ellipse','rear-top-pip-1',cx=745,cy=457,rx=26,ry=11)
for i,(x,y,r) in enumerate([(620,537,20.5),(773,543,20.5),(698,614,21),(625,690,20.5),(770,691,20.5)],1):
    el(pips,'circle',f'rear-front-pip-{i}',cx=x,cy=y,r=r)
for i,(x,y,rx,ry,rot) in enumerate([(886,487,9.5,20.5,2),(848,529,9.5,22,2),(896,603,9,22,3),(848,657,10,22.5,3)],1):
    el(pips,'ellipse',f'rear-right-pip-{i}',cx=x,cy=y,rx=rx,ry=ry,transform=f'rotate({rot} {x} {y})')

front=g(dice,'foreground-die','Foreground die',fill=CREAM,stroke=BLUE,stroke_width=3.4,stroke_linejoin='round',stroke_linecap='round')
path(front,'foreground-die-shell','''
M268 554 C270 534 284 523 299 518 L458 464 Q470 459 483 466
L610 549 Q633 562 631 586 L590 752 Q587 768 575 777
L437 891 Q416 910 400 902 Q389 907 382 891
L248 726 Q240 716 243 701 L262 567 Q264 558 268 554 Z''')
path(front,'foreground-die-left-face','''
M268 554 Q277 535 300 545 L430 671 Q444 693 441 716
L406 877 Q401 906 382 891 L248 726 Q240 716 243 701
L262 567 Q264 558 268 554 Z''')
path(front,'foreground-die-right-face','''
M457 670 L610 578 Q633 580 627 606 L590 752 Q587 768 575 777
L437 891 Q419 908 409 889 Q405 883 406 877
L441 716 Q447 690 457 670 Z''')
path(front,'foreground-die-top-face','''
M307 512 L458 464 Q470 459 483 466 L610 549
C625 558 624 569 610 578 L457 670 Q443 678 430 671
L300 545 C286 530 290 519 307 512 Z''')
pips=g(front,'foreground-die-pips','Foreground die — pips 1 / 3 / 2',fill=BLUE,stroke='none')
el(pips,'ellipse','foreground-top-pip-1',cx=460,cy=550,rx=32.5,ry=17,transform='rotate(0.5 460 550)')
for i,(x,y,rx,ry,rot) in enumerate([(287,596,17,27,5),(331,709,17,26,5),(374,821,16,27,8)],1):
    el(pips,'ellipse',f'foreground-left-pip-{i}',cx=x,cy=y,rx=rx,ry=ry,transform=f'rotate({rot} {x} {y})')
for i,(x,y,rot) in enumerate([(482,721,12),(560,748,18)],1):
    el(pips,'ellipse',f'foreground-right-pip-{i}',cx=x,cy=y,rx=15,ry=27,transform=f'rotate({rot} {x} {y})')

withword=g(art,'word-with','04 · “with” — foreground lettering',True,fill=CREAM,stroke=BLUE,stroke_width=3.8,stroke_linejoin='round',paint_order='stroke fill')
path(withword,'with-w','''
M522 771 L570 756 L585 811 L600 763 L643 769 L657 820
L670 758 L711 772 L677 876 L634 882 L619 835 L606 882 L568 888 Z''')
path(withword,'with-i','M721 766 L758 765 L759 875 L721 875 Z')
el(withword,'circle','with-i-dot',cx=740,cy=739,r=20.5)
path(withword,'with-t','''
M783 733 L818 732 L817 770 L840 770 L838 804 L818 804
L817 878 L780 876 L781 804 L766 804 L766 771 L782 771 Z''')
path(withword,'with-h','''
M850 716 L890 715 L883 779 C895 768 908 769 920 776
C937 787 944 807 944 832 L941 881 L904 883 L904 832
C904 814 900 808 891 808 C881 808 879 824 879 840 L878 880 L846 877 Z''')

fire=g(art,'word-fire','05 · FIRE — custom outlined letters',True,fill=CREAM,fill_rule='evenodd')
path(fire,'fire-f','''
M385 938 L495 923 L499 964 L441 973 L444 1000 L481 997
L491 1030 L446 1035 L450 1077 L412 1089 Z''')
path(fire,'fire-i','M509 924 L561 927 L555 1077 L514 1089 Z')
path(fire,'fire-r','''
M584 926 C611 923 638 924 661 933 C692 944 711 962 711 987
C711 1012 699 1025 679 1036 L704 1080 L664 1089
L634 1045 L623 1045 L622 1080 L581 1081 Z
M628 969 C646 963 661 972 661 985 C661 1002 646 1008 626 1004 Z''')
path(fire,'fire-e','''
M727 926 L834 922 L827 963 L771 962 L770 985 L815 987
L820 1021 L770 1023 L770 1042 L826 1043 L820 1086 L729 1072 Z''')

caption=g(art,'forest-service-caption','06 · B. C. Forest Service — outlined arc lettering',True,fill=CREAM)
caption.set('aria-label','B. C. Forest Service')
font=TTFont(str(args.caption_font))
glyphset=font.getGlyphSet()
cmap=font.getBestCmap()
upem=font['head'].unitsPerEm
size=44
scale=size/upem
# Same circular baseline, deliberately generous spacing; periods are round dots.
cx,cy,r=616.5,612.5,536
placements=[('B',196.3),('C',188.5),('F',180.75),('o',176.2),
            ('r',172.2),('e',167.9),('s',163.8),('t',160.0),
            ('S',153.7),('e',149.4),('r',145.0),('v',141.2),
            ('i',136.9),('c',134.0),('e',130.3)]
for i,(char,theta) in enumerate(placements):
    glyphname=cmap[ord(char)]
    width_units=font['hmtx'][glyphname][0]
    a=math.radians(theta)
    x=cx+r*math.cos(a)
    y=cy+r*math.sin(a)
    pen=SVGPathPen(glyphset)
    glyphset[glyphname].draw(pen)
    wrapper=g(caption,f'caption-glyph-{i:02d}',f'Caption {i+1}: {char}',transform=f'translate({x:.4f} {y:.4f}) rotate({theta-90:.4f}) scale({scale:.9f} {-scale:.9f}) translate({-width_units/2:.4f} 0)')
    path(wrapper,f'caption-outline-{i:02d}',pen.getCommands())
el(caption,'circle','caption-period-b',cx=97,cy=491,r=3.7)
el(caption,'circle','caption-period-c',cx=85,cy=566,r=3.7)
font.close()

ET.indent(root,space='  ')
args.output.write_bytes(ET.tostring(root,xml_declaration=True,encoding='UTF-8'))
print(args.output)
print('Paths:',len(root.findall('.//{%s}path'%SVG)))
print('Circles:',len(root.findall('.//{%s}circle'%SVG)))
print('Ellipses:',len(root.findall('.//{%s}ellipse'%SVG)))
