"""Independent original-PDF hash/pixel replay and context renders; no candidate values."""
from pathlib import Path
import json,hashlib,fitz
from PIL import Image,ImageDraw
ROOT=Path('/workspace/PofBC');AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native/reviews';OUT=AREA/'municipal-earliest-12-contexts';OUT.mkdir(exist_ok=True)
packet=json.loads((ROOT/'research/salaries/gap-fill-2026-11-02/municipal/independent-review-packet-earliest-12.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=[]
for i,r in enumerate(packet['reports'],1):
 assert sha(r['cachedPdf'])==r['sourceSha256']
 d=fitz.open(r['cachedPdf']);item={'sourceSha256':r['sourceSha256'],'cachedPdf':r['cachedPdf'],'salaryImages':[],'contextPages':r['contextPages']}
 for page in sorted(set(r['salaryPages'])):
  cohort=next(x for x in r['sourceCohorts'] if x['physicalPage']==page);im=Image.open(cohort['render300DpiImage']).convert('RGB');pix=d[page-1].get_pixmap(dpi=300,alpha=False)
  assert sha(cohort['render300DpiImage'])==cohort['renderSha256']
  same=im.size==(pix.width,pix.height) and im.tobytes()==pix.samples
  assert same,(i,page)
  item['salaryImages'].append({'physicalPage':page,'providedImageSha256':sha(cohort['render300DpiImage']),'pixelReplayExact':same,'width':pix.width,'height':pix.height})
 pages=[]
 for page in r['contextPages']:
  pix=d[page-1].get_pixmap(dpi=110,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((900,1200));pages.append((page,im.copy()))
 sheet=Image.new('RGB',(900*len(pages),1260),'#dddddd');dr=ImageDraw.Draw(sheet)
 for j,(page,im) in enumerate(pages):sheet.paste(im,(900*j,35));dr.text((900*j+10,10),f'report {i} original PDF physical page {page}',fill='black')
 p=OUT/f'report-{i:02d}-context.png';sheet.save(p);item['contextSheet']=str(p.relative_to(ROOT));item['contextSheetSha256']=sha(p);receipt.append(item)
(AREA/'municipal-earliest-12-original-replay.json').write_text(json.dumps({'reports':receipt,'originals':len(receipt),'salaryPages':sum(len(x['salaryImages']) for x in receipt),'candidateValuesRead':False},indent=2)+'\n')
print('Original hashes, provided image hashes, and all salarypage pixel replays exact.',len(receipt))
