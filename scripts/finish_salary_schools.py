#!/usr/bin/env python3
"""Build additive reviewed school scopes; retain every compiled partition.

Until a hash-pinned peer receipt is supplied the manifest is candidate-only.
Control differences remain literal and are never used to change an individual.
"""
import argparse
import collections
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from finish_salary_schools_native import AREA, COLLECTION, ROOT, fields


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    return gzip.compress(raw, mtime=0), raw


def write_or_check(path, raw, check):
    if check:
        assert path.read_bytes() == raw, 'Frozen candidate replay differs: '+str(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def build(check=False, peers=None):
    if not check and (AREA/'candidate-freeze.json').exists():
        raise ValueError('School candidate frozen; use --check')
    peers = peers or {}
    controls = json.loads((AREA/'native-controls-and-context.json').read_text())
    specs = json.loads((AREA/'native-source-specs.json').read_text())
    if (AREA/'scan-source-specs.json').exists():
        specs += json.loads((AREA/'scan-source-specs.json').read_text())
    revisions = json.loads((AREA/'source-revisions.json').read_text()) if (AREA/'source-revisions.json').exists() else {}
    sources = []
    for config in specs:
        config = {**config, **revisions.get(config['key'], {})}
        key = config['key']
        if key not in controls:
            continue
        peer = peers.get(key)
        if peer:
            assert sha((ROOT/peer['file']).read_bytes()) == peer['sha256']
        proof_path = AREA/config.get('proofFile', key+'-native-candidate.json.gzip')
        proof_raw = proof_path.read_bytes()
        proof = json.loads(gzip.decompress(proof_raw))
        first = proof[config.get('firstReaderField', 'popplerRows')]
        second = proof[config.get('secondReaderField', 'mupdfRows')]
        assert not proof.get('nativeReaderDifferences', proof.get('readerDifferencesAfterImageAmendments')), 'Unresolved independent-reader differences'
        assert [fields(r) for r in first] == [fields(r) for r in second]
        control = controls[key]
        for category in ('school-trustees', 'employee-remuneration'):
            rows = [r for r in first if r['category'] == category]
            slug = 'trustees' if category == 'school-trustees' else 'employees'
            basename = key+'-'+slug
            precision = config.get('amountPrecisionByCategory', {}).get(category, config.get('amountPrecision', 'whole-dollars'))
            number = (lambda value: int(Decimal(value))) if precision == 'whole-dollars' else (lambda value: float(Decimal(value)))
            normalized = [[config['employerSlug'], r['name'], r['position'], number(r['remuneration']),
                           None if r['expenses'] is None else number(r['expenses']), r['pdfPage']] for r in rows]
            # These sources explicitly print whole dollars. Reject precision loss.
            assert precision == 'cents' or all(Decimal(r[f]) == int(Decimal(r[f])) for r in rows for f in ('remuneration', 'expenses') if r[f] is not None)
            blob, raw = packed(normalized)
            data_path = COLLECTION/config.get('dataFileByCategory', {}).get(category, basename+'.json.gzip')
            write_or_check(data_path, blob, check)
            computed = proof['summaries'][category]['computedTotals']
            printed = control[category]['printedControlTotals']
            residuals = [None if p is None else str(Decimal(v)-Decimal(p)) for v, p in zip(computed, printed)]
            evidence = {'sourceSha256': config['sha256'], 'dataSha256': sha(blob), 'normalizedSha256': sha(raw),
                        'originalNativeProof': {'file': str(proof_path.relative_to(ROOT)), 'sha256': sha(proof_raw)},
                        'readerOneFields': [fields(r) for r in first if r['category'] == category],
                        'readerTwoFields': [fields(r) for r in second if r['category'] == category],
                        'originalControlAndContext': control, 'independentPeerReview': peer,
                        'acceptedRows': len(rows) if peer else 0}
            eblob, _ = packed(evidence)
            evidence_path = COLLECTION/(data_path.name.removesuffix('.json.gzip')+'-evidence.json.gzip')
            write_or_check(evidence_path, eblob, check)
            source = {'id': 'queue-completion-schools-'+basename, 'employerSlug': config['employerSlug'],
                      'employerName': config['employerName'], 'sector': 'School districts',
                      'year': '2024/25', 'slug': '2024-25', 'periodType': 'fiscal',
                      'periodStart': '2024-07-01', 'periodEnd': '2025-06-30',
                      'title': config['employerName']+', year ended June 30, 2025: '+slug,
                      'sourceUrl': config['sourceUrl'], 'sourceIndexUrl': config['sourceIndexUrl'],
                      'sha256': config['sha256'], 'file': data_path.name, 'dataSha256': sha(blob), 'normalizedSha256': sha(raw),
                      'provenanceFile': evidence_path.name, 'provenanceSha256': sha(eblob),
                      'category': category, 'scope': category, 'currency': 'CAD', 'amountUnit': 'dollars', 'amountPrecision': precision,
                      'scopeDescription': 'Complete published '+('school trustee/official table' if slug == 'trustees' else 'named employee remuneration table at the source disclosure threshold'),
                      'nameDisclosure': 'published-name-as-disclosed', 'positionDisclosure': 'published-visible-text-only',
                      'pages': sorted({r['pdfPage'] for r in rows}), 'rowCount': len(rows),
                      'totalRemuneration': number(computed[0]), 'totalExpenses': number(computed[1]),
                      'status': 'verified' if peer else 'candidate-independent-peer-review-pending', 'sourceKind': 'official',
                      'completeEmployeeSchedule': category == 'employee-remuneration',
                      'retainCompiledPartition': True, 'verifiedOn': '2026-11-01' if peer else None,
                      'publicWarning': ((control[category]['publicWarning']+' ') if control[category]['publicWarning'] else '')+'Compiled entries, where present, are retained while their edition labels and employee/trustee scopes await comparison with this complete original. No equivalence between a compiled edition label and this fiscal year is assumed.',
                      'notes': control['notes']+['Only named payments are imported. Below-threshold aggregates, employer CPP/EI, suppliers and financial-statement totals remain excluded.',
                                                 'Published spelling, initials, name order, punctuation, footnote markers and visible titles remain literal. No identity, full name or annual rate is inferred. A blank or dash expense remains null and an explicit zero remains zero.'],
                      'validation': {'originalFingerprintVerified': True, 'independentReaders': config.get('readerNames', ['Poppler pdftotext physical layout lines', 'MuPDF independently grouped word geometry']),
                                     'rowsIndependentlyChecked': len(rows), 'allSixFieldsOrderMultiplicityAgree': True,
                                     'rowsByPhysicalPage': dict(collections.Counter(r['pdfPage'] for r in rows)),
                                     'printedControlTotals': printed, 'computedComponentTotals': computed, 'controlResiduals': residuals,
                                     'summaryReconciles': False if any(r is not None and Decimal(r) != 0 for r in residuals) else None if any(p is None for p in printed) else True,
                                     'nullExpenseRows': proof['summaries'][category]['nullExpenseRows'],
                                     'knownExpenseValueCount': len(rows)-proof['summaries'][category]['nullExpenseRows'],
                                     'completeEmployeeSchedule': category == 'employee-remuneration',
                                     'compiledPartitionRetained': True,
                                     'compiledPartitionRetentionReason': 'Full official-versus-compiled multiset comparison with exact source/data/baseline fingerprints remains for root review; compiled year labels and employee/trustee scope are not assumed equivalent.',
                                     'zeroExpenseRows': proof['summaries'][category]['zeroExpenseRows'],
                                     'reportingPeriodBasis': control['reportingPeriodBasis'],
                                     'salarySchedulePrintedPeriodEnd': '2025-06-30',
                                     'approvalEvidence': control['approvalEvidence'],
                                     'nativeProofFile': str(proof_path.relative_to(ROOT)), 'nativeProofSha256': sha(proof_raw),
                                     'independentPeerReviewPending': peer is None, 'independentPeerReview': peer}}
            if key in ('sd61-2025', 'sd50-2025'):
                image_receipt = AREA/'bounded-source-image-receipts.json'
                source['validation']['boundedSourceImageReceipt'] = {'file': str(image_receipt.relative_to(ROOT)), 'sha256': sha(image_receipt.read_bytes())}
            sources.append(source)
    manifest = {'version': 1, 'reviewed': all(s['status'] == 'verified' for s in sources),
                'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
    write_or_check(COLLECTION/'sources.json', (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode(), check)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--peer-map', type=Path, default=AREA/'peer-receipts.json')
    args = parser.parse_args()
    peers = json.loads(args.peer_map.read_text()) if args.peer_map.exists() else {}
    manifest = build(args.check, peers)
    print(json.dumps({'scopes': len(manifest['sources']), 'rows': sum(s['rowCount'] for s in manifest['sources']), 'reviewed': manifest['reviewed']}))


if __name__ == '__main__':
    main()
