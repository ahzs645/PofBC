#!/usr/bin/env python3
"""McBride's five-row council-period conflict only. No accepted imports or year repair.

Build from cached official originals; replay all retained evidence offline with --verify.
Earlier frozen collections/reviews are read only. No network calls or registry writes.
"""
import argparse
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries'
OUT=BASE/'held-resolution-municipal'
REPORT=BASE/'held-resolution-2026-11-01/municipal'
CACHE=Path('/tmp/held-resolution-municipal')
PEER=BASE/'recovery-wave-2026-11-01/reviews/independent-manual-mcbride-original-transcription.json'
PEER_SHA='e681f4dba45605e2c17418e8d38028d5befdaf6bbec8d34970fda20a9b2e8cf5'
SCHEMA=['employerSlug','name','position','remuneration','expenses','pdfPage']
SPECS=[
 dict(key='sofi-current',url='https://mcbride.civicweb.net/document/45990',file='sofi-current.pdf',
      sha256='11733872fa678d7af449e391271581ca65602df4b35898661f903043a0b7e214',salaryPage=42,
      printedTableYear='2024',packageYear='2025',pagesReviewed=[1,42,48],
      status='Published signed SOFI, byte-identical to the already reviewed original. Its council table remains headed 2024; no corrected replacement found at this URL.'),
 dict(key='sofi-presentation',url='https://mcbride.civicweb.net/document/45891',file='sofi-staff-2026-06-30.pdf',
      sha256='dc1b33ecde076551c4c3c8951e44e2912a15fe41a197fba5f852fbb0a0042aba',salaryPage=44,
      printedTableYear='2024',packageYear='2025',pagesReviewed=[1,2,44],
      status='2025 SOFI presentation copy attached to AIR-26-019 for June 30, 2026. Staff approval June 25, 2026 on page 2; signed minutes approve the SOFI as presented. Actual council heading remains 2024.'),
 dict(key='annual-published',url='https://mcbride.civicweb.net/document/45695',file='annual-2025.pdf',
      sha256='c508161f75e3c8639ffabdd173553d6380a990f32505418ecbfa8b19077292f7',salaryPage=9,
      printedTableYear='2024',packageYear='2025',pagesReviewed=[1,7,8,9],
      status='Separately published 2025 Annual Report in official annual-report folder. No DRAFT watermark on reviewed salary page9; its own council heading explicitly says 2024.'),
 dict(key='annual-agenda-draft',url='https://mcbride.civicweb.net/document/45728',file='annual-staff-2026-06-23.pdf',
      sha256='6bd4f40f5f9b96792d9d7f9e8fc912d2fa9c53ec43f889c17840e42740e238a6',salaryPage=10,
      printedTableYear='2024',packageYear='2025',pagesReviewed=[1,10],
      status='Annual report attached to signed June 23, 2026 staff report. Actual salary page10 visibly watermarked DRAFT and headed 2024. This draft reproduction is corroboration only and is not an accepted source.'),
 dict(key='sofi-adoption-signed-minutes',url='https://mcbride.civicweb.net/document/46177',file='signed-minutes-2026-06-30.pdf',
      sha256='277d6f9f2aeccec9259f3e81ffc1452df1d9927421ea9cc83ba9d62486e08585',pagesReviewed=[1,3,4],
      status='Signed June 30, 2026 special minutes. Page 3 motion 090630.26 carried: approves Village2025 SOFI as presented; page 4 has Mayor and Corporate Officer signatures. No row-specific correction or year clarification.'),
 dict(key='annual-reception-minutes',url='https://mcbride.civicweb.net/document/46161',file='minutes-2026-06-23.pdf',
      sha256='513a29a82e6e8d340b24904578fa9a6db41431062f1358f0b6e572ff9a14dfe6',pagesReviewed=[4],
      status='June 23, 2026 regular minutes page 4, motion 080623.26, receive the 2025 Annual Report for information. This does not correct the council-table heading.')
]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw)if path.suffix=='.gzip'else raw)
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    path.write_bytes(gzip.compress(raw,mtime=0)if path.suffix=='.gzip'else raw)
    return sha(path)
def amount(token):
    token=token.replace('$','').replace(',','').strip()
    if token in {'','-','—'}:return None
    assert re.fullmatch(r'-?\d+\.\d{2}',token),token
    return float(Decimal(token))

def poppler_rows(layout):
    """Independent fixed-width reader of the five annual-report table rows."""
    result=[]
    for line in layout.splitlines():
        m=re.match(r'^\s*([^$]+?,[^$]+?)\s{2,}(\$[\d,.]+)\s+(\$[\d,.]+)\s+(\$[\d,.]+)\s*$',line)
        if m:result.append([m[1].strip(),*[amount(m[i])for i in (2,3,4)]])
    return result

def positioned_rows(words):
    """Independent PyMuPDF cell reader; no Poppler strings/name list consumed."""
    anchors=sorted([w for w in words if 45<w[0]<160 and 160<w[1]<310 and w[4].endswith(',')],key=lambda w:w[1])
    result=[]
    for anchor in anchors:
        strip=sorted([w for w in words if abs(w[1]-anchor[1])<1],key=lambda w:w[0])
        name=' '.join(w[4]for w in strip if w[0]<170)
        values=[amount(w[4])for w in strip if w[0]>=170 and w[4].startswith('$')]
        assert len(values)==3,(name,values)
        result.append([name,*values])
    return result

def held_from_frozen_peer():
    assert sha(PEER)==PEER_SHA
    page=next(p for p in read(PEER)['pages']if p.get('packageYear')==2025 and p['pdfPage']==42)
    assert page['printedPeriod']=='2024 FINANCIAL INFORMATION'
    return page,[["village-of-mcbride",*r[:4],42]for r in page['rows']]

def annual_equality(inputs,peer):
    first=poppler_rows(inputs['popplerLayout'])
    second=positioned_rows(inputs['words'])
    assert first==second and len(first)==5,(first,second)
    expected=[[r[0],r[2],r[3],r[4]]for r in peer['rows']]
    assert first==expected,(first,expected)
    # The schedule's own year is explicit and cannot be replaced by its footer year.
    assert 'VILLAGE COUNCIL 2024 - REMUNERATION & EXPENSES'in inputs['popplerLayout']
    assert '2025 Annual Report'in inputs['popplerLayout']
    return first

def build():
    import fitz
    peer,held=held_from_frozen_peer()
    snapshots=[];receipts=[]
    # Preserve exact original HTML bytes in deterministic compressed snapshots.
    for path in sorted(CACHE.glob('*.html')):
        target=REPORT/'snapshots'/(path.stem+'.html.gzip')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(gzip.compress(path.read_bytes(),mtime=0))
        snapshots.append(dict(cachePath=str(path),file=str(target.relative_to(ROOT)),originalSha256=sha(path),snapshotSha256=sha(target)))
    for spec in SPECS:
        path=CACHE/spec['file'];assert sha(path)==spec['sha256']
        doc=fitz.open(path)
        text={str(num):doc[num-1].get_text()for num in spec['pagesReviewed']}
        rendered=[]
        for num in spec['pagesReviewed']:
            image=CACHE/f'{path.stem}-p{num}.png'
            if image.exists():rendered.append(dict(physicalPage=num,cachePath=str(image),sha256=sha(image),render='PyMuPDF full page,1.8x RGB'))
        receipts.append(dict(**spec,cachePath=str(path),physicalPages=len(doc),reviewedText=text,renderedPages=rendered,
                             originalImageReview='Only the stated pages; no claim of every page reviewed. Each of the five council rows on the stated salary page reviewed in full.'))
    annual_spec=next(s for s in SPECS if s['key']=='annual-published')
    annual_path=CACHE/annual_spec['file'];doc=fitz.open(annual_path)
    inputs=dict(words=doc[8].get_text('words'),popplerLayout=subprocess.check_output(['pdftotext','-f','9','-l','9','-layout',str(annual_path),'-']).decode())
    annual=annual_equality(inputs,peer)
    data_file='held/mcbride-council-conflicting-period.json.gzip'
    data_hash=write(OUT/data_file,held)
    evidence_hash=write(OUT/'evidence/annual-native-row-comparison.json.gzip',dict(originalSha256=annual_spec['sha256'],physicalPage=9,readerInputs=inputs,
        independentReaders=['Poppler fixed-width line table parser','PyMuPDF positioned cell parser'],rows=annual,
        controls=[45600,42578.05,88178.05],printedCouncilYear='2024',printedReportYear='2025',allRowFieldsAgree=True,
        roleDisclosure='No position column on annual table. Mayor/Councillor roles remain the literal positions on held SOFI page 42, not inferred into annual rows.'))
    write(REPORT/'originals-and-status.json',receipts)
    write(REPORT/'snapshot-index.json',snapshots)
    write(REPORT/'retrieval-receipts.json',dict(retrievedOn='2026-11-01',receiptFiles={p.name:read(p)for p in sorted(CACHE.glob('*.json'))}))
    history=[]
    manifest=read(BASE/'recovery-municipal/sources.json')
    for s in manifest['sources']:
        if s['employerSlug']=='village-of-mcbride' and s['category']=='elected-officials':
            rows=read(BASE/'recovery-municipal'/s['file'])
            history.append(dict(sourceId=s['id'],year=s['year'],sourceUrl=s['sourceUrl'],dataSha256=s['dataSha256'],rows=rows,
                                knownRemuneration=s['totalRemuneration'],knownExpenses=s['totalExpenses']))
    old=next(s for s in history if s['year']=='2024');by_name={r[1]:r for r in old['rows']}
    comparison=[]
    for row in held:
        prior=by_name[row[1]]
        comparison.append(dict(name=row[1],role=row[2],prior2024Role=prior[2],pay=row[3],prior2024Pay=prior[3],
                               unresolvedPeriodExpense=row[4],prior2024Expense=prior[4],
                               expenseDifference=float(Decimal(str(row[4]))-Decimal(str(prior[4])))))
    decision=dict(status='held-period-conflict-unresolved',acceptedRows=0,heldRows=5,acceptedSources=0,
        proposedInferredYear=None,printedCouncilYear='2024',enclosingReportYear='2025',
        finding='The five council rows are reproduced consistently, but every examined council heading explicitly says2024. Approval of the 2025 SOFI package establishes package adoption and does not resolve the council-specific period.',
        rejectedInferences=['Do not treat upload, cover, annual-report footer or whole-package adoption as a silent council-year correction.',
                            'Do not replace accepted2024council rows with this conflicting alternate2024-labelled table.',
                            'Identical names/roles/pay in2024 and 2025 context and different expense cells do not uniquely identify reporting year.',
                            'No claim that a printed year is a typo; no issuer correction located.'],
        heldDataFile=data_file,heldDataSha256=data_hash,annualEvidenceFile='evidence/annual-native-row-comparison.json.gzip',annualEvidenceSha256=evidence_hash,
        priorIndependentImageTranscription=dict(file=str(PEER.relative_to(ROOT)),sha256=PEER_SHA,physicalPage=42),
        heldControls=dict(remuneration=45600,expenses=42578.05,combined=88178.05),
        acceptedCouncilHistory=history,heldVsAccepted2024=comparison,heldMinusAccepted2024KnownExpenses=-17573.82,
        sofiAdoption=dict(url='https://mcbride.civicweb.net/document/46177',sha256=SPECS[4]['sha256'],date='2026-06-30',physicalPage=3,motion='090630.26',signedPage=4,
                          text='Council approves the Village of McBride2025Statement of Financial Information as presented.',
                          limitation='No council row, amount or corrected council-year heading is named in the motion.'),
        boundedPublicResearch=dict(agendaHtmlPagesChecked=24,scope='All 24 regular/special 2026 HTML agenda links exposed by the public year folders, plus finance/SOFI/annual-report folders and directly relevant linked originals; not an exhaustive archive claim.',
                                  result='Only2025 annual-report and2025 SOFI routes among relevant hits; no corrected or separately dated council disclosure found.',
                                  civicwebGlobalSearch='Four direct keyword searches display a sign-in page; no credentials or authentication attempted. A sign-in response is not a zero-result search.',webSearch='Three bounded official-domain web queries returned no results; retained receipt.'),
        publicWarning='Five council observations remain unimported. The2025 SOFI presentation/published versions and2025 annual-report versions all show a council heading explicitly identifying2024. Their five expense amounts differ from the accepted2024SOFI. Whole-package2025adoption is established, but the council-table reporting period remains unresolved.',
        nextAction='Obtain an existing corrected official council schedule or a written issuer clarification identifying the reporting period of the five cells. Draft only; no request sent.')
    write(REPORT/'decision-and-year-comparison.json',decision)
    write(OUT/'sources.json',dict(version=1,rowSchema=SCHEMA,sources=[],notes=['No council rows accepted or relabelled; five held rows staged separately with unresolved reporting period.'],
         heldCandidates=[dict(id='held-resolution-municipal-mcbride-council-period',employerSlug='village-of-mcbride',status=decision['status'],file=data_file,dataSha256=data_hash,
                              rowCount=5,printedCouncilYear='2024',reportYear='2025',category='elected-officials')]))
    queue=[]
    for suffix,route,status,next_action,reason in [
     ('adoption-found','processing','package-adoption-resolved-council-period-still-held','Retain signedJune 30, 2026minutes motion 090630.26 as package-adoption evidence; keep the five council rows held.',
      'New adopted presentation 45891 and signed minutes 46177 resolve whole-package approval, not the explicit 2024 council heading. Links prior recovery-municipal-clarify-mcbride-2025-council-period and continuation-municipal-745c924ec3956e1c / continuation-municipal-dbbe229bcb97c4ac.'),
     ('request-period-copy','clarification-request','not-sent-period-clarification-draft','Use the attached focused draft to obtain an existing corrected council schedule or exact issuer period clarification; no message has been sent.',
      'Five cells agree acrosspublished SOFI 45990, adoptedpresentation 45891 andannual 45695; all council headings explicitly 2024. Annual agenda 45728 copy has a DRAFT watermark. Accepted 2024 expenses differ; no year repair or duplicate import authorized.')]:
        queue.append(dict(id='held-resolution-municipal-mcbride-'+suffix,employerSlug='village-of-mcbride',employerName='Village of McBride',sector='Municipalities',reportingPeriods=['2024','2025'],
                          sourceUrl='https://mcbride.civicweb.net/document/45990',sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',status=status,route=route,nextAction=next_action,reason=reason))
    write(REPORT/'work-queue.json',queue)
    write(REPORT/'handoff.json',dict(verifiedOn='2026-11-01',status=decision['status'],acceptedSources=0,acceptedRows=0,heldSources=1,heldRows=5,
         collection='research/salaries/held-resolution-municipal/sources.json',decisionFile='decision-and-year-comparison.json',
         originals=[{k:v for k,v in r.items()if k!='reviewedText'}for r in receipts],
         heldDataFile=str((OUT/data_file).relative_to(ROOT)),heldDataSha256=data_hash,annualEvidenceSha256=evidence_hash,
         councilYearRelabelled=False,existingAcceptedRowsChanged=False,newEmployeeRows=0,newCouncilRows=0,noGlobalOrOldFrozenEdits=True,noContacts=True,
         peerReviewTargets=['annual-publishedphysical 9 five native rows/year 2024 heading','sofi-presentationphysical 44 five image rows/year 2024 heading','annual-agenda-draftphysical10DRAFT watermark',
                            'signed-minutesJune30physical3motion 090630.26/physical4signatures'],
         reproduction=['python scripts/resolve_held_municipal.py --verify','python -m unittest discover -s scripts -p test_resolve_held_municipal.py'],
         requestDraft='existing-record-period-clarification-draft.md'))
    print('Built zero accepted sources/rows; five council rows remain held. Adoption evidence and exact version/year comparison retained.')

def verify():
    peer,held=held_from_frozen_peer()
    m=read(OUT/'sources.json');assert not m['sources']
    candidate=m['heldCandidates'][0]
    assert read(OUT/candidate['file'])==held and sha(OUT/candidate['file'])==candidate['dataSha256']
    e=read(OUT/'evidence/annual-native-row-comparison.json.gzip');annual_equality(e['readerInputs'],peer)
    decision=read(REPORT/'decision-and-year-comparison.json')
    assert decision['acceptedRows']==0 and decision['proposedInferredYear']is None
    assert decision['heldDataSha256']==candidate['dataSha256']
    assert sha(OUT/decision['annualEvidenceFile'])==decision['annualEvidenceSha256']
    for history in decision['acceptedCouncilHistory']:
        source=next(s for s in read(BASE/'recovery-municipal/sources.json')['sources']if s['id']==history['sourceId'])
        assert source['dataSha256']==history['dataSha256']
        assert read(BASE/'recovery-municipal'/source['file'])==history['rows']
    for snap in read(REPORT/'snapshot-index.json'):
        assert sha(ROOT/snap['file'])==snap['snapshotSha256']
        assert hashlib.sha256(gzip.decompress((ROOT/snap['file']).read_bytes())).hexdigest()==snap['originalSha256']
    print('Verified held rows, independent annual row readers, literal2024 headings, existing 2022–24 council payload hashes and HTML snapshot integrity; no accepted import.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args()
    if args.build:build()
    if args.verify:verify()
