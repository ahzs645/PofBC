#!/usr/bin/env python3
"""Delta selected visible fields; hidden text overflow is not a complete name."""
import gzip,json,hashlib,collections
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA,ROOT

def sha(b):return hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def run():
 import fitz
 from PIL import Image
 path=AREA/'sd37-native-candidate-v4.json.gzip';base=json.loads(gzip.decompress(path.read_bytes()));chosen=json.loads((AREA/'sd37-primary-crowded-name-title-readings-v2.json').read_text());rows=[dict(x) for x in base['mupdfRows']];decisions=[]
 for d in chosen['readings']:
  seq=d['sequence'];r=rows[seq-1];r['nativeReaderFieldsBeforeSourceImageSelection']=[{k:x[k] for k in base['fields']} for x in [base['popplerRows'][seq-1],base['mupdfRows'][seq-1]]];r['name']=d['name'];r['position']=d['position'];r['sourceVisibleNameQualification']=d['qualification']
  if d.get('visibleNameFragment'):r['sourceVisibleNameFragment']=d['visibleNameFragment']
  decisions.append({'sequence':seq,'selectedFields':{k:r[k] for k in base['fields']},'primarySelection':ref(AREA/'sd37-primary-crowded-name-title-readings-v2.json')})
 controls={}
 for cat,printed in [('employee-remuneration',['114425758','579812']),('school-trustees',['247664','17194'])]:
  xs=[r for r in rows if r['category']==cat];computed=[str(sum(Decimal(r[f] or '0') for r in xs)) for f in ['remuneration','expenses']];controls[cat]={'rows':len(xs),'literalPrintedControls':printed,'computed':computed,'residuals':[str(Decimal(a)-Decimal(b)) for a,b in zip(computed,printed)]}
 peer=ROOT/'research/salaries/gap-fill-2026-11-02/municipal/reviews/school-south/delta-eight-bounded-peer-review.json';peer_data=json.loads(peer.read_text());assert peer_data['status']=='pass-for-explicit-bounded-name-title-scope';assert peer_data['sourceOriginalSha256']==base['source']['sha256'];assert peer_data['selectedPrimaryV2']==ref(AREA/'sd37-primary-crowded-name-title-readings-v2.json');assert all(r['visibleNameAndTitleAgree'] for r in peer_data['comparisons'])
 result={'district':37,'source':base['source'],'fields':base['fields'],'rows':rows,'rawCandidate':ref(path),'imageFieldSelections':decisions,'boundedNameTitlePeerReview':ref(peer),'controls':controls,'status':'selected-candidate-pending-complete-source-peer-replay','originalRasterVisibility':ref(AREA/'sd37-native-original-raster-visibility-v2.json.gzip'),'noOutreach':True}
 out=AREA/'sd37-selected-candidate-v5.json.gzip';out.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
 pdf=Path(base['source']['cachePath']);assert sha(pdf.read_bytes())==base['source']['sha256'];doc=fitz.open(pdf);root=AREA/'delta-peer-images';root.mkdir(exist_ok=True);contexts=[];targets=[]
 for p in [1,2,3,54,69]:
  target=root/f'sd37-context-p{p}-180.png';doc[p-1].get_pixmap(dpi=180).save(target);contexts.append({'physicalPage':p,'dpi':180,**ref(target)})
 flagged={r['sequence'] for r in chosen['readings']};pool=[i for i in range(1,len(rows)+1) if i not in flagged];hold=sorted(pool,key=lambda i:sha(f'delta-native-source-holdout-v1:{i}'.encode()))[:10];pages={}
 for seq in sorted(flagged|set(hold)):
  r=rows[seq-1];p=r['pdfPage'];y=r['sourceY']
  if p not in pages:
   pix=doc[p-1].get_pixmap(dpi=600);pages[p]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  scale=600/72;box=[0,max(0,int((y-7)*scale)),pages[p].width,int((y+7)*scale)+1];target=root/f'sd37-seq{seq}-source600.png';pages[p].crop(box).save(target);targets.append({'sequence':seq,'physicalPage':p,'integerBox600Dpi':box,'kind':'previously-peer-reviewed-source-name-title-flag' if seq in flagged else 'withheld-native-agreement-benchmark',**ref(target)})
 packet={'district':37,'source':{k:base['source'][k] for k in ['sourceUrl','sha256','cachePath']},'rawCandidate':ref(path),'selectedCandidate':ref(out),'nativeParser':ref(ROOT/'scripts/gap_school_south_native.py'),'salaryPages':base['spec']['pages'],'targets':targets,'contexts':contexts,'boundedEightFieldPeerReceipt':ref(peer),'reviewStillNeeded':'Independent full original native-reader replay, complete payment census and10 personally source-read agreement benchmarks/context/controls. Eight flagged visible name/title cases already independently source-read;926 incomplete name is null with explicit visible fragment.','noChosenValuesIncluded':True,'noOutreach':True}
 (AREA/'sd37-complete-source-peer-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'rows':len(rows),'controls':controls,'peerPacket':str(AREA/'sd37-complete-source-peer-packet.json')}))
if __name__=='__main__':run()
