"""Full original replay plus broad payment anchors independent of the named-row predicate."""
from pathlib import Path
from decimal import Decimal
import json,gzip,hashlib,csv,io,re,sys,collections,shutil
ROOT=Path('/workspace/PofBC');A=Path(__file__).parent;S=ROOT/'research/salaries/gap-fill-2026-11-02/school_south';sys.path.insert(0,str(ROOT/'scripts'))
import gap_school_south_scan as parser
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()))
code=A/'replayed-processing-code-final-v14';code.mkdir(exist_ok=True)
for name in ['gap_school_south_scan.py','gap_school_south_census.py','gap_school_south_dash.py','gap_school_south_finalize_scans.py','gap_school_south_packets.py']:shutil.copyfile(ROOT/'scripts'/name,code/name)
import fitz
from PIL import Image
personal_dash={(int(r.split('|')[0]),int(r.split('|')[1])) for r in (A/'first-personal-flag-and-holdout-transcript.txt').read_text().splitlines() if r and not r.startswith('#') and r.split('|')[6]=='-'}
reports=[]
for d in [69,70,78]:
 packet=json.loads((A/f'sd{d}-scan-source-only-peer-packet.json').read_text());raw_candidate=load(packet['rawReaderSnapshot']['path']);chosen=load(S/f'sd{d}-scan-reviewed-candidate-v14.json.gzip');assert len(raw_candidate['tesseractRows'])==len(raw_candidate['paddleRows'])==len(chosen['rows']);assert not chosen['remainingFlags'];doc=fitz.open(packet['source']['cachePath']);assert sha(packet['source']['cachePath'])==packet['source']['sha256'];pages=[];all_outside=[];low=[];whitespace=[];geometry=[]
 for seq,(one,two) in enumerate(zip(raw_candidate['tesseractRows'],raw_candidate['paddleRows']),1):
  assert one['pdfPage']==two['pdfPage']
  gap=abs(one['sourceY300dpi']-two['sourceY300dpi'])
  if gap>20:geometry.append({'sequence':seq,'page':one['pdfPage'],'deltaY300Dpi':gap})
  ta=[float(w['conf'])/100 for w in one['tesseractWords']if re.search('[A-Za-z0-9]',w['text'])and w['text']not in ['S','$']];pa=[w['confidence']for w in two['paddleBoxes']if re.search('[A-Za-z0-9]',w['text'])and w['text']not in ['S','$']]
  if min(ta,default=0)<.3 or min(pa,default=0)<.7:
   target=next((x for x in packet['targets']if x['sequence']==seq),None);assert target is not None,(d,seq,'low score absent from full peer image review');low.append({'sequence':seq,'minTesseractSignal':min(ta,default=0),'minRapidSignal':min(pa,default=0),'peerPersonallySourceRead':True})
 for p in packet['salaryPages']:
  path=S/'raw-ocr'/f'sd{d}-sofi-2025-p{p}.json.gzip';raw=load(path);assert raw['sourceSha256']==packet['source']['sha256'];pix=doc[p-1].get_pixmap(dpi=300);assert hashlib.sha256(pix.tobytes('png')).hexdigest()==raw['imageSha256'];tess=parser.tesseract(raw,d);paddle=parser.paddle(raw,d)
  assert tess==[x for x in raw_candidate['tesseractRows']if x['pdfPage']==p];assert paddle==[x for x in raw_candidate['paddleRows']if x['pdfPage']==p]
  ys=[r['sourceY300dpi']for r in raw_candidate['tesseractRows']if r['pdfPage']==p];spec=parser.SPECS[d];bounds=spec.get('boundsByPage',{}).get(p,spec['bounds']);payleft,payright=bounds[1],bounds[2];tsv=list(csv.DictReader(io.StringIO(raw['tesseractRawTsv']),delimiter='\t',quoting=csv.QUOTE_NONE));words=[w for w in tsv if w['level']=='5'and w['text'].strip()];extras=[]
  for engine,observed in [('tesseract',[{'x':int(w['left']),'y':int(w['top'])+int(w['height'])/2,'text':w['text']}for w in words]),('rapid',[{'x':min(q[0]for q in box),'y':sum(q[1]for q in box)/4,'text':text}for box,text,score in raw['rapidOcrRaw']])]:
   anchors=[w for w in observed if payleft<=w['x']<payright and re.search(r'\d',w['text'])];outside=[w for w in anchors if not any(abs(w['y']-y)<22 for y in ys)]
   for w in outside:
    vicinity=' '.join(z['text']for z in sorted(observed,key=lambda z:z['x'])if abs(z['y']-w['y'])<22)
    item={'engine':engine,'page':p,'payAnchor':w,'wholePageHorizontalText':vicinity};extras.append(item);all_outside.append(item)
  pages.append({'physicalPage':p,'originalRasterSha256':raw['imageSha256'],'rawOcrSha256':sha(path),'bothRawReadersReplayedExact':True,'selectedCount':len(ys),'broadPayAnchorsOutsideSelectedRows':extras})
 # Exact source-cell ink proof for every selected null expense.
 glyph=load(S/f'sd{d}-source-expense-glyphs.json.gzip');features={r['sequence']:r for r in glyph['features']};cal=json.loads((S/'expense-dash-primary-calibration.json').read_text())['calibrations'].get(str(d));nulls=[];pageimages={}
 for seq,row in enumerate(chosen['rows'],1):
  if row['expenses']is not None:continue
  assert row['category']=='employee-remuneration';g=features[row['legacySequenceV6']];p=g['physicalPage']
  if p not in pageimages:
   pix=doc[p-1].get_pixmap(dpi=300,alpha=False);pageimages[p]=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L')
  cell=pageimages[p].crop(g['sourceExpenseCellBox300Dpi']);w,h=cell.size;points={(x,y)for y in range(h)for x in range(w)if cell.getpixel((x,y))<128};assert points,(d,seq,'blank cannot establish dash');xs=[x for x,y in points];ys=[y for x,y in points];width=max(xs)-min(xs)+1;height=max(ys)-min(ys)+1;rem=set(points);components=0
  while rem:
   components+=1;stack=[rem.pop()]
   while stack:
    x,y=stack.pop()
    for v in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if v in rem:rem.remove(v);stack.append(v)
  calibrated=components==1 and cal['widthRange'][0]<=width<=cal['widthRange'][1]and cal['heightRange'][0]<=height<=cal['heightRange'][1]and width/height>=cal['minimumAspectRatio']and len(points)/(width*height)>=cal['minimumInkFill']
  assert calibrated or (d,seq)in personal_dash,(d,seq,'not a calibrated full-cell dash and no independent personal source-dash reading')
  assert width==g['glyphWidth']and height==g['glyphHeight']and len(points)==g['blackPixels'];nulls.append({'sequence':seq,'physicalPage':p,'legacySequence':row['legacySequenceV6'],'fullExpenseCellBox300Dpi':g['sourceExpenseCellBox300Dpi'],'completeCellBlackPixels':len(points),'oneConnectedHorizontalGlyph':calibrated,'independentPersonalSourceDashReading':(d,seq)in personal_dash,'connectedInkComponents':components,'blankRejected':True})
 reports.append({'district':d,'rawCandidateRows':len(chosen['rows']),'rawReaderReplaySha256':sha(packet['rawReaderSnapshot']['path']),'selectedV14Sha256':sha(S/f'sd{d}-scan-reviewed-candidate-v14.json.gzip'),'allOriginalSalaryPages':pages,'allLowSignalRowsPersonallySourceRead':low,'largeYGeometryDifferences':geometry,'allNullExpenseSourceCellsIndependentlyPixelChecked':nulls,'outsideSelectedPayAnchors':all_outside})
p=A/'full-source-coverage-and-guard-audit-v14.json';p.write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
for r in reports:
 print(r['district'],'rows',r['rawCandidateRows'],'outside',len(r['outsideSelectedPayAnchors']),'lowSignals',len(r['allLowSignalRowsPersonallySourceRead']),'nullDashes',len(r['allNullExpenseSourceCellsIndependentlyPixelChecked']),'geometry',r['largeYGeometryDifferences'])
 for x in r['outsideSelectedPayAnchors']:print(x['engine'],x['page'],x['payAnchor']['y'],x['wholePageHorizontalText'])
