from pathlib import Path
import json,hashlib,fitz,shutil
from PIL import Image,ImageDraw
R=Path('/workspace/PofBC');A=R/'research/salaries/gap-fill-2026-11-02/school_native/reviews/south-scans';A.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();allr=[]
for district in [69,70,78]:
 packet=R/f'research/salaries/gap-fill-2026-11-02/school_south/sd{district}-scan-source-only-peer-packet.json';j=json.loads(packet.read_text());shutil.copyfile(packet,A/packet.name);assert sha(j['source']['cachePath'])==j['source']['sha256'];assert sha(j['candidateSnapshot']['path'])==j['candidateSnapshot']['sha256'];assert sha(j['rawReaderSnapshot']['path'])==j['rawReaderSnapshot']['sha256'];d=fitz.open(j['source']['cachePath']);cached={};items=[]
 for target in j['targets']:
  p=target['physicalPage']
  if p not in cached:
   pix=d[p-1].get_pixmap(dpi=300,alpha=False);cached[p]=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  provided=Image.open(target['path']).convert('RGB');fresh=cached[p].crop(target['integerBox300Dpi']);assert provided.size==fresh.size and provided.tobytes()==fresh.tobytes(),(district,p,target['sequence']);assert sha(target['path'])==target['sha256'];items.append((target,fresh))
 sheets=[]
 for start in range(0,len(items),8):
  group=items[start:start+8];sheet=Image.new('RGB',(2440,110*len(group)),'white');draw=ImageDraw.Draw(sheet)
  for y,(t,im) in enumerate(group):draw.text((20,110*y+5),f"SD{district} CURRENT seq {t['sequence']} / PDF page {t['physicalPage']} / {','.join(t['kinds'])}",fill='black');sheet.paste(im,(0,110*y+32))
  sp=A/f'sd{district}-source-first-sheet-{start//8+1}.png';sheet.save(sp);sheets.append({'file':str(sp.relative_to(R)),'sha256':sha(sp),'sequences':[x[0]['sequence'] for x in group]})
 for ctx in j['contexts']:
  pix=d[ctx['physicalPage']-1].get_pixmap(dpi=ctx['dpi'],alpha=False);provided=Image.open(ctx['path']).convert('RGB');assert provided.size==(pix.width,pix.height)and provided.tobytes()==pix.samples;assert sha(ctx['path'])==ctx['sha256']
 for benchmark in j['sourceOnlyExpenseGlyphBenchmarks']:
  p=benchmark['physicalPage']
  if p not in cached:
   pix=d[p-1].get_pixmap(dpi=300,alpha=False);cached[p]=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  image=R/benchmark['path'];im=Image.open(image).convert('RGB');fresh=cached[p].crop(benchmark['box300Dpi']);assert im.size==fresh.size and im.tobytes()==fresh.tobytes();assert sha(image)==benchmark['sha256']
 allr.append({'district':district,'sourceSha256':j['source']['sha256'],'sourcePdf':j['source']['cachePath'],'sourceOnlyPacketSnapshot':str((A/packet.name).relative_to(R)),'packetSha256':sha(A/packet.name),'allTargetImagesPixelReplayed':len(items),'allContextImagesPixelReplayed':len(j['contexts']),'allGlyphBenchmarkImagesPixelReplayed':len(j['sourceOnlyExpenseGlyphBenchmarks']),'candidateSnapshotOnlyHashCheckedValuesUnread':True,'sheets':sheets})
(A/'first-original-pixel-replay.json').write_text(json.dumps(allr,indent=2)+'\n');print([(r['district'],r['allTargetImagesPixelReplayed'],r['allContextImagesPixelReplayed'],r['allGlyphBenchmarkImagesPixelReplayed'])for r in allr])
