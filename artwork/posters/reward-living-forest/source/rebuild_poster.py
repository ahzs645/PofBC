#!/usr/bin/env python3
"""Rebuild the supplied Forest Service poster as editable SVG paths.
Hand-authored geometry; no automatic image tracing or embedded raster imagery.
Supporting lettering uses Nimbus Sans Bold; REWARD is custom-drawn.
Run from any directory. SVGs are written beside this script's source/ directory.
Set POSTER_FONT to a compatible local bold OTF/TTF to use another font.
"""
from pathlib import Path
from copy import deepcopy
import math, os, json
from lxml import etree as E
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT; OUT.mkdir(parents=True,exist_ok=True)
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
NSMAP={None:SVG,'inkscape':INK}
C={'paper':'#F4F2EB','navy':'#00264F','blue':'#009EDB','lime':'#AFE052',
   'yellow':'#FFCD08','orange':'#FF6722','bark':'#795D4F','branch':'#58829C',
   'mask':'#503A31','muzzle':'#92735E','cream':'#FFD580','white':'#FCFCF7',
   'tree':'#061C16',
   'emblem_badge':'#278F38','emblem_map':'#FFFFFF','emblem_tree':'#00240B'}
N=C['navy']; B=C['blue']; G=C['lime']; Y=C['yellow']; O=C['orange']

def el(tag,parent=None,**attrs):
    e=E.Element('{%s}%s'%(SVG,tag))
    for k,v in attrs.items():
        if v is not None:e.set(k.replace('_','-'),str(v))
    if parent is not None:parent.append(e)
    return e

def group(parent,id,label=None,layer=False,**attrs):
    g=el('g',parent,id=id,**attrs)
    if label:g.set('{%s}label'%INK,label)
    if layer:g.set('{%s}groupmode'%INK,'layer')
    return g

def path(p,d,fill=N,stroke=None,sw=None,**attrs):
    return el('path',p,d=d,fill=fill,stroke=stroke,stroke_width=sw,
              stroke_linecap='round' if stroke else None,
              stroke_linejoin='round' if stroke else None,**attrs)

def line(p,x1,y1,x2,y2,stroke=N,sw=4,**attrs):
    return el('path',p,d=f'M{x1:g} {y1:g} L{x2:g} {y2:g}',fill='none',stroke=stroke,
              stroke_width=sw,stroke_linecap='round',stroke_linejoin='round',**attrs)

def ellipse(p,cx,cy,rx,ry,fill,stroke=None,sw=None):
    return el('ellipse',p,cx=cx,cy=cy,rx=rx,ry=ry,fill=fill,stroke=stroke,stroke_width=sw)

def clip(defs,id,d):
    cp=el('clipPath',defs,id=id,clipPathUnits='userSpaceOnUse');path(cp,d,'#FFFFFF');return id

def new_svg(viewbox='80 67 930 1308',width='297mm',height='417.716129mm',title='REWARD — A Living Forest'):
    s=E.Element('{%s}svg'%SVG,nsmap=NSMAP,version='1.1',width=width,height=height,viewBox=viewbox)
    el('title',s).text=title
    el('desc',s).text=('Clean vector reconstruction of the supplied British Columbia Forest Service '
        'campfire poster. Manually authored Bézier artwork and custom headline lettering; '
        'supporting sans-serif lettering has been fitted and outlined. Not an original agency master. '
        'No raster image, automatic contour trace, or scan texture is included.')
    s.set('shape-rendering','geometricPrecision')
    return s

def title_letters(p):
    g=group(p,'reward-title','REWARD — custom drawn letters',True)
    r=('M163 138 C148 137 139 142 139 151 C139 158 149 159 152 165 '
       'C156 172 155 185 155 199 L155 235 C155 246 151 249 146 252 '
       'C141 255 140 262 145 267 C153 274 180 274 196 271 '
       'C205 270 210 266 210 260 C210 254 203 253 201 249 '
       'C197 243 196 230 196 217 C200 214 205 217 209 224 '
       'C214 233 214 248 221 260 C227 270 238 273 251 272 '
       'C265 272 275 268 275 261 C275 255 270 253 266 250 '
       'C261 245 262 232 257 220 C254 211 248 205 240 202 '
       'C252 195 259 185 259 172 C259 149 241 138 220 138 '
       'C199 137 181 141 163 138 Z '
       'M196 164 C203 162 211 167 212 179 C213 190 205 195 196 194 Z')
    path(g,r,N,fill_rule='evenodd',id='letter-R-1',transform='translate(139 0) scale(.979 1) translate(-139 0)')
    e=('M294 138 C283 138 276 142 276 150 C276 157 284 159 288 165 '
       'C292 173 291 190 291 207 L291 232 C291 245 289 249 282 253 '
       'C277 256 276 262 280 267 C283 271 292 271 304 270 '
       'L365 270 C374 270 378 274 382 269 C389 259 394 242 394 235 '
       'C394 226 389 221 383 223 C375 224 374 235 365 241 '
       'C358 247 348 248 340 247 C334 247 332 244 332 237 L332 218 '
       'C332 213 336 211 340 215 C346 220 345 232 351 234 '
       'C360 238 366 224 366 204 C366 184 364 173 357 172 '
       'C348 171 348 180 345 188 C342 196 339 196 332 194 '
       'L332 169 C332 160 336 160 345 160 C357 159 362 162 368 171 '
       'C374 180 379 183 384 179 C391 174 389 157 385 145 '
       'C382 134 377 130 371 133 C365 137 363 138 354 138 Z')
    path(g,e,N,id='letter-E')
    w=('M424 136 C404 136 391 141 391 151 C391 157 397 160 402 163 '
       'C409 167 411 176 415 187 L444 260 C448 271 451 274 458 273 '
       'C466 273 469 267 473 258 L488 214 L509 261 '
       'C513 271 518 274 524 272 C531 271 534 264 538 255 '
       'L574 174 C578 165 581 162 587 160 C593 158 596 153 594 147 '
       'C591 138 581 135 564 135 C546 135 537 139 535 146 '
       'C532 155 539 158 542 162 C545 167 541 177 537 187 L533 199 '
       'C527 189 522 177 518 168 C515 163 516 160 522 156 '
       'C528 152 528 147 524 142 C518 137 507 135 494 135 '
       'C477 135 466 139 464 146 C461 154 467 158 472 162 '
       'C478 167 475 176 472 184 L467 196 C461 185 457 174 454 166 '
       'C451 160 454 159 458 154 C463 148 458 142 452 139 '
       'C445 137 433 136 424 136 Z')
    path(g,w,N,id='letter-W')
    a=('M600 157 C602 139 607 132 618 132 C628 132 635 141 642 156 '
       'L678 232 C683 243 685 245 690 248 C698 252 698 259 693 264 '
       'C687 269 675 270 660 269 C641 270 630 267 629 261 '
       'C628 255 633 252 635 248 C638 241 633 237 620 237 '
       'L604 237 C595 237 593 240 595 246 C596 250 603 250 605 256 '
       'C610 265 597 269 581 270 C567 270 557 267 557 260 '
       'C556 252 564 249 570 244 C576 238 579 228 584 216 '
       'L596 179 C599 170 599 165 600 157 Z '
       'M605 211 C607 204 610 195 614 188 C615 185 617 185 619 188 '
       'C623 195 626 203 628 209 C629 212 627 213 624 213 L609 213 '
       'C606 213 604 213 605 211 Z')
    path(g,a,N,fill_rule='evenodd',id='letter-A',transform='translate(557 0) scale(.95 1) translate(-557 0)')
    r2=('M714 134 C700 133 692 139 692 147 C692 154 700 157 704 162 '
        'C708 168 707 181 707 195 L707 231 C707 243 704 247 698 250 '
        'C691 254 693 262 699 266 C707 272 735 271 748 267 '
        'C759 264 760 257 754 252 C748 248 747 246 746 237 '
        'L746 214 C751 211 757 215 760 222 C765 233 765 249 772 259 '
        'C778 268 788 271 801 269 C814 268 822 264 822 257 '
        'C822 252 817 250 814 247 C810 243 811 230 806 218 '
        'C802 208 797 202 789 199 C800 192 807 184 807 170 '
        'C807 149 793 134 771 133 C750 132 733 136 714 134 Z '
        'M746 159 C753 157 761 161 763 174 C764 186 757 191 747 190 '
        'C746 181 746 168 746 159 Z')
    path(g,r2,N,fill_rule='evenodd',id='letter-R-2')
    d=('M846 133 C831 133 824 137 824 145 C824 152 832 155 836 160 '
       'C840 165 839 177 839 194 L839 229 C839 239 837 243 831 247 '
       'C824 251 823 258 828 262 C833 267 842 266 855 266 '
       'L893 266 C934 266 954 242 954 198 C954 154 931 132 892 132 '
       'C875 132 860 134 846 133 Z '
       'M880 160 C881 153 891 155 897 160 C907 167 910 182 910 198 '
       'C910 215 907 230 899 237 C893 242 882 243 880 237 '
       'C879 224 880 175 880 160 Z')
    path(g,d,N,fill_rule='evenodd',id='letter-D')
    return g

FONT_PATH=os.environ.get('POSTER_FONT','/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf')
if not Path(FONT_PATH).is_file():
    raise SystemExit('Font not found. Set POSTER_FONT to your local NimbusSans-Bold.otf or compatible bold font.')
FONT=TTFont(FONT_PATH); GS=FONT.getGlyphSet(); CMAP=FONT.getBestCmap(); HM=FONT['hmtx'].metrics
KERN={}
if 'kern' in FONT:
    for st in FONT['kern'].kernTables:KERN.update(st.kernTable)

def outlined_text(parent,text,x,y,w,h,id):
    g=group(parent,id,text,False,fill=N,aria_label=text)
    positions=[];xp=0;last=None
    for ch in text:
        gn=CMAP.get(ord(ch),'space')
        if last:xp+=KERN.get((last,gn),0)
        positions.append((gn,xp,ch));xp+=HM[gn][0];last=gn
    bounds=[]
    for gn,xx,ch in positions:
        pen=BoundsPen(GS);GS[gn].draw(pen)
        if pen.bounds:
            x0,y0,x1,y1=pen.bounds;bounds.append((x0+xx,y0,x1+xx,y1))
    xmin=min(v[0] for v in bounds);ymin=min(v[1] for v in bounds)
    xmax=max(v[2] for v in bounds);ymax=max(v[3] for v in bounds)
    sx=w/(xmax-xmin);sy=h/(ymax-ymin)
    g.set('transform',f'matrix({sx:.8f} 0 0 {-sy:.8f} {x-xmin*sx:.5f} {y+ymax*sy:.5f})')
    for i,(gn,xx,ch) in enumerate(positions):
        if ch==' ':continue
        pen=SVGPathPen(GS);GS[gn].draw(pen)
        path(g,pen.getCommands(),N,N,18,transform=f'translate({xx} 0)',id=f'{id}-glyph-{i+1}')
    g.set('data-original-text',text);g.set('data-fit-box',f'{x},{y},{w},{h}')
    return g

def lettering(parent):
    t=group(parent,'supporting-lettering','Supporting lettering — outlined',True)
    star=group(t,'asterisk','Six-point asterisk')
    for ang in [0,60,120]:
        a=math.radians(ang);dx=17*math.sin(a);dy=17*math.cos(a)
        line(star,215-dx,337-dy,215+dx,337+dy,N,7.8)
    outlined_text(t,'A LIVING FOREST.',249,300,626,71,'living-forest')
    outlined_text(t,'OBSERVE CAMPFIRE',152,1042,786,72,'observe-campfire')
    outlined_text(t,'REGULATIONS',274,1138,537,69,'regulations')
    outlined_text(t,'BRITISH COLUMBIA FOREST SERVICE',141,1270,650,36,'forest-service-name')
    return t

def add_blue_fronds(parent,defs):
    g=group(parent,'blue-forest-boughs','Blue forest boughs',True)
    top=('M622 445 C650 424 685 434 716 446 C754 460 789 482 812 504 '
         'C830 519 835 535 828 550 C819 570 790 576 758 571 '
         'C711 568 664 547 641 522 C624 504 615 471 622 445 Z')
    path(g,top,B,id='top-right-blue-blade')
    cp=clip(defs,'clip-top-right-blade',top)
    v=group(g,'top-right-needles',clip_path=f'url(#{cp})')
    up=[(637,461,656,447),(650,473,676,447),(665,482,699,451),(681,490,721,460),
        (698,499,741,467),(714,506,757,475),(732,513,774,485),(749,520,790,495),
        (766,526,803,509),(783,531,817,520),(799,536,824,531),(812,540,826,545)]
    down=[(637,488,657,526),(649,496,676,541),(664,503,692,552),(679,511,711,563),
          (695,517,733,570),(713,524,754,575),(731,531,776,576),(750,536,796,574),
          (769,541,815,564),(790,543,828,554)]
    for pts in up+down:line(v,*pts,N,3.9)
    path(g,'M619 445 C655 486 735 516 814 535 L820 543 C751 544 670 520 623 486 Z',N,id='top-right-branch-outline')
    path(g,'M626 460 C663 493 743 522 809 535 C745 531 674 510 627 478 Z',C['branch'],id='top-right-branch-wood')
    mid=('M622 590 C651 574 689 584 721 599 C762 619 799 650 818 677 '
         'C832 696 835 711 826 722 C812 740 780 737 749 732 '
         'C701 725 654 705 635 678 C622 660 616 615 622 590 Z')
    path(g,mid,B,id='middle-right-blue-blade')
    cp=clip(defs,'clip-middle-right-blade',mid);v=group(g,'middle-right-needles',clip_path=f'url(#{cp})')
    up=[(635,604,658,591),(648,615,679,595),(663,627,701,606),(680,639,724,616),
        (697,649,747,629),(715,660,770,642),(733,670,789,655),(752,681,809,673),
        (771,691,820,691),(790,700,824,705),(810,707,827,718)]
    down=[(636,634,645,684),(647,643,660,700),(660,652,678,711),(675,661,696,720),
          (690,671,712,727),(707,680,735,733),(724,690,756,737),(743,698,777,741),
          (762,705,797,735),(783,711,817,729)]
    for pts in up+down:line(v,*pts,N,4)
    path(g,'M619 584 C658 625 748 679 814 702 L820 713 C747 704 660 661 621 626 Z',N,id='middle-right-branch-outline')
    path(g,'M627 602 C674 644 752 688 809 702 C748 687 672 651 626 617 Z',C['branch'],id='middle-right-branch-wood')
    left=('M522 598 C492 588 449 615 410 644 C361 678 314 718 289 752 '
          'C273 773 268 791 275 805 C283 825 314 826 350 816 '
          'C406 800 463 769 499 730 C521 706 532 659 531 626 Z')
    path(g,left,B,id='middle-left-blue-blade')
    cp=clip(defs,'clip-middle-left-blade',left);v=group(g,'middle-left-needles',clip_path=f'url(#{cp})')
    up=[(509,637,485,606),(498,652,466,617),(484,666,449,627),(469,679,429,640),
        (454,691,411,651),(438,703,394,663),(422,715,378,674),(406,727,361,687),
        (389,739,345,701),(372,751,331,717),(355,762,316,733),(337,774,300,749),
        (320,786,286,766),(303,797,279,785),(289,805,280,814)]
    down=[(510,651,502,725),(495,668,490,750),(479,682,474,766),(463,696,457,779),
          (446,709,439,789),(429,722,419,798),(412,735,400,807),(394,748,380,815),
          (376,760,361,821),(358,772,341,823),(340,783,320,825),(321,795,302,823),
          (304,804,284,823)]
    for pts in up+down:line(v,*pts,N,4)
    path(g,'M519 604 C517 648 410 727 288 798 L284 811 C414 756 503 693 535 652 L537 615 Z',N,id='middle-left-branch-outline')
    path(g,'M520 621 C505 660 404 739 300 795 C411 741 498 682 524 650 Z',C['branch'],id='middle-left-branch-wood')
    for d in ['M494 650 L506 641 L521 655 L510 666 Z','M464 674 L476 666 L489 680 L477 689 Z',
              'M432 698 L443 690 L456 706 L444 714 Z','M398 723 L409 715 L420 732 L409 739 Z']:
        path(g,d,C['bark'],opacity='.55')
    low=('M510 785 C468 777 423 799 379 826 C331 856 281 894 264 926 '
         'C250 950 248 971 263 982 C280 997 318 992 354 984 '
         'C408 972 467 947 500 912 C520 891 529 831 510 785 Z')
    path(g,low,B,id='lower-left-blue-blade')
    cp=clip(defs,'clip-lower-left-blade',low);v=group(g,'lower-left-needles',clip_path=f'url(#{cp})')
    up=[(507,817,490,792),(494,830,473,799),(480,842,455,807),(463,855,438,817),
        (447,868,420,826),(430,880,401,837),(413,891,382,849),(396,903,364,861),
        (377,915,345,875),(359,927,327,889),(340,939,311,905),(320,950,293,922),
        (299,962,274,941),(278,974,264,961)]
    down=[(480,855,490,925),(462,867,472,940),(443,881,453,954),(424,895,433,965),
          (405,908,414,975),(385,922,394,982),(365,935,372,987),(345,948,351,992),
          (324,959,328,995),(302,970,306,995),(282,979,282,995)]
    for pts in up+down:line(v,*pts,N,4)
    path(g,'M510 789 C506 836 405 902 267 970 L262 983 C393 937 492 875 526 841 L527 810 Z',N,id='lower-left-branch-outline')
    path(g,'M511 807 C494 847 404 907 279 969 C399 917 484 865 514 836 Z',C['branch'],id='lower-left-branch-wood')
    return g

def tree_trunk(parent,defs):
    g=group(parent,'tree-trunk','Tree trunk and bark',True)
    trunk=('M520 411 L632 411 L637 416 L637 806 '
           'C637 829 658 851 682 867 L658 900 C611 887 566 863 537 847 '
           'C526 864 510 875 488 881 L461 865 '
           'C497 841 513 821 516 786 L520 680 L520 558 Z')
    path(g,trunk,C['bark'],N,13,id='trunk-silhouette')
    cp=clip(defs,'clip-bark',trunk);b=group(g,'bark-ribbons',clip_path=f'url(#{cp})')
    ds=[
      'M528 415 L534 415 C530 476 535 527 532 579 C535 635 530 692 531 742 C530 786 520 817 509 835 L500 841 C519 811 523 782 523 743 C525 683 522 635 525 579 C529 522 524 468 528 415 Z',
      'M544 413 L551 413 C547 465 550 511 550 554 C547 601 551 640 550 690 C550 743 544 789 535 814 L526 829 C539 799 542 746 543 700 C544 644 541 603 543 554 C545 503 542 457 544 413 Z',
      'M560 414 L569 414 C565 448 565 475 565 503 L563 550 L568 584 L564 638 C565 684 568 731 564 770 C560 801 555 823 554 837 L545 833 C546 814 554 791 556 765 C560 725 557 675 558 638 L561 584 L556 550 C560 502 555 456 560 414 Z',
      'M578 414 L585 414 C579 462 580 492 584 526 L580 582 C579 620 581 659 582 700 C581 747 581 791 574 836 L569 842 C572 800 574 751 575 701 C573 660 575 619 575 582 L578 527 C573 489 574 453 578 414 Z',
      'M591 414 L599 414 L592 454 C596 496 591 541 594 577 C600 613 598 656 597 691 C594 735 599 775 595 826 L589 850 L584 847 C591 817 589 774 589 734 C589 689 595 657 591 617 L587 577 C589 539 587 495 587 454 Z',
      'M607 414 L614 414 C608 459 610 505 606 546 C606 573 610 598 610 627 C606 661 609 686 611 715 C610 763 609 811 616 853 L608 857 C601 812 604 762 604 716 C602 685 602 659 604 627 C604 598 598 573 600 546 C604 501 602 458 607 414 Z',
      'M625 414 L631 414 L628 491 C633 530 627 565 628 606 C631 647 623 690 626 728 C627 775 623 811 631 839 L646 865 L635 861 C617 837 619 806 619 773 L620 727 C618 689 624 647 621 606 C621 565 626 530 622 491 Z',
      'M550 508 C547 532 553 550 556 566 L560 574 L560 591 C553 577 547 561 547 547 Z',
      'M572 467 C570 492 570 514 575 535 L578 556 L580 547 C576 522 578 494 577 472 Z',
      'M585 620 C582 638 581 660 585 680 L590 700 L590 682 C585 660 589 643 589 624 Z',
      'M601 761 C595 789 604 818 611 840 L619 860 L619 849 C610 825 606 796 607 778 Z',
      'M541 789 C536 807 523 821 513 832 L509 844 C526 834 537 820 544 805 Z',
      'M555 812 C549 834 539 844 530 849 L540 854 C550 845 558 832 560 821 Z',
      'M574 827 C576 847 594 865 612 875 L627 880 C601 862 587 847 583 832 Z'
    ]
    for i,d in enumerate(ds):path(b,d,N,id=f'bark-ribbon-{i+1:02d}')
    path(g,'M519 598 C519 626 506 642 493 655 L507 674 C523 656 535 644 536 624 L536 600 Z',N,id='upper-branch-junction')
    path(g,'M520 617 C518 638 508 649 501 657 L508 665 C522 650 528 639 528 623 Z',C['branch'])
    path(g,'M513 789 C510 817 492 836 477 846 L493 864 C518 847 528 829 529 807 Z',N,id='lower-branch-junction')
    path(g,'M515 806 C511 824 497 839 486 847 L494 855 C512 841 519 827 520 813 Z',C['branch'])
    return g

def bird(parent,defs):
    g=group(parent,'bird','Bird — body, plumage, eye, beak and feet',True)
    outer=('M416 437 C441 417 461 408 480 411 C501 410 520 425 531 439 '
           'L556 456 L520 477 C505 489 500 508 493 534 '
           'C490 566 483 600 467 622 C439 661 386 674 336 646 '
           'C321 686 299 726 278 745 C270 753 263 756 256 748 '
           'C247 738 246 721 247 705 C230 718 213 724 205 717 '
           'C192 706 207 680 225 653 C254 609 293 565 325 523 '
           'C357 481 388 452 416 437 Z')
    path(g,outer,N,id='bird-silhouette')
    tails=group(g,'bird-tail-feathers','Tail feather inlays')
    tds=[
      'M311 619 C301 646 287 671 275 691 C270 684 271 673 275 660 C287 645 299 630 311 619 Z',
      'M287 646 C279 666 271 684 270 695 C265 701 260 708 258 715 C252 701 256 681 264 668 Z',
      'M308 651 C301 674 290 696 279 714 C276 705 276 696 280 688 C290 673 298 660 308 651 Z',
      'M293 687 C285 708 276 722 268 730 C264 725 262 720 263 713 C272 708 283 697 293 687 Z',
      'M267 634 C257 649 251 660 248 669 C242 671 240 666 243 659 C250 649 258 641 267 634 Z',
      'M254 660 C248 673 243 683 238 687 C232 687 232 683 235 678 Z',
      'M239 677 C234 689 228 697 222 700 C219 696 221 690 226 685 Z',
      'M226 695 L221 707 L213 709 C214 703 219 698 226 695 Z',
      'M251 685 C247 696 241 703 234 707 L230 705 C233 697 241 690 251 685 Z',
      'M266 665 C262 678 258 688 253 691 L249 687 C253 678 258 671 266 665 Z',
      'M277 625 L269 644 C265 647 262 645 261 642 Z',
      'M263 652 L257 663 L252 664 L253 659 Z',
      'M242 672 L237 678 L232 677 L234 673 Z',
      'M230 687 L225 693 L219 692 L222 688 Z',
      'M278 701 C276 711 271 718 267 722 L264 717 L268 710 Z'
    ]
    for i,d in enumerate(tds):path(tails,d,B,id=f'tail-inlay-{i+1:02d}')
    feet=group(g,'bird-feet','Orange feet')
    path(feet,'M426 646 L437 641 L452 659 L449 666 L443 665 L438 668 Z',O,N,4)
    path(feet,'M450 631 L462 626 L477 645 L473 651 L468 650 L465 654 Z',O,N,4)
    path(g,'M337 628 C368 632 418 614 449 584 C462 571 471 557 479 542 '
           'C478 581 465 613 442 630 C414 652 369 655 337 628 Z',Y,N,7,id='yellow-breast')
    path(g,'M413 445 C433 429 459 419 479 422 C496 422 511 430 516 443 '
           'C521 456 516 477 505 486 C493 497 488 510 482 527 '
           'C482 503 477 485 462 476 C448 468 437 469 425 471 '
           'C412 474 405 467 406 458 C407 452 409 449 413 445 Z',O,N,6,id='orange-head')
    cover=group(g,'bird-shoulder-markings','Lime shoulder markings')
    path(cover,'M389 466 C394 473 399 476 405 479 L380 500 C370 507 366 503 367 495 Z',G,N,4)
    path(cover,'M359 498 C362 505 366 508 373 507 C369 517 360 525 352 526 C344 527 344 524 348 517 Z',G,N,4)
    path(cover,'M340 530 C347 534 351 534 358 531 C353 542 343 550 335 555 C334 547 336 538 340 530 Z',G,N,4)
    path(g,'M318 558 C324 562 334 559 343 554 C337 574 333 594 326 609 '
           'C310 621 292 632 282 635 C280 626 292 598 304 578 Z',Y,N,6,id='yellow-long-covert')
    wing=('M437 479 C457 473 477 485 479 507 C483 537 462 565 437 585 '
          'C410 608 371 625 336 621 C340 591 350 560 367 533 C388 500 414 483 437 479 Z')
    path(g,wing,B,N,8,id='blue-wing')
    feather=group(g,'wing-feather-panels','Wing feather panel contours')
    for d in [
      'M406 491 C400 507 398 523 400 537 C412 540 430 528 441 514',
      'M447 480 C444 491 437 501 438 511 C434 522 437 537 446 541 C457 546 469 538 477 531',
      'M382 515 C380 538 370 558 367 569 C365 579 374 583 382 574 C391 561 398 546 400 537',
      'M399 540 C393 559 386 574 377 587 C386 591 399 584 405 576 C413 561 421 543 423 532',
      'M366 550 C361 568 354 584 356 596 C359 607 366 608 375 593',
      'M377 587 C369 599 365 610 364 620',
      'M405 576 C409 584 404 598 403 604',
      'M405 576 C429 570 458 551 472 536',
      'M438 542 C431 551 423 559 417 567',
      'M350 593 C348 608 352 615 356 621'
    ]:path(feather,d,'none',N,5.3)
    eye=group(g,'bird-eye','Bird eye')
    ellipse(eye,486,454,23.4,25.4,N)
    ellipse(eye,486,453,13.9,14.8,C['white'])
    ellipse(eye,486.7,453.1,8.3,9.1,N)
    path(g,'M520 445 L548 456 L520 455 Z',O,N,4.4,id='upper-beak')
    path(g,'M520 460 L548 457 L520 472 Z',O,N,4.4,id='lower-beak')
    return g

def bear_body(parent):
    g=group(parent,'bear','Bear — head, mask, muzzle and foreleg',True)
    path(g,'M558 819 C594 796 637 795 675 801 C711 791 748 800 764 817 '
           'C788 839 773 877 759 920 L734 984 L655 994 L555 976 L532 890 Z',N,id='bear-underbody')
    path(g,'M588 729 C607 711 638 704 666 707 C675 687 689 684 703 691 '
           'C720 699 723 718 714 735 C735 759 743 788 734 817 '
           'C726 849 704 876 676 885 C650 894 627 886 609 872 '
           'C595 861 584 856 571 855 C551 856 546 837 548 815 L551 775 '
           'C535 764 534 747 542 734 C553 715 574 714 588 729 Z',Y,N,13,id='bear-head')
    mask=group(g,'bear-eye-mask','Brown eye mask')
    path(mask,'M603 754 C598 748 608 744 617 743 C625 742 632 745 637 749 '
              'C644 739 655 737 666 741 C671 742 674 747 679 748 C684 750 685 755 681 759 '
              'C682 779 672 793 659 798 L662 807 C666 814 661 817 655 811 '
              'L641 798 C628 809 610 808 601 798 C589 786 591 766 603 754 Z',C['mask'],id='mask-silhouette')
    ellipse(mask,623,775,17.1,19.9,N)
    ellipse(mask,623,775,12.6,15.1,C['white'])
    ellipse(mask,624,776,8.1,10.1,C['tree'])
    ellipse(mask,657,769,15.8,18.5,N)
    ellipse(mask,657,769,11.9,14.1,C['white'])
    ellipse(mask,657,770,7.9,9.6,C['tree'])
    path(g,'M640 801 C659 791 678 802 691 817 C706 834 705 856 697 870 '
           'C689 886 668 889 650 895 C625 899 608 892 603 872 '
           'C597 851 603 828 615 814 C623 807 631 803 640 801 Z',N,id='muzzle-outline')
    path(g,'M615 825 C626 833 640 837 648 848 C655 859 649 878 640 886 '
           'C628 886 618 878 614 866 C609 852 610 838 615 825 Z',Y,id='muzzle-left-lobe')
    path(g,'M674 809 C686 817 694 832 692 848 C692 860 689 868 682 867 '
           'C671 863 660 854 658 844 C655 833 666 821 674 809 Z',Y,id='muzzle-right-lobe')
    path(g,'M650 883 L658 867 L676 878 C668 882 659 885 650 883 Z',C['cream'],id='mouth-highlight')
    path(g,'M625 810 C634 800 649 798 662 803 L670 809 '
           'C664 820 655 829 651 840 L646 836 C641 827 631 823 625 819 Z',N,id='nose-base')
    path(g,'M645 814 C650 816 652 811 658 812 L666 811 C664 820 658 823 654 824 '
           'L650 834 L647 830 C646 825 642 821 645 814 Z',C['muzzle'],id='nose-warm-plane')
    path(g,'M627 818 C632 814 638 818 643 821 L643 829 L635 826 Z',C['cream'],id='nose-left-highlight')
    path(g,'M645 833 L650 833 L650 843 L646 840 Z',C['cream'],id='nose-tip-highlight')
    path(g,'M652 902 L677 894 L673 919 Z',Y,id='chest-mark')
    path(g,'M669 925 L674 922 L672 934 L668 932 Z',C['muzzle'],id='lower-chest-mark')
    return g

def fmt(p):return f'{p[0]:.2f} {p[1]:.2f}'

def green_panel(parent,points,id):
    d='M'+fmt(points[0])+' '+' '.join('L'+fmt(p) for p in points[1:])+' Z'
    return path(parent,d,G,G,.75,id=id)

def foreground(parent):
    g=group(parent,'foreground-foliage','Foreground lime and navy foliage',True)
    path(g,'M411 958 L551 899 L635 928 L735 919 L804 991 L453 991 Z',N,id='foliage-baseline')
    path(g,'M484 850 L530 865 L560 922 L540 945 L496 914 Z',N,id='foliage-interior-shadow')
    path(g,'M730 991 L804 991 C822 960 830 926 827 893 C824 853 811 805 797 779 '
           'L788 769 L781 811 L773 822 L755 814 L731 884 Z',N,id='right-hand-dark-foliage')
    rg=group(g,'right-upright-fern','Right upright fern')
    path(rg,'M794 840 C807 871 816 899 812 927 C809 952 798 975 790 991 '
            'L748 991 C741 974 742 955 749 934 C758 905 778 871 794 840 Z',N)
    upper=[[(792,849),(796,861),(792,873),(790,865)],
           [(787,869),(793,880),(787,893),(782,880)],
           [(779,886),(787,900),(781,911),(773,898)],
           [(771,904),(782,920),(777,931),(765,916)],
           [(763,922),(776,939),(771,949),(758,934)],
           [(756,941),(769,958),(764,968),(752,952)],
           [(751,960),(762,976),(759,985),(747,970)]]
    lower=[[(798,861),(801,868),(796,879),(793,882)],
           [(802,880),(804,887),(794,900),(788,903)],
           [(806,897),(806,905),(790,921),(785,922)],
           [(806,918),(804,927),(785,941),(780,941)],
           [(802,940),(798,949),(778,962),(773,961)],
           [(793,960),(789,970),(772,980),(766,982)],
           [(784,980),(780,986),(766,990),(762,990)]]
    for i,pts in enumerate(upper+lower):green_panel(rg,pts,f'right-upright-pinna-{i+1:02d}')
    cg=group(g,'middle-rising-fern','Middle rising fern')
    path(cg,'M501 820 C522 837 545 845 562 862 C587 886 612 934 635 992 '
            'L579 992 C553 962 527 938 515 914 C504 890 495 848 501 820 Z',N)
    cr=[[(514,845),(520,850),(522,854),(518,852)],
        [(533,852),(538,857),(542,869),(538,865)],
        [(545,861),(550,867),(554,888),(549,880)],
        [(557,873),(563,880),(565,909),(559,900)],
        [(569,885),(574,892),(575,926),(570,918)],
        [(580,902),(585,910),(587,942),(581,934)],
        [(592,921),(597,929),(598,958),(592,950)],
        [(604,940),(609,948),(606,974),(602,968)],
        [(615,959),(619,968),(615,984),(611,979)],
        [(624,980),(627,988),(625,992),(622,989)]]
    cl=[[(513,854),(521,857),(528,864),(519,861)],
        [(517,869),(536,878),(544,888),(523,878)],
        [(519,885),(545,898),(554,910),(529,898)],
        [(523,903),(556,918),(567,930),(540,917)],
        [(532,922),(568,939),(579,951),(548,936)],
        [(547,942),(580,957),(589,969),(560,951)],
        [(563,961),(591,975),(599,984),(578,975)],
        [(586,983),(603,988),(605,992),(594,990)]]
    for i,pts in enumerate(cr+cl):green_panel(cg,pts,f'middle-pinna-{i+1:02d}')
    mg=group(g,'right-middle-fern','Right middle fern')
    path(mg,'M573 849 C591 852 606 863 619 880 C642 912 657 955 666 992 '
            'L622 992 C605 965 595 939 588 910 C583 888 577 871 573 849 Z',N)
    mr=[[(602,864),(608,871),(612,883),(606,878)],
        [(616,879),(622,886),(623,909),(617,901)],
        [(629,893),(635,903),(635,926),(630,916)],
        [(640,911),(646,921),(643,947),(639,937)],
        [(649,932),(654,943),(649,965),(646,956)],
        [(657,954),(661,966),(656,982),(653,976)],
        [(659,980),(662,987),(660,991),(657,990)]]
    ml=[[(577,862),(584,866),(586,872),(582,869)],
        [(582,875),(597,880),(603,885),(591,883)],
        [(588,890),(610,899),(617,909),(596,902)],
        [(594,908),(623,921),(629,932),(603,920)],
        [(602,930),(635,944),(640,955),(610,942)],
        [(613,951),(645,965),(649,975),(620,963)],
        [(625,972),(650,984),(653,991),(634,984)],
        [(638,987),(651,990),(653,992),(641,992)]]
    for i,pts in enumerate(mr+ml):green_panel(mg,pts,f'right-middle-pinna-{i+1:02d}')
    lg=group(g,'left-sweeping-fern','Large sweeping foreground fern')
    path(lg,'M374 807 C377 829 389 844 411 858 C442 877 475 896 505 918 '
            'C540 943 570 968 591 994 L448 994 C422 975 399 954 385 932 '
            'C371 909 365 881 369 852 C371 835 371 819 374 807 Z',N)
    lr=[[(393,845),(397,850),(400,860),(397,855)],
        [(404,852),(409,857),(415,884),(410,878)],
        [(416,861),(421,866),(430,898),(422,889)],
        [(430,870),(437,875),(447,913),(438,905)],
        [(444,879),(451,884),(461,925),(454,917)],
        [(459,889),(466,894),(476,937),(468,929)],
        [(473,899),(480,904),(490,947),(482,939)],
        [(488,909),(495,914),(505,958),(497,950)],
        [(503,920),(510,925),(520,968),(512,960)],
        [(519,931),(526,937),(532,979),(525,971)],
        [(535,943),(542,950),(547,988),(540,981)],
        [(550,956),(555,962),(560,991),(553,987)],
        [(563,969),(568,975),(572,992),(566,990)],
        [(576,982),(580,986),(583,992),(578,992)]]
    ll=[[(384,852),(386,867),(384,872),(399,879),(391,866)],
        [(386,883),(404,888),(415,898),(390,892)],
        [(392,901),(412,905),(424,911),(395,907)],
        [(398,914),(424,918),(440,927),(410,924),(404,922)],
        [(409,933),(433,937),(450,936),(461,942),(443,946),(422,942)],
        [(420,948),(442,949),(459,946),(468,952),(450,956),(431,956)],
        [(432,963),(453,963),(473,958),(484,965),(463,970),(444,969)],
        [(450,974),(470,975),(488,968),(497,974),(476,978),(459,979)],
        [(454,982),(479,981),(502,976),(511,982),(490,987),(470,985)],
        [(468,987),(492,990),(521,983),(532,990),(516,992),(480,992)]]
    for i,pts in enumerate(lr+ll):green_panel(lg,pts,f'large-leaf-pinna-{i+1:02d}')
    return g

def foreleg(parent):
    g=group(parent,'bear-foreleg','Bear foreleg and paw',True)
    path(g,'M739 810 C757 814 775 829 776 847 C778 865 761 906 750 935 '
           'L735 964 C746 978 752 992 744 1000 C737 1009 727 1001 721 990 '
           'C720 1004 712 1009 702 1005 C694 1003 691 997 689 991 '
           'C684 1000 680 1004 673 998 C665 992 666 978 668 958 '
           'L681 882 C710 868 729 841 739 810 Z',Y,N,12,id='yellow-foreleg-paw')
    return g

def emblem(parent):
    # BC evergreen emblem, shared with forest-sign-rebuild (source: bc-evergreen-vector/bc-evergreen-remade.svg).
    # Source artwork spans 882 x 886 units centred on (624, 616); fitted into the 112 x 121 corner slot.
    g=group(parent,'forest-service-emblem','Forest Service corner emblem',True)
    art=group(g,'emblem-artwork','BC evergreen emblem (from bc-evergreen-vector)',
              transform='translate(887.000 1277.500) scale(0.126984) translate(-624 -616)')
    badge=group(art,'emblem-badge-layer','01 · Curved badge')
    path(badge,'M 264,213 C 383,186 504,173 624,173 C 744,173 865,186 984,213 C 1006,218 1016,230 1022,255 C 1051,378 1065,497 1065,616 C 1065,735 1051,854 1022,977 C 1016,1002 1006,1014 984,1019 C 865,1046 744,1059 624,1059 C 504,1059 383,1046 264,1019 C 242,1014 232,1002 226,977 C 197,854 183,735 183,616 C 183,497 197,378 226,255 C 232,230 242,218 264,213 Z',C['emblem_badge'],id='emblem-badge')
    land=group(art,'emblem-map-layer','02 · Mainland and islands',fill=C['emblem_map'])
    for id in ['mainland','island-north','island-middle','island-south']:
        el('path',land,id='emblem-'+id,d=EMBLEM_MAP[id])
    tree=group(art,'emblem-tree-layer','03 · Evergreen',fill=C['emblem_tree'])
    el('rect',tree,id='emblem-tree-trunk',x=757.5,y=625,width=48,height=68)
    el('polygon',tree,id='emblem-tree-crown',points='781.5,285 939,633.5 624,633.5')
    return g

EMBLEM_MAP={
    'mainland':'M 315.5,354.5 L 702.5,354.5 L 708.5,447 L 692.5,602 L 697.5,652.5 L 858,841.5 H 602 C 592.5,841.5 589.8,831.1 585.4,823.1 C 580.9,819.9 572.4,819.6 566.4,813.2 C 559.5,806.6 559.1,797.7 551.8,790.7 C 543.7,782.8 530.5,778.7 522.4,771.9 C 513.4,764.2 512.7,751.6 505.5,746.7 C 499,742.2 489.1,741.4 481.5,732.7 C 471.6,721.3 473.3,707.8 470.1,691.6 C 466.8,675.3 458,661 450.9,646.1 C 443.9,631.6 441.1,619.4 444.3,607.4 C 447.8,595 461,584.9 469.6,577.7 C 473.4,574.5 473.9,569.5 474.2,564.3 L 475.7,545.8 C 466.7,542.6 460.2,539.2 455.9,531.7 L 384.7,406.5 C 380.5,399.1 374.2,395.7 366.1,398.6 C 354.2,402.9 335,414.8 326.9,404 C 324.3,400.6 324.1,396 323.3,391.6 Z',
    'island-north':'M 377.9,587.2 C 387.3,590.2 397.5,592.5 406.1,596.5 C 412.9,599.6 415.3,604.1 413.7,611.1 C 411.8,619.2 412.4,624.3 412.5,630.1 C 412.9,638 410.2,642.5 404.8,642.8 C 396.6,643.3 389.9,636.3 385.4,627.5 C 380.6,617.7 376.5,604.2 374.6,593.2 C 374,589.1 374.9,586.2 377.9,587.2 Z',
    'island-middle':'M 394.8,664 C 404.3,666.3 414.7,668.6 419.1,674.4 C 423,679.5 424,689.2 426.1,699.1 C 428.3,709.6 424.7,713.2 418.1,709.5 C 406,702.7 395.2,690 391.1,677.9 C 388.5,670.4 389.3,662.6 394.8,664 Z',
    'island-south':'M 441.3,751.1 L 480.2,761.9 C 501.3,767.5 510.4,781.7 522.6,800 L 554.7,849.6 C 560.6,859.1 563.4,869.4 556.6,874 C 551.4,877.5 543.2,875.2 536,871.7 C 512.8,860.4 498.6,852 489.9,839.4 C 484.7,831.9 481.2,824.5 478.6,817.7 C 466.5,812.5 458.8,807.3 452.1,800.5 C 441.8,790 432.9,777.7 429,767.7 C 424.3,755.4 428.4,747.7 441.3,751.1 Z',
}

def build():
    s=new_svg();defs=el('defs',s)
    bg=group(s,'paper','Clean warm-white paper',True)
    el('rect',bg,x=80,y=67,width=930,height=1308,fill=C['paper'])
    title_letters(s);lettering(s)
    art=group(s,'forest-illustration','Forest illustration',True)
    frame=group(art,'picture-frame','Open rectangular frame')
    el('rect',frame,x=282,y=414,width=523,height=581,fill='none',stroke=N,stroke_width=9)
    add_blue_fronds(art,defs)
    tree_trunk(art,defs)
    bird(art,defs)
    bear_body(art)
    foreground(art)
    foreleg(art)
    emblem(s)
    return s

def save_svg(s,p):
    E.indent(s,space='  ')
    p.write_bytes(E.tostring(s,pretty_print=True,encoding='UTF-8',xml_declaration=True))

def live_text_variant(src):
    s=deepcopy(src)
    ns={'s':SVG}
    for id in ['living-forest','observe-campfire','regulations','forest-service-name']:
        old=s.xpath(f'//s:g[@id="{id}"]',namespaces=ns)[0]
        text=old.get('data-original-text')
        ng=group(None,id,text)
        ng.set('transform',old.get('transform'))
        te=el('text',ng,x=0,y=0,font_family='Nimbus Sans, Helvetica, Arial, sans-serif',font_weight='bold',
              font_size=FONT['head'].unitsPerEm,fill=N,stroke=N,stroke_width=18,stroke_linejoin='round',
              font_kerning='none',transform='scale(1 -1)')
        te.text=text
        old.getparent().replace(old,ng)
    el('metadata',s).text='Supporting text requires Nimbus Sans Bold for an exact match. Headline remains custom vector shapes.'
    return s

def main():
    s=build();save_svg(s,OUT/'forest-service-poster.svg')
    save_svg(live_text_variant(s),OUT/'forest-service-poster-live-text.svg')
    ns={'s':SVG}
    art=new_svg('192 402 648 614','648px','614px','Forest illustration — bird, bear and foliage')
    art.append(deepcopy(s.find('{%s}defs'%SVG)))
    art.append(deepcopy(s.xpath('//s:g[@id="forest-illustration"]',namespaces=ns)[0]))
    save_svg(art,OUT/'forest-illustration.svg')
    badge=new_svg('826 1212 122 131','244px','262px','British Columbia Forest Service — redrawn emblem')
    badge.append(deepcopy(s.xpath('//s:g[@id="forest-service-emblem"]',namespaces=ns)[0]))
    save_svg(badge,OUT/'forest-service-emblem.svg')
    (OUT/'palette.json').write_text(json.dumps(C,indent=2)+'\n')
    for p in OUT.glob('*.svg'):
        t=E.parse(str(p))
        print(p.name,'paths=',len(t.findall('.//{%s}path'%SVG)),'images=',len(t.findall('.//{%s}image'%SVG)))

if __name__=='__main__':main()
