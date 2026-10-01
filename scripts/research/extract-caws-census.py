"""Re-extract the four CAWS rosters from local source captures (pip install beautifulsoup4).
Run from repository root; raw captures belong in tmp/research/raw, not in git.
Does not infer founding, continuous parentage, or abolition from a missing row.
"""
from bs4 import BeautifulSoup
from pathlib import Path
import json, re, hashlib
MINISTRY = "Ministry of Community, Aboriginal and Women's Services"
def clean(text): return ' '.join(text.split())
def rows_for(period, page):
    path=Path(f'tmp/research/raw/{period}-{page}.html')
    soup=BeautifulSoup(path.read_bytes(), 'html.parser')
    h=soup.find('h1'); content=h.parent
    rows=[]; department=None; parent=None
    def add(name, level, parent_name):
        rows.append({'ordinal':len(rows)+1,'name_as_printed':name,'level':level,'parent_as_printed':parent_name,'ministry_as_printed':MINISTRY})
    if page=='appendixc':
        for tr in h.find_next('table').find_all('tr'):
            if tr.find('h3'):
                department=clean(tr.h3.get_text());parent=department;add(department,'department',MINISTRY);continue
            if tr.find(class_='footnote'):continue
            cells=tr.find_all('td');texts=[clean(c.get_text()) for c in cells]
            text=' '.join(t for t in texts if t and t!='•')
            if not text:continue
            child='•' in texts
            add(text,'nested_unit' if child else 'unit',parent if child else department)
            if not child:parent=text
    elif page=='appendixb':
        for p in h.find_all_next('p'):
            if p.parent is not content:continue
            if not p.find('b'):continue
            lines=[clean(t) for t in p.get_text(separator='\n').splitlines() if clean(t)]
            # Raw text newline wrapping is not a unit boundary: use <br> boundaries.
            parts=re.split(r'<br\s*/?>',str(p),flags=re.I)
            lines=[clean(BeautifulSoup(part,'html.parser').get_text()) for part in parts]
            lines=[x for x in lines if x]
            department=lines[0];parent=department;add(department,'department',MINISTRY)
            for part,text in zip([x for x in parts[1:] if clean(BeautifulSoup(x,'html.parser').get_text())],lines[1:]):
                plain=BeautifulSoup(part,'html.parser').get_text()
                # Whitespace includes HTML source indentation: non-breaking spaces give hierarchy.
                child=plain.count('\xa0')>=6
                add(text,'nested_unit' if child else 'unit',parent if child else department)
                if not child:parent=text
    else:
        for tag in h.find_next_siblings():
            if tag.name=='h3':department=clean(tag.get_text());continue
            if tag.name!='p':continue
            if tag.find('b'):department=clean(tag.b.get_text());continue
            for sup in tag.find_all('sup'):sup.decompose()
            for part in re.split(r'<br\s*/?>',str(tag),flags=re.I):
                text=clean(BeautifulSoup(part,'html.parser').get_text())
                if text:add(text,'listed_body_or_board',department)
    for row in rows:row['locator']=f'{page}, {row["parent_as_printed"]}, roster occurrence {row["ordinal"]}'
    url=f'https://www.bcbudget.gov.bc.ca/annual_reports/{period}/caws/caws_{page}.htm'
    return {'id':f'caws-{period}-{page}','source_url':url,'capture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'report_period':period[:4]+'/'+period[-2:],'observed_on':'2003-05-30' if page=='appendixc' else None,'coverage':'dated_observation' if page=='appendixc' else 'report_roster_temporal_scope_unresolved','rows':rows}
rosters=[rows_for(p,a) for p,a in [('2002_2003','appendixc'),('2003_2004','appendixb'),('2002_2003','appendixa'),('2003_2004','appendixa')]]
for r in rosters:
    r['limitation']='A printed roster entry is not a founding date or proof of continuous parentage. Absence from the adjacent roster is not proof of abolition.'
    if r['id'].endswith('2002_2003-appendixc'):r['limitation']+=' The footnote dates this chart after its report fiscal period.'
    if r['id'].endswith('2003_2004-appendixb'):r['limitation']+=' The narrative limits the chart to the first ten months and reports transfers that conflict with some listed placements.'
    if r['id'].endswith('appendixa'):r['limitation']+=' Corporate governing boards are distinct from their corporations; listed responsibility does not establish administrative supervision.'
# Explicit matches only. Similar wording is a candidate, not institutional continuity.
known={}
for name in ['bodies','sub-divisions','sub-tribunals','sub-subsidiaries']:
    for r in json.load(open(f'research/history/{name}.json'))['records']:
        known.setdefault(clean(r['name']).lower(), []).append(r['id'])
aliases={'Public Library Services Branch':'public-libraries-branch','Building Policy Branch':'building-and-safety-standards','Government Agents Branch':'service-bc','Electrical Safety Review Board':'electrical-safety-board-of-review','Royal British Columbia Museum':'royal-bc-museum','First Peoples\' Heritage, Language and Culture Council':'first-peoples-cultural-council'}
for roster in rosters:
    for row in roster['rows']:
        name=row['name_as_printed'];matches=sorted(set(known.get(name.lower(),[])))
        row['match_ids']=matches
        row['disposition']='exact_name_match_identity_unverified' if matches else 'historical_unit_candidate'
        if name in aliases:
            row['candidate_id']=aliases[name];row['disposition']='identity_requires_reconciliation'
        if name in ['Community Charter Implementation','Infrastructure and Financial Management','Child Care Programs']:
            row['disposition']='program_or_unit_unresolved'
        if 'Board of Commissioners' in name or 'Board of Directors' in name:
            row['disposition']='governance_board_not_corporation'
        if name in ['Boards of Variance','Municipal Insurance Association']:
            row['disposition']='scope_requires_review'
        if name=='Fire Safety Advisory Council' and any(x['name_as_printed']==name and x['ordinal']<row['ordinal'] for x in roster['rows']):
            row['disposition']='repeated_source_entry'
result={'schema_version':'historical-census/1','reviewed_on':'2026-09-30','ministry':MINISTRY,'scope':'Complete entries in four organization/ABC appendices; narrative reconciliations kept separately. These are source rosters, not established entity lifecycles.','rosters':rosters}
Path('research/censuses/caws-2002-2004.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print([(r['id'],len(r['rows'])) for r in rosters])
