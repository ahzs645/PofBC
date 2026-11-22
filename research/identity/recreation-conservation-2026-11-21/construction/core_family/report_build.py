from pathlib import Path
import io, json, html, re
from PIL import Image, ImageDraw, ImageFont
import fitz, cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, Color, white

BASE=Path('/workspace/scratch/450a952ae3f7')
QA=BASE/'research/report_qa'; QA.mkdir(parents=True,exist_ok=True)
OUT=BASE/'output/BC_Recreation_Conservation_Research_and_Overlay_Review.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=landscape(A4)
M=42
PAPER='#F5F3EA';GREEN='#173B32';TEXT='#283B33';MUTED='#54645B';LINE='#C4CCC0';LIGHT='#E6EADF'
fonts=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('Body',str(fonts)))
pdfmetrics.registerFont(TTFont('BodyBold',str(fonts.with_name('DejaVuSans-Bold.ttf'))))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
STYLES={}
def style(size=10,lead=None,color=TEXT,bold=False):
 k=(size,lead,color,bold)
 if k not in STYLES:STYLES[k]=ParagraphStyle(str(k),fontName='BodyBold' if bold else 'Body',fontSize=size,leading=lead or size*1.45,textColor=HexColor(color),spaceAfter=0,allowWidows=0,allowOrphans=0)
 return STYLES[k]
C=canvas.Canvas(str(QA/'report_base.pdf'),pagesize=(W,H))
C.setTitle('BC Recreation and Conservation - Research and Overlay Review')
C.setAuthor('Historical graphic reconstruction prepared for Ahmad Jalil')
C.setSubject('Five reconstructed branch identities, source comparisons and historical evidence')
placements=[];PAGE=0

def text(x,top,s,size=10,color=TEXT,bold=False):
 C.setFillColor(HexColor(color));C.setFont('BodyBold' if bold else 'Body',size);C.drawString(x,H-top-size*.83,s)
def para(x,top,s,width,size=10,lead=None,color=TEXT,bold=False):
 s=s.replace('F&W','F&amp;W')
 p=Paragraph(s,style(size,lead,color,bold));_,h=p.wrap(width,H);p.drawOn(C,x,H-top-h);return h
def line(x1,t1,x2,t2,color=LINE,width=.7):
 C.setStrokeColor(HexColor(color));C.setLineWidth(width);C.line(x1,H-t1,x2,H-t2)
def rect(x,top,w,h,fill=PAPER,stroke=None,radius=0):
 C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(stroke or fill));
 if radius:C.roundRect(x,H-top-h,w,h,radius,stroke=bool(stroke),fill=1)
 else:C.rect(x,H-top-h,w,h,stroke=bool(stroke),fill=1)
def image(path,x,top,w,h,contain=True):
 im=Image.open(path);iw,ih=im.size
 if contain:
  scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;x+=(w-dw)/2;top+=(h-dh)/2;w,h=dw,dh
 C.drawImage(str(path),x,H-top-h,w,h,mask='auto',preserveAspectRatio=False)
def svg(path,x,top,w,h):placements.append((PAGE,Path(path),fitz.Rect(x,top,x+w,top+h)))
def link(x,top,label,url,width=500,size=9):
 para(x,top,f'<link href="{html.escape(url,quote=True)}" color="{GREEN}">{html.escape(label)}</link>',width,size=size,lead=size*1.35)
def base(section,title,sub='',title_size=26):
 global PAGE
 C.setFillColor(HexColor(PAPER));C.rect(0,0,W,H,fill=1,stroke=0)
 text(M,28,'BC RECREATION & CONSERVATION',9,GREEN,True)
 C.setFont('Body',8.5);C.setFillColor(HexColor(MUTED));C.drawRightString(W-M,H-35,section.upper())
 text(M,61,title,title_size,GREEN,True)
 if sub:para(M,99,sub,W-2*M,size=10.5,color=MUTED)
 line(M,122,W-M,122)
 # footer stays clear of all content
 line(M,H-38,W-M,H-38)
 text(M,H-25,'Historical reconstruction  |  Research checked 21 November 2026',8,MUTED)
 C.setFont('Body',8);C.drawRightString(W-M,H-(H-25)-7,f'{PAGE+1:02d} / 09')
def end():
 global PAGE
 C.showPage();PAGE+=1

def overlay_path(n,fallback):
 p=BASE/f'output/package/review/{n}_overlay.png'
 return p if p.exists() else BASE/fallback

marks=[
 {'id':'department','name':'Department of Recreation and Conservation','short':['Department','Recreation and Conservation'],'svg':BASE/'components/core/department.svg','ref':BASE/'components/core/department_reference.png','fallback':'components/core/department_overlay.png','source':'1973 report, printed 1974  |  Marine Resources divider: AA143 / PDF 144','source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf#page=144','caption':'Four lobes and central circle','construction':'A compound field with five transparent openings. One lobe is rotated through four positions, retaining the square outer corners and curved junctions at the central ring.','review':'The overlay checks the central circle, lobe shoulders, narrow connecting bridges and enclosing silhouette. Slight asymmetry and print spread in the scan are regularized.','limit':'The four-lobe meaning is unverified. No original construction drawing or ink specification was located.','metric':.9047},
 {'id':'fishwildlife','name':'Fish and Wildlife Branch','short':['Fish and Wildlife','Deer-and-fish square'],'svg':BASE/'components/fishwildlife/fishwildlife.svg','ref':BASE/'components/fishwildlife/reference.png','fallback':'components/fishwildlife/fishwildlife_overlay.png','source':'1971 report, printed 1972  |  Branch divider: DD15 position / PDF 16','source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf#page=16','caption':'Overlapping fish and antlered deer','construction':'Separate fish-body, gill, deer face, ear, neck and branched-antler curves. The eyes and tail junction are independent editable details; the frame covers intended line endpoints.','review':'Three inspected constructions refined the fish flank, antler fork, ear, muzzle and neck. The overlay excludes a thin horizontal scanner rule from quantitative comparison.','limit':'Fine eyes and antler joins remain interpretations at this scan resolution. No species identification is asserted.','metric':.8681},
 {'id':'parks','name':'Provincial Parks Branch','short':['Provincial Parks','Paired spirals'],'svg':BASE/'components/core/parks.svg','ref':BASE/'components/core/parks_reference.png','fallback':'components/core/parks_overlay.png','source':'1971 report, printed 1972  |  Branch divider: DD63 position / PDF 64','source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf#page=64','caption':'Mirrored spirals on upright stems','construction':'One deliberately drawn, tapering spiral is mirrored to form its partner. Both stems join the rounded frame, with the narrow central gap preserved.','review':'Compared the outer spiral arcs, white channels, inner terminals, stem spacing and border joins. Mirroring removes small reproduction differences between the source halves.','limit':'A fern or other botanical interpretation is plausible but not established by an official explanation.','metric':.9019},
 {'id':'museum','name':'British Columbia Provincial Museum','short':['Provincial Museum','BCPM monogram'],'svg':BASE/'components/museum/museum.svg','ref':BASE/'components/museum/source_crop.png','fallback':'components/museum/overlay.png','source':'1971 report, printed 1972  |  Museum divider: DD97 position / PDF 98','source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf#page=98','caption':'Shared-stroke BCPM monogram','construction':'Custom B and P bowls, shared vertical stems, a closed C outline with horizontal terminals, and two M diagonals. The four letters are geometry, with no font dependency.','review':'Refined the C terminals, M apex and diagonal alignment; closed unintended gaps at the central four-letter junction and the upper B/frame connection.','limit':'The small printed reference is 208 x 210 pixels. Handbook colour variants do not establish exact historic ink values.','metric':.9055},
 {'id':'fisheries','name':'Commercial Fisheries / Marine Resources','short':['Commercial Fisheries','Later Marine Resources'],'svg':BASE/'components/core/fisheries.svg','ref':BASE/'components/core/fisheries_reference.png','fallback':'components/core/fisheries_overlay.png','source':'1973 report, printed 1974  |  Marine Resources divider: AA143 / PDF 144','source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf#page=144','caption':'Three fish crossed by a grid','construction':'A single fish master, including eye and gill, is reused three times. Two vertical and two horizontal grid lines sit above the fish, within a separate rounded-square frame.','review':'The tail profile, body taper, gill scale, row spacing and crossing grid were compared with the source. Repetition restores an internally consistent three-fish arrangement.','limit':'Both branch names use this same symbol. Interpreting the grid as a fishing net remains unconfirmed.','metric':.8346},
]

# 1. Cover and vector overview
base('Overview','A family of five marks','Geometric reconstruction, registered comparisons and historical evidence',title_size=32)
col=(W-2*M)/5
for i,m in enumerate(marks):
 x=M+i*col
 text(x,150,f'{i+1:02d}',9,MUTED,True)
 svg(m['svg'],x+9,178,125,125)
 text(x+5,323,m['short'][0],10,GREEN,True)
 para(x+5,343,m['short'][1],col-15,size=8.8,lead=12,color=MUTED)
rect(M,394,W-2*M,129,GREEN)
for i,(h,t) in enumerate([
 ('SOURCE','Official annual-report specimens, checked against the supplied screenshots and the museum handbook reference.'),
 ('METHOD','Editable curves, repeated geometry and shared strokes; each mark compared with a registered raster reference.'),
 ('STATUS','New historical reconstructions. Original vector masters, exact ink values, designer credits and first-use dates remain unverified.')]):
 x=M+20+i*((W-2*M-40)/3)
 text(x,414,h,8.5,'#D9E4D5',True)
 para(x,435,t,(W-2*M-70)/3,size=10,lead=14.5,color='#FFFFFF')
text(M,536,'Five symbol masters. Black is neutral; the green used in this report is an editorial colour.',8.5,MUTED)
end()

# 2-6. Individual comparison studies
for i,m in enumerate(marks):
 base(f'Study {i+1} of 5',m['name'],m['caption'],title_size=25 if m['id']=='department' else 26)
 xs=[M,310,578];S=222
 for x,l in zip(xs,['01  SOURCE SCAN','02  RECONSTRUCTED VECTOR','03  REGISTERED OVERLAY']):text(x,138,l,8.7,GREEN,True)
 for x in xs:rect(x,159,S,S,'#FFFFFF')
 image(m['ref'],xs[0]+2,161,S-4,S-4)
 svg(m['svg'],xs[1]+2,161,S-4,S-4)
 op=overlay_path(m['id'],m['fallback'])
 image(op,xs[2]+2,161,S-4,S-4)
 consistent=(BASE/f'output/package/review/{m["id"]}_overlay.png').exists() or m['id'] in ['department','parks','fisheries']
 legend=[('#EB4A72','Source only'),('#32A0CF','Vector only'),('#27313B','Shared ink')] if consistent else ([('#00A9D9','Source only'),('#F96343','Vector only'),('#27313B','Shared ink')])
 for j,(c,l) in enumerate(legend):
  rect(M+j*130,396,9,9,c);text(M+15+j*130,395,l,8.5,MUTED)
 text(578,395,'Small printed glyph: about 210 native pixels',8.0,MUTED)
 para(M,424,'<b>Construction.</b> '+m['construction'],472,size=9.4,lead=13.2)
 para(M,471,'<b>Review.</b> '+m['review'],472,size=9.4,lead=13.2)
 rect(550,420,250,92,LIGHT)
 text(564,431,'INTERPRETATION LIMIT',8.1,GREEN,True)
 para(564,450,m['limit'],221,size=9,lead=12.8)
 text(M,527,m['source'],8.3,MUTED)
 link(M,541,'Open the official source page',m['source_url'],500,size=8.3)
 end()

# 7. History
base('Historical findings','What the reports establish','Report year and printing year are separate dates. Sources [1]-[5] are indexed on page 9.')
x=M;left=455
rows=[
 ('1970 report / printed 1971','The General Administration divider uses an oval dogwood emblem, serif type and a thin rectangular frame. It differs from the following report edition. [2]'),
 ('1971 report / printed 1972','All five marks appear with institutional labels in the coordinated rounded-square arrangement. This dates a printed specimen, not the identity\'s first use. [1]'),
 ('1972 report / printed 1973','The same family continues on the General Administration divider, confirming use across successive annual-report editions. [3]'),
 ('1973 report / printed 1974','Commercial Fisheries is renamed Marine Resources, with the three-fish mark retained. The interior dividers incorporate the later two-panel F&W identity. [4]')]
y=146
for h,t in rows:
 text(x,y,h,12,GREEN,True);para(x,y+24,t,left,size=10.1,lead=14.6);line(x,y+82,x+left,y+82);y+=95
rect(527,146,273,376,LIGHT)
text(545,165,'MEANING AND AUTHORSHIP',10,GREEN,True)
y=190
for heading,t in [
 ('No confirmed designer','No direct credit, commission record or identity manual was located for the five-mark family.'),
 ('Jean André: a research lead','The 1969 report names him Chief Designer in the museum\'s Display Division. Publication graphics appear among that division\'s 1971 work. Neither passage attributes these marks. [1,5]'),
 ('Parks proposal: a separate lead','AA105 / PDF 106 describes a December 1973 logo proposal without its drawing or designer. It cannot date the spirals already present in the earlier report. [4]')]:
 text(545,y,heading,9.6,GREEN,True);h=para(545,y+18,t,235,size=9.4,lead=13.3);y+=h+36
text(M,535,'Four branches, fern fronds and a fishing net are possible readings; no official explanation was found.',8.6,MUTED)
end()

# 8. Related report graphics
base('Related graphics','Other designs found in the reports','These source extracts are documented separately from the five reconstructed marks.')
text(M,142,'01  PARK SIGNAGE',9,GREEN,True)
image(BASE/'research/1971_proposed_park_symbols_crop.png',M,165,273,367)
para(332,145,'<b>22 circular pictograms</b><br/>1971 report: DD67 / PDF 68. The accompanying text says approved signs would begin replacing written signs in 1972, initially at larger park entrances. [1]',205,size=9.8,lead=14)
link(332,257,'View the full symbol sheet','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf#page=68',205,size=9)
text(332,292,'02  PARKS SHIELD',9,GREEN,True)
image(BASE/'research/1973_parks_shield_crop.png',332,315,130,157)
para(471,316,'Dogwood and province silhouette on the Parks organization chart. The spiral mark also appears elsewhere in the same report. [4]',101,size=9.1,lead=13)
text(332,491,'AA79 / PDF 80',8.4,MUTED)
link(332,509,'Open the source page','https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1973.pdf#page=80',235,size=8.8)
text(602,142,'03  LATER F&W',9,GREEN,True)
image(BASE/'research/1973_fw_replacement_crop.png',602,165,198,217)
para(602,401,'The two-panel F&W arrangement takes the older deer-and-fish square\'s position on the 1973 interior dividers. [4]',198,size=9.8,lead=14.3)
text(602,472,'AA21 position / PDF 22',8.4,MUTED)
link(602,491,'Open the source page','https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1973.pdf#page=22',198,size=8.8)
end()

# 9. Sources / methods and limits
base('Sources and limits','A reconstruction with an audit trail','Clickable primary references and the limits of comparison with small printed specimens.')
entries=[
 ('[1]  1971 annual report, printed 1972','PDF 2 imprint; 10 department; 16 F&W; 64 Parks; 98 museum; 126 fisheries. DD67 / PDF 68 signage; DD77 / PDF 78 rollout; DD116 / PDF 117 publication graphics.','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf'),
 ('[2]  1970 annual report, printed 1971','PDF 10: General Administration divider with the earlier oval dogwood emblem and rectangular layout.','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1970.pdf'),
 ('[3]  1972 annual report, printed 1973','PDF 2: imprint. PDF 10: continued use of the coordinated five-mark family.','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1972.pdf'),
 ('[4]  1973 annual report, printed 1974','PDF 2 imprint; 10 renaming; 22 later F&W; 78 spirals; 80 Parks shield; 106 logo proposal; 112 museum; 144 Marine Resources.','https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1973.pdf'),
 ('[5]  1969 annual report, printed 1970','Printed CC58 and CC64: Jean André\'s museum design role. No attribution of this identity family.','https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1969.pdf')]
y=145
for h,t,u in entries:
 text(M,y,h,10.1,GREEN,True)
 hh=para(M,y+19,t,451,size=8.9,lead=12.8)
 link(M,y+21+hh,'Open official report',u,451,size=8.4)
 y+=hh+45
rect(531,145,269,389,LIGHT)
text(548,162,'READING THE OVERLAYS',10,GREEN,True)
items=[
 'Source and vector ink bounds are scaled independently in x and y to a common square. No local warping was used.',
 'Pink marks source-only ink; blue marks vector-only ink; dark areas show shared ink. Scan defects can produce visible differences.',
 'Approximate 210-pixel glyphs cannot support claims of recovered master precision. Enlargement adds no original detail.',
 'The supplied SVGs are new editable constructions with transparent backgrounds. Their black ink is neutral; report green is approximate editorial styling.',
 'This report\'s captions use a modern editorial typeface. They do not reproduce the historical branch lettering.'
]
y=188
for t in items:
 hh=para(548,y,t,235,size=9.3,lead=13.5);y+=hh+13
text(M,535,'Also checked: the supplied screenshots and four-page BCPM handbook visual reference.',8.4,MUTED)
end()
C.save()
# Place actual vector PDFs on top of the report's layout. No rasterization of the recreated logos.
doc=fitz.open(QA/'report_base.pdf')
cache={}
for pi,path,r in placements:
 if path not in cache:
  data=cairosvg.svg2pdf(url=str(path));cache[path]=fitz.open(stream=data,filetype='pdf')
 doc[pi].show_pdf_page(r,cache[path],0,keep_proportion=True,overlay=True)
doc.set_metadata({'title':'BC Recreation and Conservation - Research and Overlay Review','author':'Prepared for Ahmad Jalil','subject':'Geometric reconstructions and source evidence for five historical BC marks'})
doc.save(OUT,garbage=4,deflate=True)
doc.close()
# Final render for visual inspection; structural audit distinguishes vector marks from raster source crops.
doc=fitz.open(OUT)
checks=[]
for i,p in enumerate(doc):
 pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False);pix.save(QA/f'page_{i+1:02}.png')
 checks.append({'page':i+1,'images':len(p.get_images()),'vector_drawings':len(p.get_drawings()),'links':len(p.get_links()),'text_chars':len(p.get_text())})
thumbs=[]
for i in range(len(doc)):
 im=Image.open(QA/f'page_{i+1:02}.png');im.thumbnail((500,354));thumbs.append(im)
contact=Image.new('RGB',(1530,1100),'#CAD1C5');dr=ImageDraw.Draw(contact)
for i,im in enumerate(thumbs):contact.paste(im,((i%3)*510+5,(i//3)*365+5))
contact.save(QA/'contact_sheet.png')
(QA/'verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps({'output':str(OUT),'pages':len(doc),'size_bytes':OUT.stat().st_size,'checks':checks},indent=2))
