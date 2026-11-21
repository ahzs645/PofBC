#!/usr/bin/env python3
"""Construct the BC Forest Service F.P.19 poster from editable geometry.

The supplied photograph supplies proportions and layout, not vector contours.
No pixel tracing, raster embedding, filters, or generated imagery are used.
Background brush marks are newly authored deterministic vector marks.
"""
from pathlib import Path
import math, random, re, json, sys, copy, argparse
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

HERE=Path(__file__).resolve().parent
OUT=HERE.parent if HERE.name=='source' else HERE.parent/'output'/'BC_Forest_Service_Matches'
REVISION=HERE if HERE.name=='source' else HERE/'revision2'
RESERVE_SOURCE=HERE if HERE.name=='source' else HERE/'revision3'
PAINT_SOURCE=HERE if HERE.name=='source' else HERE/'revision4'
DETAIL_SOURCE=HERE if HERE.name=='source' else HERE/'revision4'
INK='#1d2424'; PAPER='#e7f3f2'; YELLOW='#f6cd08'; GOLD='#f5b80a'; ORANGE='#f24b0b'; RED='#e43710'
NS='http://www.w3.org/2000/svg'; INKSCAPE='http://www.inkscape.org/namespaces/inkscape'
FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
SERIF=Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')
BACKGROUND_FIELDS=[]

def point_in_polygon(x,y,points):
    inside=False
    j=len(points)-1
    for i,(xi,yi) in enumerate(points):
        xj,yj=points[j]
        if ((yi>y)!=(yj>y)) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:
            inside=not inside
        j=i
    return inside

def base_paint_colour(x,y):
    col=YELLOW
    for pts,c in BACKGROUND_FIELDS:
        if point_in_polygon(x,y,pts):col=c
    return col

def blend_hex(fore,back,opacity):
    a=float(opacity)
    f=[int(fore[i:i+2],16) for i in (1,3,5)]
    b=[int(back[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(a*ff+(1-a)*bb):02x}' for ff,bb in zip(f,b))

def path(d,fill=INK,**attrs):
    extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
    return f'<path d="{d}" fill="{fill}" {extra}/>'

def poly(points,fill,**attrs):
    # Precompose brush colours against the authored paint field. This uses only
    # construction geometry, never photograph pixels. Solid vectors keep PDFs
    # compact and eliminate tens of thousands of PDF transparency groups.
    if 'opacity' in attrs and fill.startswith('#'):
        x=sum(p[0] for p in points)/len(points);y=sum(p[1] for p in points)/len(points)
        fill=blend_hex(fill,base_paint_colour(x,y),attrs.pop('opacity'))
    return path('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z',fill,**attrs)

def layer(id,label,content):
    return f'<g id="{id}" inkscape:groupmode="layer" inkscape:label="{label}">\n{content}\n</g>'

def rough_polygon(points,seed,amplitude=3,step=12):
    rng=random.Random(seed); out=[]
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]; dist=math.hypot(dx,dy)
        n=max(1,round(dist/step))
        for i in range(n):
            t=i/n; z=rng.uniform(-amplitude,amplitude)
            out.append((a[0]+dx*t-dy/max(dist,1)*z,a[1]+dy*t+dx/max(dist,1)*z))
    return out

def brush(x,y,w,h,color,seed,alpha=1):
    """An irregular brush swatch, constructed analytically from vertical ribbons."""
    rng=random.Random(seed); out=[]
    bands=max(4,int(w/rng.uniform(.8,1.7)))
    for i in range(bands):
        bx=x+w*i/bands; bw=w/bands*rng.uniform(.85,1.1)
        by=y+rng.uniform(-.25,.30)*h; bh=h*rng.uniform(.30,1.13)
        lean=rng.uniform(-1.4,1.4)
        pts=[(bx,by),(bx+bw*.46,by-rng.uniform(0,4)),(bx+bw,by+rng.uniform(-4,4)),
             (bx+bw+lean,by+bh*.67),(bx+bw+lean*.5,by+bh),(bx+lean*.6,by+bh+rng.uniform(-4,4)),(bx+lean,by+bh*.55)]
        out.append(poly(pts,color,opacity=f'{alpha*rng.uniform(.65,1):.3f}'))
    return ''.join(out)

def background(textured=True):
    global BACKGROUND_FIELDS
    out=[f'<rect width="1000" height="1400" fill="{YELLOW}"/>']
    # Deliberately composed paint fields. They are not photo contours.
    fields=[
      ([(0,0),(78,0),(76,78),(40,80),(0,65)],RED),
      ([(0,107),(35,130),(30,173),(84,196),(100,237),(168,263),(182,324),(183,499),(89,516),(96,561),(60,563),(61,690),(0,701)],ORANGE),
      ([(0,714),(62,734),(76,844),(130,856),(147,984),(92,1010),(104,1098),(190,1116),(205,1227),(0,1224)],ORANGE),
      ([(479,263),(512,285),(502,324),(548,333),(605,336),(612,411),(684,419),(704,486),(701,585),(674,608),(714,670),(717,966),(733,989),(712,1101),(622,1145),(512,1101),(548,1008),(578,947),(584,869),(575,774),(592,695),(535,683),(504,639),(524,581),(500,533),(455,513),(449,465),(478,413),(475,359)],ORANGE),
      ([(0,982),(60,990),(95,976),(136,1017),(181,1004),(215,1028),(248,1003),(279,1037),(317,1027),(350,1014),(386,1039),(414,1061),(449,1028),(478,1064),(514,1031),(553,1055),(641,1091),(742,1077),(756,1238),(807,1278),(1000,1252),(1000,1400),(0,1400)],RED),
      ([(841,1292),(898,1281),(893,1220),(938,1188),(938,1132),(988,1110),(1000,1112),(1000,1400),(839,1400)],ORANGE),
      ([(602,174),(715,177),(779,183),(787,293),(779,336),(736,301),(720,265),(672,241),(627,224)],ORANGE),
      ([(936,0),(979,0),(1000,1263),(946,1262),(952,1128),(967,1004),(952,866),(970,730),(944,633),(963,491),(941,399),(952,281),(934,186)],GOLD),
      ([(186,110),(243,183),(255,282),(239,426),(224,486),(214,623),(183,646),(181,499),(182,324),(168,263),(100,237),(94,193)],GOLD),
      ([(359,163),(422,172),(470,226),(475,359),(451,445),(429,477),(398,455),(390,357),(369,291)],GOLD),
      ([(722,433),(775,457),(787,487),(770,527),(786,587),(762,636),(777,739),(759,815),(776,995),(752,1019),(754,1122),(729,1122),(715,966),(714,670),(704,486)],GOLD),
    ]
    BACKGROUND_FIELDS=fields
    for i,(pts,col) in enumerate(fields):
        pts=[(-20 if x==0 else 1020 if x==1000 else x,-20 if y==0 else 1420 if y==1400 else y) for x,y in pts]
        out.append(poly(rough_polygon(pts,700+i,4.5 if textured else 1.2,7),col))
    if not textured: return ''.join(out)
    marks=[];rng=random.Random(19661967)
    # Yellow dry brush over the left orange and central orange paint masses.
    zones=[(0,65,175,1020,160),(420,180,320,900,210),(0,970,790,300,180),(820,20,180,1230,200),(140,70,330,970,170)]
    for zi,(x,y,w,h,n) in enumerate(zones):
        for j in range(n):
            bx=x+rng.random()*w; by=y+rng.random()*h
            if zi==0: col=rng.choice([YELLOW,GOLD,ORANGE,RED]); aw,ah=rng.uniform(3,28),rng.uniform(3,35)
            elif zi==1: col=rng.choice([YELLOW,GOLD,ORANGE]); aw,ah=rng.uniform(3,32),rng.uniform(3,36)
            elif zi==2: col=rng.choice([YELLOW,GOLD,ORANGE]); aw,ah=rng.uniform(4,34),rng.uniform(3,26)
            elif zi==3: col=rng.choice([GOLD,ORANGE,YELLOW]); aw,ah=rng.uniform(2,20),rng.uniform(5,44)
            else: col=rng.choice([GOLD,ORANGE,YELLOW]);aw,ah=rng.uniform(2,16),rng.uniform(3,28)
            marks.append(brush(bx,by,aw,ah,col,10000+zi*1000+j,rng.uniform(.13,.48)))
    # Recompose coarse paint-break regions near the authored field boundaries.
    # All points are generated from the design geometry, never source-image pixels.
    for fi,(pts,col) in enumerate(fields[:7]):
        for a,b in zip(pts,pts[1:]+pts[:1]):
            length=math.dist(a,b)
            for j in range(max(1,int(length/6))):
                t=rng.random();bx=a[0]+(b[0]-a[0])*t+rng.gauss(0,9);by=a[1]+(b[1]-a[1])*t+rng.gauss(0,8)
                if bx<3 or bx>997 or by<65 or by>1325:continue
                marks.append(brush(bx,by,rng.uniform(2,20),rng.uniform(3,25),rng.choice([YELLOW,GOLD,col]),40000+fi*1000+j,rng.uniform(.24,.85)))
    # Striated roller edges and short, dry breaks make the paint read as paint.
    for j in range(5000):
        bx=rng.uniform(0,1000);by=rng.uniform(60,1322)
        col=rng.choice([GOLD,YELLOW,ORANGE]); ww=rng.uniform(.35,2.3); hh=rng.uniform(1,11)
        marks.append(poly([(bx,by),(bx+ww,by+.4),(bx+ww+.7,by+hh),(bx+.2,by+hh+.3)],col,opacity=f'{rng.uniform(.10,.42):.3f}'))
    out.append('<g id="reconstructed-brush-marks">'+''.join(marks)+'</g>')
    return ''.join(out)

def halos():
    shapes=[
      [(226,105),(239,82),(263,67),(306,77),(331,80),(373,84),(400,74),(424,65),(448,73),(472,47),(502,59),(531,83),(550,96),(572,75),(592,80),(614,90),(640,83),(665,91),(687,81),(713,89),(736,86),(760,80),(791,82),(810,76),(837,87),(862,88),(891,96),(889,127),(879,172),(863,204),(836,217),(791,190),(784,161),(724,158),(675,157),(641,151),(600,164),(552,153),(504,167),(456,164),(411,160),(391,158),(365,162),(350,157),(316,177),(292,175),(264,165),(244,146)],
      [(458,56),(483,47),(511,70),(548,104),(575,141),(616,170),(634,202),(662,225),(690,259),(718,284),(748,315),(771,345),(798,369),(828,394),(855,412),(879,432),(893,458),(902,479),(889,503),(861,517),(836,509),(813,491),(791,462),(775,433),(748,412),(722,382),(690,352),(672,327),(640,302),(617,278),(585,248),(563,226),(542,201),(517,178),(493,153),(472,132),(447,102),(437,84)],
      [(794,164),(832,162),(853,180),(852,245),(860,291),(853,352),(862,405),(864,451),(856,507),(861,561),(856,607),(863,647),(854,682),(851,744),(861,824),(852,878),(861,937),(855,986),(860,1033),(851,1101),(853,1162),(847,1231),(783,1240),(780,1206),(774,1159),(775,1098),(773,1066),(779,1013),(771,964),(777,922),(767,868),(772,807),(768,763),(774,721),(763,692),(761,662),(769,625),(765,599),(785,596),(780,552),(781,506),(772,473),(783,445),(780,411),(785,361),(783,301),(786,256)],
      [(310,155),(354,157),(360,191),(354,240),(359,287),(356,326),(367,367),(367,428),(371,482),(363,515),(318,513),(319,465),(324,426),(328,388),(330,354),(319,321),(316,269),(311,218)],
      [(293,484),(316,479),(341,481),(366,487),(373,518),(369,550),(372,581),(397,608),(463,641),(478,655),(455,695),(408,667),(371,647),(369,705),(369,768),(404,797),(456,829),(489,831),(517,844),(525,868),(517,894),(503,902),(480,897),(454,884),(420,861),(385,844),(353,821),(326,815),(306,854),(285,911),(241,887),(262,851),(284,813),(306,777),(306,746),(306,706),(300,653),(266,674),(236,694),(211,713),(184,708),(163,691),(159,670),(175,649),(202,635),(212,619),(243,609),(279,590),(299,568),(307,545),(297,526)],
    ]
    return ''.join(poly(rough_polygon(p,900+i,2,10),PAPER) for i,p in enumerate(shapes))

def shaft(points,id):
    return poly(points,PAPER,stroke=INK,stroke_width='6.4',stroke_linejoin='miter',id=id)

def figures():
    o=[]
    o.append(shaft([(347,112),(810,115),(811,140),(347,138)],'upper-beam-shaft'))
    o.append(path('M350 112 C325 108 304 94 281 94 C266 94 256 106 256 122 C256 140 268 149 282 150 C307 154 331 140 350 138 Z',id='upper-beam-match-head'))
    o.append(path('M280 98 C267 98 259 110 259 123 C259 138 267 145 280 147 Z',PAPER,id='upper-beam-match-tip'))
    o.append(shaft([(801,178),(824,178),(824,644),(798,644)],'upper-post-shaft'))
    o.append(path('M801 189 C790 171 782 149 784 133 C785 119 797 108 813 107 C827 106 838 118 842 133 C848 150 831 182 827 190 Z',id='upper-post-head'))
    o.append(path('M789 128 C793 116 803 110 813 110 C824 111 833 117 838 129 Z',PAPER,id='upper-post-tip'))
    o.append(shaft([(797,699),(823,699),(825,1208),(798.5,1208)],'lower-post-shaft'))
    o.append(path('M796 714 C788 696 779 675 781 656 C782 641 794 631 810 631 C825 632 836 642 839 656 C842 674 828 704 824 715 Z',id='lower-post-head'))
    o.append(path('M786 653 C788 642 798 635 809 634 C821 635 832 643 835 654 Z',PAPER,id='lower-post-tip'))
    o.append(shaft([(456,82),(476,64),(836,422),(816,441)],'diagonal-brace-shaft'))
    o.append(path('M819 416 C834 419 850 430 869 443 C885 456 889 475 876 488 C863 502 845 494 831 482 C820 468 812 449 804 437 Z',id='diagonal-brace-head'))
    o.append(path('M874 450 L840 484 C851 493 864 495 875 485 C884 476 885 462 874 450 Z',PAPER,id='diagonal-brace-tip'))
    # The child is assembled from separate match components, in layer order.
    o.append(shaft([(324,597),(216,652),(227,673),(324,623)],'child-left-arm-shaft'))
    o.append(shaft([(345,591),(456,653),(444,672),(344,620)],'child-right-arm-shaft'))
    o.append(path('M224 647 C211 646 195 647 184 656 C174 665 177 684 187 692 C202 703 221 691 237 677 Z',id='child-left-hand-head'))
    o.append(path('M185 660 L207 692 C195 698 184 690 181 680 C178 672 180 666 185 660 Z',PAPER,id='child-left-hand-tip'))
    o.append(shaft([(345,775),(474,847),(462,866),(338,794)],'child-right-leg-shaft'))
    o.append(path('M464 841 C478 840 492 844 505 853 C516 861 518 875 507 887 C500 898 488 899 476 890 C465 883 457 874 451 866 Z',id='child-right-foot-head'))
    o.append(path('M499 851 L480 888 C491 896 500 894 507 884 C515 873 513 861 499 851 Z',PAPER,id='child-right-foot-tip'))
    o.append(path('M324.5 548 L346 548 L345.5 776 L337 792 L278 891 L260.5 880 L325 775 Z',PAPER,stroke=INK,stroke_width='6.4',stroke_linejoin='miter',id='child-body-left-leg'))
    o.append(path('M322 549 C317 537 309 518 311 504 C312 490 320 487 333 487 C346 487 357 491 359 505 C360 523 351 539 347 550 Z',id='child-head'))
    o.append(path('M315 511 C313 500 318 490 333 490 C348 490 356 496 356 511 Z',PAPER,id='child-head-tip'))
    # Sparse, manually reconstructed gaps between the wrapped tie strands.
    # These make the ties read as overlapping cord, not a generic triangular bow.
    o.append('<g id="reconstructed-tie-gaps">'+
        path('M345.2 116.5 C344.5 122 344.7 128 343.4 134.4 Q345.2 135.3 346.8 133.5 C348.2 127.6 347.9 121.2 348.3 116.7 Z',PAPER)+
        path('M351.3 116.3 C350.8 120.7 350.1 125.3 350.4 131.1 L352.0 128.7 C353.5 124.9 353.5 121.0 353.5 117.0 Z',PAPER)+
        path('M321 544 C330 546 339 546.5 349 544 L349 558 L344 561 L327 556 L321 556 Z',INK)+
        path('M331 547.6 Q337 548.5 343 547.6 L342.8 550 Q336.2 550.4 330.4 549 Z',PAPER)+
        path('M328.4 551 Q333 553 338 553 L337 555 Q332 554.5 328.7 553.9 Z',PAPER)+'</g>')
    # Fine ties and the suspended thread remain stroked editable vector curves.
    threads=[('M342 140 C341 243 342 368 342 487',1.7),
      ('M349 112 C357 105 366 89 378 76 Q389 77 392 84 L381 90',1.8),
      ('M351 112 C362 103 373 96 381 90',.8),
      ('M348 113 C345 126 345 142 349 157 C343 173 347 184 350 196',1.6),
      ('M354 114 C350 128 353 140 357 150 C353 169 354 181 356 190',1.1),
      ('M355 119 C374 126 370 141 382 144',.85),
      ('M352 124 C359 147 376 157 383 153',1.05),
      ('M319.5 545.5 Q326 547 330.4 546.7 M320.5 551 Q324 553 328 553.6',1.45),
      ('M347 549 L367 537 Q370 539 369 546 L349 554',1.4),
      ('M349 554 L362 570 L350 572 Z',1.2),
      ('M346 552 C347 567 354 580 358 587',1.0)]
    o.append('<g id="thread-and-ties" fill="none" stroke="'+INK+'" stroke-linecap="round">'+''.join(path(d,'none',stroke_width=w) for d,w in threads)+'</g>')
    # A small local reconstruction supplies the broken wood shoulder, the
    # irregular split and tapered splinters. The long shafts stay editable.
    junction=external_children(DETAIL_SOURCE/'crack_joint.svg')
    if not junction:raise FileNotFoundError(DETAIL_SOURCE/'crack_joint.svg')
    o.append(junction)
    return ''.join(o)

FONT_CACHE={}
def outline_text(text,x,y,w,h,font=FONT,tracking=0,fill=INK,id='text'):
    """Outline ordinary supporting typography and fit its ink bounds to a box."""
    font=str(font)
    if font not in FONT_CACHE: FONT_CACHE[font]=TTFont(font)
    ft=FONT_CACHE[font];gs=ft.getGlyphSet(); cmap=ft.getBestCmap(); parts=[];cur=0;bounds=[]
    for ch in text:
        name=cmap.get(ord(ch),'.notdef');g=gs[name];p=SVGPathPen(gs);g.draw(p)
        bp=BoundsPen(gs);g.draw(bp)
        if bp.bounds:
            a,b,c,d=bp.bounds;bounds.append((cur+a,b,cur+c,d));parts.append(f'<path transform="translate({cur} 0)" d="{p.getCommands()}"/>')
        cur+=ft['hmtx'][name][0]+tracking
    a=min(t[0] for t in bounds);b=min(t[1] for t in bounds);c=max(t[2] for t in bounds);d=max(t[3] for t in bounds)
    sx=w/(c-a);sy=h/(d-b)
    return f'<g id="{id}" aria-label="{text}" fill="{fill}" transform="matrix({sx:.8f} 0 0 {-sy:.8f} {x-a*sx:.6f} {y+d*sy:.6f})">'+''.join(parts)+'</g>'

def rounded_rect(x,y,w,h,r=2):
    return f'M{x+r},{y} H{x+w-r} Q{x+w},{y} {x+w},{y+r} V{y+h-r} Q{x+w},{y+h} {x+w-r},{y+h} H{x+r} Q{x},{y+h} {x},{y+h-r} V{y+r} Q{x},{y} {x+r},{y} Z'

def footer():
    # A compact, square sans alphabet with open counters; each master is geometric.
    # These are reconstruction glyphs, not an asserted historical font identity.
    rr=rounded_rect
    glyph={
      'I':('M0 0 H5 V24 H0 Z',5),
      'L':('M0 0 H5 V19 H17 V24 H0 Z',17),
      'T':('M0 0 H19 V5 H12 V24 H7 V5 H0 Z',19),
      'H':('M0 0 H5 V9 H13 V0 H18 V24 H13 V14 H5 V24 H0 Z',18),
      'O':(rr(0,0,19,24,3)+rr(5,5,9,14,1),19),
      'C':('M19 0 V5 H6 Q5 5 5 6 V18 Q5 19 6 19 H19 V24 H4 Q0 24 0 20 V4 Q0 0 4 0 Z',19),
      'U':('M0 0 H5 V18 Q5 19 6 19 H12 Q13 19 13 18 V0 H18 V20 Q18 24 14 24 H4 Q0 24 0 20 Z',18),
      'M':('M0 24 V0 H6 L12 10 L18 0 H24 V24 H19 V8 L12 18 L5 8 V24 Z',24),
      'A':('M0 24 L7 0 H14 L21 24 H16 L14.5 18 H6.5 L5 24 Z M8 13 H13 L10.5 4 Z',21),
      'B':(rr(0,0,19,24,3)+'M5 5 H12 Q14 5 14 7 V8 Q14 10 12 10 H5 Z M5 14 H12 Q14 14 14 16 V17 Q14 19 12 19 H5 Z',19),
      'R':('M0 24 V0 H14 Q19 0 19 5 V10 Q19 14 14 14 L21 24 H15 L9 14 H5 V24 Z M5 5 V10 H12 Q14 10 14 8 V7 Q14 5 12 5 Z',21),
      'S':('M19 0 V5 H6 Q5 5 5 6 V8 Q5 9 6 9 H15 Q19 9 19 13 V20 Q19 24 15 24 H0 V19 H13 Q14 19 14 18 V15 Q14 14 13 14 H4 Q0 14 0 10 V4 Q0 0 4 0 Z',19),
      'E':('M0 0 H19 V5 H5 V9 H16 V14 H5 V19 H19 V24 H0 Z',19),
      'F':('M0 0 H19 V5 H5 V10 H16 V15 H5 V24 H0 Z',19),
      'V':('M0 0 H5 L10.5 18 L16 0 H21 L14 24 H7 Z',21),
    }
    words=[('BRITISH',56,248),('COLUMBIA',284,507),('FOREST',545,715),('SERVICE',754,933)]
    o=['<g id="footer-custom-lettering" fill="'+PAPER+'" fill-rule="evenodd" aria-label="BRITISH COLUMBIA FOREST SERVICE">']
    for word,x0,x1 in words:
        track=11; raw=sum(glyph[ch][1] for ch in word)+track*(len(word)-1);sx=(x1-x0)/raw;cx=0
        o.append(f'<g id="footer-{word.lower()}" transform="translate({x0} 1335) scale({sx:.6f} 1)">')
        for i,ch in enumerate(word):
            d,w=glyph[ch];o.append(path(d,PAPER,transform=f'translate({cx} 0)',id=f'footer-{word.lower()}-{i}-{ch}'));cx+=w+track
        o.append('</g>')
    o.append('</g>');return ''.join(o)

def centennial():
    out=['<g id="centennial-mark" transform="translate(52 11) scale(.19)">']
    out.append(path('M0 0 H100 V255 H0 Z M5 5 V250 H95 V5 Z',INK,fill_rule='evenodd'))
    out.append('<circle cx="50" cy="48" r="39" fill="none" stroke="'+INK+'" stroke-width="3.4"/>')
    # Triangular construction of the leaf, following the clearer 1966 meter mark.
    leaf='M50 14 L39 33 H18 L29 52 L18 72 H43 V84 Q50 91 57 84 V72 H82 L71 52 L82 33 H61 Z M39 33 H61 M29 52 H71 M39 33 L50 52 L61 33 M29 52 L39 72 M50 52 L39 72 M50 52 L61 72 M61 33 L71 52'
    out.append(path(leaf,'none',stroke=INK,stroke_width='2.8',stroke_linejoin='miter'))
    # Tall 100 numeral, rebuilt from three simple contours.
    out.append(path('M11 111 L24 100 H32 V176 H18 V123 L11 125 Z'))
    for x in [37,65]:
        out.append(path(rounded_rect(x,100,23,76,9)+rounded_rect(x+8,126,7,28,3),INK,fill_rule='evenodd'))
    # A six-lobed flower in a disc. Unresolved petal details are deliberately omitted.
    flower=['M50 186 A32 32 0 1 1 49.99 186 Z']
    for a in range(6):
        pts=[]
        for px,py in [(-7,-12),(-11,-23),(-5,-27),(0,-30),(5,-27),(11,-23),(7,-12)]:
            an=math.radians(a*60);pts.append((50+px*math.cos(an)-py*math.sin(an),218+px*math.sin(an)+py*math.cos(an)))
        flower.append('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'Z')
    flower.append('M50 208 L58.66 213 L58.66 223 L50 228 L41.34 223 L41.34 213 Z')
    out.append(path(' '.join(flower),INK,fill_rule='evenodd'))
    out.append('</g>')
    out.append(outline_text('1966',77,33,20,12,id='centennial-year-1966'))
    out.append(outline_text('1967',77,48,20,12,id='centennial-year-1967'))
    out.append(outline_text('CENTENARY OF THE UNION OF THE COLONIES OF VANCOUVER ISLAND AND BRITISH COLUMBIA UNDER THE NAME BRITISH COLUMBIA',104,37,468,5.0,tracking=250,id='centennial-1966-caption'))
    out.append(outline_text('CENTENARY OF THE CONFEDERATION OF CANADA',104,52,177,5.0,tracking=250,id='centennial-1967-caption'))
    return ''.join(out)

def small_marks():
    # Signature is a readable reconstruction of the photographed mark, not authentication.
    d='M5 0 L4 7 Q3 10 0 8 M8 9 L8.3 8.5 M16 0 L15 7 Q14 10 11 8 M19 9 L19.3 8.5 M24 9 L30 0 L33 9 M27 6 L32 6 M37 9 L39 0 L45 9 L47 0 M50 9 L52 0 Q61 -1 60 4 Q60 10 50 9 M64 9 L66 0 Q74 -1 73 3 Q72 5 65 5 M69 5 L74 9 M78 0 L87 0 M78 0 L76 9 L85 9 M77 4.5 L84 4.5'
    signature='<g id="signature-reading-unconfirmed" aria-label="Signature appears to read J.J. ANDRE; attribution unconfirmed" transform="translate(889 1380) scale(.92 1) skewX(-12)">'+path(d,'none',stroke='#ef853c',stroke_width='.85',stroke_linecap='round',stroke_linejoin='round',opacity='.75')+'</g>'
    return outline_text('F. P. 19',20,1379,61,11,font=SERIF,tracking=80,id='publication-code')+signature

def external_children(file):
    if not Path(file).exists():return ''
    t=Path(file).read_text()
    t=re.sub(r'^.*?<svg\b[^>]*>','',t,count=1,flags=re.S)
    t=re.sub(r'</svg>\s*$','',t,flags=re.S)
    t=re.sub(r'<(?:title|desc)>.*?</(?:title|desc)>','',t,flags=re.S)
    return t

def svg_doc(content,title,desc,width=1000,height=1400):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}" height="{height}" viewBox="0 0 1000 1400" version="1.1">
<title>{title}</title><desc>{desc}</desc>
<defs><clipPath id="artboard-clip"><rect width="1000" height="1400"/></clipPath></defs>
<g clip-path="url(#artboard-clip)">{content}</g></svg>'''

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    from headline import headline_group
    headline=headline_group()
    emblem=external_children(REVISION/'emblem_v2.svg')
    reserves=external_children(RESERVE_SOURCE/'reserves_v3.svg').replace('#e6f1ed',PAPER)
    if not reserves:raise FileNotFoundError(RESERVE_SOURCE/'reserves_v3.svg')
    if not emblem:emblem=external_children(HERE/'emblem.svg')
    residue=external_children(RESERVE_SOURCE/'edge_residue.svg')
    clipped_residue=''
    if residue:
        reserve_root=ET.fromstring('<svg xmlns="'+NS+'">'+reserves+'</svg>')
        clip_shapes=[]
        for e in reserve_root.iter('{'+NS+'}path'):
            attrs={'d':e.get('d','')}
            if e.get('fill-rule'):attrs['clip-rule']=e.get('fill-rule')
            if e.get('transform'):attrs['transform']=e.get('transform')
            clip_shapes.append(ET.tostring(ET.Element('path',attrs),encoding='unicode'))
        clipped_residue='<defs><clipPath id="white-edge-deposit-clip" clipPathUnits="userSpaceOnUse">'+''.join(clip_shapes)+'</clipPath></defs><g id="white-edge-pigment" clip-path="url(#white-edge-deposit-clip)">'+residue+'</g>'
    middle=layer('paper-reserves','02 Refined painted white edges',reserves+clipped_residue)+layer('matchstick-illustration','03 Matchstick illustration and ties',figures())
    if (REVISION/'signature_v2.svg').exists():
        marks=outline_text('F. P. 19',20,1379,61,11,font=SERIF,tracking=80,id='publication-code')+external_children(REVISION/'signature_v2.svg')
    else:marks=small_marks()
    # The source's oval lettering exposes the paint beneath; no flat ochre patch.
    end=layer('headline-lettering','04 Reconstructed headline',headline)+layer('forest-service-oval','05 Refined Forest Service oval seal',emblem)+layer('footer-lettering','06 Reconstructed footer',footer().replace(PAPER,'#edf3e8'))+layer('centennial-caption','07 Centennial mark and captions',centennial())+layer('publication-marks','08 Publication code and signature reading',marks)
    for textured,name in [(True,'BCFS_Matches_Reconstructed'),(False,'BCFS_Matches_Clean')]:
        paint=external_children(PAINT_SOURCE/('paint_v4.svg' if textured else 'paint_v4_clean.svg'))
        if not paint:raise FileNotFoundError('Revised paint component is required')
        content=layer('painted-background','01 Rebuilt paint background',paint)+middle+end
        desc='Revision 4: recomposed vector paint fields and material, plus a manually reconstructed broken match junction and tapered splinters at the child hips. Revision 3 curved white edges are retained; custom headline and fitted seal remain editable. Photo-mask overlays are diagnostic only. No embedded raster image or photo contour tracing. Colours fit the supplied photograph; original print dimensions and inks remain unverified. The 1000 by 1400 artboard is an estimated registration plane.'
        (OUT/(name+'.svg')).write_text(svg_doc(content,'MATCHES ARE NOT FOR CHILDREN!! - BC Forest Service F.P.19 reconstruction',desc))
    (HERE/'structure-ink.svg').write_text(svg_doc(figures()+headline+emblem,'Structural ink analysis','Rasterize only for comparison against the photograph.'))
    (OUT/'BCFS_Matchstick_Illustration.svg').write_text(svg_doc(figures(),'Matchstick illustration - reconstructed geometry','Transparent component; paper-coloured match interiors retained.'))
    (OUT/'BCFS_White_Reserve.svg').write_text(svg_doc(reserves,'White illustration reserve - revision 3','Deliberately constructed curved contours and brush-edge details; editable independently of the painted background.'))
    if clipped_residue:
        (OUT/'BCFS_White_Edge_Residue.svg').write_text(svg_doc(clipped_residue,'Faint paint deposits along the white edge','Six sparse opaque vector paths, clipped to the reconstructed reserve. Place above the pale reserve and below the black drawing.'))
    (OUT/'BCFS_Paint_Background.svg').write_text((PAINT_SOURCE/'paint_v4.svg').read_text())
    (OUT/'BCFS_Child_Crack.svg').write_text((DETAIL_SOURCE/'crack_joint.svg').read_text())
    (OUT/'BCFS_Forest_Service_Oval.svg').write_text((REVISION/'emblem_v2_isolated.svg').read_text())
    print('Wrote poster SVGs and component artwork to',OUT)

if __name__=='__main__':main()
