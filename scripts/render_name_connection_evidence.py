from pathlib import Path
import json,gzip,hashlib,fitz
from PIL import Image,ImageDraw,ImageFont
import argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Reproduce original-source row crops. Re-rendering invalidates existing visual-review hashes until reviewed again.')
parser.add_argument('--cache',type=Path,required=True,help='Folder containing source-ID.pdf originals with the accepted hashes')
args=parser.parse_args()
base=args.cache
area=ROOT/'research/salaries/name-links/source-verification-2026-11-02'
out=area/'renders';out.mkdir(exist_ok=True)
rows=[row for row in json.loads((area/'dispositions.json').read_text()) if row['status']=='ready-for-rendered-source-review']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
docs={};pagecache={};items=[];issues=[]
for c in rows:
 for mi,match in enumerate(c['matches']):
  e=match['official'];sid=e['sourceId'];pn=e['physicalPage'];pdf=base/(sid+'.pdf')
  if not pdf.exists():issues.append({'id':c['id'],'reason':'Original PDF not retrieved','sourceId':sid});continue
  if sid not in docs:
   assert hashlib.sha256(pdf.read_bytes()).hexdigest()==e['pdfSha256']
   docs[sid]=fitz.open(pdf)
  page=docs[sid][pn-1]
  if sid.startswith('queue-completion-phsa-'):
   key=sid.removeprefix('queue-completion-').removesuffix('-employees')
   ep=ROOT/f'research/salaries/queue-completion-phsa/evidence/{key}-rows-p{pn:03d}.json.gzip'
   d=json.loads(gzip.decompress(ep.read_bytes()))
   assert d['sourceSha256']==e['pdfSha256']
   wanted=e['row']
   fits=[r for r in d['rows'] if r['candidateRow'][3:5]==wanted[2:4]]
   if len(fits)!=1:
    def nk(s):return ''.join(ch.lower() for ch in s if ch.isalpha())
    fits=[r for r in d['rows'] if any(nk(t)==nk(wanted[0]) for t in [r['candidateRow'][1],r['tesseract']['name'],r['rapidocr']['name']])]
   if len(fits)!=1:issues.append({'id':c['id'],'reason':'No unique source-band locator','rows':len(fits)});continue
   r=fits[0];band=r['sourceNameBand'];a=max(0,band['top']-14);b=band['bottom']+14
   rect=fitz.Rect(200*72/300,a*72/300,2390*72/300,b*72/300)
   locator={'path':str(ep.relative_to(ROOT)),'sha256':hashlib.sha256(ep.read_bytes()).hexdigest(),'sourceRowOnPage':r['sourceRowOnPage']}
  else:
   blocks=page.get_text('blocks')
   def nk(s):return ''.join(ch.lower() for ch in s if ch.isalpha())
   wanted=nk(e['row'][0])
   words=page.get_text('words')
   lines=[]
   for w in sorted(words,key=lambda w:((w[1]+w[3])/2,w[0])):
    cy=(w[1]+w[3])/2
    group=next((ls for ls in reversed(lines[-3:]) if abs((ls[0][1]+ls[0][3])/2-cy)<2.5),None)
    if group is None:lines.append([w])
    else:group.append(w)
   hits=[ls for ls in lines if wanted in nk(' '.join(w[4] for w in sorted(ls,key=lambda w:w[0])))]
   if len(hits)!=1:issues.append({'id':c['id'],'reason':'No unique native name line','hits':len(hits)});continue
   ls=hits[0];top=min(w[1] for w in ls);bottom=max(w[3] for w in ls)
   rect=fitz.Rect(20,max(0,top-4),page.rect.width-15,bottom+4)
   locator={'nativeNameLine': [w[4] for w in ls]}
  pix=page.get_pixmap(dpi=300,alpha=False,clip=rect)
  path=out/f'case-{c["id"]:04d}-match-{mi+1:02d}.png';pix.save(path)
  im=Image.open(path).convert('RGB');im.thumbnail((1380,95))
  item=Image.new('RGB',(1400,145),'white');draw=ImageDraw.Draw(item)
  label=f'#{c["id"]}  {sid.replace("queue-completion-","")} p.{pn}'
  draw.text((8,3),label,font=font,fill='black')
  draw.text((8,25),f'Proposed: {e["row"][0]} | pay {e["row"][2]:,} | expenses {e["row"][3]:,}',font=font,fill='black')
  item.paste(im,(8,48))
  items.append({'id':c['id'],'match':mi+1,'sourceId':sid,'physicalPage':pn,'pdfSha256':e['pdfSha256'],
   'rectPdfPoints':list(rect),'locator':locator,'crop':str(path.relative_to(ROOT)),'cropSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
   'renderer':'PyMuPDF '+fitz.VersionBind,'renderDpi':300,'panel':item})
for start in range(0,len(items),10):
 chunk=items[start:start+10];im=Image.new('RGB',(1400,145*len(chunk)),(230,230,230))
 for n,item in enumerate(chunk):im.paste(item.pop('panel'),(0,n*145));item['sheet']=start//10+1;item['panelOnSheet']=n+1
 p=out/f'sheet-{start//10+1:02d}.png';im.save(p)
for item in items:item.pop('panel',None)
(area/'render-manifest.json').write_text(json.dumps({'schemaVersion':1,'purpose':'Rendered original row review, not replacement salary data. Labels are annotations; the source row pixels are unretouched.',
 'pdfs':[{'sourceId':sid,'sha256':hashlib.sha256((base/(sid+'.pdf')).read_bytes()).hexdigest()} for sid in docs],
 'cases':items,'issues':issues},indent=2)+'\n')
print('rendered matches',len(items),'unique cases',len({x['id'] for x in items}),'issues',issues)
