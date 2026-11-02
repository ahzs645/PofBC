#!/usr/bin/env python3
"""One predeclared uniform column-Tesseract monetary calibration, not acceptance."""
import os
for key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ[key]='1'
import argparse
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
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
CACHE=Path('/tmp/queue-completion-phsa/money-column-trial-001')
CONFIG=AREA/'money-column-trial-profile-001.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def load_pin(reference):
    p=ROOT/reference['path']
    if sha(p.read_bytes())!=reference['sha256']:raise ValueError('Frozen calibration input changed')
    return json.loads(p.read_text())


def freeze():
    if CONFIG.exists():raise ValueError('Do not replace a predeclared benchmark profile')
    inventory=AREA/'source-inventory.json';sources=json.loads(inventory.read_text())['sources'];profiles=[]
    for source in sources:
        pp=AREA/(source['id']+'-processing-profile-001.json');profile=json.loads(pp.read_text())
        top=max(h['box'][3] for h in profile['firstTableHeaders'].values())+8
        bottom=min(int(profile['imageDimensions'][1]*profile['tableBodyBottomFraction']),profile['sourceLegalFooterTop']-5)
        profiles.append({'sourceId':source['id'],'sourceSha256':source['sourceSha256'],
                         'profile':pin(pp),'physicalPage':profile['firstSalaryPhysicalPage'],
                         'sourceImagePath':str(Path('/tmp/queue-completion-phsa')/source['id']/'images'/f"p{profile['firstSalaryPhysicalPage']:03d}.png"),
                         'crops':{'remuneration':[profile['namePayBoundary']-8,top,profile['payExpenseBoundary']+8,bottom],
                                  'expenses':[profile['payExpenseBoundary']-8,top,2422,bottom]}})
    model=Path('/usr/share/tesseract-ocr/5/tessdata/eng.traineddata')
    value={'frozenBeforeAnyTrialOcrOrBenchmarkComparison':True,'date':'2026-11-01',
           'sourceInventory':pin(inventory),'profiles':profiles,'uniformOptions':['-l','eng','--psm','6','-c','tessedit_create_txt=1','-c','tessedit_create_tsv=1'],
           'noCharacterWhitelistOrGlyphAlteration':True,'actualRgb300DpiNativePixels':True,'resampling':False,
           'rowMapping':'Map every recognized word center into the unchanged independent actual-source row-cell vertical interval. Require exactly one TSV text line per monetary cell; retain all missing/extra/ambiguous groups.',
           'tesseractVersion':subprocess.check_output(['tesseract','--version'],text=True).splitlines()[0],
           'tesseractBinarySha256':sha(Path('/usr/bin/tesseract').read_bytes()),
           'engModelPath':str(model),'engModelSha256':sha(model.read_bytes()),
           'threadEnvironment':{key:os.environ[key] for key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},
           'maximumConcurrentOcrWorkers':3,'perRowModelChoiceForbidden':True,
           'originalRawProfilesAndReservedReviewsUnchanged':True,'doesNotAuthorizeAnyDataOrPolicyChange':True}
    CONFIG.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(pin(CONFIG)))


def job(task):
    from PIL import Image
    profile,config_sha=task;key=profile['sourceId'];pn=profile['physicalPage'];CACHE.mkdir(parents=True,exist_ok=True)
    source_image=Path(profile['sourceImagePath']);image=Image.open(source_image);results={}
    for field,box in profile['crops'].items():
        prefix=CACHE/(key+'-'+field);crop=prefix.with_suffix('.png');image.crop(box).save(crop)
        command=['tesseract',str(crop),str(prefix),'-l','eng','--psm','6','-c','tessedit_create_txt=1','-c','tessedit_create_tsv=1']
        started=time.perf_counter();completed=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,text=True)
        results[field]={'cropOriginalPixels':box,'inputCropSha256':sha(crop.read_bytes()),'command':command,
                        'rawTsv':prefix.with_suffix('.tsv').read_text(),'rawText':prefix.with_suffix('.txt').read_text(),
                        'stderr':completed.stderr,'wallSeconds':time.perf_counter()-started}
    return {'sourceId':key,'physicalPage':pn,'sourceSha256':profile['sourceSha256'],
            'sourceImageSha256':sha(source_image.read_bytes()),'frozenProfileSha256':config_sha,'fields':results}


def map_cells(trial,page,field):
    raw=trial['fields'][field];left,top,_,_=raw['cropOriginalPixels'];groups={};outside=[]
    for word in readers.tess_words(raw['rawTsv']):
        word={**word,'x':word['x']+left,'y':word['y']+top,
              'box':[word['box'][0]+left,word['box'][1]+top,word['box'][2]+left,word['box'][3]+top]}
        matches=[r for r in page['rows'] if r['expenseOriginalImage']['sourceExpenseCellBox'][1]<=word['y']<r['expenseOriginalImage']['sourceExpenseCellBox'][3]]
        if len(matches)!=1:outside.append(word);continue
        rn=matches[0]['sourceRowOnPage'];groups.setdefault(rn,[]).append(word)
    result=[]
    for row in page['rows']:
        words=sorted(groups.get(row['sourceRowOnPage'],[]),key=lambda w:w['x']);lines={tuple(w['line']) for w in words}
        token=readers.money(' '.join(w['text'] for w in words))
        if len(lines)>1:token={'kind':'ambiguous-multiple-lines','value':None,'raw':token['raw']}
        result.append({'sourceRowOnPage':row['sourceRowOnPage'],'parsed':token,'words':words,'lineCount':len(lines)})
    return result,outside


def run():
    config=json.loads(CONFIG.read_text());config_sha=sha(CONFIG.read_bytes());load_pin(config['sourceInventory'])
    for profile in config['profiles']:load_pin(profile['profile'])
    if sha(Path(config['engModelPath']).read_bytes())!=config['engModelSha256']:raise ValueError('Wrong frozen Tesseract model')
    raw_path=AREA/'money-column-trial-001-raw.json.gzip';out=AREA/'money-column-trial-001-comparison.json'
    if out.exists():raise ValueError('Never replace a frozen comparison')
    if raw_path.exists():raw=json.loads(gzip.decompress(raw_path.read_bytes()))
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
            results=list(pool.map(job,[(p,config_sha) for p in config['profiles']],chunksize=1))
        raw={'predeclaredConfiguration':pin(CONFIG),'script':pin(Path(__file__).resolve()),'sources':results}
        raw_path.write_bytes(gzip.compress(json.dumps(raw,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    if raw['predeclaredConfiguration']!=pin(CONFIG):raise ValueError('Trial did not use the predeclared profile')
    results=[]
    # Frozen image-first truth is opened ONLY after every raw trial is retained.
    for trial,profile_ref in zip(raw['sources'],config['profiles']):
        profile=load_pin(profile_ref['profile']);source=trial['sourceId'];pn=trial['physicalPage']
        page=json.loads(gzip.decompress((COLLECTION/'evidence'/f'{source}-rows-p{pn:03d}.json.gzip').read_bytes()))
        if page['sourceImageSha256']!=trial['sourceImageSha256']:raise ValueError('Wrong actual source pixels')
        fixture=ROOT/profile['fixture']['path']
        if sha(fixture.read_bytes())!=profile['fixture']['sha256']:raise ValueError('Image-first truth changed')
        truth=list(csv.DictReader(fixture.open(),delimiter='\t'));fields={}
        for field,token_key,literal_key in [('remuneration','pay','remunerationLiteral'),('expenses','expense','expensesLiteral')]:
            cells,outside=map_cells(trial,page,field);comparisons=[]
            for cell,row,literal in zip(cells,page['rows'],truth):
                exact=readers.money(literal[literal_key]);baseline=row['tesseract'][token_key] if row['tesseract'] else readers.money('')
                candidate=cell['parsed'];match=lambda a:a['kind']==exact['kind'] and a['value']==exact['value']
                comparisons.append({**cell,'imageFirstLiteral':literal[literal_key],'imageFirstParsed':exact,
                                    'newColumnMatches':match(candidate),'baselineMatches':match(baseline),'baseline':baseline})
            fields[field]={'fields':len(truth),'baselineExact':sum(c['baselineMatches'] for c in comparisons),
                           'uniformColumnExact':sum(c['newColumnMatches'] for c in comparisons),
                           'missingColumnCells':sum(c['parsed']['kind']=='not-recognized' for c in comparisons),
                           'unparsedOrAmbiguousColumnCells':sum(c['parsed']['kind'] in ['unparsed','ambiguous-multiple-lines'] for c in comparisons),
                           'extraOrUnmappedWords':outside,'comparisons':comparisons}
        results.append({'sourceId':source,'sourceSha256':trial['sourceSha256'],'fields':fields})
    value={'predeclaredConfiguration':pin(CONFIG),'completeRawTrial':pin(raw_path),'results':results,
           'totalImageFirstMonetaryFields':sum(f['fields'] for s in results for f in s['fields'].values()),
           'notASecondIndependentEngine':True,'noPerRowChoice':True,'noSourceProfilePolicyOrDataChangeAuthorized':True,
           'expenseDetectorOmissionNeverBecomesDashOrZero':True}
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'comparison':pin(out),'counts':[{s['sourceId']:{f:{k:v for k,v in d.items() if k not in ['comparisons','extraOrUnmappedWords']} for f,d in s['fields'].items()}} for s in results]}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--run',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    elif a.run:run()
    else:p.error('Use --freeze before --run')
