"""Build an illustrated brand guide with vector PDF placements and source photos.
ReportLab draws document typography; pypdf places genuine vector asset PDFs.
Only the explicitly labelled source photographs are raster content.
"""
from pathlib import Path
import io,json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader,PdfWriter,Transformation
from PIL import Image
from build_brand_board import palette

ROOT=Path(__file__).resolve().parents[1];G=ROOT/'guide'
W,H=842,595;INK='#1D1D1B';GRAY='#66645F';LIGHT='#E4E1D8';PAPER='#F6F3EB';ORANGE='#D17A42'
pdfmetrics.registerFont(TTFont('Guide','/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('GuideBold','/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf'))
buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H));placements=[];page_no=0

def color(h):return HexColor(h)
def box(x,y,w,h,fill=None,stroke=None,sw=1):
    if fill:c.setFillColor(color(fill))
    if stroke:c.setStrokeColor(color(stroke));c.setLineWidth(sw)
    c.rect(x,H-y-h,w,h,fill=bool(fill),stroke=bool(stroke))
def line(x,y,x2,y2,col=LIGHT,sw=1):
    c.setStrokeColor(color(col));c.setLineWidth(sw);c.line(x,H-y,x2,H-y2)
def txt(t,x,y,size=10,bold=False,col=INK):
    c.setFont('GuideBold' if bold else 'Guide',size);c.setFillColor(color(col));c.drawString(x,H-y-size,t)
def para(t,x,y,w,size=10,leading=None,col=GRAY):
    style=ParagraphStyle('p',fontName='Guide',fontSize=size,leading=leading or size*1.45,textColor=color(col),spaceAfter=0)
    p=Paragraph(t,style);_,h=p.wrap(w,700);p.drawOn(c,x,H-y-h);return h
def label(t,x,y):txt(t,x,y,9,True,col=GRAY)
def asset(name,x,y,w,h):placements.append((page_no-1,name,x,y,w,h))
def photo(name,x,y,w,h):
    p=ROOT/'reference'/name;im=Image.open(p);s=min(w/im.width,h/im.height)
    dw,dh=im.width*s,im.height*s;c.drawImage(ImageReader(im),x+(w-dw)/2,H-y-(h+dh)/2,width=dw,height=dh,mask='auto')
def start(title,sub=''):
    global page_no
    page_no+=1;box(0,0,W,H,'#FFFFFF');box(42,27,26,3,ORANGE)
    txt('INTERIOR UNIVERSITY SOCIETY',80,21,8,True,col=GRAY)
    txt(title,42,49,25,True)
    if sub:para(sub,42,87,758,9.5,13)
def end():
    line(42,557,800,557)
    txt('HISTORICAL IDENTITY RECONSTRUCTION  /  VERSION 1.2',42,568,7,col=GRAY)
    txt(f'{page_no:02d} / 13',758,567,8,True,col=GRAY);c.showPage()

# 01. Cover and scope.
start('A working vector kit.', 'Reconstructed from six original photographs and four supplied clean-up references.')
asset('ius-print-colour',52,151,492,291)
box(590,128,210,373,PAPER)
txt('26 editable assets',610,150,18,True)
para('Logos, pin artwork, campaign buttons, stickers, stationery, forms and supporting illustrations.',610,188,168,10,15)
for i,(a,b) in enumerate([('SVG','Editable artwork masters'),('PDF / EPS','Scalable print exports'),('PNG','Transparent quick-use copies'),('HTML','Offline visual catalogue')]):
    txt(a,610,267+i*46,10,True);txt(b,610,284+i*46,8.5,col=GRAY)
para('The masters are constructed from outlined type, geometric shapes and deliberate curves. They contain no embedded photographs or live font dependencies.',52,472,492,10.5,15)
end()

# 02. Source comparison.
start('The photographs set the geometry.', 'Original artifacts are the main reference; earlier clean-up images are retained as separate alternatives.')
label('P04 / PHOTOGRAPHED PRINT',42,119);label('REBUILT PRINT MASTER',442,119)
photo('print-mark-detail.png',42,142,344,188);asset('ius-print-colour',442,142,358,188)
para('The stepped bars project beyond the word endings. The original printed letters are wider than the earlier condensed interpretations.',42,345,758,10,14)
label('P06 / ENAMEL PIN',42,390);label('FLAT VECTOR RECONSTRUCTION',255,390)
photo('pin-rectified.png',42,411,178,130);asset('ius-enamel-pin',255,411,176,130)
para('The pin has a clipped lower-left corner and pale metal around the black letters and burgundy bars. Version 1.1 increases the black letter weight slightly; metal remains within the O and R counters.',480,407,320,10,15)
end()

# 03. Construction.
start('A consistent construction.', 'The values below are reconstruction coordinates fitted to the photographed brochure, not recovered historical specifications.')
box(48,133,498,310,None,LIGHT)
asset('ius-print-colour',71,150,452,267)
c.setDash(3,3);line(490,143,490,430,'#B8B2A6',0.8);c.setDash()
txt('Words share a right edge.',72,451,10,True)
para('The bars continue 66 units farther. Each bar is one quadrilateral with a 45-degree leading cut.',72,474,450,9.5,14)
txt('Working geometry',582,131,15,True)
rows=[('Content width','1000 units'),('Cap height','107 units'),('Row pitch','207 units'),('Text right edge','934 units'),('Word widths','690 / 880 / 640'),('Bar height','44 units'),('Bar starts','0 / 174 / 338'),('Bar-to-type gap','23 units')]
for i,(a,b) in enumerate(rows):
    yy=169+i*34;txt(a,582,yy,9,col=GRAY);txt(b,710,yy,9,True)
para('A four-unit export buffer protects curved-letter overshoot. It is not the suggested clear space around a placed logo.',582,461,218,9,13)
end()

# 04. Reproductions and reference variants.
start('Reproduction variants.', 'The primary print family preserves one geometry. Compact and extended reference layouts remain separately labelled.')
variants=[('ius-print-colour','SOURCE PRINT / COLOUR'),('ius-print-black','SOURCE PRINT / SINGLE BLACK'),
          ('ius-print-white','SOURCE PRINT / WHITE, TRANSPARENT'),('ius-reference-compact','REFERENCE ALTERNATIVE / COMPACT'),
          ('ius-reference-extended','REFERENCE ALTERNATIVE / EXTENDED'),('ius-three-bars','SEPARATE BAR COMPONENT')]
for i,(name,cap) in enumerate(variants):
    x=42+(i%2)*398;y=125+(i//2)*137
    label(cap,x,y)
    if name=='ius-print-white':box(x,y+22,360,102,INK)
    asset(name,x+12,y+28,336,90)
para('The white file has no background. A separate reversed-panel file includes the dark rectangle. The reference alternatives reproduce the supplied clean-up directions; they are not additional authenticated historical logos.',42,532,758,8.3,11.5)
end()

# 05. Physical artifacts.
start('Pins and campaign buttons.', 'Flat artwork separates design from photographic glare, perspective and material reflections.')
asset('ius-enamel-pin',42,140,226,168);asset('northern-u-button',330,126,208,208);asset('say-yes-button',590,126,208,208)
for x,title,note in [(42,'Clipped-corner pin','Orange enamel, black lettering, burgundy bars and pale metal. Includes a one-colour adaptation and a separate silhouette component.'),
                     (330,'Northern U','Version 1.2 pairs a custom capital N with fitted Bookman-derived “orthern” and a separate custom U. The N corrects the serif and diagonal shapes; the original typeface remains unconfirmed.'),
                     (590,'University button','Condensed serif headings, rounded geometric NORTHERN, collegiate INTERIOR outlines and letters placed around the lower arc.')]:
    txt(title,x,368,14,True);para(note,x,397,210,9.5,14)
para('The photographs provide no physical scale. Pin and button proportions are working estimates; their SVG viewBoxes are not measured tooling dimensions.',42,514,758,9,13)
end()

# 06. Stickers and apparel.
start('Campaign typography.', 'Different artifacts use different lettering families; the kit keeps those differences visible.')
label('SUPPORTER BUMPER STICKER',42,125);asset('i-support-interior-university-sticker',42,151,470,131)
para('Italic serif introduction, condensed uppercase main line and simple underline on yellow stock.',42,299,470,9.5,14)
label('HISTORICAL TOLL-FREE LABEL',42,359);asset('call-toll-free-sticker',42,385,470,149)
para('The printed number is archival content, not a verified current contact.',42,535,470,8.3,11)
txt('Outlined, not font-linked.',560,129,15,True)
para('Lettering is made of editable paths. Individual letters and material regions can be recoloured or adjusted without installing the original fonts.',560,163,240,10,15)
label('OPTIONAL SWEATSHIRT INTERPRETATION',560,287)
asset('interior-university-sweatshirt-interpretive',562,315,236,147)
para('The photograph shows only part of this treatment. The arch, lower word and burgundy colour are interpretive reconstruction choices.',560,480,240,9,13)
end()

# 07. Stationery.
start('Stationery and re-typeset letters.', 'The vertical logo and rose-red top band are visible on the supplied correspondence.')
docs=[('ius-letterhead-template','Letterhead template','Blank working page. The uncertain small historical address block is omitted.'),
      ('ius-invitation-1988-retypeset','8 June 1988 invitation','Visible event wording is re-typeset. The handwritten RSVP oval is omitted.'),
      ('ius-fundraising-letter-retypeset','$100 business appeal','Italic campaign headlines, readable appeal and historical address are re-typeset.')]
for i,(name,title,note) in enumerate(docs):
    x=42+i*261;box(x,126,220,285,'#FFFFFF',LIGHT)
    asset(name,x,126,220,285);txt(title,x,431,12,True);para(note,x,456,220,9.5,14)
para('These are reconstructed applications. Letter paper size, line breaks and substitute type are working choices; historical dates, amounts and contacts are documentary content.',42,520,758,8.5,12)
end()

# 08. Forms.
start('Membership and supporter forms.', 'The grids, labels and visible membership options are rebuilt as editable vector elements.')
asset('ius-membership-card-reconstructed',42,131,358,343)
asset('ius-supporter-card-reconstructed',456,131,344,287)
txt('Membership card',42,493,12,True);para('$10 per year voting member and $5 non-voting supporter choices.',42,516,358,9,13)
txt('Supporter-only form',456,435,12,True)
para('The dense statement-of-support text cannot be read confidently. Its area remains blank. Cell counts and spacing are reconstruction estimates; serials and autographs are omitted.',456,462,344,9.5,14)
end()

# 09. Petition spread.
start('The supporter petition spread.', 'A complete source-derived layout joins the campaign appeal with the supporter form.')
asset('ius-supporter-petition-spread-reconstructed',42,139,758,317)
para('The left panel is re-typeset across the supplied photographs. Reflections and partial occlusion mean punctuation and line breaks are reconstruction choices. The form keeps its unreadable statement area blank. No signature or serial number has been fabricated.',42,488,758,10,15)
end()

# 10. Illustration and brochure.
start('Brochure and graduate illustration.', 'The composition is supported by the photograph; the fine drawing is a new interpretation.')
asset('ius-support-campaign-cover-interpretive',42,130,176,373)
asset('ius-graduates-interpretive',259,130,279,349)
txt('An interpretive redrawing',582,130,15,True)
para('Ten figures retain the broad 2 / 3 / 3 / 2 arrangement, the foreground bareheaded person and the graduate with glasses. Faces, folds and hatching are deliberately redrawn because the image cannot supply exact original detail.',582,164,218,9.5,14)
label('P04 / PHOTOGRAPHED COVER',582,325)
photo('brochure-rectified.png',603,349,143,186)
para('The artwork is labelled interpretive in its filename, SVG description and catalogue. It is not the recovered original artist file.',42,520,496,9,13)
end()

# 11. Palette and letterform choices.
start('A practical reconstruction palette.', 'Approximate sRGB colours. The photographs include aged paper, glass reflections and uncontrolled lighting.')
for i,(name,hx) in enumerate(palette):
    x=42+(i%4)*198;y=129+(i//4)*86
    box(x,y,57,42,hx, LIGHT if hx in ['#F2ECD9','#D8D4C8','#F1E4C5'] else None)
    txt(name,x+70,y+2,9.3,True);txt(hx,x+70,y+24,9,col=GRAY)
line(42,411,800,411)
txt('Working letterforms',42,432,14,True)
para('<b>Print:</b> Nimbus Sans Bold. <b>Pin:</b> separate optical weight adjustment. <b>Campaign:</b> Nimbus Roman, Nimbus Sans Narrow and URW Bookman, plus custom letters. See IUS_Font_Review.pdf for source comparisons; original font identities remain unconfirmed.',42,459,485,10,15)
para('Palette files: Adobe ASE, GIMP GPL, CSS and JSON. No Pantone match or colour-managed CMYK specification is claimed.',580,441,220,10,15)
end()

# 12. Editing and use.
start('Use and edit the kit.', 'The following are new working recommendations for this reconstruction, not an original standards manual.')
txt('Choose the file for the task',42,128,15,True)
formats=[('SVG','Master artwork for shape editing and web use.'),('PDF','Scalable placement in print and document layouts.'),('EPS','Vector exchange with older illustration workflows.'),('PNG','Convenient rendered copy; it is not the vector master.'),('index.html','Search and inspect all 26 assets without a server.')]
for i,(a,b) in enumerate(formats):
    yy=165+i*52;txt(a,42,yy,11,True);para(b,116,yy,292,10,14)
txt('Edit paths and preserve proportions',42,450,13,True)
para('Open the SVG in a vector editor. Ungroup to reach words, letters, bars or material areas. Scale the complete mark uniformly. The outlined masters need no font installation; wording changes require new typesetting or the supplied builder scripts.',42,476,366,9.3,13.5)
txt('Suggested clear space',460,128,15,True)
para('Leave at least one capital height around the complete print mark, measured from the outermost bar. For this construction, that is 107 units on a 1000-unit content width.',460,163,340,10,15)
txt('Small-size starting points',460,261,14,True)
para('Start at 200 px wide on screen or 35 mm in print for the full source mark. Proof the chosen output method and increase size when small gaps or outlines begin to close.',460,294,340,10,15)
asset('ius-print-colour',460,376,244,145)
para('Colour and pin outlines can need more room than a single black reproduction.',726,384,74,8.5,12)
end()

# 13. Sources and limitations.
start('Source index and evidence limits.', 'All ten supplied files are retained in reference/supplied. Original photographs and prior reconstruction images are identified separately.')
rows=[
('P01','IMG_7947.jpeg','Exhibition overview, forms, buttons and stickers'),
('P02','IMG_7950.jpeg','Invitation dated 8 June 1988; YES button'),
('P03','IMG_7952.jpeg','Toll-free stickers and campaign materials'),
('P04','IMG_7953(1).jpeg','Brochure, graduate illustration, sweatshirt'),
('P05','IMG_7955(1).jpeg','Bumper sticker, Northern U, business appeal'),
('P06','IMG_7956(2).jpeg','Enamel pin close-up'),
('R01','3840431D-FB14-4CD2-A30C-6D868DDDEE7C.jpeg','Prior reconstruction board'),
('R02','B4E31A32-20F0-444B-A017-ABD644E9B08D.jpeg','Prior white-background logo reconstruction'),
('R03','1B984201-883D-4DBB-A32D-153BC2AFB6E1.png','Prior transparent logo reconstruction'),
('R04','F7B0189A-D6D4-4CB3-B2E8-9AE3FD44EC01.png','Prior heavy transparent reconstruction')]
label('ID',42,122);label('SUPPLIED FILE',85,122);label('PRIMARY USE',435,122)
line(42,141,800,141)
for i,(a,b,d) in enumerate(rows):
    yy=152+i*29;txt(a,42,yy,8.7,True);txt(b,85,yy,7.8);txt(d,435,yy,8.3,col=GRAY);line(42,yy+23,800,yy+23,LIGHT,0.5)
para('The invitation is direct evidence that the identity was used for an event dated 8 June 1988. It does not establish the original design date. The visible archive accession 1992.2 is an archival reference, not a creation date.',42,461,758,9.5,14)
para('No original vector files, font identification, measured colour targets or manufacturing dimensions were supplied. Every asset records its reconstruction status. Photographic inspection crops belong to the reference folder; they are never embedded in production SVG masters.',42,513,758,8.5,12)
end()

c.save();buf.seek(0);reader=PdfReader(buf);writer=PdfWriter()
cache={}
for i,page in enumerate(reader.pages):
    for pi,name,x,y,w,h in placements:
        if pi!=i:continue
        if name not in cache:cache[name]=PdfReader(ROOT/'pdf'/(name+'.pdf'))
        art=cache[name].pages[0]
        aw,ah=float(art.mediabox.width),float(art.mediabox.height)
        s=min(w/aw,h/ah);tx=x+(w-aw*s)/2;ty=H-y-h+(h-ah*s)/2
        page.merge_transformed_page(art,Transformation().scale(s,s).translate(tx,ty))
    writer.add_page(page)
writer.add_metadata({'/Title':'Interior University Society - Vector Brand Guide','/Author':'Prepared for Ahmad Jalil','/Subject':'Historical identity reconstruction from supplied photographs','/Keywords':'IUS, Interior University Society, vector, reconstruction, brand kit'})
with (ROOT/'IUS_Brand_Guide.pdf').open('wb') as f:writer.write(f)
print('Built',len(writer.pages),'page vector brand guide')
