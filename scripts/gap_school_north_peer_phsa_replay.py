"""Read-only PHSA peer replay of pinned original rasters and both raw readers.

This does not rerun OCR or claim a complete personal field transcription.
"""
from pathlib import Path
import argparse
import collections
import gzip
import hashlib
import json
import statistics

import fitz
import gap_phsa_history_scan as scan
import gap_phsa_history_readers as readers

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02/phsa_history'
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gzip') else data)


def canonical(value):
    return json.loads(json.dumps(value))


def replay(key):
    candidate_path = BASE / f'{key}-candidate-observed-first-v4.json.gzip'
    candidate = load(candidate_path)
    original = Path('/workspace/gap-phsa-history-cache') / f'{key}.pdf'
    assert sha(original.read_bytes()) == candidate['source']['sourceSha256']
    doc = fitz.open(original)
    first_raw = load(ROOT / candidate['pages'][0]['rawPath'])
    prof = scan.profile(scan.adapt(first_raw))
    assert canonical(prof) == candidate['profile']
    pages = []
    for page in candidate['pages']:
        physical = page['physicalPage']
        raw_path = ROOT / page['rawPath']
        assert sha(raw_path.read_bytes()) == page['rawSha256']
        raw = load(raw_path)
        assert raw['sourceSha256'] == sha(original.read_bytes())
        assert raw['physicalPage'] == physical
        raster = Path(raw['sourceImageCachePath'])
        assert sha(raster.read_bytes()) == raw['sourceImageSha256'] == page['sourceImageSha256']
        fresh = doc[physical - 1].get_pixmap(dpi=300, alpha=False)
        assert sha(fresh.tobytes('png')) == raw['sourceImageSha256'], (key, physical, 'original raster')
        adapted = scan.adapt(raw)
        if key == 'phsa-2012-13' and physical == 87:
            assert not raw['rapidOcrRaw'] and not readers.tess_words(raw['tesseractRawTsv'])
            # Source pixels, rather than reader absence, prove this terminal blank.
            # Personally viewed full original: one isolated black scan speck,
            # no letters, numbers, heading, table, or payment rows.
            import numpy as np
            samples = np.frombuffer(fresh.samples, dtype=np.uint8).reshape(fresh.height, fresh.width, fresh.n)
            ys, xs = np.where(samples[:, :, :3].mean(axis=2) < 200)
            assert list(zip(xs.tolist(), ys.tolist())) == [(883, 1993)] and len(page['rows']) == 0
            pages.append(dict(physicalPage=physical, rawPath=page['rawPath'], rawSha256=page['rawSha256'],
                              sourceImageSha256=raw['sourceImageSha256'], noVisibleTextOrTable=True,
                              isolatedOriginalScanSpeckPixels=[[883, 1993]], literalBlankDisposition='Personally viewed original terminal page has no table/text; exact one-pixel scan speck retained.'))
            print(key, physical, 'original blank', flush=True)
            continue
        words = readers.tess_words(raw['tesseractRawTsv'])
        foot_lines = {x['line'] for x in words if x['text'].lower() in ['this', 'statement'] and x['y'] > raw['imageHeight'] * .85}
        foot_words = [x for x in words if x['line'] in foot_lines]
        page_profile = dict(prof, sourceLegalFooterTop=min(x['box'][1] for x in foot_words) if foot_words else prof['sourceLegalFooterTop'])
        one, total_one, err_one = readers.read_tesseract(adapted, page_profile)
        two, total_two, err_two = readers.read_rapid(adapted, page_profile)
        assert canonical(foot_words) == page['pageFooterWords']
        assert canonical(total_one) == page['totalsTesseract']
        assert canonical(total_two) == page['totalsRapid']
        assert err_one + err_two == page['readerErrors']
        assert len(one) == page['tesseractCount'] and len(two) == page['rapidCount']
        geom = page['geometry']
        for sequence in page['rows']:
            row = candidate['rows'][sequence - 1]
            assert row['sequence'] == sequence and row['physicalPage'] == physical
            for label, independent in [('tesseract', one), ('rapid', two)]:
                hits = [r for r in independent if abs(r['y'] - geom['nameToPaymentOffsets'][label] - row['sourceNameBand']['center']) < geom['rowPitchPixels'] * .38]
                assert canonical(hits[0] if len(hits) == 1 else None) == row[label], (key, sequence, label)
        for label, independent in [('tesseract', one), ('rapid', two)]:
            outside = [r for r in independent if not any(abs(r['y'] - geom['nameToPaymentOffsets'][label] - b['center']) < geom['rowPitchPixels'] * .38 for b in geom['nameBands'])]
            assert canonical(outside) == page['outsidePaintedNameBands'][label]
        pages.append(dict(physicalPage=physical, rawPath=page['rawPath'], rawSha256=page['rawSha256'],
                          sourceImageSha256=raw['sourceImageSha256'], tesseractCount=len(one), rapidCount=len(two),
                          mappedPaymentRows=len(page['rows']), outsideRows={k: len(v) for k, v in page['outsidePaintedNameBands'].items()},
                          readerErrors=page['readerErrors']))
        if physical % 10 == 0:
            print(key, physical, 'exact original + two raw reader fields', flush=True)
    packet = load(AREA / 'source-only-packets' / f'{key}-v4/packet.json')
    targets = {x['sequence'] for x in packet['targets']}
    true_flags = {x['sequence'] for x in candidate['rows'] if any(not r.startswith('low-') for r in x['reasons'])}
    assert true_flags <= targets
    return dict(key=key, sourceSha256=sha(original.read_bytes()), candidateSnapshotSha256=sha(candidate_path.read_bytes()),
                sourcePages=len(doc), replayedPages=len(pages), salaryRows=len(candidate['rows']),
                allOriginal300dpiRastersExact=True, bothRawReaderAllFieldsExact=True,
                trueFieldGeometryFlagCount=len(true_flags), allTrueFieldGeometryFlagsPersonallyRead=True,
                rawReaderOutsideRows=sum(sum(p.get('outsideRows', {}).values()) for p in pages),
                pages=pages,
                limit='Read-only deterministic replay of retained raw OCR and exact original pixels, plus complete independent payment-band census elsewhere. This is not OCR rerun or a complete personal transcription of all payment fields.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    destination = BASE / 'two-source-raw-readers-and-original-raster-replay.json'
    result = dict(sources=[replay(key) for key in ['phsa-2011-12', 'phsa-2012-13']], noOutreach=True)
    if args.check:
        assert load(destination) == result
    else:
        assert not destination.exists()
        destination.write_text(json.dumps(result, indent=2) + '\n')
    print('receipt', sha(destination.read_bytes()), flush=True)


if __name__ == '__main__':
    main()
