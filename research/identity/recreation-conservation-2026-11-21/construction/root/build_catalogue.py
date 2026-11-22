"""Build a vector overview and an illustrated, source-linked collection guide."""
from pathlib import Path
import json, math, html, copy, textwrap, re
from collections import Counter
from lxml import etree
from PIL import Image
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLFont

ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'branding_rebuild';OUT=ROOT/'output';PKG=OUT/'branding_collection'
STEM='BC_Recreation_Conservation_Branding'
NS='http://www.w3.org/2000/svg';XL='http://www.w3.org/1999/xlink'
INK='#163c35';PAPER='#f3f0e5';MUTED='#5c7165';LINE='#b6c1b2';DARK='#0c1c1b';CREAM='#e3e0cb'
FONTFILE='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLDFILE='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT=TTFont(FONTFILE);GL=FONT.getGlyphSet();CM=FONT.getBestCmap();UPM=FONT['head'].unitsPerEm
ASSETS=json.loads((PKG/'manifest.json').read_text())['assets']
BY={m['id']:m for m in ASSETS}
def group(g):return [m for m in ASSETS if m['group']==g]
def find(g,part):return next(m for m in group(g) if part in Path(m['svg']).stem)
def etext(text,x,y,size=24,color=INK,anchor='start'):
 width=sum(FONT['hmtx'][CM.get(ord(ch),'question')][0] for ch in text)*size/UPM
 if anchor=='middle':x-=width/2
 if anchor=='end':x-=width
 pieces=[];pos=0
 for ch in text:
  glyph=CM.get(ord(ch),'question');pen=SVGPathPen(GL);GL[glyph].draw(pen)
  pieces.append(f'<path transform="translate({pos} 0)" d="{pen.getCommands()}"/>');pos+=FONT['hmtx'][glyph][0]
 return f'<g transform="translate({x} {y}) scale({size/UPM} {-size/UPM})" fill="{color}">'+''.join(pieces)+'</g>'

def fit_svg(path,x,y,w,h,prefix):
 r=etree.fromstring(Path(path).read_bytes());vx,vy,vw,vh=map(float,r.get('viewBox').split());s=min(w/vw,h/vh)
 xx=x+(w-vw*s)/2;yy=y+(h-vh*s)/2
 ids={el.get('id'):prefix+'-'+el.get('id') for el in r.iter() if el.get('id')}
 for el in r.iter():
  for k,v in list(el.attrib.items()):
   if k=='id':el.set(k,ids[v]);continue
   for a,b in ids.items():v=v.replace('url(#'+a+')','url(#'+b+')');v='#'+b if v=='#'+a else v
   el.set(k,v)
 children=''.join(etree.tostring(el,encoding='unicode') for el in r if etree.QName(el).localname not in ['title','desc','metadata'])
 return f'<g transform="translate({xx} {yy}) scale({s}) translate({-vx} {-vy})">{children}</g>'

def overview():
 W,H=1800,3440;parts=[f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',f'<rect width="{W}" height="175" fill="{INK}"/>']
 parts +=[etext('BRITISH COLUMBIA / HISTORICAL RECONSTRUCTION',65,49,21,CREAM),etext('Recreation & Conservation',62,119,64,CREAM),etext('Reports, emblems, lettering, handbook panels and proposed park signs',65,151,22,CREAM)]
 def heading(n,title,y,note=''):
  parts.append(etext(n+'  '+title,65,y,30));parts.append(f'<path d="M65 {y+20}H1735" stroke="{LINE}" stroke-width="2"/>')
  if note:parts.append(etext(note,65,y+52,18,MUTED))
 def art(m,x,y,w,h):parts.append(fit_svg(PKG/m['svg'],x,y,w,h,re.sub(r'[^a-zA-Z0-9]','',m['id'])+str(x)+str(y)))
 def label(s,cx,y,width=30,size=19):
  for line in textwrap.wrap(s,width):parts.append(etext(line,cx,y,size,INK,'middle'));y+=size*1.35
 heading('01','The five-symbol family',231)
 names=['Department','Fish and Wildlife','Provincial Parks','Provincial Museum','Fisheries / Marine Resources']
 for i,(key,name) in enumerate(zip(['01_','02_','03_','04_','05_'],names)):
  m=find('symbols',key);m=next(v for v in group('symbols') if Path(v['svg']).stem.startswith(key) and Path(v['svg']).stem.endswith('report_green'))
  x=80+i*340;art(m,x+34,285,235,235);label(name,x+151,555,25,21)
 heading('02','Associated emblems',642,'Separate documented designs; the oval departmental badge is an earlier 1970 treatment.')
 for i,m in enumerate(group('related_emblems')):
  x=65+i*421;art(m,x+35,721,335,255);label(m['title'],x+202,1010,31,19)
 heading('03','Report layouts',1112,'Ten section dividers cover the 1971/1972 and 1973 layout generations.')
 for i,m in enumerate(group('report_dividers')):
  row,col=divmod(i,5);x=72+col*337;y=1187+row*323
  art(m,x+30,y,255,267);label(m['title'].replace(' / ',' · ').replace(' divider',''),x+157,y+290,29,16)
 heading('04','Museum handbook branding',1885,'24 photographed variants / 23 titles, rebuilt as panels with open illustration fields.')
 templates=group('handbook_templates')
 chosen=[]
 for key in [20,23,29,35]:
  chosen.append(next((m for m in templates if m.get('handbook_number')==key or f'_HB{key}_' in Path(m['svg']).stem),templates[len(chosen)]))
 for i,m in enumerate(chosen):art(m,65+i*325,1965,285,382)
 for i,m in enumerate(group('handbook_emblems')):art(m,1440,1965+i*130,120,120);label(m['title'].split(' handbook')[0],1650,2015+i*130,14,17)
 heading('05','All 22 proposed park signs',2435,'Reconstructed from printed DD67 / PDF 68 of the 1971 report. Proposal status retained.')
 for i,m in enumerate(group('park_symbols')):
  row,col=divmod(i,11);x=65+col*152;y=2520+row*180
  art(m,x+17,y,116,116);label(m['title'],x+75,y+141,18,14)
 heading('06','Cover blocks and back-cover stacks',2953)
 for i,m in enumerate(group('cover_headers')):art(m,65+i*430,3010,400,234);label(str(m.get('source_report','')),265+i*430,3273,18,20)
 for i,m in enumerate(group('cover_stacks')):art(m,1420+i*155,3002,110,304)
 parts.append(etext('Editable SVGs + vector PDFs · Outlined lettering · Source crops, overlays and construction notes',65,3360,22))
 parts.append(etext('Reconstructed artwork, not recovered originals. Colours approximate the scans. Handbook illustrations are separate.',65,3400,18,MUTED))
 document=f'<svg xmlns="{NS}" xmlns:xlink="{XL}" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>British Columbia Recreation and Conservation — reconstructed branding overview</title><desc>Overview of the reconstructed identity collection. All lettering and artwork are vector paths or geometry; no embedded images or font dependencies.</desc>'+''.join(parts)+'</svg>'
 p=OUT/(STEM+'_Overview.svg');p.write_text(document)
 cairosvg.svg2png(url=str(p),write_to=str(OUT/(STEM+'_Overview.png')))
 cairosvg.svg2pdf(url=str(p),write_to=str(OUT/(STEM+'_Overview.pdf')))
 for ext in ['svg','png','pdf']:(PKG/(STEM+'_Overview.'+ext)).write_bytes((OUT/(STEM+'_Overview.'+ext)).read_bytes())

pdfmetrics.registerFont(RLFont('DV',FONTFILE));pdfmetrics.registerFont(RLFont('DVB',BOLDFILE))
PW,PH=landscape(A4);M=38
class Book:
 def __init__(self,path):
  self.c=canvas.Canvas(str(path),pagesize=(PW,PH));self.c.setTitle('British Columbia Recreation and Conservation — Branding Collection');self.c.setAuthor('Historical reconstruction prepared for the user');self.n=0
 def page(self,title,sub=''):
  if self.n:self.c.showPage()
  self.n+=1;c=self.c;c.setFillColor(HexColor(PAPER));c.rect(0,0,PW,PH,fill=1,stroke=0)
  c.setFillColor(HexColor(INK));c.setFont('DVB',22);c.drawString(M,PH-47,title)
  if sub:self.para(sub,M,69,PW-2*M,9,MUTED)
  c.setStrokeColor(HexColor(LINE));c.line(M,PH-94,PW-M,PH-94)
  c.setFont('DV',8);c.setFillColor(HexColor(MUTED));c.drawString(M,20,'BC Recreation & Conservation · reconstructed branding collection');c.drawRightString(PW-M,20,str(self.n))
 def para(self,s,x,top,w,size=10,color=INK,bold=False):
  s=re.sub(r'&(?!#\d+;|#x[0-9a-fA-F]+;|[A-Za-z]+;)', '&amp;',s)
  style=ParagraphStyle('p',fontName='DVB' if bold else 'DV',fontSize=size,leading=size*1.42,textColor=HexColor(color),spaceAfter=0)
  p=Paragraph(s,style);aw,ah=p.wrap(w,1000);p.drawOn(self.c,x,PH-top-ah);return top+ah
 def img(self,path,x,top,w,h,bg=None):
  if bg:self.c.setFillColor(HexColor(bg));self.c.rect(x,PH-top-h,w,h,fill=1,stroke=0)
  im=Image.open(path);iw,ih=im.size;s=min(w/iw,h/ih);dw,dh=iw*s,ih*s
  self.c.drawImage(ImageReader(im),x+(w-dw)/2,PH-top-h+(h-dh)/2,dw,dh,mask='auto',preserveAspectRatio=True)
 def asset(self,m,x,top,w,h):self.img(PKG/m['preview'],x,top,w,h,DARK if m.get('treatment')=='transparent_white' else None)
 def caption(self,s,x,top,w,size=9):return self.para(s,x,top,w,size,MUTED)
 def box(self,x,top,w,h,fill='#fffdf5'):
  self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(LINE));self.c.roundRect(x,PH-top-h,w,h,8,fill=1,stroke=1)
 def save(self):self.c.save()

def short(m):
 t=m['title'];t=t.replace('British Columbia Provincial Museum','Provincial Museum').replace('Commercial Fisheries / Marine Resources','Fisheries / Marine Resources')
 return t

def catalogue():
 b=Book(OUT/(STEM+'_Catalogue.pdf'));W=PW-2*M;counts=Counter(m['group'] for m in ASSETS)
 b.page('Recreation & Conservation','British Columbia · reconstructed identity collection · 21 November 2026')
 b.para('A working collection of the documented symbols, lettering and publication layouts.',M,115,W,20,bold=True)
 b.para('Five square emblems form the core. Associated badges, annual-report applications, museum handbook panels and a complete proposed park-sign sheet extend the collection.',M,176,W,12)
 for i,k in enumerate(['01_','02_','03_','04_','05_']):
  m=next(v for v in group('symbols') if Path(v['svg']).stem.startswith(k) and Path(v['svg']).stem.endswith('report_green'));b.asset(m,M+i*(W/5)+16,255,W/5-32,130)
 b.para(f'<b>{len(ASSETS)} production SVG files</b> · matching vector PDFs · PNG previews · source evidence and overlays',M,421,W,12)
 b.para('This count includes colour treatments and fixed wording components. The collection reconstructs the checked references; it does not claim recovered original production artwork or every identity ever used by these branches.',M,467,W,10,MUTED)

 b.page('01 / The five-symbol family','Five independently rebuilt emblems; 25 colour/treatment files. Master shapes have transparent negative spaces.')
 cols=['black','report_green','report_pale','reverse','transparent_white']
 coltitles=['Black master','Report green','Pale secondary','Reverse sample','White / transparent']
 # Each row is a family member; each column a colour treatment.
 for c,t in enumerate(coltitles):b.caption(t,M+c*W/5,108,W/5,9)
 for row,k in enumerate(['01_','02_','03_','04_','05_']):
  for col,t in enumerate(cols):
   candidates=[v for v in group('symbols') if Path(v['svg']).stem.startswith(k) and v.get('treatment')==t]
   if not candidates:candidates=[v for v in group('symbols') if Path(v['svg']).stem.startswith(k) and Path(v['svg']).stem.endswith(t)]
   if candidates:b.asset(candidates[0],M+col*W/5+44,135+row*78,68,68)
 b.caption('Rows: department · Fish and Wildlife · Provincial Parks · Provincial Museum · Commercial Fisheries / Marine Resources.',M,534,W,9)

 b.page('02 / Associated emblems','The 1970 oval is a predecessor. The two F&W files are one emblem and its paired name-panel arrangement.')
 for i,m in enumerate(group('related_emblems')):
  x=M+(i%4)*W/4;b.asset(m,x+12,120,W/4-24,265);b.para(m['title'],x+3,405,W/4-9,10,bold=True)
  b.caption('Report PDF page '+str(m.get('pdf_page',''))+'. '+('Botanical hatching and small type remain approximate.' if '1970' in m['id'] else 'Geometric reconstruction; small lettering uses a close outlined substitute.'),x+3,446,W/4-9,9)
 b.caption('Primary sources: 1970 report PDF 10; 1973 report PDF 22 and PDF 80. Source crops and transparent overlay comparisons accompany each asset.',M,531,W,9)

 b.page('03 / Lettering and spacing','Corporatus is the modern comparison for the report’s Corporate-style lettering. Supplied wordmarks and layouts are outlined.')
 for i,p in enumerate(['01_General','02_Department','06_Commercial','07_marine']):
  m=find('wordmarks',p);b.asset(m,M,119+i*72,W,54)
 b.para('General Administration',M,422,210,11,bold=True);b.para('Department line',M+W/2,422,210,11,bold=True)
 b.para('100% horizontal scale; tracking about −45 to −50 per 1000 em. Reduce the nominal word space by about 0.22 em.',M,446,W/2-24,10)
 b.para('Starting fit near 97% horizontal scale; tracking about −22 to −25. Reduce the nominal word space by about 0.30 em.',M+W/2,446,W/2-24,10)
 b.caption('These are starting settings from the earlier live-specimen study. Finished path layouts use their own measured bounds and reconstructed advances; their internal tracking values are not interchangeable with a live font. A fitted 97% ratio does not prove an original production instruction.',M,515,W,9)

 for year in [1971,1973]:
  b.page(f'04 / Report section dividers — {year}',('The same design generation occurs in the 1972 report. Five active-branch arrangements.' if year==1971 else 'Later F&W paired panel on interior pages; renamed Marine Resources heading.'))
  items=[m for m in group('report_dividers') if m.get('source_report')==year]
  for i,m in enumerate(items):
   row,col=divmod(i,3);x=M+col*W/3;top=108+row*224;b.asset(m,x+28,top,195,190)
   b.caption(short(m).replace(' / ',' · ').replace(' divider','')+f' · PDF {m.get("source_pdf_page")}',x+6,top+193,W/3-12,8)

 b.page('05 / Reusable department and branch bands','Five compact arrangements derived from the full dividers. These are practical components, not additional historical specimens.')
 for i,m in enumerate(group('branch_lockups')):
  b.asset(m,M+110,111+i*82,470,76);b.caption(short(m).split(' / ')[0],M,132+i*82,110,8)

 b.page('06 / Cover branding','The three report cover blocks and two back-cover symbol stacks. Cover photographs sit outside these branding assets.')
 for i,m in enumerate(group('cover_headers')):
  b.asset(m,M,113+i*130,410,118);b.caption(str(m.get('source_report')),M+421,145+i*130,60,11)
 for i,m in enumerate(group('cover_stacks')):b.asset(m,M+515+i*118,116,104,350)
 b.caption('The 1973 back cover retains the earlier Fish and Wildlife square. The supporting arms artwork is a refined reconstruction from a 1960 Museum engraving; it is a period analogue, not the exact cover engraving.',M+494,481,270,9)

 b.page('07 / Museum handbook components','Three category emblems plus fixed outlined lettering. The ram-head emblem also appears on bird titles in this series.')
 for i,m in enumerate(group('handbook_emblems')):
  x=M+i*W/3;b.asset(m,x+35,122,184,184);b.para(m['title'],x+8,329,W/3-16,11,bold=True)
  b.caption(m.get('note','Source-limited geometric reconstruction.'),x+8,367,W/3-16,10)
 b.para('The panel lettering uses Neue Helvetica Pro 43 Extended Light as the closest inspected modern comparison. The historical handbook typeface remains unconfirmed. Category symbols are manually constructed geometry; their tiny source photographs limit fine detail.',M,466,W,11)
 b.caption('Source photographs: nos. 29 (ram), 23 (crab), 16 and 20 (flower). Seller dates alone are not accepted as printing or design-introduction dates.',M,531,W,9)

 templates=group('handbook_templates')
 for start in range(0,len(templates),6):
  b.page(f'08 / Handbook branding panels — {start+1}–{min(start+6,len(templates))}', 'Normalized title, number, emblem and publisher-panel variants. The illustration field is intentionally open.')
  for j,m in enumerate(templates[start:start+6]):
   row,col=divmod(j,3);x=M+col*W/3;top=109+row*225;b.asset(m,x+52,top,150,188)
   b.caption(short(m),x+7,top+190,W/3-14,8)

 parks=group('park_symbols')
 for start in [0,11]:
  b.page(f'09 / Proposed park signs — {start+1}–{min(start+11,22)}','All 22 pictograms on printed DD67 / PDF 68 of the 1971 report. The report explicitly presents them as proposals.')
  for j,m in enumerate(parks[start:start+11]):
   row,col=divmod(j,4);x=M+col*W/4;top=112+row*141;b.asset(m,x+43,top,100,100)
   b.caption(f'{start+j+1:02d} · {m["title"]}',x+10,top+107,W/4-20,9)

 b.page('10 / Review against the source','Source at left, reconstruction at centre, overlay at right. Colour residuals reveal differences rather than hiding them.')
 for i,k in enumerate(['1971_general_divider','1973_fisheries_divider']):
  p=WORK/'collection/review/report_dividers'/f'{k}_overlay.png';b.img(p,M,109+i*214,W,204)
 b.caption('Registration uses a single frame-relative affine transform; no local warping. Pale halftone marks are excluded from the primary-ink metric, but remain visible in the comparison. Pixel overlap is not a percentage of historical authenticity.',M,537,W,8)

 b.page('11 / What the records establish','Use these findings to keep visual variants separate from unsupported attribution or chronology.')
 y=115
 notes=[
  ('1971 and 1972: one coordinated layout generation.','The five square symbols, framed dividers, departmental footer and vertical cover stack form the report family. The 1972 examples retain the earlier Fish and Wildlife square. [R71, R72]'),
  ('1973: coexistence and a branch-name change.','The interior pages use the later F&W paired panel, while the back cover retains the earlier square. The three-fish emblem accompanies Marine Resources Branch with [Commercial Fisheries] below. [R73: PDF 22, 144, 162]'),
  ('Two Parks designs, plus an unidentified proposal.','The spiral square appears on the divider; a dogwood/province shield appears on the organisation chart. The text on AA105 describes a logo submitted for approval without showing it. It cannot identify that unseen proposal with either visible design. [R73: PDF 78, 80, 106]'),
  ('Handbook evidence comes from pictured copies.','The inventory records 24 photographed variants across 23 titles. The edible-plants fourth-edition notice verifies 1972 for that copy. Most other dates are seller metadata; they do not prove when the branding was introduced. [H]')]
 for title,body in notes:
  y=b.para(title,M,y,W,12,bold=True)+5;y=b.para(body,M,y,W,10)+20
 b.caption('No original identity manual or credited designer was established for the five-symbol report family in the checked references.',M,535,W,9)

 b.page('12 / Source directory and practical use','Every production SVG is self-contained. The PDF and PNG folders mirror the vector filenames.')
 y=113
 sources=[('R70 / Earlier departmental oval','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1970.pdf','PDF 10'),('R71 / First checked coordinated family','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf','PDF 10, 16, 64, 68, 98, 126, 139'),('R72 / Continuing report layout','https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1972.pdf','PDF 10, 14, 60, 88, 110, 122'),('R73 / Later branch treatments','https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf','PDF 12, 22, 78, 80, 106, 112, 144, 162'),('T / Corporatus modern comparison','https://www.myfonts.com/collections/corporatus-font-alex-rosario-type','Foundry description identifies the revival of Roc Mitchell’s Corporate.')]
 for label,url,note in sources:
  y=b.para(label,M,y,W,10,bold=True)+2;y=b.para(f'<link href="{url}" color="{MUTED}">{url}</link>',M,y,W,8)+2;y=b.para(note,M,y,W,8,MUTED)+12
 b.para('H / Handbook sources',M,438,270,10,bold=True)
 b.para('Individual pictured-copy URLs and date qualifications appear in reference/BC_Handbook_Variants_Inventory.csv. The original photographs, header/footer crops and template manifest accompany the panel reconstructions.',M,458,350,9)
 b.para('Editing and review',M+390,438,300,10,bold=True)
 b.para('Open index.html for searchable previews. Import SVGs to edit paths and fills. Black and white masters are transparent; page and panel assets retain editable background objects. Use the source overlays when changing detailed geometry.',M+390,458,370,9)
 b.save()
 (PKG/(STEM+'_Catalogue.pdf')).write_bytes((OUT/(STEM+'_Catalogue.pdf')).read_bytes())
 print(json.dumps({'catalogue_pages':b.n,'svg_assets':len(ASSETS),'files':[str(OUT/(STEM+'_Catalogue.pdf')),str(OUT/(STEM+'_Overview.svg'))]},indent=2))

if __name__=='__main__':overview();catalogue()
