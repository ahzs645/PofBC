#!/usr/bin/env python3
"""Close public school clarification routes without pretending issuer issues resolved."""
import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    receipts = json.loads((AREA/'public-route-receipts.json').read_text())
    by_key = {r['key']: r for r in receipts}
    for receipt in receipts:
        if receipt.get('cachePath'):
            assert sha(Path(receipt['cachePath'])) == receipt['sha256']
    assert by_key['sd10-current-sofi']['sha256'] == '193808051072d321077d9f2dd0fc57af454ffccf8010a2690ad04b6fff1a767a'
    assert by_key['sd8-current-sofi']['sha256'] == 'b9a2483c8a81e0414c1e55d620cfe234fcba6af1f4e2d8388ed59e492cc2d47f'
    alternative = json.loads((AREA/'sd10-alternative-render-comparison.json').read_text())
    assert len(alternative['pages']) == 12 and all(p['matchingCompletePhysicalPages'] for p in alternative['pages'])
    ocr_path = AREA/'bounded-original-ocr.json.gzip'
    assert sha(ocr_path) == 'b7484e78b4619df486ad22629c4172096ca07991acfe6b2b7a6fcdef5743440d'
    minutes = [p for p in json.loads(gzip.decompress(ocr_path.read_bytes()))['pages'] if p['key'].startswith('sd10-board-')]
    assert len(minutes) == 12
    assert not any(re.search(r'\bSOFI\b|statement of financial information', p['tesseractText'], re.I) for p in minutes)
    return {
        'reviewedOn': '2026-11-01', 'acceptedPriorObservationsUnchanged': 398, 'newObservationsFromTheseTwoIssues': 0,
        'publicRouteReceipts': {'file': str((AREA/'public-route-receipts.json').relative_to(ROOT)), 'sha256': sha(AREA/'public-route-receipts.json')},
        'sd10': {
            'predecessorTaskId': 'held-resolution-schools-sd10-2025-approval-clarification',
            'status': 'public-routes-checked-issuer-existing-record-clarification-still-needed',
            'originalUnchanged': True, 'alternativeOriginalSha256': alternative['alternativeOriginalSha256'],
            'alternativeFinding': 'Official public media search locates a second12page SOFI; all12 actual PDF-rendered pages are pixel-identical to selected pages in the complete50page accepted source, including declaration3, management5 and remuneration pages47–48 equivalents9–10. This existing abridged copy preserves the same conflicts.',
            'laterBoardRecords': [{'key': p['key'], 'physicalPage': p['physicalPage'], 'sourceSha256': p['sourceSha256'], 'method': 'complete Tesseract discovery text read with corresponding native agenda context'} for p in minutes],
            'boardFinding': 'Later adopted minutes February24, April7, May12 and June16,2026 and published later2026 agendas contain no located SOFI-specific adoption/approval item or explanation of the declaration/management dates. Earlier December2025 and January2026 public checks remain preserved in prior receipts. These finite checks do not prove a record exists nowhere.',
            'publicContentSearchFinding': 'The official WordPress SOFI content search returns the already checked finance and board-record index pages; public media search returns22 existing attachments and reveals the abridged current copy. No explanatory correction found in these published records.',
            'unresolvedFacts': ['Declaration physical3 body certifies June30,2024 despite2024–2025 year field, explicitly2025 remuneration tables and December18,2025 date fields.', 'Management physical5 prints December18,2024 under a June30,2025 header.', 'No cause, template-typo explanation or2025 SOFI adoption record is established.'],
            'existingRecordsRequested': ['An already corrected declaration/management page or existing issuer explanation addressing these exact conflicting printed dates.', 'Any existing resolution/minutes specifically approving/adopting the2024/25 SOFI, if such a record exists.'],
            'contactReceipt': {'file': str((AREA/'sd10-contact-public-snapshot-receipt.json').relative_to(ROOT)), 'sha256': sha(AREA/'sd10-contact-public-snapshot-receipt.json')},
            'outreachSent': False,
        },
        'sd8': {
            'predecessorTaskId': 'held-resolution-schools-sd08-2026-issuer-clarification',
            'status': 'public-routes-checked-issuer-existing-record-clarification-still-needed',
            'originalUnchanged': True,
            'laterBoardFinding': 'The latest linked October13,2026 public agenda repeats the September8 presentation in attached minutes physical15. Its substantive agenda and follow-up items contain no located SOFI-specific adoption motion or explanation of the conflicting heading/aggregate amounts. The separately posted September8 adopted minutes remain byte-identical to prior evidence. Approval of audited financial statements and adoption of meeting minutes are not treated as SOFI adoption.',
            'searchFinding': 'Official site search and its linked GoogleCSE fallback return a JavaScript/search-shell interface without server-delivered result records. No absent-result inference is made. Finance, board indexes, final posted SOFI and actual complete latest agenda were separately checked.',
            'unresolvedFacts': ['Final finance SOFI physical52 prints June30,2025 while its other employee pages print2026; every340 employee row exactly matches the explicitly2026 agenda schedule. This establishes the qualified observed payment period, not the cause of the conflicting heading.', 'Finance reconciliation physical64 prints remuneration56431182 and expenses594827; schedule59 prints56431196 and594437. Reconciliation minus schedule remains −14 remuneration and +390 expenses.', 'No explicit SOFI adoption record or issuer explanation has been located. Signature areas are redacted; no signature authentication is claimed.'],
            'existingRecordsRequested': ['An already corrected physical52 or existing published explanation of the conflicting year heading.', 'An existing reconciliation or correction explaining the exact−$14 remuneration/+$390 expense aggregate differences.', 'Any existing SOFI-specific approval/adoption resolution or minutes, if such a record exists.'],
            'ordinaryContactUrl': 'https://www.sd8.bc.ca/contact', 'ordinaryPublishedEmail': 'info@sd8.bc.ca',
            'outreachSent': False,
        },
        'interpretationLimits': ['Existing qualified observations remain accepted with their warnings; these public research steps do not relabel, duplicate or alter those records.', 'An issuer clarification remains an external dependency. A concrete unsent request can finish the preparatory work but cannot supply a missing issuer explanation.', 'No institution contacted, form submitted, FOI filed or fee incurred.'],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build()
    path = AREA/'clarification-public-route-closure.json'
    raw = (json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode()
    if args.check:
        assert path.read_bytes() == raw
    else:
        if path.exists():
            raise ValueError('Clarification receipt frozen; use --check')
        path.write_bytes(raw)
    print(json.dumps({'file': str(path.relative_to(ROOT)), 'sha256': sha(path), 'externalIssuerItemsUnresolved': 2, 'newRows': 0}))


if __name__ == '__main__':
    main()
