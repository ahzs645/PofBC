from pathlib import Path
import sys, json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy import ndimage as ndi
from scipy.interpolate import CubicSpline
from PIL import Image
from lxml import etree as ET
from vector_utils import *

R=ROOT
O=R/'output'; O.mkdir(exist_ok=True)
a=source_array()
INK=PALETTE['ink']; IVORY=PALETTE['ivory']; GOLD=PALETTE['gold']; BLUE=PALETTE['blue']; RED=PALETTE['red']; PINK=PALETTE['ribbon']

def path(d,fill=INK,stroke=None,sw=1,id=None):
    attrs=f'fill="{fill}" d="{d}"'
    if stroke: attrs+=f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
    if id:attrs+=f' id="{id}"'
    return '<path '+attrs+'/>'

shield_d='M441 523 C593 525 757 525 906 523 L905 936 C905 973 883 990 837 999 C775 1005 714 1024 670 1045 C628 1016 572 1004 514 999 C464 997 439 975 439 938 Z'
defs=f'<defs><clipPath id="shield-clip">{path(shield_d)}</clipPath></defs>'
shield=[f'<g id="shield" clip-path="url(#shield-clip)">',path(shield_d,IVORY),'<g id="union-flag">',path('M436 520 H912 V740 H436 Z',IVORY)]
# Each blue quarter and each diagonal is drawn independently. The inset rounded
# red tips and open white junctions follow the source's hand-lettered flag.
blue_quarters=[
 ('northwest-upper','M492 525 L603 527 L603 575 Z'),
 ('northwest-outer','M441 556 L523 592 L442 594 Z'),
 ('northeast-upper','M734 529 L818 527 L734 576 Z'),
 ('northeast-outer','M906 548 L905 596 L800 594 Z'),
 ('southwest-outer','M441 667 L531 669 L446 704 Z'),
 ('southwest-lower','M497 735 L604 689 L605 736 Z'),
 ('southeast-outer','M799 670 L906 670 L906 715 Z'),
 ('southeast-lower','M733 691 L820 736 L733 736 Z')]
for name,d in blue_quarters:shield.append(path(d,BLUE,INK,4.7,'flag-blue-'+name))
RED_EDGE='#ae3343'
shield.append(path('M442 527 L482 527 C515 544 556 567 597 588 Q608 594 600 598 L575 598 C529 576 484 552 442 535 Z',RED,RED_EDGE,2.4,'saltire-northwest'))
shield.append(path('M740 587 L848 530 L904 528 L904 537 L773 594 Q763 599 751 599 L741 599 Q730 598 734 592 Q736 589 740 587 Z',RED,RED_EDGE,2.4,'saltire-northeast'))
shield.append(path('M448 716 L578 674 Q588 670 599 671 Q608 672 601 680 C565 701 524 718 485 734 L448 733 Z',RED,RED_EDGE,2.4,'saltire-southwest'))
shield.append(path('M742 671 C751 670 759 673 769 676 L901 727 L885 736 L862 735 C820 715 779 696 739 682 Q730 678 734 674 Q736 672 742 671 Z',RED,RED_EDGE,2.4,'saltire-southeast'))
shield.append(path('M615 529 L721 530 L721 609 L907 610 L907 655 L721 655 L721 738 L615 738 L615 655 L440 654 L440 610 L615 610 Z',RED,RED_EDGE,2.4,'cross-of-st-george'))
shield.append('</g>')
# Lower field: regularised gently curved waves follow the original spacing.
shield.append(path('M436 738 H912 V1051 H436 Z',IVORY))
shield.append(path('M440 736.2 C535 738 573 735.8 615 736.7 C666 737.5 716 735.6 770 735.9 L906 737.2','none',INK,4.6,'chief-divider'))
def wave_band(y,height):
    xx=np.array([432,470,510,550,590,630,670,710,750,790,830,870,915],float)
    yy=np.array([0,3,-2,0,4,0,-3,2,4,0,-1,2,3],float)+y
    cs=CubicSpline(xx,yy,bc_type='natural')
    slope=cs(xx,1)
    segments=[]
    for i in range(len(xx)-1):
        h=xx[i+1]-xx[i]
        segments.append(((xx[i],yy[i]),(xx[i]+h/3,yy[i]+slope[i]*h/3),(xx[i+1]-h/3,yy[i+1]-slope[i+1]*h/3),(xx[i+1],yy[i+1])))
    fmt=lambda p:f'{p[0]:.2f} {p[1]:.2f}'
    commands=['M'+fmt(segments[0][0])]
    for p0,c1,c2,p1 in segments: commands.append('C'+fmt(c1)+' '+fmt(c2)+' '+fmt(p1))
    commands.append('L'+fmt((xx[-1],yy[-1]+height)))
    for p0,c1,c2,p1 in reversed(segments):
        commands.append('C'+fmt((c2[0],c2[1]+height))+' '+fmt((c1[0],c1[1]+height))+' '+fmt((p0[0],p0[1]+height)))
    return ' '.join(commands)+' Z'
shield.append('<g id="waves">')
for i,(y,h) in enumerate([(753,6),(774,39),(837,7),(859,40),(931,7),(951,42)]):
    shield.append(path(wave_band(y,h),BLUE,id=f'wave-{i+1}'))
shield.append('</g>')
# The sun's original long asymmetric rays are reconstructed as clean curves.
sun_d='''M 670.52,1040.62 C 624.13,1010.46 554.42,992.79 471.15,963.97 C 515.00,956.79 544.82,978.30 580.34,978.08 Q 587.34,979.41 578.95,967.92 C 541.75,944.63 503.99,927.56 471.09,900.02 C 521.98,917.11 562.37,946.31 596.19,961.11 Q 600.11,960.13 598.59,959.58 C 567.26,927.04 538.00,893.11 506.21,857.09 C 557.00,878.00 574.00,924.67 619.33,944.88 Q 621.34,945.45 619.60,940.72 C 591.29,886.00 565.08,852.67 551.96,809.03 C 584.11,850.58 621.99,905.77 637.22,928.21 Q 643.13,931.50 641.72,925.46 C 614.00,857.62 611.75,824.00 588.02,783.10 C 636.57,814.45 637.00,884.21 656.51,911.00 Q 663.15,932.54 663.85,919.31 C 668.85,877.53 661.74,808.00 669.98,770.53 C 674.53,819.00 679.08,872.88 681.63,921.78 Q 682.40,936.07 689.74,918.87 C 698.38,865.51 715.58,834.00 726.04,789.65 C 737.62,829.00 707.00,877.07 705.53,924.83 Q 700.75,932.67 703.63,931.23 C 737.12,891.00 754.00,849.00 779.06,822.00 C 757.00,866.00 736.15,908.00 724.91,942.92 Q 724.99,948.89 741.89,934.01 C 771.39,900.96 802.38,864.00 829.89,831.43 C 807.42,887.00 776.68,913.66 755.13,951.75 Q 740.36,967.12 756.81,960.05 C 787.00,935.96 826.00,924.00 852.00,897.39 C 819.00,940.54 787.00,952.18 767.84,972.37 Q 753.20,980.10 773.29,980.49 C 800.00,971.26 845.00,962.00 872.00,946.18 C 843.00,972.21 807.00,974.12 792.45,993.26 Q 781.58,991.48 814.40,997.86 L 831.63,997.78 C 771.06,1006.41 710.00,1014.00 670.52,1040.62 Z'''
shield.append('<g id="setting-sun">'+path(sun_d,GOLD,INK,3.4,'sun-rays')+'</g>')
shield.append('</g>')
shield.append(path(shield_d,'none',INK,5.5,'shield-outline'))
# Small crown placed in the upper field, redrawn as editable curves.
small=[f'<g id="shield-crown">',
 path('M620 607 L638 618 L639 594 Q640 592 642 596 L654 612 Q656 615 658 610 L665 585 Q667 581 669 588 L678 611 Q679 614 681 611 L695 594 L692 619 L713 606 L701 638 C681 627 655 626 637 640 Z',GOLD,INK,3.9,'shield-crown-points'),
 path('M637 640 C654 627 680 625 701 638 L697 650 C680 641 657 640 641 653 Z',GOLD,INK,3.9,'shield-crown-band'),
 path('M642 654 C642 648 654 644 668 644 C683 644 695 648 696 653 C697 660 683 664 668 664 C654 664 642 660 642 654 Z',GOLD,INK,4.8,'shield-crown-underside'),
 '</g>']
shield.extend(small)
save_svg(R/'components'/'shield.svg',defs+''.join(shield))


print('Wrote shield.svg')
