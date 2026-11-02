#!/usr/bin/env python3
"""Acquire every uncovered, explicitly catalogued employee schedule in seven serials."""
import json,re,concurrent.futures,pathlib,gzip,subprocess
import fitz
from gap_health_employees_fetch import ROOT,AREA,fetch,read,sha
from gap_health_employees_library import originals

SLUG={'Fraser Health':'fraser-health','Interior Health':'interior-health','Northern Health':'northern-health','Providence Health Care':'providence-health-care','Provincial Health Services Authority':'provincial-health-services-authority','Vancouver Coastal Health':'vancouver-coastal-health','Vancouver Island Health':'island-health'}

def candidates():
    baseline=json.loads(subprocess.check_output(['git','show','de42c55e98e42b8001f07e4ecbd210f892ab2716:public/salaries/employers/index.json'],cwd=ROOT));accepted=set()
    for e in baseline['employers']:
        for year,c in zip(baseline['years'],e['coverage']):
            if any(baseline['sources'][i].get('sourceKind')!='compiled' and baseline['sources'][i].get('scope') in ('employee-remuneration','named-employees-over-threshold') for i in c.get('sourceIds',[])):
                accepted.add((e['slug'],year))
    out=[]
    for item in json.loads((AREA/'exact-serial-catalogue.json').read_bytes()):
        serial=' '.join(item['serialIssue'])
        if not re.search(r'employee|remuneration|financial information',serial,re.I) or re.search(r'board|contract employees',serial,re.I):continue
        m=re.search(r'(\d{4})/(\d{4})',serial)
        if not m:continue
        year=m[1]+'/'+m[2][-2:];slug=SLUG[item['issuer']]
        if (slug,year) in accepted:continue
        out.append({**item,'candidateYear':year,'employerSlug':slug,'cataloguePeriodIsNotAcceptanceEvidence':True})
    (AREA/'uncovered-employee-catalogue-items.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out

def one(item):
    streams=originals(item);out=[]
    for bs in streams:
        r=fetch(bs['url'],'Download explicitly catalogued ORIGINAL employee/SOFI candidate',item['issuer']);e={**bs,'retrieval':{k:v for k,v in r.items() if k!='headers'}}
        if r.get('candidateOriginal'):
            d=fitz.open(r['cachePath']);pages=[]
            for n,p in enumerate(d):
                text=p.get_text();pages.append({'physicalPage':n+1,'textLength':len(text),'text':text})
            text='\n'.join(p['text'] for p in pages)
            raw=gzip.compress(json.dumps({'sourceSha256':r['responseSha256'],'pages':pages},ensure_ascii=False,separators=(',',':')).encode(),mtime=0)
            ep=AREA/'native-text-probes'/(r['responseSha256']+'.json.gzip');ep.parent.mkdir(exist_ok=True);ep.write_bytes(raw)
            e.update(pdfPages=len(d),repaired=d.is_repaired,sourceSha256=r['responseSha256'],textEvidencePath=str(ep.relative_to(ROOT)),textEvidenceSha256=sha(raw),nativeCharacters=len(text),imageOnlyPages=[p['physicalPage'] for p in pages if p['textLength']<30],nativeFirstPages=[p['text'][:800] for p in pages[:3]],nativeLastPage=pages[-1]['text'][-1200:])
        out.append(e)
    print(json.dumps({'issuer':item['issuer'],'year':item['candidateYear'],'items':len(out),'files':[{'name':x['name'],'pages':x.get('pdfPages'),'native':x.get('nativeCharacters'),'path':x.get('retrieval',{}).get('cachePath'),'status':x['retrieval'].get('status')} for x in out]}),flush=True)
    return out

def main():
    items=candidates()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:out=[x for group in p.map(one,items) for x in group]
    (AREA/'recovered-employee-originals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cataloguedUncoveredItems':len(items),'originalStreams':len(out),'pdfs':sum(x['retrieval'].get('candidateOriginal',False) for x in out)}))

if __name__=='__main__':main()
