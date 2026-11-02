#!/usr/bin/env python3
"""Calibrate Tesseract input/model against frozen literal source-name fixtures."""
import os
for key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import concurrent.futures
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
import finish_salary_phsa_rows as readers

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
REVIEWS=ROOT/'research/salaries/queue-completion-2026-11-01/reviews'
CACHE=Path('/tmp/queue-completion-phsa')


def job(task):
    from PIL import Image
    source,config=task;key=source['id'];year=source['year'].replace('/','-')
    fp=REVIEWS/f'independent-phsa-history-batches-benchmark-{year}-original-transcript.tsv'
    fixture=list(csv.DictReader(fp.open(),delimiter='\t'));pn=int(fixture[0]['physicalPage'])
    raw=json.loads(gzip.decompress((CACHE/key/'raw'/f'p{pn:03d}.json.gzip').read_bytes()))
    profile=readers.source_profile(raw,fixture)
    out=CACHE/key/(config+'.json')
    if out.exists():result=json.loads(out.read_text())
    else:
        image=Path(raw['sourceImagePath']);crop=None
        if 'column' in config:
            im=Image.open(image);crop=[profile['firstTableHeaders']['Name']['box'][0]-15,
                                       profile['firstTableHeaders']['Name']['box'][3]+8,
                                       profile['namePayBoundary']-20,int(im.height*.94)]
            image=CACHE/key/(config+'.png');im.crop(crop).save(image)
        prefix=CACHE/key/config
        args=['tesseract',str(image),str(prefix),'-l','eng','--psm','6']
        if 'best' in config:args+=['--tessdata-dir','/tmp/queue-completion-phsa/tessdata-best']
        # An isolated model directory does not contain the system txt/tsv config files.
        args+=['-c','tessedit_create_txt=1','-c','tessedit_create_tsv=1'];started=time.perf_counter()
        subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        result={'sourceSha256':source['sourceSha256'],'sourceImageSha256':raw['sourceImageSha256'],
                'imageInputSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'cropBox':crop,'configuration':config,
                'tesseractRawTsv':prefix.with_suffix('.tsv').read_text(),'tesseractRawText':prefix.with_suffix('.txt').read_text(),
                'wallSeconds':time.perf_counter()-started,'invocation':args}
        out.write_text(json.dumps(result,ensure_ascii=False)+'\n')
    if 'column' in config:
        grouped={}
        for w in readers.tess_words(result['tesseractRawTsv']):grouped.setdefault(w['line'],[]).append(w)
        parsed=[{'name':' '.join(w['text'] for w in sorted(ws,key=lambda w:w['x']))} for _,ws in sorted(grouped.items(),key=lambda kv:min(w['y'] for w in kv[1]))]
    else:
        alt=dict(raw);alt['tesseractRawTsv']=result['tesseractRawTsv'];parsed,_,_=readers.read_tesseract(alt,profile)
    compare=[]
    for i,f in enumerate(fixture):
        r=parsed[i] if i<len(parsed) else None
        compare.append({'row':i+1,'literal':f['name'],'recognized':r['name'] if r else None,
                        'nameMatch':bool(r) and readers.name_comparison(r['name'])==readers.name_comparison(f['name'])})
    return {'sourceId':key,'configuration':config,'rows':len(parsed),'fixtureRows':len(fixture),
            'nameMatches':sum(r['nameMatch'] for r in compare),'perRowComparison':compare,
            'rawTrialFile':str(out),'rawTrialSha256':hashlib.sha256(out.read_bytes()).hexdigest()}


def run():
    selected=json.loads((AREA/'source-inventory.json').read_text())['sources']
    tasks=[(s,c) for c in ['best-full-300','fast-column-300','best-column-300'] for s in selected]
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        for result in pool.map(job,tasks,chunksize=1):
            results.append(result);print(json.dumps({k:result[k] for k in ['sourceId','configuration','rows','fixtureRows','nameMatches']}),flush=True)
    out=AREA/'first-table-tesseract-benchmark-trials.json'
    if out.exists():raise ValueError('Frozen benchmark already exists')
    out.write_text(json.dumps({'results':results,'independence':'Multiple Tesseract models/configurations remain one engine. Every chosen per-source reader must independently agree with Paddle or be image resolved.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':run()
