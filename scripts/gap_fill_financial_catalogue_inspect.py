#!/usr/bin/env python3
"""Complete actual-PDF native/page/index evidence for the finite28 financial originals."""
from pathlib import Path
import json,gzip,hashlib,subprocess,re,fitz
from PIL import Image,ImageDraw
R=Path('/workspace/PofBC');A=R/'research/salaries/gap-fill-2026-11-02/reviews/financial-catalogue-audit';sha=lambda b:hashlib.sha256(b).hexdigest();inp=json.loads((A/'input-items.json').read_text());priority=json.loads((R/'research/salaries/gap-fill-2026-11-02/health_employees/metadata-only-financial-priority.json').read_text());pri={x['itemUuid']for x in priority};items=sorted(inp['items'],key=lambda x:(x['itemUuid']not in pri,inp['items'].index(x)));summary=[]
for serial,item in enumerate(items,1):
 uid=item['itemUuid'];retr=json.loads((A/f'{uid}-retrieval.json').read_text());assert len(retr['originals'])==1;o=retr['originals'][0];assert o['isPdf'];p=Path(o['retrieval']['cachePath']);assert sha(p.read_bytes())==o['retrieval']['sha256'];d=fitz.open(p);pages=[];textall=[];thumbs=[];od=A/uid;od.mkdir(exist_ok=True)
 for num,page in enumerate(d,1):
  text=page.get_text('text',sort=True);textall.append(text);words=page.get_text('words');matches=[]
  for match in re.finditer(r'remunerat\w*|remenerat\w*|compensat\w*|salar(?:y|ies)|\b(?:employee|trustee|director|board|disclosur)\w*|75[,\s.]?000',text,re.I):
   if len(matches)<40:matches.append(text[max(0,match.start()-100):match.end()+180].replace('\n',' '))
  pages.append({'physicalPage':num,'nativeCharacters':len(text.strip()),'nativeWords':len(words),'imageCount':len(page.get_images()),'replacementCharacters':text.count('\ufffd'),'headerLines':[x for x in text.splitlines()if x.strip()][:6],'scopeKeywordContexts':matches})
  pix=page.get_pixmap(dpi=60,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((306,398));thumbs.append((num,im.copy()))
  if num<=3 or num==len(d):page.get_pixmap(dpi=150,alpha=False).save(od/f'context-p{num}-150dpi.png')
 pop=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True).stdout.decode('utf-8','replace');(od/'native-pymupdf-pages.json.gzip').write_bytes(gzip.compress((json.dumps(textall,ensure_ascii=False)+'\n').encode(),mtime=0));(od/'native-poppler-layout.txt.gzip').write_bytes(gzip.compress(pop.encode(),mtime=0))
 sheets=[]
 for start in range(0,len(thumbs),20):
  group=thumbs[start:start+20];sheet=Image.new('RGB',(1530,440*((len(group)+4)//5)),'#ddd');dr=ImageDraw.Draw(sheet)
  for idx,(n,im)in enumerate(group):x=(idx%5)*306;y=(idx//5)*440;dr.text((x+5,y+5),f'item{serial} / actual PDF page{n}',fill='black');sheet.paste(im,(x,y+24))
  out=od/f'whole-page-index-{start//20+1}.png';sheet.save(out);sheets.append({'file':str(out.relative_to(R)),'sha256':sha(out.read_bytes()),'physicalPages':[n for n,im in group]})
 info={'serial':serial,'itemUuid':uid,'issuer':item['issuer'],'employerSlug':item['employerSlug'],'cataloguePeriodDiscoveryOnly':item['catalogueYearDiscoveryOnly'],'actualSourcePeriodVerified':False,'priorityWithoutLocatedSalaryCounterpart':uid in pri,'sourceUrl':o['sourceUrl'],'sourceSha256':o['retrieval']['sha256'],'cachePdf':str(p),'pdfPages':len(d),'minBodyNativeCharacters':min(x['nativeCharacters']for x in pages[1:])if len(pages)>1 else 0,'nativeSparsePages':[x['physicalPage']for x in pages if x['nativeCharacters']<100],'pymupdfTextSha256':sha((od/'native-pymupdf-pages.json.gzip').read_bytes()),'popplerTextSha256':sha((od/'native-poppler-layout.txt.gzip').read_bytes()),'pages':pages,'wholePageIndexSheets':sheets,'status':'actual-PDF-extracted-and-rendered-awaiting-personal-scope-review','noOutreach':True};(od/'page-evidence.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');summary.append({k:v for k,v in info.items()if k!='pages'});print(serial,item['employerSlug'],item['catalogueYearDiscoveryOnly'],len(d),'sparse',info['nativeSparsePages'],'keywordPages',sum(bool(x['scopeKeywordContexts'])for x in pages),flush=True)
(A/'all28-actual-source-page-index.json').write_text(json.dumps({'inputItemCount':28,'priorityWithoutOtherLocatedSalaryCounterparts':10,'items':summary,'noMetadataAbsenceInference':True,'noOutreach':True},ensure_ascii=False,indent=2)+'\n')
