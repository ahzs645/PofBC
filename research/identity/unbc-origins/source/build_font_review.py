"""Build the font audit from labelled source/candidate comparison boards.

The report contains photographic evidence and rendered comparison previews.
Production assets remain in svg/, pdf/ and eps/ as independent vector files.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/font-audit'
W,H=612,792
INK='#1D1D1B'; MUTED='#625F58'; RULE='#DAD5CA'; PAPER='#F7F5EF'; ORANGE='#D17A42'
pdfmetrics.registerFont(TTFont('Audit','/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('AuditBold','/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf'))
c=canvas.Canvas(str(ROOT/'IUS_Font_Review.pdf'),pagesize=(W,H))
c.setTitle('Interior University Society — Font Review, Version 1.2')
c.setAuthor('Prepared from the supplied IUS photographs')
c.setSubject('Visual typography audit, reconstruction fonts, corrections and uncertainty')
page=0

def txt(t,x,y,size=10,bold=False,col=INK):
    c.setFillColor(HexColor(col));c.setFont('AuditBold' if bold else 'Audit',size)
    c.drawString(x,H-y-size,t)

def para(t,x,y,w,size=9,leading=None,col=MUTED):
    st=ParagraphStyle('audit',fontName='Audit',fontSize=size,leading=leading or size*1.45,textColor=HexColor(col))
    p=Paragraph(t,st);_,h=p.wrap(w,900);p.drawOn(c,x,H-y-h);return h

def line(y):
    c.setStrokeColor(HexColor(RULE));c.setLineWidth(.6);c.line(42,H-y,570,H-y)

def start(title,sub):
    global page
    page+=1;c.setFillColor(HexColor('#FFFFFF'));c.rect(0,0,W,H,stroke=0,fill=1)
    c.setFillColor(HexColor(ORANGE));c.rect(42,H-30,28,3,stroke=0,fill=1)
    txt('INTERIOR UNIVERSITY SOCIETY  /  FONT REVIEW',82,21,7.2,True,col=MUTED)
    txt(title,42,49,24,True)
    para(sub,42,87,528,9,13)

def end():
    line(747);txt('SOURCE-LED RECONSTRUCTION  /  VERSION 1.2',42,758,7,col=MUTED)
    txt(f'{page:02d} / 07',531,757,8,True,col=MUTED);c.showPage()

def board(path,y,h):
    im=Image.open(path);s=min(528/im.width,h/im.height)
    dw,dh=im.width*s,im.height*s
    c.drawImage(ImageReader(im),42+(528-dw)/2,H-y-(h+dh)/2,width=dw,height=dh,mask='auto')

# 01: decisions and exact reconstruction-font schedule.
start('Fonts checked. Artwork revised.',
      'The original artifact photographs determine the review. The earlier clean-up images are retained as reference alternatives; they are not independent proof of the historical typefaces.')
txt('Reconstruction font schedule',42,137,13,True)
st=ParagraphStyle('cell',fontName='Audit',fontSize=8,leading=11,textColor=HexColor(INK))
rows=[['Use','Font / lettering in v1.2','Decision'],
      ['Main print logo','Nimbus Sans Bold','Retain; curved R and stroke proportions fit the photographed style.'],
      ['Enamel pin','Fitted Nimbus Sans Bold + optical weight adjustment','Increase black edges by 2% of the original cap height.'],
      ['Toll-free label','URW Bookman Demi; Nimbus Sans Regular for small society text','Replace the previous Times-style label lettering and numerals.'],
      ['Northern U','Custom N + Bookman-derived “orthern”; separate custom U','v1.2: correct N serifs and diagonal. Retain the v1.1 U.'],
      ['YES button','Nimbus Roman Bold + custom geometric and collegiate letters','Condense top heading; round NORTHERN corners.'],
      ['Supporter sticker','Nimbus Roman Bold Italic; Nimbus Sans Narrow Bold','Retain as fitted substitutes; exact cuts unconfirmed.'],
      ['Fundraising letter','Nimbus Roman Regular, Bold and Bold Italic','Restore actual italic display outlines.'],
      ['Invitation / forms','Nimbus Mono PS Regular / Nimbus Sans Regular and Bold','Retain typewriter and sans-serif styles respectively.']]
data=[[Paragraph(s,st) for s in row] for row in rows]
t=Table(data,colWidths=[102,197,229],hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(PAPER)),('LINEBELOW',(0,0),(-1,0),.7,HexColor(INK)),
                      ('LINEBELOW',(0,1),(-1,-1),.4,HexColor(RULE)),('VALIGN',(0,0),(-1,-1),'TOP'),
                      ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                      ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
tw,th=t.wrap(528,500);t.drawOn(c,42,H-164-th)
y=176+th
txt('What the review establishes',42,y,12,True)
y+=25
para('The photographs support the style corrections and the relative shapes shown on the following pages. They do <b>not</b> establish an exact original font family, foundry or cut. Every named font above is the actual working font used to construct the delivered outlines.',42,y,528,9.1,13)
y+=62
para('Also refined: CAMPAIGN now has 82.5% of SUPPORT’s cap height. The invitation preserves the photographed DAHLLOFF / Dahlloff spelling. All affected artwork remains editable vector geometry.',42,y,528,9.1,13)
end()

# 02: equal-cap-height family comparisons.
start('Main mark: retain the font basis.',
      'Nimbus Sans Bold remains the closest practical candidate among the tested local families. The curved R leg, I stem weight and O counter support that choice.')
board(REF/'main/main-font-comparison.png',124,573)
para('The main print fitting changes natural word width by only +0.45% to +1.48%. “Helvetica-like” is a visual family assessment; Nimbus Sans is the actual substitute in the kit. Full-size candidate boards and contour measurements accompany this report.',42,707,528,8,11)
end()

# 03: controlled pin weight experiment.
start('Pin: a separate optical weight.',
      'The metal-and-enamel object has a heavier apparent black inlay than the print logo. The photographs also include reflections and relief shadows.')
board(REF/'main/pin-weight-trials.png',129,486)
txt('Adopted: Trial A (+0.020 cap height per edge)',42,635,12,True)
para('Version 1.1 applies a 4.32-unit black outline around the original 108-unit cap-height glyphs, while retaining the metal backing. The same adjustment is used in the one-colour pin adaptation. The earlier “current vector” on this board is version 1.0.',42,661,528,9,13)
para('The base pin words remain horizontally fitted to about 86–88% of their natural widths. This is an optical reconstruction choice, not evidence for a named historical condensed or black cut.',42,709,528,8,11)
end()

# 04: preserved v1.0-to-v1.1 campaign before/after proof.
start('Campaign review: v1.0 to v1.1.',
      'These panels preserve the first font-review changes, with source photographs at left. The later v1.2 correction to the orange button’s capital N is shown separately on page 7.')
board(REF/'campaign/06-campaign-before-after.png',122,580)
para('v1.1 changed toll-free lettering to Bookman Demi, drew a separate U, condensed the YES heading and rounded NORTHERN corners. The Bookman-derived N visible in this historical comparison is superseded by the v1.2 proof on page 7.',42,713,528,8,11)
end()

# 05: application corrections.
start('Applications: restore the italics.',
      'The fundraising display is visibly italic beside upright questions and body text on the same photographed page. The revised artwork uses true italic font outlines.')
board(REF/'applications-before-after.png',126,520)
txt('Other typography reviewed',42,665,12,True)
para('The invitation’s monospaced slab-serif style remains Nimbus Mono PS Regular. Small form-label spacing and the sweatshirt’s obscured lower line cannot be identified precisely from the photographs. The sweatshirt remains explicitly interpretive.',42,691,528,9,13)
end()

# 06: evidence, methodology and precise limits.
start('Evidence, sources and editing.',
      'This review separates what is visible in an artifact from the substitute font used to rebuild it.')
txt('How the comparison was made',42,131,13,True)
y=159
for head,body in [
    ('1. Original sources first.', 'Print logo: IMG_7953(1).jpeg and IMG_7950.jpeg. Pin: IMG_7956(2).jpeg. Buttons and bumper sticker: IMG_7955(1).jpeg and IMG_7950.jpeg. Toll-free labels: IMG_7952.jpeg. The earlier raster reconstructions are not font-identification evidence.'),
    ('2. Control size before judging shape.', 'Candidates were compared at equal cap or ink heights and their natural widths. Where a source-span fit was also shown, it was labelled separately. Important comparisons included R legs, O counters, U bowls, serif construction, stroke mass and italic forms.'),
    ('3. Keep uncertainty visible.', 'Perspective corrections are approximate. Blur, curved button faces, glass reflections, raised metal and ink spread affect apparent weight. A plausible digital substitute is not proof of the original commercial family, weight or foundry.'),
    ('4. Preserve editable production files.', 'Revised SVGs use font outlines and deliberate geometry. No font binaries are bundled; no installed font is needed to open, scale or recolour the masters. Re-typesetting changed wording requires the authoring fonts or another deliberate font choice.')]:
    txt(head,42,y,10,True);y+=19
    y+=para(body,42,y,528,8.7,12.5)+17
line(y);y+=17
txt('Primary type-family references',42,y,12,True);y+=25
refs=[
    ('URW Base35 package documentation', 'https://ctan.org/tex-archive/fonts/urw/base35?lang=en', 'Documents Nimbus Sans / Helvetica, Nimbus Roman / Times and Nimbus Mono / Courier substitution relationships. It does not identify the fonts in the IUS photographs.'),
    ('Artifex Nimbus Sans font configuration', 'https://github.com/ArtifexSoftware/urw-base35-fonts/blob/master/fontconfig/urw-nimbus-sans.conf', 'Explicit mappings for Nimbus Sans and Nimbus Sans Narrow.'),
    ('Monotype / Linotype: Eurostile Next', 'https://www.myfonts.com/pages/linotype-eurostile-next', 'Background on the squared, extended Microgramma / Eurostile family. This is a stylistic comparator for NORTHERN, not a verified original identification.')]
for title,url,desc in refs:
    h=para(f'<b><link href="{url}" color="#89512D">{title}</link></b> — {desc}',42,y,528,8.1,11.5);y+=h+11
para('The complete font schedule is in FONT_NOTES.md. Additional full-size comparison boards and metrics are in reference/font-audit/. The photographs and report previews are evidence material; production SVG/PDF/EPS files remain vector artwork.',42,707,528,8,11)
end()

# 07: focused v1.1-to-v1.2 Northern capital-N proof.
start('Northern: correct the capital N.',
      'Version 1.2 changes the initial N on the orange button. The fitted Bookman-derived “orthern” and the separately drawn large U retain their v1.1 treatment.')
board(REF/'northern-n/Northern_N_Detail.png',127,440)
txt('An independently constructed vector letter',42,589,13,True)
para('The earlier Bookman-derived N has thick slab serifs and a heavy diagonal. The original photograph instead supports thinner tapered serifs, a lighter diagonal and a top-right serif that projects mainly to the left. The new N follows those visible structural differences.',42,618,528,9.1,13)
para('The letter is deliberately drawn as editable geometry, without automatic bitmap tracing. The remaining word is still a fitted Bookman-derived substitute. This focused correction does not establish the exact original typeface or a complete recovered alphabet.',42,686,528,8.5,12)
end();c.save()
print('Built 7-page font review:',ROOT/'IUS_Font_Review.pdf')
