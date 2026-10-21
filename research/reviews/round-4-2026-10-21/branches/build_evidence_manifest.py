"""Inventory full originals and create faithful extracts of large cited PDFs.

The original files are retained. Extracts contain selected original PDF pages,
not transcriptions or re-renderings, and carry explicit source-page mappings.
"""
import json, hashlib
from pathlib import Path
from collections import Counter
from pypdf import PdfReader, PdfWriter

B=Path(__file__).parent
sources=json.loads((B/'sources.json').read_text())
claims=json.loads((B/'claims.json').read_text())
by_claim={c['id']:c for c in claims}
pages={
 'R4B-003':[37,46,47],
 'R4B-006':[1,17,18],
 'R4B-007':[1,5],
 'R4B-027':[1,3,22,26],
 'R4B-035':[1,2,239,242],
 'R4B-038':[1,6],
 'R4B-039':[1,149,150,151,152],
 'R4B-049':[1,2673],
 'R4B-050':[1,4],
 'R4B-075':[1,11],
}
E=B/'excerpts';E.mkdir(exist_ok=True)
rows=[]
for s in sources:
    used=[by_claim[c] for c in s.get('claim_ids',[])]
    f=B/s['local_file'] if s.get('local_file') else None
    substantive=[c for c in used if c['evidence_role']=='substantive_historical_finding']
    if s['id'].startswith('R3'):
        category='prior_original_reused'
    elif substantive:
        category='accepted_original'
    elif used:
        category='diagnostic_or_lead_original'
    elif s.get('retrieval_status')=='retrieved':
        category='screened_only'
    else:
        category='unusable_retrieval'
    row={
        'source_id':s['id'], 'title':s['title'], 'url':s['url'],
        'category':category, 'original_local_file':s.get('local_file'),
        'original_sha256':s.get('sha256'), 'original_bytes':s.get('bytes'),
        'retrieval_status':s.get('retrieval_status'),
        'claim_evidence':[{'claim_id':c['id'],'role':c['evidence_role'],'locator':c['locator']} for c in used],
        'include_in_compact_evidence_package':bool(used),
    }
    if s['id'] in pages:
        p=E/(s['id']+'-cited-pages.pdf')
        reader=PdfReader(str(f));writer=PdfWriter()
        for n in pages[s['id']]:writer.add_page(reader.pages[n-1])
        writer.add_metadata({'/Title':s['title']+' — cited source pages','/Subject':'Verbatim PDF page extract. Source-page mapping is in evidence-manifest.json; full original is retained.'})
        with p.open('wb') as h:writer.write(h)
        row['compact_local_file']=str(p.relative_to(B))
        row['compact_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        row['compact_bytes']=p.stat().st_size
        row['compact_kind']='selected_original_pdf_pages'
        row['page_mapping']=[{'excerpt_pdf_page':i+1,'original_pdf_page':n} for i,n in enumerate(pages[s['id']])]
    elif used:
        row['compact_local_file']=s.get('local_file')
        row['compact_sha256']=s.get('sha256')
        row['compact_bytes']=s.get('bytes')
        row['compact_kind']='full_original'
    rows.append(row)
manifest={
 'checked':'2026-10-21',
 'policy':'Full originals retained. Compact extracts preserve selected PDF pages without re-rendering; they are derivatives, not byte-identical complete originals. Original and derivative hashes and page mappings are provided. Screened candidates are not counted as accepted sources.',
 'source_count':len(rows),
 'counts_by_category':dict(Counter(r['category'] for r in rows)),
 'used_original_bytes':sum(r.get('original_bytes') or 0 for r in rows if r['claim_evidence']),
 'compact_used_bytes':sum(r.get('compact_bytes') or 0 for r in rows if r['claim_evidence']),
 'rows':rows,
}
(B/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
lines=['# Evidence packaging manifest','',manifest['policy'],'',
       f"Catalog: {len(rows)} source records; categories: {manifest['counts_by_category']}.",'',
       f"Cited full originals total {manifest['used_original_bytes']:,} bytes; the compact selection totals {manifest['compact_used_bytes']:,} bytes.",'',
       '| Source | Role | Package file | Original PDF pages in extract | Claims |',
       '|---|---|---|---|---|']
for r in rows:
    if not r['claim_evidence']:continue
    loc=r.get('compact_local_file') or ''
    pg=', '.join(str(x['original_pdf_page']) for x in r.get('page_mapping',[])) or 'Full original'
    lines.append(f"| {r['source_id']} | {r['category']} | `{loc}` | {pg} | "+', '.join(c['claim_id'] for c in r['claim_evidence'])+' |')
lines += ['','The JSON manifest carries SHA-256 hashes, byte sizes, source URLs, exact claim locators, and every screened or failed candidate. PDF-page numbers above count from the first page of the complete source, starting at 1.']
(B/'evidence-manifest.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='rows'},indent=2))
