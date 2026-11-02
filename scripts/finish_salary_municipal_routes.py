#!/usr/bin/env python3
"""Pin bounded public-route research without changing previously frozen evidence."""
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01/municipal'
CACHE = Path('/tmp/queue-completion-municipal')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, str(path)
    else:
        path.write_bytes(data)


def run():
    snapshots = []
    for key in ['mcbride-finance', 'mcbride-policies', 'mcbride-council', 'mcbride-bylaws', 'terrace-finance']:
        original = CACHE / (key + '.html')
        out = AREA / 'route-snapshots' / (key + '.html.gzip')
        freeze(out, gzip.compress(original.read_bytes(), mtime=0))
        snapshots.append({'key': key, 'bodySha256': sha(original), 'snapshot': str(out.relative_to(ROOT)), 'snapshotSha256': sha(out)})
    originals = []
    for filename in ['retrievals-initial.json', 'mcbride-route-retrievals.json', 'terrace-historical-retrievals.json']:
        original = CACHE / filename
        out = AREA / 'route-snapshots' / filename
        freeze(out, original.read_bytes())
        originals.append({'path': str(out.relative_to(ROOT)), 'sha256': sha(out)})
    audited = CACHE / 'mcbride-2025-audited.pdf'
    assert sha(audited) == 'fefdddcd4e49402f49097a6eb7affc7b6f9fff692bdc94c04a09436b178346eb'
    doc = fitz.open(audited)
    mupdf = [p.get_text() for p in doc]
    poppler = subprocess.run(['pdftotext', '-layout', str(audited), '-'], check=True, capture_output=True).stdout.decode().split('\f')
    if poppler[-1].strip() == '':
        poppler.pop()
    assert len(mupdf) == len(poppler) == 35
    targets = ['Runtz', 'Bennett', 'Caputo', 'Frear', 'Kolida', '8,700.20', '7,812.21', '5,978.57', '6,812.47', '13,274.60', '42,578.05']
    matches = {engine: {needle: [i+1 for i, text in enumerate(pages) if needle.casefold() in text.casefold()] for needle in targets} for engine, pages in [('MuPDF', mupdf), ('Poppler', poppler)]}
    evidence = {'url': 'https://mcbride.civicweb.net/document/45694/', 'sha256': sha(audited), 'bytes': audited.stat().st_size, 'physicalPages': 35, 'mupdfPages': mupdf, 'popplerLayoutPages': poppler, 'searchedExactTerms': targets, 'matches': matches, 'limitation': 'Complete native-text search of both independent engines only. This is supporting negative research, not a claim that every image or unindexed municipal record was examined, and not a council-period inference.'}
    evidence_path = AREA / 'mcbride-audited-native-research.json.gzip'
    freeze(evidence_path, gzip.compress(json.dumps(evidence, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))
    prior_path = ROOT / 'research/salaries/held-resolution-2026-11-01/municipal/decision-and-year-comparison.json'
    prior = json.loads(prior_path.read_text())
    receipt = {
        'date': '2026-11-01', 'status': 'held-period-conflict-unresolved', 'newAcceptedMcBrideRows': 0,
        'priorFrozenDecision': {'path': str(prior_path.relative_to(ROOT)), 'sha256': sha(prior_path)},
        'priorFindingRetained': prior['finding'], 'printedCouncilYear': '2024', 'enclosingReportYear': '2025',
        'heldRows': 5, 'proposedInferredYear': None, 'heldControls': prior['heldControls'],
        'currentPublicRouteFindings': [
            'The current official finance page still links SOFI45990 and audited financial statements45694; no corrected council-specific original linked there.',
            'The public policies folder109 lists17 policies; no council travel, remuneration or annual individual-expense disclosure appeared among the exposed entries.',
            'The public bylaws folder108 lists25 entries; no council-remuneration bylaw appeared among the exposed entries. A generic rate or entitlement would not independently date these exact five expense amounts.',
            'The current council page exposes no annual individual-expense disclosure.',
            'The35-page2025 audited statements have no literal held names or exact expense cells in either complete native-text extraction. Generic2025 financial statement headings and council approval do not date the separate council table.',
            'Six new bounded indexed web queries produced no specifically dated exact five-row council disclosure. Search limitations are preserved; no exhaustive archive-absence claim.'
        ],
        'snapshots': snapshots, 'retrievalReceipts': originals,
        'auditedNativeEvidence': {'path': str(evidence_path.relative_to(ROOT)), 'sha256': sha(evidence_path), 'originalSha256': sha(audited)},
        'publicSearchReceipt': 'research/salaries/queue-completion-2026-11-01/municipal/mcbride-current-web-search.json',
        'externalNeed': 'An existing corrected official council schedule or an issuer clarification that specifically dates these five names/pay/expense cells. Adoption of the2025 package alone remains insufficient.',
        'requestDraft': 'research/salaries/held-resolution-2026-11-01/municipal/existing-record-period-clarification-draft.md',
        'outboxOwner': 'recovery_education; freshly verified mcbride@mcbride.ca ordinary administrative routing',
        'messagesSent': False, 'formsSubmitted': False, 'feesIncurred': False,
        'terraceHistoricalTriage': 'Current finance index earliest linked SOFI2017; all2017–2025 salary scopes already accepted. Two guessed2015/2016 SOFI paths returned404. The linked2015/2016 annual reports were downloaded and native-keyword checked without finding named remuneration schedules; no assertion that those years never had a public schedule. No new Terrace rows proposed.'
    }
    out = AREA / 'mcbride-current-public-route-review.json'
    freeze(out, (json.dumps(receipt, ensure_ascii=False, indent=2)+'\n').encode())
    print(json.dumps({'receipt': str(out.relative_to(ROOT)), 'sha256': sha(out), 'newMcBrideRows': 0}))


if __name__ == '__main__':
    run()
