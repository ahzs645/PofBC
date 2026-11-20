"""Construct the IUS wordmarks and pin as real vector geometry.

The historical-print geometry is fitted to the supplied original brochure.
The compact and extended geometries deliberately retain the separate supplied
reconstruction references. They are not presented as additional historic marks.
"""
from pathlib import Path
import json
from vector_utils import *

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'svg';OUT.mkdir(exist_ok=True)
INK='#1D1D1B'; ORANGE='#D17A42'; PAPER='#F2ECD9'
METAL='#D8D4C8'; ENAMEL='#C7722D'; BURGUNDY='#78353A'
MANIFEST=[]

# Separate optical correction for the photographed enamel lettering.
# This is not an identified historical font cut. Metal backing geometry stays fixed.
PIN_CAP_HEIGHT=108
PIN_BLACK_EDGE_EXPANSION=0.020 * PIN_CAP_HEIGHT
PIN_BLACK_OUTLINE_WIDTH=2 * PIN_BLACK_EDGE_EXPANSION

def save(name,w,h,body,title,desc,sources,kind='reconstructed',physical=None):
    # Optical overshoot in round letters must remain inside the export canvas.
    # This four-unit buffer is distinct from the recommended reproduction clearspace.
    if physical is None:
        body=f'<g id="artwork" transform="translate(4 4)">{body}</g>'
        w+=8;h+=8
    (OUT/(name+'.svg')).write_text(svg_doc(w,h,body,title,desc,physical))
    MANIFEST.append(dict(id=name,title=title,width=w,height=h,sources=sources,
        status=kind,description=desc,svg='svg/'+name+'.svg'))

def logo(kind='print',ink=INK,accent=ORANGE):
    if kind=='print':
        cap=107; pitch=207; right=934; widths=[690,880,640]
        bar_starts=[0,174,338];bar_y=130;bar_h=44;W=1000;H=588
        font='bold'
    elif kind=='compact':
        cap=142; pitch=207;right=1000;widths=[755,940,680]
        bar_starts=[0,90,265];bar_y=164;bar_h=28;W=1000;H=606
        font='bold'
    elif kind=='extended':
        cap=102;pitch=180;right=1000;widths=[525,680,500]
        bar_starts=[0,210,405];bar_y=123;bar_h=32;W=1000;H=515
        font='bold'
    parts=[]
    for i,(word,width,left) in enumerate(zip(['INTERIOR','UNIVERSITY','SOCIETY'],widths,bar_starts)):
        parts.append(text_paths(word,right,i*pitch,cap,font=font,fill=ink,width=width,align='right',ident='word-'+word.lower()))
        parts.append(bar(left,i*pitch+bar_y,W,bar_h,accent,'bar-'+str(i+1)))
    return W,H,'\n'.join(parts)

def build_logos():
    for suffix,ink,accent in [('colour',INK,ORANGE),('black','#000000','#000000'),('white','#FFFFFF','#FFFFFF')]:
        w,h,body=logo(ink=ink,accent=accent)
        save('ius-print-'+suffix,w,h,body,'Interior University Society - source print '+suffix,
            'Reconstructed from original supplied print photographs. Outlined Nimbus Sans Bold is a close working substitute, not a verified original font. Right-aligned letters, projecting orange bars, 45-degree left bar cuts. All artwork consists of editable vector paths. Colours are approximations.',
            ['IMG_7953(1).jpeg','IMG_7950.jpeg'])
    w,h,body=logo(ink='#FFFFFF',accent='#FFFFFF')
    save('ius-print-reversed-panel',w+128,h+128,rect(0,0,w+128,h+128,INK,'ink-panel')+f'<g transform="translate(64 64)">{body}</g>',
        'Interior University Society - reversed display panel','Reconstructed one-colour reversed reproduction on a dark vector rectangle. The panel is optional. Historical use of this precise panel is not independently verified.',[], 'derived')
    for name in ['compact','extended']:
        w,h,body=logo(name)
        save('ius-reference-'+name,w,h,body,'Interior University Society - '+name+' reconstruction alternative',
            'Faithful vector construction of the separately supplied clean-up reference layout. This is a contemporary reconstruction variant, not evidence of an additional historical identity. Outlined and fitted type; geometric bars; no raster content.',
            ['3840431D-FB14-4CD2-A30C-6D868DDDEE7C.jpeg'] if name=='compact' else ['B4E31A32-20F0-444B-A017-ABD644E9B08D.jpeg'],'reference-alternative')
    w,h,body=logo()
    save('ius-print-vertical',h,w,f'<g id="rotated-print-mark" transform="translate(0 {w}) rotate(-90)">{body}</g>',
        'Interior University Society - vertical stationery mark','The print reconstruction rotated minus 90 degrees to reproduce the orientation visible on the original letterhead. Transparent background; outlined lettering.', ['IMG_7950.jpeg','IMG_7947.jpeg'])

def pin_body():
    # Deliberate five-sided geometry with small corner radii, not a bitmap contour.
    return 'M20 0H980Q1000 0 1000 20V720Q1000 740 980 740H398Q390 740 384 734L8 254Q0 244 0 232V20Q0 0 20 0Z'

def pin_lettering(word, y, width, ident, metal=False):
    """Keep the outlined base and add a documented optical black-inlay weight.

    +0.020 cap height per black edge = 2.16 units at a 108-unit base cap.
    The 4.32-unit black outline expands the overall visible cap by 4%.
    This adjustment is separate from, and does not identify, a font family/cut.
    """
    if not metal:
        return text_paths(word,928,y,PIN_CAP_HEIGHT,font='bold',fill=INK,
            width=width,align='right',ident=ident,stroke=INK,
            sw=PIN_BLACK_OUTLINE_WIDTH)
    # The existing metal surrounds and solid O/R backing contours are unchanged.
    base=text_paths(word,928,y,PIN_CAP_HEIGHT,font='bold',fill=INK,width=width,
        align='right',ident=ident,stroke=METAL,sw=15,solid_counters=True)
    inlay=text_paths(word,928,y,PIN_CAP_HEIGHT,font='bold',fill=INK,width=width,
        align='right',ident=ident+'-optical-black-inlay',stroke=INK,
        sw=PIN_BLACK_OUTLINE_WIDTH)
    return base + '\n' + inlay

def build_pin():
    body=[f'<path id="metal-body" d="{pin_body()}" fill="{METAL}"/>',
          '<path id="enamel-field" d="M24 16H976Q984 16 984 24V716Q984 724 976 724H402L16 238V24Q16 16 24 16Z" fill="'+ENAMEL+'"/>']
    words=['INTERIOR','UNIVERSITY','SOCIETY'];widths=[595,768,560];starts=[75,236,402]
    for i,word in enumerate(words):
        body.append(pin_lettering(word,70+i*206,widths[i],'pin-word-'+word.lower(),metal=True))
        body.append(bar(starts[i],204+i*206,936,38,BURGUNDY,'pin-bar-'+str(i+1),METAL,9))
    save('ius-enamel-pin',1000,740,'\n'.join(body),'Interior University Society - enamel pin artwork',
        'Reconstructed flat vector artwork: five-sided chamfered body, warm orange enamel, black lettering, burgundy bars, and pale metal surrounds on individual letters and bars. The outlined Nimbus Sans Bold black inlays receive a separate +0.020-cap-height optical edge expansion (4.32-unit black outline at a 108-unit base cap), while the metal backing contours remain unchanged. This is a reconstruction adjustment, not an identified historical font cut. Photographic colours, metal finish and dimensions are uncalibrated. Nominal viewBox only, not a production die or certified manufacturing drawing.',
        ['IMG_7956(2).jpeg','IMG_7955(1).jpeg'])
    line=f'<path id="pin-silhouette" d="{pin_body()}" fill="none" stroke="{INK}" stroke-width="8"/>'
    for i,word in enumerate(words):
        line+=pin_lettering(word,70+i*206,widths[i],'mono-pin-word-'+word.lower())
        line+=bar(starts[i],204+i*206,936,38,INK,'mono-pin-bar-'+str(i+1))
    save('ius-pin-one-colour',1012,752,f'<g transform="translate(6 6)">{line}</g>','Interior University Society - one-colour pin adaptation',
        'Derived single-ink version of the reconstructed enamel pin, including the separately documented +0.020-cap-height optical black-edge adjustment. This reproduction adaptation is not asserted to be a surviving historical pin.',[], 'derived')
    save('ius-pin-body',1000,740,f'<path id="body-silhouette" d="{pin_body()}" fill="{INK}"/>','IUS pin - separate silhouette component',
        'Editable five-sided geometric silhouette with rounded corners. Estimated proportions from photograph; not a measured cutline.', ['IMG_7956(2).jpeg'],'component')

def build_components():
    body='\n'.join(bar(s,207*i,1000,44,ORANGE,'standalone-bar-'+str(i+1)) for i,s in enumerate([0,174,338]))
    save('ius-three-bars',1000,458,body,'IUS three bars - separate graphic component',
        'Three separately editable quadrilateral bars with a common right edge and 45-degree leading cuts. Source-print proportions. This is a component, not a separately documented historical standalone symbol.', ['IMG_7953(1).jpeg'],'component')
    save('support-campaign-wording',1000,360,
        text_paths('SUPPORT',1000,0,160,font='bold',width=1000,align='right',ident='support')+text_paths('CAMPAIGN',1000,200,132,font='bold',width=860,align='right',ident='campaign'),
        'Support Campaign - brochure wording','Outlined and fitted sans serif lettering reconstructed from the brochure cover. Approximate typography.', ['IMG_7953(1).jpeg'])

if __name__=='__main__':
    build_logos();build_pin();build_components()
    (ROOT/'source'/'core_manifest.json').write_text(json.dumps(MANIFEST,indent=2))
    print('Built',len(MANIFEST),'core SVG assets')
