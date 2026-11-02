"""Read-only exact PHSA2011/12+2012/13 normalized adoption replay."""
from collections import Counter
from decimal import Decimal
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'package.json').is_file())
HERE = Path(__file__).resolve().parent
PEER = HERE.parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
COLLECTION = ROOT / 'research/salaries/gap-fill-phsa-history'
DESTINATION = HERE / 'two-final-normalized-sources-replay-v2.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def pinned(ref):
    path = (ROOT / ref['path']).resolve()
    assert path.is_relative_to(ROOT) and sha(path) == ref['sha256'], ref
    return load(path)


def diff(a, b, prefix=''):
    if type(a) is not type(b):
        return [{'pointer': prefix, 'before': a, 'after': b}]
    if isinstance(a, dict):
        result = []
        for key in sorted(set(a) | set(b)):
            if key not in a:
                result.append({'pointer': prefix + '/' + key, 'beforeAbsent': True, 'after': b[key]})
            elif key not in b:
                result.append({'pointer': prefix + '/' + key, 'before': a[key], 'afterAbsent': True})
            else:
                result.extend(diff(a[key], b[key], prefix + '/' + key))
        return result
    return [] if a == b else [{'pointer': prefix, 'before': a, 'after': b}]


def literal_name(name):
    return re.sub(r'\s*,\s*', ',', ' '.join(name.split()))


def replay():
    candidate_path = COLLECTION / 'sources-candidate.json'
    final_path = COLLECTION / 'sources.json'
    adoption_path = AREA / 'reviews/root-nine-phsa-history-source-acceptance.json'
    handoff_path = AREA / 'phsa_history/handoff.json'
    addendum_path = PEER / 'integration/adaptive-surname-guard/final-v4-selection-addendum.json'
    assert sha(candidate_path) == '069f8c7b8add887dba2d2bccbe33b8327b0b332308b7a7f6dd994decfcc26b7e'
    assert sha(final_path) == '875759c22c8e745be566ff619ddd70e3462d1f240797255b58f14ef42a68a529'
    assert sha(adoption_path) == '0ac2f26bd907c1d46fd93fed52a35ab4ccd4d7e895bb98a47e2c6b5fadf7481a'
    assert sha(handoff_path) == '367764ddda835f7e16b5bd874cc1f21000394ccd26dfdaea9aaffd8bb169e4b9'
    assert sha(addendum_path) == '619456cdac8bbaa7ffca94ab29c92846b0a1df807255ade4952f040bafee29fd'
    candidate, final, adoption, handoff, addendum = map(load, [candidate_path, final_path, adoption_path, handoff_path, addendum_path])
    assert adoption['accepted'] is True and handoff['accepted'] is True and not handoff['pending']
    assert handoff['manifest'] == pin(final_path) and adoption['candidateManifest'] == pin(candidate_path)
    assert final['rootSourceAcceptance'] == pin(adoption_path) and final['noOutreach'] is True
    assert handoff['numericRows'] == 22796 and handoff['compiledRowsRemoved'] == 0
    cases = []
    for case in addendum['sources']:
        key = case['sourceKey']
        source_id = 'gap-phsa-history-' + key
        source = next(s for s in final['sources'] if s['id'] == source_id)
        first = next(s for s in candidate['sources'] if s['id'] == source_id)
        root_source = next(s for s in adoption['sources'] if s['sourceId'] == source_id)
        prior_peer = pinned(case['oldIndependentReceipt'])
        selected = pinned(case['acceptedNewSelected'])
        pinned(case['oldSelected'])
        assert not selected['pending'] and selected['sourceSha256'] == source['sha256'] == prior_peer['sourceSha256']
        assert source['validation']['sourceSelection'] == case['acceptedNewSelected'] == root_source['selectedInput']
        expected = []
        for index, record in enumerate(selected['rows'], 1):
            assert record['sequence'] == index and not record['pending']
            row = record['selected']
            assert row.get('position') is None and type(row['remuneration']) is int
            assert row['expenses'] is None or type(row['expenses']) is int
            expected.append(['provincial-health-services-authority', literal_name(row['name']), None,
                             row['remuneration'], row['expenses'], row['pdfPage']])
        data_path = COLLECTION / source['file']
        proof_path = COLLECTION / source['provenanceFile']
        assert sha(data_path) == source['dataSha256'] == first['dataSha256'] == root_source['dataSha256']
        assert sha(proof_path) == source['provenanceSha256'] == first['provenanceSha256'] == root_source['provenanceSha256']
        values, proof = load(data_path), load(proof_path)
        assert all(len(r) == 6 and isinstance(r[1], str) and r[2] is None and type(r[3]) is int
                   and (r[4] is None or type(r[4]) is int) and type(r[5]) is int for r in values)
        assert values == expected and len(values) == source['rowCount'] == root_source['rowCount']
        assert proof['sourceSha256'] == source['sha256'] and proof['sourceSelection'] == case['acceptedNewSelected']
        assert proof['rows'] == [dict(rowIndex=i, pdfPage=r[5], name=r[1], sourceFootnoteMarker=None) for i, r in enumerate(values, 1)]
        assert all(type(r['rowIndex']) is int and type(r['pdfPage']) is int for r in proof['rows'])
        for proof_key, selected_key in [('primaryImageReceipts', 'primaryPersonalReceipts'),
                                        ('primaryPersonallyReadRows', 'primaryPersonallyReadRows'),
                                        ('finiteSourceGuard', 'finiteSourceGuard'), ('primaryCorrections', 'primaryCorrections')]:
            assert proof[proof_key] == selected[selected_key]
        for reference in proof['primaryImageReceipts'] + proof['independentPeerReviews']:
            pinned(reference)
        assert proof['independentPeerReviews'] == source['validation']['independentPeerReviews'] == root_source['peerReviews']
        pinned(proof['sourceContextAcceptance'])
        assert proof['literalRowsRemainInPrintedOrderIncludingRepeatedObservations'] is True and proof['noOutreach'] is True
        assert 'not an all-row manual transcription' in proof['readingMethod']
        assert 'do not prove an underlying Unicode character' in proof['sourceTypographyQualification']
        assert source['scope'] == source['category'] == 'employee-remuneration'
        assert source['sourceKind'] == 'official' and source['periodType'] == 'fiscal'
        start = int(key[5:9])
        assert source['year'] == f'{start}/{str(start + 1)[-2:]}'
        assert source['periodStart'] == f'{start}-04-01' and source['periodEnd'] == f'{start + 1}-03-31'
        assert source['threshold'] == 75000 and source['thresholdComparison'] == 'as-published'
        assert source['completeEmployeeSchedule'] is source['validation']['completeEmployeeSchedule'] is True
        assert source['retainCompiledPartition'] is source['validation']['compiledPartitionRetained'] is True
        assert source['validation']['compiledPartitionRetentionReason'].strip()
        assert source['validation']['initialAndSupersededReaderEvidenceRetained'] is True
        assert all(term in source['publicWarning'] for term in ['not annual base salary rates', 'unknown', 'compiled', 'no complete-copy'])
        assert source['validation']['printedEmployeeNarrativeCount'] == source['rowCount']
        assert source['validation']['printedNarrativeCountIsReportingPeriodControl'] is True
        sums = [sum(Decimal(str(r[i])) for r in values if r[i] is not None) for i in (3, 4)]
        assert [int(n) for n in sums] == prior_peer['literalComputedNamedComponents']
        assert [str(n) for n in sums] == [source['validation']['literalRemunerationSum'], source['validation']['literalKnownExpenseSum']]
        assert source['validation']['literalNamedControlResiduals'] == ['0', '0']
        by_page = dict(sorted(Counter(r[5] for r in values).items()))
        assert {str(k): v for k, v in by_page.items()} == root_source['namedRowsByPhysicalPage']
        changes = diff(first, source)
        assert {c['pointer'] for c in changes} == {'/status', '/validation/candidateOnly', '/validation/independentPeerVerified', '/validation/pendingGates', '/validation/rootSourceAcceptance', '/verifiedOn'}
        assert source['status'] == 'verified' and source['validation']['candidateOnly'] is False
        assert source['validation']['independentPeerVerified'] is True and source['validation']['pendingGates'] == []
        assert source['validation']['rootSourceAcceptance'] == pin(adoption_path) and source['verifiedOn'] == '2026-11-02'
        cases.append(dict(sourceId=source_id, sourceSha256=source['sha256'], selectedInput=case['acceptedNewSelected'],
                          initialBoundedPeerReceipt=case['oldIndependentReceipt'], surnameTypographyAddendum=pin(addendum_path),
                          rows=len(values), data=pin(data_path), provenance=pin(proof_path),
                          everyNormalizedRowExactlyMatchesFinalPeerSelection=True, sourceOrderAndMultiplicityPreserved=True,
                          everyProvenanceNamePageAndIndexMatches=True, candidateDataBytesUnchangedAfterPromotion=True,
                          candidateProvenanceBytesUnchangedAfterPromotion=True, metadataOnlyPromotionChanges=changes,
                          actualFiscalPeriod=source['year'], actualPrintedPeriodEnd=source['periodEnd'],
                          conventionalFiscalStartExplicitlyQualified=source['periodStart'],
                          actualThresholdWording='remuneration exceeding75000; final threshold metadata conservatively says as-published',
                          nullExpenseRows=sum(r[4] is None for r in values), literalKnownComponents=[str(n) for n in sums],
                          residuals=['0', '0'], namedRowsByPhysicalPage={str(k): v for k, v in by_page.items()}))
    assert sum(c['rows'] for c in cases) == 6774
    return dict(status='passed-final-normalized-two-source-replay', candidateManifest=pin(candidate_path),
                finalAcceptedManifest=pin(final_path), rootNormalizedAdoption=pin(adoption_path),
                finalProducerHandoff=pin(handoff_path), producerFreeze=pin(ROOT / handoff['freeze']['path']),
                finalV4PeerAddendum=pin(addendum_path), sources=cases, rows=6774, noOutreach=True,
                reviewCode=pin(Path(__file__).resolve()),
                firstExecutionReceipt=pin(HERE / 'two-final-normalized-sources-replay.json'),
                firstExecutionCode=pin(HERE / 'first-execution-code.py'),
                firstCheckQualification=pin(HERE / 'first-check-json-key-qualification.json'),
                scope='Exact normalized data/provenance mapping for two independently reviewed PHSA scans only; no new transcription, identity resolution, balancing, source reclassification or compiled deletion.',
                limitations='Initial and superseded peer/primary readings and source-specific qualifications remain in their immutable receipts. Prior personal coverage was878 unique rows plus3 candidate-aware surname observations; this mapping replay is exhaustive over all6774 normalized rows but is not a claim to personal transcription or infallible OCR of all names.',
                draftLedgerEdited=False, producerInputsEdited=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = replay()
    if args.check:
        assert load(DESTINATION) == result
    else:
        assert not DESTINATION.exists()
        DESTINATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status='passed', rows=result['rows'], receipt=pin(DESTINATION))))
