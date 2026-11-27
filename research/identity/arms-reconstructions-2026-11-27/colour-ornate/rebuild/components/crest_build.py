from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vector_utils import *
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp'/'crest'; TMP.mkdir(parents=True,exist_ok=True)
a=source_array(); rgb=a[:,:,:3].astype(float); alpha=a[:,:,3].astype(float)
# Descreen first, then rebuild broad pigment regions and their contour geometry.
b=ndi.gaussian_filter(rgb,(.65,.65,0))
r,g,bl=b[:,:,0],b[:,:,1],b[:,:,2]
opaque=ndi.gaussian_filter(alpha,.6)>183
lion_area=polygon_mask([(480,0),(835,0),(835,327),(694,327),(694,263),(633,263),(633,327),(480,327)])
crown_area=polygon_mask([(642,262),(690,262),(690,304),(724,306),(771,306),(806,318),(834,351),(843,385),(820,423),(795,469),(808,495),(788,515),(788,535),(547,535),(545,515),(523,495),(541,473),(511,429),(488,390),(489,361),(516,331),(549,307),(598,306),(638,316)])
raw_gold=(r>140)&(g>96)&(bl<120)&(r>bl*1.5)&(g>bl*1.35)&opaque
# The small crown contains bright paper highlights within its continuous gold arch.
# Include these locally so a white printing highlight cannot split the arch.
yy,xx=np.indices(r.shape)
small_crown=(xx>=518)&(xx<=612)&(yy>=3)&(yy<=89)
raw_gold |= small_crown & (r>165)&(g>135)&(g>r*.64)&opaque
raw_red=(r>140)&(g<128)&(r>g*1.55)&(r>bl*1.6)&opaque
raw_blue=(bl>105)&(g>83)&(r<120)&(bl>r*1.5)&opaque
raw_white=(r>157)&(g>148)&(bl>125)&(r-bl<65)&opaque
ink=PALETTE['ink'];gold=PALETTE['gold'];red=PALETTE['red'];blue=PALETTE['blue'];ivory=PALETTE['ivory']
def vec(mask,color,sigma=.65,min_size=9,hole=10,opt=.32,alpha=1.0):
    mask=clean_mask(mask,sigma=sigma,min_size=min_size,hole_size=hole)
    return mask_path(mask,color,turdsize=min_size,alphamax=alpha,opttolerance=opt)
def component(area,name):
    if name=='royal-crown':
        area=area&(np.indices(area.shape)[0]<474)
    parts=[f'<g id="{name}">']
    inkmask=opaque&area
    if name=='royal-crown':
        # Preserve lion toes in front of the crown, instead of painting over them.
        paw_gold=raw_gold&lion_area&(yy<332)
        inkmask &= ~ndi.binary_dilation(paw_gold,iterations=1)
    parts+=[vec(inkmask,ink,.45,12,12,.24)]
    goldmask=raw_gold&area
    if name=='lion-crest':
        goldmask[251:299,807:823]=False
    if name=='royal-crown':
        goldmask=goldmask&((yy>=332)|((xx>=642)&(xx<=690)))
    crossmask=goldmask&(yy<36) if name=='lion-crest' else np.zeros_like(goldmask)
    if name=='lion-crest':
        goldmask=goldmask&(yy>=36)
    parts+=[vec(goldmask,gold,.3,7,8,.17,.9 if name=='lion-crest' else 1.1)]
    if name=='lion-crest':
        parts+=[vec(crossmask,gold,.55,5,6,.22,1.25)]
    parts+=[vec(raw_red&area&np.indices(area.shape)[0].__lt__(512),red,.6,10,15,.32)]
    if name=='royal-crown':
        parts+=[vec(raw_blue&area,blue,.5,10,10,.3)]
        # White pearls rebuilt as separate clean geometric beads below.
    parts+=['</g>']
    return '\n'.join(parts)
lion=component(lion_area,'lion-crest')
shoulder=f'<path id="lion-shoulder-clear" fill="{gold}" d="M584 217 L596 214 L609 207 L617 207 L618 213 L609 221 L591 227 L584 226 Z"/><path id="lion-shoulder-incision" fill="{ink}" d="M587.7 222.7 C590.4 219.5 593.9 221.8 597.6 219.8 C603 217.6 608.8 215.5 613.7 211 L615.4 209.6 C615.5 211.5 610.5 215.8 606.2 218.1 C601 220.7 595.6 222.2 591.9 222 L588.2 224 Z"/>'
lion=lion.replace('</g>',shoulder+'</g>')
crown=component(crown_area,'royal-crown')
# Clean pearl beads preserve the original uneven arch and proportions.
pearls=[(537,329,12.2,11.3,-13),(568,319,12.2,11.1,-9),(596,319,11.3,10.4,1),(624,320,10.1,10.5,-19),(514,348,11.7,12.1,10),(505.5,375,11.2,12.1,5),(512.5,402.1,10.2,11.3,-15),(525.6,423,5.0,8.6,-34),(666,314.6,12.5,12.5,0),(665,338.8,7.1,7.7,0),(665.6,356.5,5.6,7.1,0),(666.4,374,4.7,5.9,0),(716,329.6,10.5,10.5,0),(742.4,325.8,11.3,11.0,0),(770.2,327.3,10.7,10.7,0),(796.2,334.3,10.7,11.2,-8),(814,352.6,10.4,11.4,-8),(821.5,376,11.0,11.4,0),(818.3,401.6,10.1,10.7,10),(804.1,422.2,6.0,8.5,31)]
beads=[]
for i,(cx,cy,rx,ry,ang) in enumerate(pearls):
    beads.append(f'<ellipse id="pearl-{i+1:02d}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{ivory}" stroke="{ink}" stroke-width="3" transform="rotate({ang} {cx} {cy})"/>')
# Rebuild the jewel band with separate gold bar, lozenges, and circlets.
jewels=[f'<g id="crown-jewel-band" stroke="{ink}" stroke-linejoin="round">',
    f'<path id="crown-jewel-gold" fill="{gold}" stroke-width="5" d="M548 474 L785 474 L786 513 L547 513 Z"/>']
# Outer and inner lozenges are measured separately: the old centred stroke
# enlarged the blue and red gems beyond the surviving printed outlines.
for i,(outer,inner,col) in enumerate([
    ('M528 493 L546 477 L567 493 L549 511 Z','M535 493 L547 482 L561 493 L548 505 Z',red),
    ('M583 493 L602 477 L623 494 L604 510 Z','M590 493 L602 484 L617 493 L603 503 Z',blue),
    ('M640 493 L660 478 L681 492 L662 510 Z','M648 493 L660 483 L674 493 L662 503 Z',red),
    ('M705 493 L724 478 L744 491 L745 495 L727 508 Z','M714 492 L725 484 L736 492 L726 501 Z',blue),
    ('M770 493 L785 478 L801 493 L786 510 Z','M776 493 L785 483 L795 493 L786 504 Z',red)]):
    jewels.append(f'<g id="crown-lozenge-{i+1}" stroke="none"><path fill="{ink}" d="{outer}"/><path fill="{col}" d="{inner}"/></g>')
jewels.append(f'<path id="crown-left-divider" fill="{ink}" stroke="none" d="M565 487 L572 491 L578 487 L578 492 L574 495 L576 500 L571 499 L568 494 L564 493 Z"/>')
for i,(cx,cy,rr,inner) in enumerate([(631,486,7.5,3.7),(632,500,7.0,3.6),(694,486,7.6,3.7),(694.6,500,7.0,3.5),(755,493,7.1,3.6)]):
    jewels.append(f'<g id="crown-circlet-{i+1}" stroke="none"><circle fill="{ink}" cx="{cx}" cy="{cy}" r="{rr}"/><circle fill="{gold}" cx="{cx}" cy="{cy}" r="{inner}"/></g>')
jewels.append(f'<path id="crown-divider-links" stroke="none" fill="{ink}" d="M628 475 H634 V479 H628 Z M629 507 H635 V513 H629 Z M691 475 H697 V479 H691 Z M692 507 H698 V513 H692 Z"/>')
jewels.append('</g>')
crown=crown.replace('</g>', '<g id="crown-pearls">'+''.join(beads)+'</g>'+''.join(jewels)+'<path id="crown-lower-band-outline" fill="'+ink+'" d="M548 511 C626 510 706 511 785 511 L784 534 L551 535 Z"/><path id="crown-lower-band" fill="'+gold+'" d="M554 515 C628 514 705 515 779 515 L779 530 C704 531 627 530 555 530 Z"/></g>')
# The eye/nose/muzzle contours in the source have been kept; only the random
# ink speckle and halftone holes were excluded from the paths.
body=lion+crown
save_svg(ROOT/'components'/'crest.svg',body)
print('wrote',ROOT/'components'/'crest.svg')
