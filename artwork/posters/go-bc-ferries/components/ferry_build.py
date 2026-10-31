from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent
CREAM='#ffe9aa'; TEAL='#1b9fa8'; INK='#0b1211'; NAVY='#00272c'
elems=[]
def path(id,d,fill):
 elems.append(f'<path id="{id}" d="{d}" fill="{fill}"/>')
def rect(id,x,y,w,h):
 elems.append(f'<rect id="{id}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{INK}"/>')
def circle(id,x,y,r):
 elems.append(f'<circle id="{id}" cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>')
elems.append('<g id="ferry-illustration">')
elems.append('<title>Hand-built coastal ferry illustration</title>')
elems.append('<desc>Reconstructed with cubic curves, polygons, rectangular windows, and circular portholes on the original 1354 by 1161 reference coordinate grid. Gull is a separate overlaid group. Hidden geometry behind the gull is continued coherently.</desc>')
elems.append('<g id="ferry-funnel-and-mast">')
path('ferry-funnel','M 646 554.8 C 664.1 553.6 670.2 540.5 683.8 510.3 L 789.8 495.6 L 797.1 532.9 C 781.1 532.6 775.9 536 763.4 544 C 752.2 551.1 691.4 555.1 646 554.8 Z',TEAL)
path('ferry-funnel-cream-band','M 680.3 518.8 L 791.4 502.6 L 795.5 524.1 L 669.9 541.3 Z',CREAM)
path('ferry-funnel-dark-cap','M 683.8 510.3 L 789.8 495.6 L 791.4 502.6 L 680.3 518.8 Z',NAVY)
path('ferry-funnel-mark','M 721.8 520 L 743.4 517.2 L 744.3 529.7 L 722.6 532.3 Z',TEAL)
path('ferry-mast','M 793.6 448.5 L 798.3 446.6 L 839.5 533.1 L 826.6 533.1 Z',CREAM)
elems.append('</g>')
elems.append('<g id="ferry-superstructure">')
path('ferry-superstructure-body','M 228.5 603.9 L 248.7 565.2 L 435.4 565.2 L 442 554.9 L 646 554.9 C 691.5 554.9 746.3 552.9 763.2 545.2 C 773.4 537.3 779.7 532.5 796.1 532.5 L 978.3 532.5 L 988.5 565.6 L 999.2 565.6 C 1005.6 565.6 1008.5 568.5 1011.2 574.5 L 1024.6 606.7 L 228.5 606.7 Z',CREAM)
# Upper bridge row: individual panes follow the photographed stepped facade.
rect('ferry-bridge-window-01',796.8,544.2,16.1,14.9)
rect('ferry-bridge-window-02',840.4,544.3,16.0,14.8)
rect('ferry-bridge-window-03',886.3,544.5,15.6,14.6)
rect('ferry-bridge-window-04',925.4,544.5,15.2,14.6)
path('ferry-bridge-window-05','M 948.5 544.5 H 961.4 L 963.8 559.2 H 949.8 Z',INK)
path('ferry-bridge-window-06','M 969.5 544.5 H 982.0 L 986.5 559.2 H 972.0 Z',INK)
# The small rectangular ventilator/window row.
for i,(x,w) in enumerate([(466.7,11.3),(509.5,10.9),(551.7,11.0),(592.5,11.1),(628.1,10.9)],1):
 rect(f'ferry-upper-window-{i:02}',x,562.6,w,8.7)
# Visible aft angular window; the gull covers adjoining panes.
path('ferry-aft-main-window','M 268.3 580.6 L 298.7 580.6 L 288.8 595.8 L 265.1 595.8 Z',INK)
# Continue panes behind gull so illustration remains independently editable.
rect('ferry-main-window-hidden-01',307,581.7,25,14.7)
rect('ferry-main-window-partly-covered',342,581.7,38.6,14.7)
for i,(x,w) in enumerate([(390.3,28.2),(427.0,25.2),(461.7,25.9),(497.1,28.1),(534.9,26.1),(570.9,25.9),(606.5,25.1),(642.1,30.2),(682.4,27.0),(727.1,12.2),(762.2,12.1),(796.7,12.0)],1):
 rect(f'ferry-main-window-{i:02}',x,581.7,w,14.7)
# Forward windows: curved saloon pane and the two sloped bow panes.
path('ferry-forward-window-01','M 828 596.1 C 839.7 575.9 853.6 576.7 862.6 576.5 L 888.1 576.5 L 885.8 596.1 Z',INK)
path('ferry-forward-window-02','M 899.3 576.5 H 940.5 L 940.4 596.1 H 897.1 Z',INK)
path('ferry-forward-window-03','M 950.5 576.5 H 979.8 L 983.7 596.1 H 950.3 Z',INK)
path('ferry-forward-window-04','M 990.4 576.5 L 1012 576.5 L 1020 596.1 H 994.0 Z',INK)
elems.append('</g>')
elems.append('<g id="ferry-lower-deck">')
path('ferry-lower-deck-body','M 202.7 604.0 L 1023.1 604.0 L 1024.3 606.7 L 1185.5 606.7 L 1163.6 649.5 L 182.1 649.5 Z',CREAM)
path('ferry-upper-teal-stripe','M 202.7 604.0 L 1023.1 604.0 L 1024.3 606.7 L 1150.9 606.7 L 1176.2 625.0 L 1171.7 633.7 L 1147.4 617.8 L 196.0 616.5 Z',TEAL)
# The slight diagonal corners at the stern are intentional.
path('ferry-stern-loading-opening-01','M 189.3 636.3 L 211.2 636.3 L 204.7 651.8 L 180.9 651.8 Z',NAVY)
path('ferry-stern-loading-opening-02','M 224.3 636.3 L 251.2 636.3 L 243.7 651.8 L 217.0 651.8 Z',NAVY)
for i,x in enumerate([357.8,448.7,544.2,629.8,719.9,811.2,901.7,995.9,1085.5],1):
 circle(f'ferry-porthole-{i:02}',x,633.3,5.0)
elems.append('</g>')
elems.append('<g id="ferry-waterline-and-hull">')
path('ferry-lower-teal-stripe','M 180.9 651.8 L 261.7 649.5 L 1163.6 649.5 L 1157.0 663.1 L 157.9 663.1 L 157.9 652.0 Z',TEAL)
path('ferry-hull','M 157.8 662.9 L 1160.6 662.9 L 1152.0 685.3 L 189.3 685.3 C 181.5 673.2 177.9 669.4 165.8 669.0 C 160.8 668.8 159.4 667.9 157.8 662.9 Z',NAVY)
elems.append('</g></g>')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1354" height="1161" viewBox="0 0 1354 1161">\n'+'\n'.join(elems)+'\n</svg>\n'
(ROOT/'ferry.svg').write_text(svg)
print(ROOT/'ferry.svg')
