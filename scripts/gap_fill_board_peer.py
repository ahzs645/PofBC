#!/usr/bin/env python3
"""Root peer receipt: source-pixel replay, complete native comparison and money meaning.

All25 original board tables were personally inspected. This combines bounded
personal image checks with complete independent native-reader corroboration;
it does not claim a person's transcription of every monetary cell.
"""
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
WORK = AREA / 'health_boards'
COLLECTION = ROOT / 'research/salaries/gap-fill-health-boards'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def literal_amount(text):
    value = text.replace('$', '').replace(',', '').strip()
    if value in {'', '-', '‐', '–', '—'}:
        return None
    if not re.fullmatch(r'(?:-?\d+(?:\.\d{2})?|\(\d+(?:\.\d{2})?\))', value):
        raise ValueError('Unexpected original monetary text: ' + repr(text))
    return Decimal(value.replace('(', '-').replace(')', ''))


def source_pay(cells, spec):
    if spec.get('directPayField'):
        return literal_amount(cells[spec['directPayField']])
    values = []
    for field in spec['payComponentFields']:
        for token in cells[field].replace('$', ' ').split():
            value = literal_amount(token)
            if value is not None:
                values.append(value)
    return sum(values, Decimal()) if values else None


def main():
    import fitz
    from PIL import Image
    import gap_health_boards as worker
    packet_path = WORK / 'peer-review-packet-v2.json'
    notes_path = AREA / 'reviews/root-health-board-source-image-observations.json'
    notes = read(notes_path)
    assert notes['viewedWholeScheduleImages'] is True
    assert notes['packet'] == ref(packet_path)
    packet = read(packet_path)
    specs = read(WORK / 'source-specs.json')
    assert len(specs) == len(packet['sources']) == 25
    assert {x['id'] for x in specs} == {x['id'] for x in packet['sources']}
    manifest = read(COLLECTION / 'sources.json')
    published_candidates = {x['id']: x for x in manifest['sources']}
    visibility_path = WORK / 'visibility-manifest-v2.json'
    diagnostics = read(visibility_path)
    assert {x['sourceId'] for x in diagnostics} == {x['id'] for x in specs}
    receipts, views = [], []
    numeric_count = held_count = edge_flags = 0
    for spec in specs:
        entry = next(x for x in packet['sources'] if x['id'] == spec['id'])
        assert entry['sha256'] == spec['sha256']
        original = Path(spec['cachePath'])
        assert sha(original.read_bytes()) == spec['sha256']
        doc = fitz.open(original)
        for view in entry['renders']:
            path = Path(view['cachePath'])
            assert sha(path.read_bytes()) == view['sha256']
            pix = doc[view['physicalPage'] - 1].get_pixmap(dpi=view['dpi'])
            replay = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            image = Image.open(path).convert('RGB')
            assert image.size == replay.size and image.tobytes() == replay.tobytes(), spec['id']
            views.append({'sourceId': spec['id'], 'sourceSha256': spec['sha256'],
                          'physicalPage': view['physicalPage'], 'dpi': view['dpi'],
                          'renderedImageSha256': view['sha256'], 'exactOriginalPixelsReproduced': True})
        proof_path = COLLECTION / 'evidence' / (spec['id'] + '.json.gzip')
        proof = read(proof_path)
        assert proof['sourceSha256'] == spec['sha256']
        controls = worker.validate_source_readings(proof, spec)
        a, cells_a, b, cells_b = worker.compare_native_rows(proof, spec)
        assert a == b and len(a) == spec['namedRows']
        expected = []
        held = []
        for row, detail in zip(a, cells_a):
            pay = source_pay(detail['rawCells'], spec)
            expense = literal_amount(detail['rawCells']['expenses']) if 'expenses' in detail['rawCells'] else None
            assert (None if row[3] is None else Decimal(str(row[3]))) == pay
            assert (None if row[4] is None else Decimal(str(row[4]))) == expense
            assert row[0] == spec['employerSlug'] and row[5] == spec['page']
            (held if pay is None else expected).append(row)
        data_path = COLLECTION / (spec['id'] + '.json.gzip')
        assert read(data_path) == expected
        numeric_count += len(expected)
        held_count += len(held)
        if expected:
            candidate = published_candidates[spec['id']]
            assert candidate['sha256'] == spec['sha256']
            assert candidate['dataSha256'] == sha(data_path.read_bytes())
            assert candidate['rowCount'] == len(expected)
            assert candidate['scope'] == 'board-remuneration'
            assert candidate['completeEmployeeSchedule'] is False
            assert candidate['publicWarning'].strip()
            assert candidate['validation']['compiledPartitionRetained'] is True
            for field, digest in [('provenanceFile', 'provenanceSha256'), ('evidenceFile', 'evidenceSha256')]:
                assert sha((COLLECTION / candidate[field]).read_bytes()) == candidate[digest]
        else:
            assert spec['id'] not in published_candidates
        diagnostic = next(x for x in diagnostics if x['sourceId'] == spec['id'])
        assert diagnostic['sourceSha256'] == spec['sha256']
        assert sha((ROOT / diagnostic['path']).read_bytes()) == diagnostic['sha256']
        for key, value in diagnostic['flags'].items():
            if key == 'nativeWordsCrossingReviewedFieldEdges':
                edge_flags += value
            else:
                assert value == 0, (spec['id'], key, value)
        receipts.append({'sourceId': spec['id'], 'sourceSha256': spec['sha256'],
                         'dataSha256': sha(data_path.read_bytes()), 'numericPayRows': len(expected),
                         'supportingOnlyNonnumericPayRows': len(held), 'publishable': bool(expected),
                         'sourceWordEvidence': ref(proof_path), 'literalControlReadings': controls,
                         'visibilityReceipt': diagnostic})
    assert numeric_count == 266 and held_count == 57 and len(published_candidates) == 23
    assert edge_flags == 37
    receipt = {'schema': 'salary-board-histories-root-peer-v1', 'accepted': True,
               'noOutreach': True, 'sources': receipts, 'numericPayRows': numeric_count,
               'supportingOnlyNonnumericPayRows': held_count, 'nonemptyCohorts': 23,
               'personalSourceImageObservations': ref(notes_path), 'peerPacket': ref(packet_path),
               'sourceSpecification': ref(WORK / 'source-specs.json'),
               'visibilityManifest': ref(visibility_path), 'sourceViews': views,
               'fieldEdgeDisposition': 'All37 reviewed boundary flags retain entire native words assigned by centre in both readers; no glyph or cell value is cut. Actual source-column assignments checked on original images.',
               'reviewScope': notes['personalReviewScope'],
               'reviewCode': ref(Path(__file__).resolve())}
    dest = AREA / 'reviews/root-health-board-histories-source-review.json'
    assert not dest.exists(), 'Preserve immutable review; issue a new revision if inputs change'
    dest.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': str(dest.relative_to(ROOT)), 'originals': 25,
                      'nonemptyCohorts': 23, 'numericPayRows': numeric_count,
                      'supportingOnlyRows': held_count, 'originalViewsReplayed': len(views)}))


if __name__ == '__main__':
    main()
