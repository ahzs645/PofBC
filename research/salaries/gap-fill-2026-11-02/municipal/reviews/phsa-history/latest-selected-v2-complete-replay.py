"""Independent complete-source guards plus explicit replay of producer readers.

The original pixel census and expense classification predate candidate access.
Replaying producer row readers is a computational reproducibility check, not a
claim to independent model inference or whole-cohort human transcription.
"""
import collections
import gzip
import hashlib
import json
import pathlib
import re
import sys

import fitz
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[6]
BASE = pathlib.Path(__file__).resolve().parent
PRODUCER = ROOT / 'research/salaries/gap-fill-2026-11-02/phsa_history'
sys.path.insert(0, str(ROOT / 'scripts'))
import gap_phsa_history_readers as readers
import gap_phsa_history_scan as scan
import gap_phsa_history_select as selector


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gzip' else path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def canonical(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False))


def name(value):
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value.strip()))


def fields(row):
    return [name(row['name']), row.get('position'), row['remuneration'], row['expenses'], row['pdfPage']]


pixel_census = read(BASE / 'latest-two-scan-independent-pixel-census.json')
expense_calibration = read(BASE / 'latest-two-scans-source-expense-glyph-calibration.json')
for key in ['phsa-2013-14', 'phsa-2014-15']:
    raw_path = PRODUCER / (key + '-scan-candidate-v4.json.gzip')
    final_path = PRODUCER / (key + '-scan-selected-v2.json.gzip')
    human_path = BASE / (key + '-selected-v2-final-personal-source-readings.json')
    candidate, final, human = read(raw_path), read(final_path), read(human_path)
    pc = next(s for s in pixel_census['sources'] if s['sourceKey'] == key)
    glyph = next(s for s in expense_calibration['sources'] if s['sourceKey'] == key)
    assert final['candidateSha256'] == sha(raw_path.read_bytes())
    assert candidate['source']['sourceSha256'] == final['sourceSha256'] == pc['sourceSha256'] == glyph['sourceSha256']
    assert not final['pending']
    assert len(candidate['rows']) == len(final['rows']) == len(pc['pixelRows']) == len(glyph['expenseGlyphs'])
    actual = {r['sequence']: r['selected'] for r in final['rows']}
    human_rows = {r['sequence']: r for r in human['rows']}
    assert all(fields(actual[seq]) == fields(row) for seq, row in human_rows.items())
    pixel_failures, expense_failures = [], []
    for raw, selected, pixel, g in zip(candidate['rows'], final['rows'], pc['pixelRows'], glyph['expenseGlyphs']):
        seq = raw['sequence']
        assert seq == selected['sequence'] == pixel['sequence'] == g['sequence']
        assert raw['physicalPage'] == selected['selected']['pdfPage'] == pixel['physicalPage'] == g['physicalPage']
        assert selected['selected']['remuneration'] is not None
        y = raw['sourceNameBand']['center'] * 72 / 300
        ey = (pixel['y0'] + pixel['y1']) / 2
        if abs(y - ey) > 1.5:
            pixel_failures.append(seq)
        dash = g['classification'] == 'small horizontal dash-shaped glyph'
        if (selected['selected']['expenses'] is None) != dash:
            expense_failures.append({'sequence': seq, 'originalGlyph': g['classification'], 'selectedExpense': selected['selected']['expenses']})
    assert not pixel_failures, pixel_failures
    assert not expense_failures, expense_failures
    pdf = pathlib.Path('/workspace/gap-phsa-history-cache') / (key + '.pdf')
    assert sha(pdf.read_bytes()) == pc['sourceSha256']
    doc = fitz.open(pdf)
    pages = []
    matched = collections.Counter()
    for page in candidate['pages']:
        pn = page['physicalPage']
        raw_ocr_path = ROOT / page['rawPath']
        assert sha(raw_ocr_path.read_bytes()) == page['rawSha256']
        raw_ocr = read(raw_ocr_path)
        png = pathlib.Path('/workspace/gap-phsa-history-cache/images') / f'{key}-p{pn:03d}.png'
        assert sha(png.read_bytes()) == page['sourceImageSha256'] == raw_ocr['sourceImageSha256']
        pixmap = doc[pn - 1].get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
        cached_image = Image.open(png).convert('RGB')
        assert cached_image.size == (pixmap.width, pixmap.height)
        assert cached_image.tobytes() == pixmap.samples
        adapted = scan.adapt(raw_ocr)
        # A source-specific actual footer is retained on every page.
        words = readers.tess_words(adapted['tesseractRawTsv'])
        footlines = {x['line'] for x in words if x['text'].lower() in ['this', 'statement'] and x['y'] > adapted['imageHeight'] * .85}
        footwords = [x for x in words if x['line'] in footlines]
        profile = {**candidate['profile'], 'sourceLegalFooterTop': min(x['box'][1] for x in footwords) if footwords else candidate['profile']['sourceLegalFooterTop']}
        one, totals1, err1 = readers.read_tesseract(adapted, profile)
        two, totals2, err2 = readers.read_rapid(adapted, profile)
        assert len(one) == page['tesseractCount'] and len(two) == page['rapidCount']
        assert canonical(totals1) == page['totalsTesseract'] and canonical(totals2) == page['totalsRapid']
        assert err1 + err2 == page['readerErrors']
        geo = page['geometry']
        raw_page_rows = [r for r in candidate['rows'] if r['physicalPage'] == pn]
        assert len(raw_page_rows) == page['actualNameBandCount'] == sum(p['physicalPage'] == pn for p in pc['pixelRows'])
        for row in raw_page_rows:
            for who, rerun in [('tesseract', one), ('rapid', two)]:
                hits = [r for r in rerun if abs(r['y'] - geo['nameToPaymentOffsets'][who] - row['sourceNameBand']['center']) < geo['rowPitchPixels'] * .38]
                result = hits[0] if len(hits) == 1 else None
                assert canonical(result) == row[who], (key, row['sequence'], who)
                if result is not None:
                    matched[who] += 1
        outside = {}
        for who, rerun in [('tesseract', one), ('rapid', two)]:
            outside[who] = [r for r in rerun if not any(abs(r['y'] - geo['nameToPaymentOffsets'][who] - b['center']) < geo['rowPitchPixels'] * .38 for b in geo['nameBands'])]
        assert canonical(outside) == page['outsidePaintedNameBands']
        # Each source's sole extra TSV line is the personally read printed Totals,
        # below the original horizontal rule; it is not a named individual.
        if any(outside.values()):
            assert pn == len(doc) and len(outside['tesseract']) == 1 and not outside['rapid']
            assert outside['tesseract'][0]['y'] > geo['bodyBottom']
        pages.append({'physicalPage': pn, 'rawOcrPin': pin(raw_ocr_path),
                      'originalWholePagePngSha256': page['sourceImageSha256'],
                      'freshOriginalRGBPixelSha256': sha(pixmap.samples),
                      'independentOriginalPixelPaymentRows': len(raw_page_rows),
                      'replayedReaderCounts': [len(one), len(two)],
                      'allSnapshotReaderRowsReplayedExactly': True,
                      'outsideReaderRows': outside})
    # Pure read-only replay of producer selection: all original alternatives,
    # source receipts, benchmark minima, full-cell ink and pending guards.
    replay = selector.run(key, 'v4', 'v2', write=False)
    assert canonical(replay) == final, key
    for receipt in final['primaryPersonalReceipts']:
        assert sha((ROOT / receipt['path']).read_bytes()) == receipt['sha256']
    totals = [sum(r['selected'][field] or 0 for r in final['rows']) for field in ['remuneration', 'expenses']]
    assert totals == final['literalComputedTotals']
    printed = [425632576, 8642235] if key == 'phsa-2013-14' else [438199947, 9051748]
    out = {'sourceKey': key, 'phase': 'final selected-v2 complete computational replay after personal source review',
           'sourceSha256': pc['sourceSha256'], 'candidatePin': pin(raw_path), 'selectedPin': pin(final_path),
           'personalFinalReadingPin': pin(human_path), 'personallyImageReadUniqueRows': len(human_rows),
           'completeCohortRows': len(final['rows']), 'allPersonalFieldsAgree': True,
           'allOriginalPixelPaymentRowsMappedInExactOrderAndPage': True,
           'allOriginalExpenseCellsComparedToIndependentPreCandidateGlyphGuard': True,
           'expenseGlyphCounts': glyph['classCounts'], 'expenseGlyphMismatchCount': 0,
           'allSalaryPagesOriginalRGBPixelsAndRawOCRPinsReplayed': True,
           'rawReaderMatchedNamedRowCounts': dict(matched), 'allSnapshotReaderRowsReplayedExactly': True,
           'fullSourcePaymentCensusPin': pin(BASE / 'latest-two-scan-independent-pixel-census.json'),
           'independentExpenseGuardPin': pin(BASE / 'latest-two-scans-source-expense-glyph-calibration.json'),
           'allPrimaryReceiptPinsAndFiniteGuardSelectionReplayedExactly': True,
           'sourcePeriodAllPageHeaderPin': pin(BASE / 'latest-two-scans-complete-period-header-review.json'),
           'sourceContextPin': pin(BASE / 'latest-two-scans-first-source-context-transcript.json'),
           'candidatePending': [], 'literalComputedTotals': totals, 'literalPrintedTotals': printed,
           'literalResiduals': [a - b for a, b in zip(totals, printed)],
           'residualTreatment': 'Preserve every literal row and printed control. No amount adjustment, zero imputation, inferred rounding or cause.',
           'scopeLimit': 'Bounded human source transcription; complete source-pixel census, glyph guard and raw-reader/selection replay are computational. Replayed producer readers are not independent model inference. Finite confidence benchmarks are not an accuracy rate.',
           'pages': pages, 'noOutreach': True}
    destination = BASE / (key + '-selected-v2-complete-source-replay.json')
    assert not destination.exists(), destination
    destination.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'key': key, 'receipt': pin(destination), 'humanRows': len(human_rows), 'allRows': len(final['rows']), 'residuals': out['literalResiduals']}), flush=True)
