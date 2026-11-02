#!/usr/bin/env python3
"""Audit every monetary row independently of the native readers' name predicate.

The audit deliberately does not require a comma, uppercase initial, valid amount
or recognized job title. Any name-cell text beside a payment-like cell must be
an actual candidate row or an explicitly described non-person control/header.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
NONPERSON=re.compile(r'^(?:(?:[ABCD]\.\s*)?(?:TOTAL(?=\s+(?:FOR|REMUNERATION|ELECTED|EMPLOYEES|EMPLOYER)|,\s*(?:ELECTED|EMPLOYEES))|CONSOLIDATED TOTAL|CONSOLODATED TOTAL|REMUNERATION FOR|REMUNERATION TO|REMUNERATION PAID|EMPLOYER PORTION)|WHOSE REMUNERATION|DETAILED EMPLOYEES|EMPLOYEES WITH|LIST OF|A\. LIST|YEAR ENDED|FISCAL YEAR|TO EACH EMPLOYEE FOR THE YEAR ENDED|NOTE:|PREPARED AS|SCHEDULE OF)',re.I)


def category(config,page,y):
    if page<config['employeeStartPage']:return 'school-trustees'
    if page==config['employeeStartPage']==config['pages'][0] and y<config['employeeStartY']:return 'school-trustees'
    return 'employee-remuneration'


def geometry_audit(proof):
    config=proof['source'];entries=[];unclassified=[]
    for page in proof['mupdfRawPages']:
        # Group by geometric baseline using complete word boxes, without the
        # readers' name filter or monetary regular expression.
        clusters=[]
        for word in sorted(page['words'],key=lambda w:((w[1]+w[3])/2,w[0])):
            y=(word[1]+word[3])/2
            candidates=[c for c in clusters if abs(c['y']-y)<1.7]
            if candidates:cluster=min(candidates,key=lambda c:abs(c['y']-y))
            else:cluster={'y':y,'words':[]};clusters.append(cluster)
            cluster['words'].append(word)
        for cluster in clusters:
            mode=category(config,page['physicalPage'],cluster['y'])
            bounds=config.get('boundsByCategory',{}).get(mode,config['bounds'])
            cells=[[] for _ in range(4)]
            for word in sorted(cluster['words'],key=lambda w:w[0]):
                if word[4]=='$':continue
                cells[sum(word[0]>=x for x in bounds)].append(word[4])
            name,position,pay,expense=[' '.join(c).strip() for c in cells]
            if not name or not pay or not re.search(r'[\d?OoIl]',pay):continue
            # Source headings without payment figures are not rows.
            if not re.search(r'\d',pay):continue
            item={'physicalPage':page['physicalPage'],'y':cluster['y'],'rawCells':[name,position,pay,expense]}
            if NONPERSON.match(name):
                item.update(disposition='excluded-non-person',reason='Printed aggregate/control/heading, retained literally in this audit')
            else:
                matches=[(i+1,r) for i,r in enumerate(proof['mupdfRows']) if r['pdfPage']==page['physicalPage'] and abs(r['y']-cluster['y'])<1.7]
                if len(matches)!=1:
                    item['disposition']='unclassified-payment-row';unclassified.append(item)
                else:item.update(disposition='included-named-observation',candidateSequence=matches[0][0])
            entries.append(item)
    included=[e for e in entries if e['disposition']=='included-named-observation']
    assert len(included)==len(proof['mupdfRows']),('Candidate rows not bijective to raw payment cells',len(included),len(proof['mupdfRows']))
    assert len({e['candidateSequence'] for e in included})==len(included)
    assert not unclassified,unclassified
    return entries


def text_audit(proof):
    config=proof['source'];entries=[];unclassified=[]
    accounted={(r['pdfPage'],r['sourceLine']) for r in proof['popplerRows']}
    accounted|={(r['pdfPage'],r['precedingPhysicalTextLine']) for r in proof['popplerRows'] if 'precedingPhysicalTextLine' in r}
    pages=proof['popplerRawText'].split('\f')
    for number in config['pages']:
        for line_number,line in enumerate(pages[number-1].splitlines(),1):
            text=line.strip()
            # Independent broad selection: any alphabetic text followed by a
            # table-like amount of four or more digits (with optional commas).
            significant=[m.group() for m in re.finditer(r'\d[\d,]*(?:\.\d{2})?',text)
                         if len(re.sub(r'\D','',m.group().split('.')[0]))>=4]
            if not significant or not re.search(r'[A-Za-z]',text):continue
            item={'physicalPage':number,'lineNumber':line_number,'sourceLine':line}
            if (number,line) in accounted:item['disposition']='included-named-observation'
            elif NONPERSON.match(text):item.update(disposition='excluded-non-person',reason='Printed aggregate/control/heading; no individual observation inferred')
            elif re.match(r'^[A-Z][A-Z\s]+(?:REMUNERATION|POSITION)',text):item.update(disposition='excluded-column-heading',reason='Printed column/threshold heading')
            else:item['disposition']='unclassified-significant-amount-line';unclassified.append(item)
            entries.append(item)
    assert not unclassified,unclassified
    return entries


def main():
    results=[]
    for c in json.loads((AREA/'native-specs.json').read_bytes()):
        path=AREA/c.get('candidateFile',c['key']+'-native-candidate.json.gzip');raw=path.read_bytes();proof=json.loads(gzip.decompress(raw))
        geometry=geometry_audit(proof);text=text_audit(proof)
        results.append({'key':c['key'],'sourceSha256':c['sourceSha256'],'candidate':{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()},
                        'geometryPaymentRowAudit':geometry,'physicalTextAudit':text,'allPaymentRowsAccounted':True,'candidateRows':len(proof['mupdfRows'])})
        print(c['key'],len(geometry),len(text),'PASS')
    (AREA/'native-payment-row-coverage.json').write_text(json.dumps({'status':'passed','sources':results},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
