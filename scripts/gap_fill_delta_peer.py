#!/usr/bin/env python3
"""Root's complete Delta native replay and bounded original-image review."""
import collections
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
OUT = AREA / 'reviews/delta-root'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    import fitz
    from PIL import Image
    import gap_school_south_native as readers
    packet_path = AREA / 'school_south/sd37-complete-source-peer-packet.json'
    packet = read(packet_path)
    assert packet['noOutreach'] is True
    assert sha((ROOT / packet['nativeParser']['path']).read_bytes()) == packet['nativeParser']['sha256']
    original = Path(packet['source']['cachePath'])
    assert sha(original.read_bytes()) == packet['source']['sha256']
    doc = fitz.open(original)
    for label in ['rawCandidate', 'selectedCandidate']:
        assert sha((ROOT / packet[label]['path']).read_bytes()) == packet[label]['sha256']
    raw = read(ROOT / packet['rawCandidate']['path'])
    selected = read(ROOT / packet['selectedCandidate']['path'])
    xml = subprocess.check_output(['pdftotext', '-bbox-layout', str(original), '-'])
    a = readers.poppler_geometry_reader(xml, 37)
    b, flags, visibility = readers.geometry_reader(doc, 37)
    assert a == raw['popplerRows'] and b == raw['mupdfRows'] and not flags
    assert len(a) == len(b) == len(selected['rows']) == 1056
    assert all(not p['nonPaintedOrWhiteTextTraces'] for p in visibility)
    fields = readers.FIELDS
    diffs = [(n, k) for n, (x, y) in enumerate(zip(a, b), 1) for k in fields if x.get(k) != y.get(k)]
    adoptions = {r['sequence']: r for r in selected['imageFieldSelections']}
    assert set(adoptions) == {122, 185, 199, 625, 794, 921, 926, 1019}
    for n, (left, actual) in enumerate(zip(b, selected['rows']), 1):
        if n in adoptions:
            assert all(actual.get(k) == adoptions[n]['selectedFields'].get(k) for k in fields)
        else:
            assert all(left.get(k) == actual.get(k) for k in fields), (n, 'Unbounded row alteration')
    # Wider payment census does not require a valid recognized name, title,
    # parser row, or a $75,000 minimum; every literal pay anchor is classified.
    page_census = []
    for pn in packet['salaryPages']:
        page = doc[pn - 1]
        anchors = []
        for word in page.get_text('words'):
            center = (word[0] + word[2]) / 2
            token = word[4].replace(',', '').replace('$', '')
            if not (430 <= center <= 504) or not token.isdigit():
                continue
            y = (word[1] + word[3]) / 2
            # Only column-header-bearing table body, not the fiscal year in
            # the caption or a footer. All payable rows have >=four digits.
            if int(token) < 1000:
                continue
            near = sorted([w for w in page.get_text('words') if abs((w[1] + w[3]) / 2 - y) < 1.7], key=lambda w: w[0])
            label = ' '.join(w[4] for w in near if w[0] < 430)
            matched = [row for row in selected['rows'] if row['pdfPage'] == pn and abs(row['sourceY'] - y) < 1.7]
            aggregate = label.upper().startswith(('TOTAL ', 'CONSOLIDATED '))
            if pn == 69 and token == '52002015' and not label:
                # This one printed control has its label on the preceding
                # physical line, personally verified in the full source page.
                aggregate = True
            assert len(matched) == 1 or (not matched and aggregate), (pn, label, token, 'Unclassified payment anchor')
            if matched:
                assert Decimal(matched[0]['remuneration']) == Decimal(token)
            anchors.append({'sourceY': y, 'literalPayToken': word[4], 'kind': 'named-observation' if matched else 'printed-aggregate'})
        count = sum(v['kind'] == 'named-observation' for v in anchors)
        expected = sum(row['pdfPage'] == pn for row in selected['rows'])
        assert count == expected
        page_census.append({'physicalPage': pn, 'namedRows': count, 'paymentAnchors': anchors})
    rendered = {}
    views = []
    for target in packet['targets'] + packet['contexts']:
        path = ROOT / target['path']
        assert sha(path.read_bytes()) == target['sha256']
        dpi = target.get('dpi', 600)
        cachekey = (target['physicalPage'], dpi)
        if cachekey not in rendered:
            pix = doc[target['physicalPage'] - 1].get_pixmap(dpi=dpi, alpha=False)
            rendered[cachekey] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        expected = rendered[cachekey]
        if 'integerBox600Dpi' in target:
            expected = expected.crop(target['integerBox600Dpi'])
        with Image.open(path) as image:
            assert image.convert('RGB').size == expected.size and image.convert('RGB').tobytes() == expected.tobytes()
        views.append({**pin(path), 'physicalPage': target['physicalPage'], 'dpi': dpi, 'sourcePixelsReproduced': True})
    first_path = OUT / 'first-ten-benchmark-transcript.json'
    first = read(first_path)
    assert first['candidateValuesSeen'] is False
    # First readings are preserved. These four bounded rereads were made after
    # comparison, using actual original crops; candidate feedback is disclosed.
    rereads = {
        256: {'name': 'DRINNAN, MICHELLE L.'},
        812: {'position': 'TEACHER', 'remuneration': 116360},
        963: {'position': 'TEACHER'},
        977: {'position': 'TEACHER'},
    }
    additive = {'candidateFeedbackSeen': True, 'reason': 'Root first personal contact-sheet readings contained four name/title/payment mistakes. Individually reopened source crops clearly establish these literal fields. No candidate value was changed.',
                'firstReadings': pin(first_path), 'corrections': rereads,
                'sourceImagePaths': [t for t in packet['targets'] if t['sequence'] in rereads]}
    additive_path = OUT / 'additive-four-benchmark-rereads.json'
    assert not additive_path.exists()
    additive_path.write_text(json.dumps(additive, ensure_ascii=False, indent=2) + '\n')
    for row in first['observations']:
        row.update(rereads.get(row['sequence'], {}))
        actual = selected['rows'][row['sequence'] - 1]
        for key in ['name', 'position', 'department']:
            assert row[key] == actual[key], (row['sequence'], key)
        for key in ['remuneration', 'expenses']:
            assert (None if row[key] is None else Decimal(str(row[key]))) == (None if actual[key] is None else Decimal(actual[key]))
        assert row['physicalPage'] == actual['pdfPage']
    controls = []
    for scope, printed in [('employee-remuneration', ['114425758', '579812']), ('school-trustees', ['247664', '17194'])]:
        rows = [r for r in selected['rows'] if r['category'] == scope]
        computed = [sum((Decimal(r[k]) for r in rows if r[k] is not None), Decimal()) for k in ['remuneration', 'expenses']]
        controls.append({'scope': scope, 'rows': len(rows), 'printedNamedControls': printed,
                         'literalComputed': list(map(str, computed)),
                         'residual': [str(c - Decimal(p)) for c, p in zip(computed, printed)], 'causeEstablished': False})
    assert [(r['rows'], r['residual']) for r in controls] == [(1049, ['2', '-5']), (7, ['-2', '-1'])]
    receipt = {'accepted': True, 'noOutreach': True, 'sourceSha256': packet['source']['sha256'],
               'packet': pin(packet_path), 'selectedCandidate': packet['selectedCandidate'],
               'rawCandidate': packet['rawCandidate'], 'parser': packet['nativeParser'],
               'fullNativeRows': 1056, 'completeSourcePaymentCensus': page_census,
               'nativeReaderDifferences': diffs, 'boundedEightSourceAdoptions': selected['imageFieldSelections'],
               'independentEightCasePeer': packet['boundedEightFieldPeerReceipt'],
               'originalPixelReplays': views, 'firstBenchmarkReadings': pin(first_path),
               'additiveBenchmarkRereads': pin(additive_path), 'controls': controls,
               'sourceContext': 'Actual schedule and declaration endJune30,2025; cover declares2024/2025. Cover saysOriginal Document Signed andDec9,2025, rather than showing handwritten signatures. Remuneration and expenses are distinct columns; lower-threshold aggregates excluded. Source blank expense cells remain unknown.',
               'limitations': 'Complete independent native readers and wider payment census, plus personally viewed five context pages and ten withheld benchmark source crops. Eight crowded/clipped fields rely additionally on the separately pinned municipal peer. Root did not personally transcribe all1,056rows. Four root first reading mistakes are retained and explicitly corrected from original images.',
               'nullNameAdoption': {'sequence': 926, 'name': None, 'reason': 'Source clips the final given-name glyph; keep known90486pay/42expense and visible fragment in provenance. No full given name is inferred.'},
               'reviewCode': pin(Path(__file__))}
    dest = OUT / 'complete-delta-source-acceptance.json'
    assert not dest.exists()
    dest.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(dest), 'rows': 1056, 'paymentPages': len(page_census), 'sourceViews': len(views)}))


if __name__ == '__main__':
    main()
