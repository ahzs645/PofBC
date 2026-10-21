from pathlib import Path
import json,hashlib,re,collections
from pypdf import PdfReader,PdfWriter

B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cs=read(B/'claims.json');hs=read(B.parent/'health/claims.json')
uses=collections.defaultdict(list)
for c in cs+hs:
    for sid in c.get('source_ids',[]):
        uses[sid].append(dict(claim_id=c.get('id'),locator=c.get('locator',c.get('pinpoint')),
                             role=c.get('event_type',c.get('claim_type'))))
src=read(B/'sources.json')
rows=[];errors=[]
selected={80:[1,47,48,49,77,78,90,266],81:[1,80]}
rr=PdfReader(B/'raw/R4R-081.pdf')
for i,p in enumerate(rr.pages[:100]):
    t=p.extract_text()
    if 'Election Act' in t and '101/88' in t:selected[81].append(i+1)
for n in selected:selected[n]=sorted(set(selected[n]))
(B/'excerpts').mkdir(exist_ok=True)
for s in src:
    sid=s['id'];p=B/s['local_file']; h=sha(p)
    if h!=s['sha256']:errors.append(f'hash mismatch {sid}')
    used=sid in uses
    role='supports_scoped_claim_or_guard' if used else 'screened_not_used_for_formal_claim'
    s['review_role']=role
    s['claim_locators']=uses[sid]
    s['review_scope']='Relevant clauses, named entries, dates and source-page locators only; not a claim of full historical or geographic reconstruction.' if used else 'Retrieved candidate screened during discovery; not promoted to a positive historical finding.'
    row=dict(source_id=sid,title=s['title'],url=s['url'],role=role,
             original_local_file=s['local_file'],original_sha256=h,original_bytes=p.stat().st_size,
             claim_evidence=uses[sid],include_in_claim_evidence=used)
    if used:
        n=int(sid.split('-')[1]);out=p;kind='exact_downloaded_original'
        if n in selected:
            r=PdfReader(p);w=PdfWriter()
            for page in selected[n]:w.add_page(r.pages[page-1])
            out=B/'excerpts'/f'{sid}-cited-pages.pdf'
            with out.open('wb') as f:w.write(f)
            kind='selected_original_pdf_pages'
            row['page_mapping']=[dict(excerpt_pdf_page=i+1,original_pdf_page=page) for i,page in enumerate(selected[n])]
        row.update(package_local_file=str(out.relative_to(B)),package_sha256=sha(out),package_bytes=out.stat().st_size,package_kind=kind)
    rows.append(row)
write(B/'sources.json',src)
manifest=dict(prepared_on='2026-10-21',source_catalogue_records=len(src),
    roles=dict(collections.Counter(x['role'] for x in rows)),
    originals_supporting_scoped_claims_bytes=sum(x['original_bytes'] for x in rows if x['include_in_claim_evidence']),
    selected_evidence_bytes=sum(x.get('package_bytes',0) for x in rows),
    policy='Complete small originals plus labelled page extracts of two long official statute tables. Every original is retained locally; only selected evidence is included in the claim-evidence archive. Screened candidates have separate search-audit treatment.',
    rows=rows,validation_errors=errors)
write(B/'evidence_manifest.json',manifest)

findings={
 'A8':['25 hospital improvement district incorporations and the 1969/1972 ending and transfer chains recovered; 43 regional hospital district identities reconstructed with original starts.',
       'The 1995 restriction, twelve 1996 incorporations, thirteen 1998 power restorations, five 1998 dissolutions and multiple asset recipients are separated.'],
 'G1':['New examples require separate membership, board selection, records reporting, statutory administration, asset transfer, financing and service relations.'],
 'G2':['Regional hospital district FOIPPA class begins 3 November 1994; professional Schedule 3 commencement on 6 November 1995 now has its original order. The health module adds boards and councils on 13 July 1995.'],
 'G3':['Original HID trustee and elector rules are extracted by district; contemporary RHD membership and board amendments supply dated governance checkpoints.'],
 'G4':['Capital-funding entities are distinguished from hospital service operators; direct service population is not inferred from property ownership.'],
 'G5':['The 1988 franchise amendment is identified as 1988 c.2, effective 28 March 1988 under Reg.101/88; original HID electorates require separate qualifications.'],
 'G7':['Alberni-Clayoquot treaty-land membership amendment effective 1 April 2012 and the protection from requisitions for specified prior borrowing on 17 December 2015 recovered.'],
 'C2':['Official statutory tables corroborate 21 October 1977 for identified amendments under 1977 c.75; actual proclamation and direct Health-title entry still missing.']}
remaining={
 'A8':['Old 1968 Cariboo RHD ultimate ending; first hospital Peace River-Liard rename; actual 1998 closing agreements; separately executed 1972 conveyances; remaining HIDs outside this 25-body set; full boundary histories.'],
 'G1':['Implementation remains model work; no repository mutation in this research pass.'],
 'G2':['First coverage must be matched to individual legal identity and existence; full appeal, complaint, audit and Ombudsperson histories remain incomplete.'],
 'G3':['All subsequent governance amendments and actual appointments have not been reconstructed.'],
 'G4':['The source base is not a complete service-population register for all bodies.'],
 'G5':['Remaining colonial qualifications and litigation/practical-voting intervals; original HID rules must not be extended unchanged through all later years.'],
 'G7':['No census of all First Nations governments or agreements; membership date is not Nation creation or treaty commencement.'],
 'C2':['Actual proclamation or direct official departmental-title entry for the 1977 transition.']}
coverage=[]
for item in findings:
    matching=[c for c in cs if item in c['item_ids']]
    coverage.append(dict(id=item,status='partially_resolved',new_findings=findings[item],remaining_records=remaining[item],
       claim_ids=[c['id'] for c in matching],source_ids=sorted({s for c in matching for s in c['source_ids']})))
# Prose fields are written separately below with normal spacing; exact IDs stay untouched.
write(B/'coverage.json',coverage)
print(json.dumps({k:v for k,v in manifest.items() if k not in {'rows','policy'}},indent=2))
if errors:raise SystemExit(1)
