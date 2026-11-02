#!/usr/bin/env python3
"""Apply bounded pixel corroboration, prepare source-only flags/holdout packets."""
import copy,collections,gzip,hashlib,json,re
from pathlib import Path
from gap_school_north_parse import ROOT,AREA,FIELD_NAMES,DEFS,signature,pack,sha

def main():
 pixels_path=AREA/'original-expense-cell-pixels.json.gzip';pp=json.loads(gzip.decompress(pixels_path.read_bytes()));pixels={(x['number'],x['sequence']):x for x in pp['rows']}
 targets=[];summaries=[]
 for n in DEFS:
  p=AREA/f'sd{n:02}-raw-reader-rows.json.gzip';original=json.loads(gzip.decompress(p.read_bytes()));out=copy.deepcopy(original);a,b=out['readers'].values();assert len(a)==len(b),(n,len(a),len(b))
  applied=[];differences=[]
  for index,(first,second) in enumerate(zip(a,b),1):
   assert first['pdfPage']==second['pdfPage'] and abs(first['sourceYPoints']-second['sourceYPoints'])<3.5,(n,index,first['name'],second['name'])
   pixel=pixels.get((n,index));explicit=first['expenses'] is None or second['expenses'] is None
   if pixel:
    for engine,row in [('tesseract',first),('rapid',second)]:
     v=row['expenses'];can=(isinstance(v,str) and v.startswith('UNRESOLVED:') and not re.search(r'\d',row['rawMoneyCells'][1]))
     kind=pixel['classification'];allow=kind=='visibly-empty-source-cell' or kind=='isolated-horizontal-source-dash' and explicit
     if can and allow:
      applied.append({'engine':engine,'sequence':index,'physicalPage':row['pdfPage'],'field':'expenses','before':v,'after':None,'sourcePixelProof':{'file':str(pixels_path.relative_to(ROOT)),'sha256':sha(pixels_path.read_bytes()),'rowSequence':index,'classification':kind,'roiGrayscaleSha256':pixel['roiGrayscaleSha256']}});row['expenses']=None
   da=signature(first);db=signature(second)
   problem_fields=[f for i,f in enumerate(FIELD_NAMES) if da[i]!=db[i]]
   unresolved=[f for r in [first,second] for f in ['remuneration','expenses'] if isinstance(r[f],str) and r[f].startswith('UNRESOLVED:')]
   low=any('low-reader-confidence-not-a-source-accuracy-probability' in r['flags'] for r in [first,second])
   if problem_fields or unresolved or low:
    target={'number':n,'sequence':index,'physicalPage':first['pdfPage'],'y':first['sourceYPoints'],'fields':sorted(set(problem_fields+unresolved)),'lowConfidenceGuard':low,'reasons':(['reader-field-disagreement'] if problem_fields else [])+(['unparsed-money'] if unresolved else [])+(['low-reader-confidence'] if low else [])}
    targets.append(target)
   if problem_fields or unresolved:differences.append({'sequence':index,'fields':problem_fields,'unresolved':unresolved,'tesseract':[first[f] for f in FIELD_NAMES],'rapid':[second[f] for f in FIELD_NAMES]})
  out.update(pixelCorroborationAmendments=applied,differencesAfterPixelCorroboration=differences,acceptedRows=0)
  dest=AREA/f'sd{n:02}-pixel-candidate.json.gzip';dest.write_bytes(pack(out));summary={'number':n,'rows':len(a),'pixelResolvedFields':len(applied),'remainingDifferingOrUnparsedRows':len(differences),'imageReviewTargets':len([t for t in targets if t['number']==n])};summaries.append(summary);print(json.dumps(summary))
 #Deterministic ten source rows per report selected independently of any agreement flags.
 for summary in summaries:
  n=summary['number'];r=json.loads(gzip.decompress((AREA/f'sd{n:02}-pixel-candidate.json.gzip').read_bytes()));rows=r['readers']['tesseract'];flagged={t['sequence'] for t in targets if t['number']==n};eligible=[i for i in range(1,len(rows)+1) if i not in flagged];seed=sha((AREA/f'sd{n:02}-raw-reader-rows.json.gzip').read_bytes())
  chosen=sorted(sorted(eligible,key=lambda i:sha(f'{seed}|school-north-heldout|{i}'.encode()))[:10])
  for i in chosen:
   row=rows[i-1];targets.append({'number':n,'sequence':i,'physicalPage':row['pdfPage'],'y':row['sourceYPoints'],'fields':FIELD_NAMES[:4],'lowConfidenceGuard':False,'reasons':['deterministic-source-image-holdout']})
 selection=AREA/'source-image-targets.json'
 if not selection.exists():selection.write_text(json.dumps({'summaries':summaries,'rows':targets,'transcriptValuesWithheldFromPackets':True,'acceptedRows':0},indent=2)+'\n')
 else:
  fixed=json.loads(selection.read_text()); covered={(x['number'],x['sequence']) for x in fixed['rows']}
  new=[t for t in targets if 'deterministic-source-image-holdout' not in t['reasons'] and (t['number'],t['sequence']) not in covered]
  (AREA/'additional-source-image-targets.json').write_text(json.dumps({'baseSelectionSha256':sha(selection.read_bytes()),'rows':new,'acceptedRows':0},indent=2)+'\n')
if __name__=='__main__':main()
