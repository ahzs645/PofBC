#!/usr/bin/env python3
"""Freeze complete original page evidence and every uncertain employee field."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

import finish_salary_phsa_rows as readers
import finish_salary_phsa_geometry as geometry

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
CACHE=Path('/tmp/queue-completion-phsa')
SLUG='provincial-health-services-authority'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def suspicious_name(name):
    reasons=[]
    words=re.split(r'[,\s]+',name)
    if any(w and w[0].islower() for w in words):reasons.append('source-name-lowercase-word-initial-needs-image-review')
    if '|' in name or any(c.isdigit() for c in name):reasons.append('source-name-pipe-or-digit-needs-image-review')
    if name.count(',')!=1:reasons.append('source-name-separator-needs-image-review')
    if ',' in name and re.search(r'[a-z][A-Z]',name.split(',',1)[1]):
        reasons.append('source-given-name-word-spacing-needs-image-review')
    return reasons


def match_row(rows,y,tolerance):
    matches=[r for r in rows if abs(r['y']-y)<tolerance]
    return matches[0] if len(matches)==1 else None,matches


def page(raw_path,profile_path):
    raw=json.loads(gzip.decompress(raw_path.read_bytes()));profile=json.loads(profile_path.read_text())
    if raw['sourceSha256']!=profile['sourceSha256'] or raw['sourceSpecificProfile']['sha256']!=sha(profile_path.read_bytes()):
        raise ValueError('Raw page source/profile identity changed')
    key=raw['sourceId'];pn=raw['physicalPage'];out=COLLECTION/'evidence'/f'{key}-rows-p{pn:03d}.json.gzip'
    if out.exists():return json.loads(gzip.decompress(out.read_bytes()))
    raw_target=COLLECTION/'evidence'/f'{key}-raw-p{pn:03d}.json.gzip';raw_target.parent.mkdir(parents=True,exist_ok=True)
    if raw_target.exists() and raw_target.read_bytes()!=raw_path.read_bytes():raise ValueError('Frozen raw source evidence changed')
    if not raw_target.exists():shutil.copyfile(raw_path,raw_target)
    period_end=str(int(profile['year'][:4])+1)
    tess_head=re.sub(r'[^a-z0-9]','',raw['tesseractRawText'].lower())
    rapid_head=re.sub(r'[^a-z0-9]','',' '.join(r[1] for r in raw['rapidocrRaw'] if sum(p[1] for p in r[0])/4<profile['imageDimensions'][1]*.4).lower())
    date_checks={engine:any(pattern in text for pattern in ['31march'+period_end,'march31'+period_end])
                 for engine,text in [('tesseract',tess_head),('rapidocr',rapid_head)]}
    result={'version':1,'sourceId':key,'sourceSha256':raw['sourceSha256'],'physicalPage':pn,
            'rawPage':pin(raw_target),'sourceProfile':pin(profile_path),'sourceImagePath':raw['sourceImagePath'],
            'sourceImageSha256':raw['sourceImageSha256'],'imageDimensions':profile['imageDimensions'],
            'dateTitleChecks':date_checks,'dateTitleNeedsReview':not all(date_checks.values()),
            'role':'employee-salary-table','rows':[],'pageGeometryNeedsReview':False,'pageIssues':[]}
    if pn<profile['firstSalaryPhysicalPage']:
        result['role']='explanatory-preface-no-employee-rows'
    else:
        source_geometry,ink=geometry.page_geometry(raw,profile)
        tess,tess_totals,tess_issues=readers.read_tesseract(raw,profile)
        rapid,rapid_totals,rapid_issues=readers.read_rapid(raw,profile)
        bands=source_geometry['nameBands'];pitch=source_geometry['rowPitchPixels']
        result.update({'actualSourceGeometry':source_geometry,'tesseractNamedRowCount':len(tess),
                       'rapidNamedRowCount':len(rapid),'actualRasterNameBandCount':len(bands),
                       'tesseractControlLabels':tess_totals,'rapidControlLabels':rapid_totals})
        result['pageIssues']=tess_issues+rapid_issues
        if len(tess)!=len(bands):result['pageIssues'].append('tesseract-name-count-differs-from-source-ink-bands')
        if len(rapid)!=len(bands):result['pageIssues'].append('rapid-name-count-differs-from-source-ink-bands')
        irregular=[i+1 for i,(a,b) in enumerate(zip(bands,bands[1:]))
                   if not profile['sourceFirstTableRowPitchPixels']*.65<b['center']-a['center']<profile['sourceFirstTableRowPitchPixels']*1.45]
        if irregular:result['pageIssues'].append('irregular-source-name-band-spacing')
        result['pageGeometryNeedsReview']=source_geometry['tableHeaderNeedsReview'] or bool(irregular) or not bands or (len(bands)!=len(tess) and len(bands)!=len(rapid))
        used_tess=set();used_rapid=set()
        for i,band in enumerate(bands):
            t,tm=match_row(tess,band['center'],pitch*.42);r,rm=match_row(rapid,band['center'],pitch*.42)
            if t is not None:used_tess.add(t['y'])
            if r is not None:used_rapid.add(r['y'])
            field_reasons=collections.defaultdict(list)
            for label,reader in [('tesseract',t),('rapid',r)]:
                if reader is None:
                    for field in ['name','remuneration','expenses']:field_reasons[field].append(label+'-missing-or-ambiguous-source-row')
            name=readers.name_comparison(t['name']) if t else ''
            pay=t['pay']['value'] if t and t['pay']['kind']=='number' else None
            glyph=geometry.expense_glyph(ink,source_geometry,profile,i)
            is_dash=geometry.is_source_dash(glyph,profile['dashCalibration'])
            glyph['matchesSourceCalibratedDashGeometry']=is_dash
            glyph['matchesKnownExactSourceMask']=glyph.get('maskSha256') in profile['dashCalibration']['knownMaskSha256']
            expense=t['expense']['value'] if t and t['expense']['kind']=='number' else None
            if t and r:
                if readers.name_comparison(t['name'])!=readers.name_comparison(r['name']):field_reasons['name'].append('independent-name-disagreement')
                if t['nameConfidence']<85:field_reasons['name'].append('tesseract-name-confidence-below-85')
                if r['nameConfidence']<.98:field_reasons['name'].append('rapid-name-confidence-below-0.98')
                if len(r['namePieces'])!=1:field_reasons['name'].append('rapid-name-multiple-source-boxes')
                if t['pay']['kind']!='number' or r['pay']['kind']!='number' or t['pay']['value']!=r['pay']['value']:
                    field_reasons['remuneration'].append('independent-pay-disagreement-or-unparsed')
                if t['payConfidence'] is None or t['payConfidence']<90:field_reasons['remuneration'].append('tesseract-pay-confidence-below-90')
                if r['payConfidence'] is None or r['payConfidence']<.98:field_reasons['remuneration'].append('rapid-pay-confidence-below-0.98')
                if is_dash:
                    if t['expense']['kind']=='number' or r['expense']['kind']=='number':
                        field_reasons['expenses'].append('numeric-ocr-conflicts-with-original-dash-geometry')
                    expense=None
                else:
                    if t['expense']['kind']!='number' or r['expense']['kind']!='number' or t['expense']['value']!=r['expense']['value']:
                        field_reasons['expenses'].append('independent-expense-disagreement-or-unproved-glyph')
                    if t['expenseConfidence'] is None or t['expenseConfidence']<90:field_reasons['expenses'].append('tesseract-expense-confidence-below-90')
                    if r['expenseConfidence'] is None or r['expenseConfidence']<.98:field_reasons['expenses'].append('rapid-expense-confidence-below-0.98')
            if pay is None or pay<=75000:field_reasons['remuneration'].append('source-pay-threshold-or-unparsed-needs-image-review')
            field_reasons['name']+=suspicious_name(name)
            reasons={field:values for field,values in field_reasons.items() if values}
            result['rows'].append({'sourceRowOnPage':i+1,'physicalPage':pn,'sourceNameBand':band,
                                   'candidateRow':[SLUG,name,None,pay,expense,pn],
                                   'tesseract':t,'rapidocr':r,'tesseractSourceRowMatches':tm,'rapidSourceRowMatches':rm,
                                   'expenseOriginalImage':glyph,'fieldConflicts':reasons,
                                   'requestedFields':[f for f in ['name','remuneration','expenses'] if f in reasons]})
        if len(used_tess)!=len(tess) or len(used_rapid)!=len(rapid):
            result['pageGeometryNeedsReview']=True;result['pageIssues'].append('reader-source-row-not-uniquely-mapped-to-actual-name-band')
    out.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    return result


def run():
    profile_pins=json.loads((AREA/'processing-profile-index-001.json').read_text())['sourceProfiles']
    progress=[]
    for pin in profile_pins:
        source=pin['sourceId'];profile_path=ROOT/pin['path'];stats=collections.Counter()
        for raw_path in sorted((CACHE/source/'raw-selected').glob('p*.json.gzip')):
            result=page(raw_path,profile_path);stats.update(pages=1,rows=len(result['rows']),flaggedRows=sum(bool(r['requestedFields']) for r in result['rows']),
                                                         geometryPages=int(result['pageGeometryNeedsReview']),dateTitlePages=int(result['dateTitleNeedsReview']))
        progress.append({'sourceId':source,**stats})
    out=AREA/'stage-progress.json';out.write_text(json.dumps({'sourceProgress':progress,'rawEvidenceImmutable':True,
                                                            'notAnAcceptanceClaim':True},indent=2)+'\n')
    print(json.dumps(progress))


if __name__=='__main__':run()
