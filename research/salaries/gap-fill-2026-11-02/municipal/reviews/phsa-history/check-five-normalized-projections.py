"""Pin final five normalized cohorts to completed independent source reviews."""
import argparse
import collections
from decimal import Decimal
import gzip
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
BASE = pathlib.Path(__file__).resolve().parent
COLLECTION = ROOT / 'research/salaries/gap-fill-phsa-history'


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gzip' else path.read_text())


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def source_name(value):
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value.strip()))


args = argparse.ArgumentParser()
args.add_argument('--manifest', default=str(COLLECTION / 'sources-candidate.json'))
args.add_argument('--output', default=str(BASE / 'five-final-normalized-projection-review.json'))
opt = args.parse_args()
manifest_path = pathlib.Path(opt.manifest)
manifest = read(manifest_path)
sources = {s['id'].removeprefix('gap-phsa-history-'): s for s in manifest['sources']}
output = []
native_peer = read(BASE / 'native-v2-producer-comparison.json')
native_pins = {s['sourceKey']: s for s in native_peer['sources']}
for key in ['phsa-2006-07', 'phsa-2007-08', 'phsa-2008-09', 'phsa-2013-14', 'phsa-2014-15']:
    source = sources[key]
    if key in native_pins:
        selected_path = ROOT / native_pins[key]['independentPeerRowsPin']['path']
        selected = read(selected_path)
        expected_rows = selected['rows']
        source_sha = selected['sourceSha256']
        input_pin = native_pins[key]['producerCandidatePin']
        peer_path = BASE / 'native-v2-producer-comparison.json'
    else:
        selected_path = ROOT / f'research/salaries/gap-fill-2026-11-02/phsa_history/{key}-scan-selected-v2.json.gzip'
        selected = read(selected_path)
        expected_rows = [r['selected'] for r in selected['rows']]
        source_sha = selected['sourceSha256']
        input_pin = pin(selected_path)
        peer_path = BASE / (key + '-selected-v2-complete-source-replay.json')
    expected = [['provincial-health-services-authority', source_name(r['name']), None, r['remuneration'], r['expenses'], r['pdfPage']] for r in expected_rows]
    data_path = COLLECTION / source['file']
    proof_path = COLLECTION / source['provenanceFile']
    data, proof = read(data_path), read(proof_path)
    assert data == expected, key
    assert hashlib.sha256(data_path.read_bytes()).hexdigest() == source['dataSha256']
    assert hashlib.sha256(proof_path.read_bytes()).hexdigest() == source['provenanceSha256']
    assert source['sha256'] == proof['sourceSha256'] == source_sha
    assert proof['sourceSelection'] == input_pin == source['validation']['sourceSelection']
    assert pin(peer_path) in proof['independentPeerReviews']
    additive_peer = None
    if key == 'phsa-2013-14':
        additive_peer = pin(BASE / 'phsa-2013-14-final-source-peer-acceptance-addendum.json')
        assert additive_peer in proof['independentPeerReviews']
    assert len(data) == source['rowCount'] == source['validation']['actualNamedObservations']
    assert source['sector'] == 'Health authorities' and source['scope'] == 'employee-remuneration'
    start = int(key[5:9])
    assert source['periodEnd'] == f'{start + 1}-03-31'
    assert source['year'] == f'{start}/{str(start+1)[-2:]}'
    assert source['retainCompiledPartition'] is True
    assert source['validation']['compiledPartitionRetained'] is True
    assert source['validation']['compiledPartitionRetentionReason']
    assert 'compiled' in source['publicWarning'].lower()
    assert source['validation']['residualCauseEstablished'] is False
    sums = [sum(Decimal(str(r[column])) for r in data if r[column] is not None) for column in [3, 4]]
    controls = source['validation']['printedNamedControls']
    residuals = [str(sums[0] - Decimal(str(controls['remuneration']))), str(sums[1] - Decimal(str(controls['expenses'])))]
    assert residuals == source['validation']['literalNamedControlResiduals']
    if any(Decimal(r) for r in residuals):
        assert all(r in source['publicWarning'] for r in residuals)
        assert 'no cause is established' in source['publicWarning'].lower()
    assert len(proof['rows']) == len(data)
    assert all(r['rowIndex'] == ix and r['pdfPage'] == data[ix-1][5] and r['name'] == data[ix-1][1] for ix, r in enumerate(proof['rows'], 1))
    if key in native_pins:
        assert [r.get('sourceFootnoteMarker') for r in proof['rows']] == [r['sourceNameFootnote'] for r in expected_rows]
    if key == 'phsa-2006-07':
        assert source['validation']['printedEmployeeNarrativeCount'] == 1280
        assert source['rowCount'] == 1267
        assert '1,280' in source['publicWarning'] and '1,267' in source['publicWarning']
    output.append({'sourceKey': key, 'sourceSha256': source_sha, 'rows': len(data),
                   'normalizedDataPin': pin(data_path), 'normalizedProvenancePin': pin(proof_path),
                   'completeReviewedInputPin': input_pin, 'sourcePeerReceiptPin': pin(peer_path),
                   'additiveSourcePeerReceiptPin': additive_peer,
                   'allNormalizedLiteralFieldsAndSourceOrderAgree': True,
                   'allMissingExpenseAndExplicitZeroRepresentationsPreserved': True,
                   'literalNamedControlResiduals': residuals,
                   'nullExpenseRows': sum(r[4] is None for r in data),
                   'rowsByPhysicalPage': dict(collections.Counter(r[5] for r in data)),
                   'compiledPartitionRetained': True})
destination = pathlib.Path(opt.output)
assert not destination.exists(), destination
result = {'status': 'pass for exact five normalized source/data/provenance inputs; root adoption remains separate',
          'manifestPin': pin(manifest_path), 'sources': output, 'rows': sum(s['rows'] for s in output),
          'scope': 'All normalized fields/order/footnote markers checked against prior complete native or scan source-review selection. Personal image transcription remains bounded as specified in each immutable receipt.',
          'noOutreach': True}
destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'receipt': pin(destination), 'rows': result['rows'], 'cohorts': len(output)}))
