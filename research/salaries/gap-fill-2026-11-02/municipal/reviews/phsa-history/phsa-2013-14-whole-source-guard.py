from pathlib import Path
import fitz,hashlib,json,gzip,re
from PIL import Image
R=Path('/workspace/PofBC');B=Path(__file__).resolve().parent;P=R/'research/salaries/gap-fill-2026-11-02/phsa_history';key='phsa-2013-14'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
cp=P/(key+'-scan-candidate-v4.json.gzip');d=json.loads(gzip.decompress(cp.read_bytes()));pc=next(s for s in json.loads((B/'latest-two-scan-independent-pixel-census.json').read_text())['sources'] if s['sourceKey']==key);glyph=next(s for s in json.loads((B/'latest-two-scans-source-expense-glyph-calibration.json').read_text())['sources'] if s['sourceKey']==key);packet=json.loads((P/f'source-only-packets/{key}-v4/packet.json').read_text());targets={r['sequence'] for r in packet['targets']};manual=json.loads((B/(key+'-peer-final-source-readings.json')).read_text());expected={r['sequence']:r for r in manual['rows']}
assert d['source']['sourceSha256']==pc['sourceSha256']==glyph['sourceSha256'];assert len(d['rows'])==len(pc['pixelRows'])==len(glyph['expenseGlyphs'])==3991
seqfails=[];shape=[];diffs=[]
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s or '').strip()) if isinstance(s,str) else s
for row,pix,g in zip(d['rows'],pc['pixelRows'],glyph['expenseGlyphs']):
 seq=row['sequence'];assert seq==pix['sequence']==g['sequence'];assert row['physicalPage']==pix['physicalPage']==g['physicalPage'];y=row['sourceNameBand']['center']*72/300;ey=(pix['y0']+pix['y1'])/2
 if abs(y-ey)>1.5:seqfails.append({'sequence':seq,'candidateY':y,'sourcePixelY':ey})
 isnull=row['selected']['expenses'] is None;dash=g['classification']=='small horizontal dash-shaped glyph'
 if isnull!=dash:shape.append({'sequence':seq,'physicalPage':row['physicalPage'],'originalSourceGlyphClass':g['classification'],'snapshotSelectedExpense':row['selected']['expenses'],'alreadyPersonallyRead':seq in expected,'inProducerFlagPacket':seq in targets})
 if seq in expected:
  fs={f:{'source':expected[seq][f],'candidate':row['selected'][f]} for f in ['name','position','remuneration','expenses','pdfPage'] if norm(expected[seq][f])!=norm(row['selected'][f])}
  if fs:diffs.append({'sequence':seq,'fields':fs})
assert not seqfails,seqfails
pages=[];doc=fitz.open('/workspace/gap-phsa-history-cache/'+key+'.pdf');assert sha(Path('/workspace/gap-phsa-history-cache/'+key+'.pdf').read_bytes())==pc['sourceSha256']
for p in d['pages']:
 pn=p['physicalPage'];raw=R/p['rawPath'];assert sha(raw.read_bytes())==p['rawSha256'];png=Path('/workspace/gap-phsa-history-cache/images')/f'{key}-p{pn:03d}.png';assert sha(png.read_bytes())==p['sourceImageSha256'];fresh=doc[pn-1].get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False);im=Image.open(png).convert('RGB');assert im.size==(fresh.width,fresh.height) and im.tobytes()==fresh.samples
 actual=sum(r['physicalPage']==pn for r in pc['pixelRows']);assert p['actualNameBandCount']==actual
 pages.append({'physicalPage':pn,'rawOcrPin':pin(raw),'originalWholePagePngSha256':p['sourceImageSha256'],'independentlyReplayedOriginalRGBPixelSha256':sha(fresh.samples),'independentSourcePixelPayRows':actual,'candidatePayBandCountAgrees':True,'twoReaderCounts':[p['tesseractCount'],p['rapidCount']],'outsidePaintedNameBandsCount':len(p['outsidePaintedNameBands'])})
flagcounts={}
for f in d['flags']:
 for reason in f['reasons']:flagcounts[reason]=flagcounts.get(reason,0)+1
out={'phase':'complete-source computational guards against immutable candidatev4, before producer final selection','candidatePin':pin(cp),'manualSelectedSourcePin':pin(B/(key+'-peer-final-source-readings.json')),'all3991SourcePaymentRowsMappedExactlyInOrderAndPage':True,'all91ActualBodyPagesOriginalRGBAndRawOcrPinsReplayed':True,'all3991ExpensesComparedToIndependentSourceGlyphGuard':True,'sourceGlyphCounts':glyph['classCounts'],'candidateExpenseGlyphMismatches':shape,'mismatchesOutsidePersonallyReadPacket':[x for x in shape if not x['alreadyPersonallyRead']],'finalHumanSourceReadingsVsV4Differences':diffs,'allActualV4SourceErrorsNeedProducerFinalSelectionBeforeAcceptance':True,'guardedComparisonIsNotWholeCohortHumanTranscription':True,'rawFlagReasonCounts':flagcounts,'pages':pages,'noOutreach':True}
p=B/(key+'-independent-whole-source-guards-v4.json');p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print({'sha256':sha(p.read_bytes()),'glyphMismatches':len(shape),'outsidePeerImages':len(out['mismatchesOutsidePersonallyReadPacket']),'manualFinalVsSnapshotDifferences':len(diffs),'reasons':flagcounts})
