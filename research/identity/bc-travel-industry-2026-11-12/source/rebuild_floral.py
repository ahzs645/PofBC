from pathlib import Path
from math import hypot,cos,sin,pi
P=Path(__file__).resolve().parent
S=[]
def group(name, attrs=''):
 S.append(f'<g id="{name}" {attrs}>')
def end(): S.append('</g>')
def path(d,attrs=''):
 S.append(f'<path d="{d}" {attrs}/>')
def ray(a,c,b,w=1.9,color='#53554E'):
 w*=0.55
 # A two-sided quadratic lens: pointed at both ends, deliberately tapered.
 dx,dy=b[0]-a[0],b[1]-a[1];n=hypot(dx,dy);nx,ny=-dy/n,dx/n
 path(f'M{a[0]} {a[1]} Q{c[0]+nx*w:.2f} {c[1]+ny*w:.2f} {b[0]} {b[1]} Q{c[0]-nx*w:.2f} {c[1]-ny*w:.2f} {a[0]} {a[1]} Z',f'fill="{color}" stroke="none"')
def vein(a,c,b,w=2.25):
 w*=0.80
 # A branch with a broad attached base and a sharp tip.
 dx,dy=b[0]-a[0],b[1]-a[1];n=hypot(dx,dy);nx,ny=-dy/n,dx/n
 path(f'M{a[0]+nx*w/2:.2f} {a[1]+ny*w/2:.2f} Q{c[0]+nx*w*.35:.2f} {c[1]+ny*w*.35:.2f} {b[0]} {b[1]} Q{c[0]-nx*w*.35:.2f} {c[1]-ny*w*.35:.2f} {a[0]-nx*w/2:.2f} {a[1]-ny*w/2:.2f} Z','fill="#20301f" stroke="none"')
def leaf(name,outline,branches):
 group(name)
 path(outline,'fill="#88B96D" stroke="#101810" stroke-width="4.0"')
 for a,c,b,w in branches: vein(a,c,b,w)
 end()
# Underlying connected orange stems. Their junctions are merged in the main silhouette.
group('dogwood-stems','fill="#C95632" stroke="#111710" stroke-width="3.0"')
path('M568 183 C591 188 618 196 646 204 C663 208 677 212 692 217 L674 219 C641 210 606 200 568 192 Z','id="upper-cross-branch"')
path('M570 191 C582 203 595 214 616 215 C639 214 662 208 696 215 C688 210 682 201 682 192 L693 189 C695 205 701 212 721 219 C757 230 793 246 821 262 L813 281 C784 258 753 245 719 234 C682 220 653 219 624 228 C615 230 610 233 611 239 L614 247 L606 251 C602 243 601 237 604 232 L598 237 L592 231 C598 227 604 225 610 223 C591 219 581 210 568 200 Z','id="main-branch-and-junctions"')
end()
group('upper-dogwood-leaves')
leaf('upper-left-leaf','M376.8 72.3 C400.9 79.7 423.0 82.8 434.3 96.8 C445.8 111.6 445.3 127.1 430.2 139.9 C421.6 150.6 399.7 144.4 389.0 132.6 C378.4 120.6 380.8 96.3 376.8 72.3 Z',[
 ((434,129),(409,107),(386,83),3),((408,107),(396,105),(385,99),2),((419,118),(401,120),(388,115),2),((429,127),(414,132),(401,129),2),((408,108),(405,96),(400,87),2),((420,119),(418,101),(412,91),2),((398,96),(395,89),(393,86),1.8)])
leaf('upper-pointing-leaf','M446.0 117.5 C438.1 104.2 438.5 91.2 447.1 78.7 C458.0 63.4 473.0 53.2 485.6 40.8 C487.7 64.8 493.9 82.9 493.0 98.1 C492.4 109.2 481.1 116.3 466.5 120.6 Z',[
 ((459,119),(466,87),(480,53),3),((464,103),(454,93),(452,80),2.1),((471,82),(464,74),(466,62),2),((464,103),(477,94),(485,82),2),((472,81),(482,73),(484,67),2)])
end()
# Left flower; the irregular outer lobes and broad seams are independently rebuilt.
group('left-dogwood','fill="#FDFDFB" stroke="#111711" stroke-width="4.0"')
path('M477 116 C477 105 486 98 497 96 C504 94 506 90 512 92 C521 96 534 92 541 102 C545 106 546 112 545 117 C554 113 564 115 571 125 C575 132 584 133 585 141 C585 148 581 153 583 160 C586 172 584 181 575 186 C574 194 567 198 566 207 C561 216 561 224 551 225 C537 224 530 235 515 232 C505 230 499 225 497 217 C493 231 486 237 475 237 C461 236 458 229 445 227 C436 227 435 221 432 212 C427 203 422 199 423 189 C424 180 429 173 439 170 C429 171 422 165 420 158 C416 150 422 143 426 134 C429 123 435 121 447 121 C457 115 466 114 477 116 Z','id="left-blossom-contour"')
group('left-petal-divisions','fill="none"')
for d in ['M477 116 C487 121 491 133 494 144','M545 117 C529 121 525 136 515 148','M575 186 C570 173 554 173 539 172 C528 172 521 169 519 166','M497 217 C495 204 498 188 500 179','M439 170 C458 164 471 168 486 165']:path(d)
end();end()
group('left-tapered-petal-veins')
for a,c,b,w in [((495,143),(490,129),(490,117),1.8),((500,142),(503,125),(511,108),2),((507,145),(513,132),(524,123),1.9),((519,155),(534,139),(551,130),2.1),((522,163),(545,153),(566,149),2.1),((519,173),(530,182),(539,185),1.8),((514,177),(524,195),(537,209),2),((508,180),(510,196),(516,209),1.9),((492,178),(474,193),(459,210),2),((489,173),(466,179),(451,188),1.9),((497,182),(488,201),(481,217),2),((486,155),(460,145),(446,133),2),((490,148),(478,136),(472,127),1.8)]:ray(a,c,b,w)
end()
# Right flower, four broad bracts. Middle foreground leaf naturally overlaps its lower left bract.
group('right-dogwood','fill="#FDFDFB" stroke="#111711" stroke-width="4.0"')
path('M657 70 C655 53 670 39 686 41 C696 44 704 40 712 43 C720 47 721 54 729 61 C739 68 743 76 739 84 C754 80 765 84 770 97 C771 105 769 113 773 123 C779 135 771 142 762 148 C751 160 747 166 736 166 C733 166 730 165 727 164 C732 177 724 191 712 195 C700 200 688 196 679 193 C671 188 662 188 651 185 L641 180 C636 174 640 162 644 156 C650 146 656 142 666 137 C651 144 639 147 628 146 C613 146 603 140 601 130 C599 124 602 116 600 110 C599 101 601 96 610 91 C623 86 622 79 633 73 C641 68 649 67 657 70 Z','id="right-blossom-contour"')
group('right-petal-divisions','fill="none"')
for d in ['M657 70 C672 74 678 87 682 99','M739 84 C731 100 719 106 704 110','M727 164 C713 160 707 146 700 127','M666 137 C672 133 676 131 681 128']:path(d)
end();end()
group('right-tapered-petal-veins')
for a,c,b,w in [((687,96),(686,81),(687,68),1.9),((693,95),(702,77),(710,60),2),((700,101),(708,90),(719,82),1.9),((675,110),(653,100),(628,99),2),((673,116),(649,115),(631,123),2),((678,104),(666,93),(651,88),1.8),((682,132),(668,147),(661,161),1.9),((687,135),(688,159),(684,178),2),((694,133),(698,153),(706,166),1.9),((709,113),(728,110),(744,114),1.9),((707,118),(731,123),(749,134),2),((706,124),(719,133),(729,145),1.9)]:ray(a,c,b,w)
end()
# Packed, individually outlined round florets. These are construction circles, not traced outlines.
def centre(name,cx,cy,shrink=1):
 group(name,f'transform="translate({cx} {cy}) scale({shrink}) translate({-cx} {-cy})" fill="#F2D532" stroke="#302D15" stroke-width="0.85"')
 path(f'M{cx+17.4} {cy} A17.4 17.4 0 1 1 {cx-17.4} {cy} A17.4 17.4 0 1 1 {cx+17.4} {cy} Z','fill="#302D15" stroke="none"')
 cells=[(0,-.3,4.7),(-8.5,-1.5,4.3),(-4.8,-8.3,4.3),(3.6,-8.5,4.3),(8.2,-.7,4.4),(3.8,7.2,4.3),(-5.7,6.5,4.5),
 (-16.5,0,4.0),(-14.2,-7.7,4.3),(-8.3,-14.9,4.1),(-1.3,-16.5,4.3),(7.3,-14.3,4.3),(13.1,-8.3,4.7),(15.9,-.7,4.3),(13.4,7.3,4.3),(7.8,14,4.6),(-1.1,15.8,4.5),(-8.6,13.2,4.4),(-14.3,7.1,4.5)]
 for i,(x,y,r) in enumerate(cells):
  # Four smooth cubic quadrants make each editable round floret.
  x+=cx;y+=cy;k=r*.55228475
  path(f'M{x+r:.3f} {y:.3f} C{x+r:.3f} {y+k:.3f} {x+k:.3f} {y+r:.3f} {x:.3f} {y+r:.3f} C{x-k:.3f} {y+r:.3f} {x-r:.3f} {y+k:.3f} {x-r:.3f} {y:.3f} C{x-r:.3f} {y-k:.3f} {x-k:.3f} {y-r:.3f} {x:.3f} {y-r:.3f} C{x+k:.3f} {y-r:.3f} {x+r:.3f} {y-k:.3f} {x+r:.3f} {y:.3f} Z',f'id="{name}-floret-{i+1:02}"')
 end()
centre('left-floret-cluster',502.8,162.5,.95)
centre('right-floret-cluster',688.2,112.0,.90)
group('foreground-dogwood-leaves')
leaf('middle-pointing-leaf','M594 213 C583 205 585 185 598 175 C615 163 638 159 664 165 C648 178 644 196 629 209 C615 219 605 219 594 213 Z',[
 ((595,212),(621,183),(652,169),3.1),((607,200),(604,187),(611,175),2),((619,187),(618,176),(624,168),2),((634,177),(634,170),(639,166),1.9),((607,200),(622,202),(636,196),2),((620,188),(633,190),(644,185),2),((634,178),(646,179),(651,175),1.8)])
leaf('lower-left-leaf','M500 245 C526 253 545 231 571 227 C586 223 597 230 603 237 C606 259 590 279 569 284 C539 291 514 275 500 245 Z',[
 ((602,237),(557,269),(506,249),3.0),((589,244),(586,260),(575,274),2.0),((574,252),(565,269),(551,279),2.1),((555,257),(547,266),(535,270),2.0),((589,245),(574,236),(561,233),2.0),((574,253),(553,242),(542,239),2.0),((554,258),(539,248),(526,245),2.0)])
leaf('lower-right-leaf','M611 249 C629 240 648 244 661 255 C676 269 679 285 689 296 C667 302 640 303 622 294 C602 285 600 263 611 249 Z',[
 ((612,250),(644,282),(682,295),3.0),((624,262),(621,278),(629,291),2.0),((640,276),(640,289),(649,297),2.0),((656,286),(661,294),(668,298),1.9),((624,263),(639,261),(654,264),2.0),((641,277),(655,273),(670,279),2.0),((656,286),(671,284),(679,289),1.9)])
end()
body='\n'.join(S)
head='<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="644" height="468" viewBox="0 0 644 468">\n<title>Reconstructed dogwood illustration, revised reference</title>\n<desc>Fresh hand-authored vector geometry reconstructed from the supplied November 12 screenshot. Smooth white bracts, individually outlined yellow florets, tapered veins, and black-bordered orange stems. No bitmap or automatic tracing.</desc>\n'
transform='translate(-32.3152107514 141.1728772144) scale(0.6108735492)'
svg=head+f'<g id="dogwood-illustration" transform="{transform}" stroke-linecap="round" stroke-linejoin="round">\n'+body+'\n</g>\n</svg>\n'
(P/'floral.svg').write_text(svg)
(P/'floral-preview.svg').write_text(svg.replace('<g id="dogwood-illustration"','<rect width="644" height="468" fill="#116B32"/><g id="dogwood-illustration"'))
# Screenshot-space illustration for a direct comparison.
(P/'screenshot-space-preview.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="470" height="285" viewBox="365 25 470 285"><rect x="365" y="25" width="470" height="285" fill="#075731"/><g stroke-linecap="round" stroke-linejoin="round">'+body+'</g></svg>')
print('Wrote floral.svg, preview SVGs; paths:',len([x for x in S if x.startswith('<path')]))
