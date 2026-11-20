#!/usr/bin/env python3
"""Rebuild photographed IUS forms from independent typesetting and geometric primitives.
No raster, image trace, pixel fitting, or bitmap is used by this builder.
Requires fontTools and installed Nimbus Sans OTF fonts.
"""
from pathlib import Path
import json,html,re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT=Path(__file__).resolve().parents[1]/'svg'
ROOT.mkdir(exist_ok=True)
FONTS={
 'regular':'/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf',
 'bold':'/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'}
CACHE={k:TTFont(v) for k,v in FONTS.items()}
INK='#25241F'; PAPER='#F0D88E'
def fmt(v):return f'{v:.3f}'.rstrip('0').rstrip('.')
def text(label,x,y,size=12,weight='regular',maxw=None,center=False,id=None):
 f=CACHE[weight]; gs=f.getGlyphSet();cm=f.getBestCmap();units=f['head'].unitsPerEm;s=size/units
 adv=sum(f['hmtx'].metrics[cm.get(ord(c),'space')][0] for c in label)*s
 sx=s*min(1,maxw/adv) if maxw and adv else s
 width=adv*sx/s
 if center:x-=width/2
 pen=SVGPathPen(gs);pos=0
 for c in label:
  name=cm.get(ord(c),'space');gs[name].draw(TransformPen(pen,(sx,0,0,-s,x+pos,y)));pos+=f['hmtx'].metrics[name][0]*sx
 d=re.sub(r'-?\d+\.\d+',lambda m:fmt(float(m.group(0))),pen.getCommands())
 return f'<path id="{id or "label-"+re.sub("[^a-z0-9]+","-",label.lower()).strip("-")}" aria-label="{html.escape(label,quote=True)}" fill="{INK}" d="{d}"/>'
def box(x,y,w,h,fill='none',stroke=INK,sw=1):return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def line(x1,y1,x2,y2,sw=1):return f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{INK}" stroke-width="{sw}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{INK}" stroke-width="{sw}"/>'
def cells(x,y,count,width=31,h=28):
 a=[box(x,y,count*width,h)]
 for k in range(1,count):a.append(line(x+k*width,y,x+k*width,y+h,.8))
 return ''.join(a)
def write(name,parts,h,desc):
 meta={'asset':name,'status':'Source-derived reconstructed layout; not an archival facsimile','sources':['IMG_7947.jpeg','IMG_7950.jpeg','IMG_7955(1).jpeg'],'text':'Readably photographed headings and field labels transcribed. Dense original statement-of-support microcopy is omitted; reserved blank space preserves its location. Some grid cell counts and proportions estimated.','omissions':['unreadable declaration microcopy','serial numbers','autographs','staples'],'typefaces':FONTS,'construction':'Letter outlines generated from font contours; layout and boxes constructed geometrically; no automatic tracing or embedded images.'}
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{h}" viewBox="0 0 760 {h}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(name.replace('-',' ').title())}</title><desc id="desc">{html.escape(desc)}</desc>
<metadata>{html.escape(json.dumps(meta))}</metadata>
'''+''.join(parts)+'\n</svg>\n'
 (ROOT/(name+'.svg')).write_text(svg)
 return meta

def base(h):
 a=[box(0,0,760,h,PAPER,'none',0),'<g id="typography">',text('INTERIOR UNIVERSITY SOCIETY',380,54,27,'bold',680,True,'society-heading'),text('STATEMENT OF SUPPORT',36,84,12,'bold',id='statement-heading'),'</g>']
 # Original fine declaration copy was not sufficiently legible to reproduce.
 # Its position is deliberately left empty in this reconstructed template.
 return a

# Full membership card, photographed as a separate pad.
a=base(728)
a += ['<g id="name-fields">',text('RECEIVED FROM MR. MRS. MS.   (LAST NAME)',36,169,11,'bold'),cells(36,176,20,34.4),text('GIVEN NAMES',36,218,10,'bold'),cells(36,224,20,34.4),text('ADDRESS',36,266,10,'bold'),cells(36,272,20,34.4),text('CITY',36,314,10,'bold'),cells(36,320,20,34.4),'</g>']
a += ['<g id="contact-fields">',text('POSTAL CODE',36,362,10,'bold'),cells(36,368,6,34.4),text('TELEPHONE',318,362,10,'bold'),cells(318,368,12,33.8),'</g>']
a += ['<g id="historic-payment-fields">',text('I authorize the Society to charge my credit card number for the amount indicated below.',380,424,11,'regular',685,True),text('ACCOUNT NUMBER',36,445,10,'bold'),cells(36,451,16,28),text('TYPE OF CREDIT CARD',538,445,10,'bold'),line(532,479,724,479),'</g>']
a += ['<g id="historic-membership-options">',box(36,504,282,61),line(36,535,318,535),line(278,504,278,535),text('$10.00',49,527,20,'bold'),text('Per',153,516,10,'bold'),text('Year',153,528,10,'bold'),text('VOTING MEMBER',177,556,16,'bold',250,True),box(362,504,362,61),line(362,535,724,535),line(686,504,686,535),text('Supporter $5.00',522,527,20,'bold',308,True),text('NON-VOTING',543,556,16,'bold',320,True),'</g>']
a += ['<g id="declaration-and-signature">',text('I declare to be 19 years of age or over,',36,589,12),text('and a resident of British Columbia.',36,605,12),line(362,620,724,620),text('Signature',543,636,11,'regular',center=True),line(36,681,245,681),text('198',251,683,16),line(282,681,318,681),line(362,681,724,681),text('On behalf of the Interior University Society',543,699,11,'regular',center=True),'</g>']
m1=write('ius-membership-card-reconstructed',a,728,'Geometrically rebuilt membership card, with $10 per year voting-member and $5 non-voting-supporter choices as visible in the supplied historical photographs. The small original statement-of-support body is omitted because it cannot be transcribed confidently. Historic artwork for reference, not a current registration or payment form.')

# Supporter-only variant, photographed on right side of yellow petition spread.
a=base(635)
a += ['<g id="supporter-fields">',text('RECEIVED FROM MR. MRS. MS.   (LAST NAME)',36,169,11,'bold'),cells(36,176,20,34.4),text('GIVEN NAMES',36,218,10,'bold'),cells(36,224,20,34.4),text('ADDRESS',36,266,10,'bold'),cells(36,272,20,34.4),text('CITY',36,314,10,'bold'),cells(36,320,20,34.4),text('POSTAL CODE',36,362,10,'bold'),cells(36,368,6,34.4),'</g>']
a += ['<g id="historic-supporter-option">',box(36,428,330,62),line(36,459,366,459),line(328,428,328,459),text('Supporter $5.00',184,452,20,'bold',275,True),text('NON-VOTING',201,481,16,'bold',300,True),text('I declare to be 19 years of age or over,',400,446,12,'regular',323),text('and a resident of British Columbia.',400,463,12,'regular',323),'</g>']
a += ['<g id="date-and-signature">',line(36,570,245,570),text('198',251,572,16),line(282,570,318,570),line(400,570,724,570),text('Signature',562,590,11,'regular',center=True),'</g>']
m2=write('ius-supporter-card-reconstructed',a,635,'Rebuilt supporter-only form from the right-hand panel of the photographed yellow petition spread. $5 NON-VOTING wording is transcribed. Fine statement microcopy is omitted, and cell counts are approximate. Historic artwork for reference, not a current registration form.')
(ROOT.parent/'source'/'forms_metadata.json').write_text(json.dumps({'assets':[m1,m2],'display_note':'These forms intentionally leave the original fine-print statement area blank. See metadata; no reconstructed sentence is presented as archival transcription.'},indent=2))
print('Built two source-derived form SVGs')
