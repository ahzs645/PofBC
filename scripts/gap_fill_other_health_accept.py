#!/usr/bin/env python3
"""Root's exact nine-history row adoption and independent original-word replay."""
import collections
import copy
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02'
AREA = BASE / 'health_other_history'
COLLECTION = ROOT / 'research/salaries/gap-fill-health-other-history'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def pinned(ref):
    path = ROOT / ref['path']
    assert sha(path.read_bytes()) == ref['sha256'], ref['path']
    return read(path)


def cents(value):
    if value is None:
        return None
    number = Decimal(str(value)) * 100
    assert number == number.to_integral_value()
    return int(number)


def main():
    mp = COLLECTION / 'sources-candidate.json'
    assert sha(mp.read_bytes()) == 'ab974e2780ef9fc3706b0d2d64b8fafd188644ca556a6763a4cf22ce4e8e8a22'
    closure_path = AREA / 'source-verification-closure.json'
    assert sha(closure_path.read_bytes()) == '2700bd3b47295f390d8f494562f3e98f4ee229ae23d8ba39e5135ab00c3dc239'
    closure = read(closure_path)
    for ref in closure['proofs']:
        pinned(ref)
    assert closure['all247ImageTargetsClosed'] and closure['allTwoReaderFlagsClosed']
    context_path = BASE / 'reviews/health-other-context-root/root-nine-source-context-acceptance.json'
    assert sha(context_path.read_bytes()) == '637ee861ba71716949d5e72e73bcda78e1ac6772f952cc4017270dba04d025f8'
    overlay_path = BASE / 'school_native/reviews/health-other-history/final-normalized247-source-review-overlay.json'
    assert sha(overlay_path.read_bytes()) == '9d097ada643ed3ab0f4d818163f1bb69e59b1aeb8a7979d158d50373bf5caae2'
    indices = {r['key']: r for r in read(AREA / 'native-primary-candidate-index.json')}
    evidence = {r['key']: r for r in read(AREA / 'native-reader-evidence-index-v2.json')}
    specs = {r['sourceSha256']: r for r in read(AREA / 'recovered-employee-originals-v2.json')}
    contexts = {r['key']: r for r in read(AREA / 'source-context-review-packet.json')['sources']}
    sources = read(mp)['sources']
    results, all_pages, original_words, added = [], 0, 0, 0
    for source in sources:
        key = source['id'].removeprefix('gap-health-other-history-')
        idx, ev, spec, ctx = indices[key], evidence[key], specs[source['sha256']], contexts[key]
        assert idx['sourceSha256'] == ev['sourceSha256'] == source['sha256']
        primary_path, secondary_path = ROOT / idx['file'], ROOT / idx['secondaryFile']
        assert sha(primary_path.read_bytes()) == idx['sha256']
        assert sha(secondary_path.read_bytes()) == idx['secondarySha256']
        primary, secondary = read(primary_path), read(secondary_path)
        initial_rows = [r['row'] for r in primary['rows']]
        assert initial_rows == [r['row'] for r in secondary['rows']]
        expected = copy.deepcopy(initial_rows)
        # Explicit one-row addition, positioned only by the actual literal source line.
        if key == 'island-health-2009-10':
            assert len(primary['flags']) == len(secondary['flags']) == 1
            flag = primary['flags'][0]
            assert flag['kind'] == 'pay-line-without-comma-name' and flag['physicalPage'] == 47
            assert 'WILSON. TOM' in flag['line']
            layout = pinned(ev['popplerLayout'])['pages'][46].splitlines()
            assert layout.count(flag['line']) == 1
            position = layout.index(flag['line'])
            later = [i for i, r in enumerate(primary['rows'])
                     if r['row'][5] == 47 and layout.index(r['rawLine']) > position]
            at = min(later)
            assert expected[at - 1][5] == expected[at][5] == 47
            expected.insert(at, ['island-health', 'WILSON. TOM', None, 77451, 0, 47])
            added += 1
        else:
            assert primary['flags'] == secondary['flags'] == []
        assert sha((COLLECTION / source['file']).read_bytes()) == source['dataSha256']
        actual = read(COLLECTION / source['file'])
        assert actual == expected and len(actual) == source['rowCount']
        assert all(r[0] == source['employerSlug'] and r[2] is None for r in actual)
        provpath = COLLECTION / source['provenanceFile']
        assert sha(provpath.read_bytes()) == source['provenanceSha256']
        prov = read(provpath)
        assert prov['sourceSha256'] == source['sha256'] and len(prov['rows']) == len(actual)
        page_rows = collections.Counter()
        for i, (row, evidence_row) in enumerate(zip(actual, prov['rows']), 1):
            page_rows[row[5]] += 1
            assert evidence_row['rowIndex'] == i and evidence_row['physicalPage'] == row[5]
            assert evidence_row['sourceRowOnPage'] == page_rows[row[5]]
            paytoken = evidence_row['rawRemunerationToken']
            assert cents(Decimal(paytoken.replace(',', '').replace('$', ''))) == cents(row[3])
            token = evidence_row['rawExpenseToken']
            if token not in [None, '', '-', '—']:
                number = token.replace(',', '').replace('$', '').strip()
                if number.startswith('(') and number.endswith(')'):
                    number = '-' + number[1:-1]
                assert cents(Decimal(number)) == cents(row[4])
            else:
                assert row[4] is None
        raw_words = pinned(ev['mupdfWords'])
        pinned(ev['textProbe'])
        source_path = Path(spec['retrieval']['cachePath'])
        assert sha(source_path.read_bytes()) == source['sha256']
        doc = fitz.open(source_path)
        assert len(doc) == len(raw_words['pages'])
        for page, words in zip(doc, raw_words['pages']):
            assert [list(w) for w in page.get_text('words')] == words['words']
            assert not words['unpaintedWhiteOrTransparentText']
            original_words += len(words['words'])
            all_pages += 1
        pay = sum((Decimal(str(r[3])) for r in actual), Decimal())
        expense = sum((Decimal(str(r[4])) for r in actual if r[4] is not None), Decimal())
        validation = source['validation']
        assert Decimal(validation['literalRemunerationSum']) == pay
        assert Decimal(validation['literalKnownExpenseSum']) == expense
        controls = validation['printedNamedControls']
        residuals = ([pay - Decimal(str(controls['remuneration'])),
                      expense - Decimal(str(controls['expenses']))] if controls else None)
        declared = validation['literalNamedControlResiduals']
        assert (None if declared is None else list(map(Decimal, declared))) == residuals
        if residuals and any(residuals):
            assert 'differ from printed named controls' in source['publicWarning']
        # Discovery labels are checked for consistency only. The exact pinned
        # root context receipt separately accepts the internally printed period.
        assert source['year'] == ctx['expectedDiscoveryYearNotAcceptanceEvidence'] == spec['item']['candidateYear']
        assert source['retainCompiledPartition'] is True
        assert source['completeEmployeeSchedule'] is validation['completeEmployeeSchedule'] is True
        assert validation['compiledPartitionRetained'] is True and validation['compiledPartitionRetentionReason']
        results.append({'sourceId': source['id'], 'sourceSha256': source['sha256'],
                        'dataSha256': source['dataSha256'], 'provenanceSha256': source['provenanceSha256'],
                        'rowCount': len(actual), 'exactNormalizedReconstruction': True,
                        'originalNativePageWordsReplayed': len(doc),
                        'literalRemunerationSum': str(pay), 'literalKnownExpenseSum': str(expense),
                        'literalNamedControlResiduals': None if residuals is None else list(map(str, residuals))})
    assert len(results) == 9 and sum(r['rowCount'] for r in results) == 11471
    assert added == 1 and all_pages == 230
    northern = next(s for s in sources if s['id'].endswith('northern-health-2014-15'))
    assert northern['rowCount'] == 1254 and northern['validation']['printedEmployeeSummaryCount'] == 1255
    assert 'no employee is invented' in northern['publicWarning'].lower()
    fraser_path = AREA / 'fraser-contract-context/supporting-source-disposition.json'
    assert sha(fraser_path.read_bytes()) == '83594ad522af331807635b87ea4ada5629d16a7d86b1f048d4c1ebdd49e7c6e9'
    fraser = read(fraser_path)
    for field in ['primaryLiteral', 'secondaryLiteral', 'comparison', 'rasterReplay']:
        pinned(fraser[field])
    assert fraser['newSalaryObservationsAdded'] == fraser['positionsEnriched'] == 0
    assert fraser['namedDetailObservations'] == 492
    assert fraser['exactUniqueLiteralRecordMatches'] == 430 and fraser['unresolvedLiteralNameForms'] == 62
    receipt = {'accepted': True, 'approvedBy': 'root', 'noOutreach': True,
               'candidateManifest': pin(mp), 'sourceVerificationClosure': pin(closure_path),
               'sourceContextAcceptance': pin(context_path), 'independent247NormalizedOverlay': pin(overlay_path),
               'FraserSupportingDisposition': pin(fraser_path), 'sources': results,
               'originalPhysicalPagesIndependentlyWordReplayed': all_pages,
               'originalWordsIndependentlyReplayed': original_words,
               'scope': 'Nine complete located native employee schedules;11470 original two-reader rows preserved plus one actual image-backed literal WILSON. TOM77,451/zero expense observation. Root personally reviewed the nine source contexts earlier and independently reconstructed every final normalized row/provenance payment token and replayed all230original physical-page native word lists. A separate reviewer personally read all247original-image exception targets. This is not personal transcription of11471rows.',
               'qualifications': 'All source monetary residuals and Northern2014/15summary1255versus1254actual observations remain explicit, with no balancing or invented employee. Ordinary blank/dash expense stays unknown and explicit zero stays zero. No inferred identities, title joins, calendar-equivalence corrections or compiled deletions. Fraser492detail observations and seven compensation components remain supporting evidence only;62unmatched name forms are not new-person findings.',
               'reviewCode': pin(Path(__file__))}
    output = BASE / 'reviews/root-nine-other-health-source-acceptance.json'
    assert not output.exists()
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(output), 'sources': 9, 'rows': 11471, 'originalPages': all_pages}))


if __name__ == '__main__':
    main()
