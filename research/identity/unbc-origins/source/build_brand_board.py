from pathlib import Path
import json,struct
from vector_utils import *
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'guide';OUT.mkdir(exist_ok=True)
INK='#1D1D1B';PAPER='#F7F5EF';GRAY='#68655F';ORANGE='#D17A42'
palette=[('Print orange','#D17A42'),('Ink','#1D1D1B'),('Warm paper','#F2ECD9'),
         ('Pin enamel','#C7722D'),('Pin burgundy','#78353A'),('Pale metal','#D8D4C8'),
         ('Button orange','#DE8D3F'),('Sticker yellow','#EDC367'),('Label blue','#37647A'),
         ('Label grey','#A8AA9D'),('Letterhead rose','#BD606A'),('Yes-button cream','#F1E4C5')]

def build():
    body=rect(0,0,1400,1950,PAPER,'board-background')
    body+=text_paths('HISTORICAL IDENTITY / VECTOR RECONSTRUCTION',66,52,14,font='sans',fill=GRAY,ident='board-kicker')
    body+=text_paths('INTERIOR UNIVERSITY SOCIETY',66,92,40,font='bold',width=1268,ident='board-title')
    body+=text_paths('Rebuilt from the supplied photographs. Editable paths, geometric shapes and outlined lettering.',66,155,16,font='sans',ident='board-subtitle')
    body+=rule(66,202,1334,202,INK,1.6)
    body+=text_paths('01 / SOURCE PRINT MARK',66,233,14,font='bold',ident='primary-label')
    body+=place_svg(ROOT/'svg/ius-print-colour.svg',132,288,1136,672,'primary-artwork')
    body+=text_paths('Right-aligned words. Stepped, bevelled bars. The bars extend beyond the lettering.',66,984,15,font='sans',fill=GRAY,ident='primary-note')
    body+=rule(66,1031,1334,1031,INK,1.2)
    body+=text_paths('02 / PIN AND CAMPAIGN BUTTONS',66,1062,14,font='bold',ident='badges-label')
    body+=place_svg(ROOT/'svg/ius-enamel-pin.svg',66,1110,385,285,'pin-artwork')
    body+=place_svg(ROOT/'svg/northern-u-button.svg',546,1108,285,285,'northern-artwork')
    body+=place_svg(ROOT/'svg/say-yes-button.svg',1018,1108,285,285,'yes-artwork')
    for t,x in [('Enamel pin',66),('Northern U',546),('University campaign button',1018)]:
        body+=text_paths(t,x,1428,15,font='bold',ident='badge-label-'+str(x))
    body+=text_paths('Flat vector metal and enamel',66,1461,12,font='sans',fill=GRAY,ident='pin-note')
    body+=text_paths('Outlined serif lettering',546,1461,12,font='sans',fill=GRAY,ident='northern-note')
    body+=text_paths('Collegiate outlines and curved type',1018,1461,12,font='sans',fill=GRAY,ident='yes-note')
    body+=rule(66,1510,1334,1510,INK,1.2)
    body+=text_paths('03 / SUPPORTER AND CONTACT STICKERS',66,1540,14,font='bold',ident='stickers-label')
    body+=place_svg(ROOT/'svg/i-support-interior-university-sticker.svg',66,1587,696,194,'bumper-artwork')
    body+=place_svg(ROOT/'svg/call-toll-free-sticker.svg',828,1603,506,160,'contact-artwork')
    body+=text_paths('Approximate reconstruction colours',66,1825,12,font='sans',fill=GRAY,ident='colour-note')
    for i,(name,color) in enumerate(palette[:6]):
        x=66+i*211.4;body+=rect(x,1860,66,28,color,'swatch-'+str(i))
        body+=text_paths(name,x+79,1868,9.5,font='sans',ident='swatch-name-'+str(i))
    body+=text_paths('26 SVG masters + PDF / EPS / PNG exports. Original typefaces and precise colours remain unconfirmed.',66,1920,12,font='sans',fill=GRAY,ident='board-footer')
    (OUT/'IUS_Brand_Board.svg').write_text(svg_doc(1400,1950,body,'Interior University Society - vector brand board','All artwork on this board is real vector geometry. A contemporary reconstruction based on supplied source photographs, not an original historical standards manual.'))
    pal=ROOT/'palette';pal.mkdir(exist_ok=True)
    (pal/'ius-colours.json').write_text(json.dumps({'status':'Approximate sRGB reconstruction colours; not official measured specifications.','colours':[{'name':n,'hex':c} for n,c in palette]},indent=2))
    gpl='GIMP Palette\nName: Interior University Society reconstruction\nColumns: 6\n# Approximate sRGB values.\n'
    css='/* Approximate reconstruction colours, not official standards. */\n:root {\n'
    blocks=[]
    for n,h in palette:
        rgb=[int(h[i:i+2],16) for i in (1,3,5)]
        gpl+=' '.join(str(v) for v in rgb)+'\t'+n+'\n'
        css+='  --ius-'+n.lower().replace(' ','-').replace('-button','-button')+': '+h+';\n'
        raw=(n+'\0').encode('utf-16-be')
        content=struct.pack('>H',len(n)+1)+raw+b'RGB '+struct.pack('>fff',*(v/255 for v in rgb))+struct.pack('>H',2)
        blocks.append(struct.pack('>HI',1,len(content))+content)
    (pal/'ius-colours.gpl').write_text(gpl);(pal/'ius-colours.css').write_text(css+'}\n')
    (pal/'ius-colours.ase').write_bytes(b'ASEF'+struct.pack('>HHI',1,0,len(blocks))+b''.join(blocks))

if __name__=='__main__':build();print('Built vector board and palettes')
