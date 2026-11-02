#!/usr/bin/env python3
"""Root's bounded source-image review and full native-reader checks for five schools.

Images were personally inspected before this receipt. Pixel replay establishes
source identity and view geometry, not a claim that every glyph was transcribed
by a person. Complete payment fields also require two independent native readers
and broad row-coverage checks; financial controls never supply a source cell.
"""
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
PACKET = AREA / 'school_native/native-peer-packet.json'
CONTROLS = {
    'sd34-2025': [['129600389.79', '813496.13'], ['257697.20', '29864.71']],
    'sd40-2025': [['51532101.32', '227387.65'], ['201984.72', '8861.86']],
    'sd41-2025': [['185691610.04', '844485.58'], ['246874.60', '11176.26']],
    'sd57-2025': [['88452789.87', '902523.72'], ['186610.20', '36526.96']],
    'sd62-2025': [['94036349', '460412'], ['162655', '16296']],
}
EXPECTED_RESIDUALS = {'sd62-2025': [['-5', '-1'], ['1', '1']]}
# Source-visible complete prefixes. Partly clipped final strokes are excluded
# in the Frost and Senft rows. No hidden full title is promoted as visible text.
TITLE_READINGS = [
    ('Forbes-King, Greg', 'Director, Facilities & Transportati', '211790.42', '1825.32'),
    ('Frost, Shelly', 'Senior Manager,Budget & Stude', '133747.80', '4905.36'),
    ('Hagkull, Stacey', 'Senior Manager, Human Resourc', '139753.45', '16214.90'),
    ('Harley, Adrianne', 'Senior Manager,Accounting Servi', '147770.31', '6246.77'),
    ('Kroeker, Robert', 'Manager, Information Technolog', '126101.21', '3748.03'),
    ('Muir, Kate', 'Senior Manager, Human Resourc', '137060.01', '14408.47'),
    ('Phagura, Manveer', 'Senior Manager, Human Resourc', '126947.02', '2524.35'),
    ('Ryder, David', 'Manager, International Recruitm', '130259.41', '30989.96'),
    ('Senft, Andrea', 'Manager, Early Learning & Child', '104031.63', '7412.47'),
    ('Taylor, Patrick', 'Manager, Information Technolog', '132524.41', '4573.40'),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def verify_original_views(packet):
    import fitz
    from PIL import Image
    images, docs, rendered = [], {}, {}
    for source in packet['sources']:
        path = Path(source['originalPath'])
        assert sha(path.read_bytes()) == source['sourceSha256']
        doc = fitz.open(path)
        docs[source['key']] = doc
        for view in source['sourceImageViews']:
            image_path = ROOT / view['file']
            assert sha(image_path.read_bytes()) == view['sha256']
            pix = doc[view['physicalPage'] - 1].get_pixmap(dpi=view['dpi'])
            replay = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            original = Image.open(image_path).convert('RGB')
            assert original.size == replay.size and original.tobytes() == replay.tobytes(), view
            images.append({'file': view['file'], 'sha256': view['sha256'],
                           'sourceSha256': source['sourceSha256'], 'physicalPage': view['physicalPage'],
                           'dpi': view['dpi'], 'entirePagePixelsReproduced': True})
    for target in packet['clippedTitleTargets']:
        number = target['physicalPage']
        if number not in rendered:
            pix = docs['sd34-2025'][number - 1].get_pixmap(dpi=300)
            rendered[number] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        crop = rendered[number].crop(target['integerCropBox'])
        path = ROOT / target['file']
        assert sha(path.read_bytes()) == target['sha256']
        original = Image.open(path).convert('RGB')
        assert crop.size == original.size and crop.tobytes() == original.tobytes(), target
        images.append({'file': target['file'], 'sha256': target['sha256'],
                       'physicalPage': number, 'dpi': 300, 'integerCropPixelsReproduced': True})
    return images


def main():
    import gap_school_native_coverage as coverage
    packet = read(PACKET)
    assert packet['noOutreach'] is True and len(packet['sources']) == 5
    assert len(packet['clippedTitleTargets']) == len(TITLE_READINGS) == 10
    viewed = verify_original_views(packet)
    results, decisions = [], []
    for source in packet['sources']:
        path = ROOT / source['candidatePath']
        assert sha(path.read_bytes()) == source['candidateSha256']
        raw = read(path)
        # Replay the original independent readers, rather than trusting summary
        # booleans or a matching subtotal. Coverage has its own broad predicates.
        import gap_school_native_extract as readers
        a, skipped, _ = readers.read_poppler(raw['popplerRawText'], source['config'])
        b, other_skipped = readers.read_mupdf(raw['mupdfRawPages'], source['config'])
        assert a == raw['popplerRows'] and b == raw['mupdfRows']
        assert not skipped and not other_skipped
        assert len(a) == len(b)
        differences = []
        for number, (left, right) in enumerate(zip(a, b), 1):
            for field in readers.FIELDS:
                if left[field] != right[field]:
                    differences.append((number, field))
        if source['key'] == 'sd34-2025':
            targets = packet['clippedTitleTargets']
            assert set(differences) == {(t['sequence'], 'position') for t in targets}
            for target, (name, prefix, pay, expenses) in zip(targets, TITLE_READINGS):
                row = a[target['sequence'] - 1]
                assert row['name'] == name and Decimal(row['remuneration']) == Decimal(pay)
                assert Decimal(row['expenses']) == Decimal(expenses)
                decisions.append({'sourceId': source['key'], 'sequence': target['sequence'],
                                  'physicalPage': target['physicalPage'], 'name': name,
                                  'acceptedVisiblePositionPrefix': prefix,
                                  'sourceImageFile': target['file'], 'sourceImageSha256': target['sha256'],
                                  'literalRemuneration': pay, 'literalExpenses': expenses,
                                  'qualificationRequired': 'Source title visibly clipped; no hidden trailing text inferred.'})
        else:
            assert not differences
        residuals = []
        for scope, printed in zip(['employee-remuneration', 'school-trustees'], CONTROLS[source['key']]):
            rows = [row for row in a if row['category'] == scope]
            computed = [sum((Decimal(row[field]) for row in rows if row[field] is not None), Decimal())
                        for field in ['remuneration', 'expenses']]
            actual = [str(value - Decimal(control)) for value, control in zip(computed, printed)]
            expected = EXPECTED_RESIDUALS.get(source['key'], [['0', '0'], ['0', '0']])[
                0 if scope == 'employee-remuneration' else 1]
            assert [Decimal(x) for x in actual] == [Decimal(x) for x in expected], (source['key'], scope, computed, printed, actual)
            residuals.append({'scope': scope, 'rows': len(rows), 'literalPrintedControls': printed,
                              'computedTotals': list(map(str, computed)), 'residuals': actual,
                              'causeEstablished': False if any(Decimal(x) for x in actual) else None})
        results.append({'key': source['key'], 'sourceSha256': source['sourceSha256'],
                        'candidateFile': source['candidatePath'], 'candidateSha256': source['candidateSha256'],
                        'fullNativeReaderRows': len(a), 'boundedTitleDisagreements': len(differences),
                        'sourceSalaryHeadingEndsOn': '2025-06-30', 'controls': residuals})
    # The worker executes the broader source-row coverage audit separately. Its
    # receipt and code are pinned here; root inspects its closed classifications.
    coverage_path = AREA / 'school_native/native-payment-row-coverage.json'
    audit = read(coverage_path)
    assert audit['status'] == 'passed'
    assert {entry['key'] for entry in audit['sources']} == set(CONTROLS)
    for source, result in zip(packet['sources'], results):
        entry = next(entry for entry in audit['sources'] if entry['key'] == source['key'])
        assert entry['candidate']['sha256'] == source['candidateSha256']
        assert entry['sourceSha256'] == source['sourceSha256']
        assert entry['allPaymentRowsAccounted'] is True and entry['candidateRows'] == result['fullNativeReaderRows']
        raw = read(ROOT / source['candidatePath'])
        assert coverage.geometry_audit(raw) == entry['geometryPaymentRowAudit']
        assert coverage.text_audit(raw) == entry['physicalTextAudit']
    out = AREA / 'reviews'
    out.mkdir(exist_ok=True)
    receipt = {'schema': 'salary-native-schools-root-peer-v1', 'accepted': True,
               'acceptedSubjectToExactTitleAdoptions': True, 'noOutreach': True,
               'packet': {'path': str(PACKET.relative_to(ROOT)), 'sha256': sha(PACKET.read_bytes())},
               'scope': 'Full independent native-reader comparisons and source-row coverage, plus bounded personal source-image context and all10 clipped-title targets; not personal transcription of all5239 rows.',
               'originalViewReplay': viewed, 'sources': results, 'titleAdoptions': decisions,
               'paymentRowCoverage': {'path': str(coverage_path.relative_to(ROOT)),
                                      'sha256': sha(coverage_path.read_bytes())},
               'reviewCodeSha256': sha(Path(__file__).read_bytes())}
    dest = out / 'root-five-native-school-source-review.json'
    assert not dest.exists(), 'Keep review receipts immutable; issue a new version for a rereview'
    dest.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': str(dest.relative_to(ROOT)), 'sources': len(results),
                      'rows': sum(x['fullNativeReaderRows'] for x in results), 'sourceViewsReproduced': len(viewed)}))


if __name__ == '__main__':
    main()
