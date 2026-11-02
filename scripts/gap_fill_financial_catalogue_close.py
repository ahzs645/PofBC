#!/usr/bin/env python3
"""Close the finite28 source-scope audit; no salary rows or outreach are produced."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02/reviews/financial-catalogue-audit'
HEALTH = ROOT / 'research/salaries/gap-fill-2026-11-02/health_employees'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {'file': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def main():
    source_index = AREA / 'all28-actual-source-page-index.json'
    text_index = AREA / 'all28-complete-native-or-ocr-scope-text-proof.json'
    readings = AREA / 'personal-scope-readings.json'
    locator_path = HEALTH / 'metadata-only-financial-original-locators.json'
    priority_path = HEALTH / 'metadata-only-financial-priority.json'
    index = json.loads(source_index.read_text())['items']
    native_ocr = {x['itemUuid']: x for x in json.loads(text_index.read_text())}
    personal = {x['itemUuid']: x for x in json.loads(readings.read_text())['items']}
    locators = {x['item']['uuid']: x for x in json.loads(locator_path.read_text())}
    priority = {x['itemUuid'] for x in json.loads(priority_path.read_text())}
    assert len(index) == len(native_ocr) == len(personal) == len(locators) == 28
    assert len(priority) == 10
    items = []
    ocr_pages = 0
    original_bytes = 0
    for record in index:
        uid = record['itemUuid']
        retrieval_path = AREA / f'{uid}-retrieval.json'
        retrieval = json.loads(retrieval_path.read_text())
        assert len(retrieval['originals']) == 1
        original = retrieval['originals'][0]
        locator = locators[uid]
        assert original['bitstreamUuid'] == locator['bitstreamUuid']
        assert original['sourceUrl'] == locator['url'] == record['sourceUrl']
        assert original['name'] == locator['name']
        source = Path(record['cachePdf'])
        assert sha(source) == record['sourceSha256'] == original['retrieval']['sha256']
        assert original['retrieval']['status'] == 200
        assert source.read_bytes().startswith(b'%PDF-')
        original_bytes += source.stat().st_size
        pages = list(range(1, record['pdfPages'] + 1))
        reading = personal[uid]
        assert reading['allPhysicalPagesPersonallyIndexViewed'] == pages
        assert reading['namedPaymentAppendixObserved'] is False
        assert reading['actualPrintedPeriodEnds']
        scope = native_ocr[uid]
        scope_path = ROOT / scope['completeNativeOrOcrScopeIndex']
        assert sha(scope_path) == scope['sha256']
        scope_pages = json.loads(gzip.decompress(scope_path.read_bytes()))
        assert [x['physicalPage'] for x in scope_pages] == pages
        images = []
        for sheet in record['wholePageIndexSheets']:
            assert sha(ROOT / sheet['file']) == sheet['sha256']
            images.append(sheet)
        assert [p for sheet in images for p in sheet['physicalPages']] == pages
        evidence_path = AREA / uid / 'page-evidence.json'
        evidence = json.loads(evidence_path.read_text())
        assert evidence['sourceSha256'] == record['sourceSha256']
        assert sha(AREA / uid / 'native-pymupdf-pages.json.gzip') == record['pymupdfTextSha256']
        assert sha(AREA / uid / 'native-poppler-layout.txt.gzip') == record['popplerTextSha256']
        ocr = []
        for page in record['nativeSparsePages']:
            path = AREA / uid / f'page-{page}-ocr.json.gzip'
            receipt = json.loads(gzip.decompress(path.read_bytes()))
            assert receipt['itemUuid'] == uid and receipt['physicalPage'] == page
            assert sha(Path(receipt['pngCachePath'])) == receipt['pngSha256']
            ocr.append({**pin(path), 'physicalPage': page, 'sourceRasterSha256': receipt['pngSha256']})
        ocr_pages += len(ocr)
        raw = source.read_bytes()
        items.append({
            'itemUuid': uid,
            'issuer': record['issuer'],
            'employerSlug': record['employerSlug'],
            'sourceUrl': original['sourceUrl'],
            'explicitOriginalBitstreamUuid': original['bitstreamUuid'],
            'sourceSha256': record['sourceSha256'],
            'sourceCachePath': str(source),
            'sourceBytes': len(raw),
            'cataloguePeriodDiscoveryOnly': record['cataloguePeriodDiscoveryOnly'],
            'actualPrintedPeriodEnds': reading['actualPrintedPeriodEnds'],
            'priorityWithoutLocatedSalaryCounterpart': uid in priority,
            'physicalPages': record['pdfPages'],
            'allPagesPersonallyIndexViewed': pages,
            'actualContents': reading['actualContents'],
            'disposition': 'actual-original-financial-statements-and-notes-no-named-payment-appendix-observed',
            'newSalaryRows': 0,
            'retrieval': pin(retrieval_path),
            'pageEvidence': pin(evidence_path),
            'completeNativeOrOcrScopeTextIndex': pin(scope_path),
            'wholePageIndexSheets': images,
            'ocrSparsePages': ocr,
            'storedMetadata': {'sizeBytes': original['metadataSizeBytes'], 'checksum': original['metadataChecksum']},
            'retrievedContentMd5': hashlib.md5(raw).hexdigest(),
            'retrievedEqualsStoredMetadataBytes': len(raw) == original['metadataSizeBytes'],
            'retrievedEqualsStoredMetadataMd5': hashlib.md5(raw).hexdigest() == original['metadataChecksum']['value'],
        })
    assert sum(x['physicalPages'] for x in items) == 789
    assert ocr_pages == 235
    result = {
        'status': 'complete-for-exact28-captured-financial-originals',
        'scope': 'The exact28 financial ORIGINAL relations supplied after the full606 captured catalogue label audit, including the corrected10 priority originals. No further discovery or outreach.',
        'method': 'Every actual page was personally viewed in a complete rendered page index. Complete PyMuPDF and Poppler native text were retained; every235 native-sparse/image page was independently rendered150dpi and read by Tesseract for scope review. Salary/remuneration keyword contexts, actual contents pages where present, period covers, financial note sequences and final pages were inspected. This is an appendix/scope census, not a literal transcription of every financial amount.',
        'findings': 'All28 actual files contain financial statements and financial notes; no named employee or board payment schedule was observed. Compensation language concerns aggregate expenses, payable balances, benefit plans, actuarial liabilities or Mental Health Plan accruals. No individual salary records are created from those totals. Separate salary publications being processed elsewhere are not inferred absent from these findings.',
        'sourceIdentityQualification': 'The28 downloaded content responses match the explicit item ORIGINAL-bundle bitstream UUID/name/content URL relations and have independently pinned actual response SHA256 values. In all28 cases, the retrieved PDF byte count and MD5 differ from stored DSpace metadata. The observed library cover is retained. No cause for the discrepancy is asserted, and stored metadata checksums are not represented as hashes of the retrieved bytes.',
        'ocrQualification': 'Scope review used actual page images and full-page text; OCR alone does not establish literal field accuracy. PHSA2007/08 physical24 has actual note16 Compensation and benefits; its OCR reads18. The actual source-heading crop is retained, and the personal image reading16 controls.',
        'limits': 'This closes only these28 actual files. It does not prove that an issuer never published a separate historical salary/board schedule, nor that all historical financial originals have been located.',
        'inputPins': [pin(locator_path), pin(priority_path), pin(HEALTH / 'full606-catalogue-label-scope-audit.json')],
        'personalReadings': pin(readings),
        'nativeOrOcrTextProof': pin(text_index),
        'initialSourcePageIndex': pin(source_index),
        'ocrHeadingExceptionImage': pin(AREA / 'phsa2007-08-compensation-note-heading-source.png'),
        'counts': {'originals': 28, 'priorityOriginals': 10, 'physicalPages': 789, 'ocrSparsePages': 235, 'newSalaryRows': 0, 'namedPaymentAppendicesObserved': 0, 'sourceBytes': original_bytes},
        'items': items,
        'noOutreach': True,
    }
    (AREA / 'complete-source-scope-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
