#!/usr/bin/env python3
"""Root's exact, original-image-backed municipal pay-definition adoptions."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
OUT = AREA / 'reviews/municipal-root'
OLD_ID = 'wave-lower-mainland-city-of-abbotsford-2023-employee-remuneration'
NEW_ID = 'gap-fill-municipal-city-of-abbotsford-2023-employee-remuneration'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def main():
    import fitz
    from PIL import Image
    manifest_path = ROOT / 'research/salaries/gap-fill-municipal/sources.json'
    sources = read(manifest_path)['sources']
    supplemental = read(AREA / 'municipal/abbotsford-known-column-supplement.json')
    baseline = read(AREA / 'baseline.json.gzip')
    old = baseline['sourceMetadata'][OLD_ID]
    assert supplemental['sourceSha256'] == old['sha256'] == '8cce0bc7013f866085cd7a301d406c2ce0438d2a6de5e20bf133b458c44db5ff'
    assert supplemental['exactPriorHeldRows'] == old['validation']['heldRows']
    prior = read(ROOT / supplemental['priorData']['path'])
    assert sha((ROOT / supplemental['priorData']['path']).read_bytes()) == supplemental['priorData']['sha256'] == old['dataSha256']
    assert len(prior) == 449
    source = next(s for s in sources if s['id'] == NEW_ID)
    rows = read(manifest_path.parent / source['file'])
    held = supplemental['exactPriorHeldRows']
    expected = [['city-of-abbotsford', h['name'], h['position'], h['knownRemunerationColumn'], h['expenses'], h['pdfPage']] for h in held]
    key = lambda row: json.dumps(row, ensure_ascii=False, separators=(',', ':'))
    assert Counter(map(key, rows)) == Counter(map(key, expected)) and len(rows) == 11
    assert all(h['benefits'] is None for h in held)
    assert not {(r[1], r[5]) for r in rows} & {(r[1], r[5]) for r in prior}
    assert source['completeEmployeeSchedule'] is False and source['validation']['partialCompensationDefinition']
    views = []
    original = Path('/workspace/gap-municipal-cache/city-of-abbotsford-a4b384ac4f3b.pdf')
    assert sha(original.read_bytes()) == source['sha256']
    doc = fitz.open(original)
    rendered = {}
    for spec in supplemental['cropSpecs']:
        pn = spec['physicalPage']
        if pn not in rendered:
            pix = doc[pn - 1].get_pixmap(dpi=300, alpha=False)
            rendered[pn] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        crop = rendered[pn].crop(spec['pixelCropBounds'])
        path = ROOT / spec['crop']
        assert sha(path.read_bytes()) == spec['cropSha256']
        with Image.open(path) as actual:
            assert actual.convert('RGB').size == crop.size and actual.convert('RGB').tobytes() == crop.tobytes()
        views.append({**pin(path), 'physicalPage': pn, 'sourceSha256': source['sha256'], 'sourcePixelsReproduced': True})
    rossland = []
    section_packet = read(AREA / 'municipal/independent-review-packet.json')
    for year, prefix, pn, expected_pay in [(2016, '31dadfc3ccf6', 34, [11798] + [6016] * 6),
                                          (2017, 'fd093bc75659', 35, [12010] + [6125] * 6),
                                          (2018, '11dd025d45a1', 36, [12828, 5531, 5531, 5531, 5531, 6542, 5531, 1011, 1011, 1011, 1011, 1011])]:
        s = next(s for s in sources if s['id'] == f'gap-fill-municipal-city-of-rossland-{year}-elected-officials')
        values = read(manifest_path.parent / s['file'])
        assert [r[3] for r in values] == expected_pay
        page_image = Path(f'/workspace/gap-municipal-cache/city-of-rossland-{prefix}-p{pn}-300dpi.png')
        section = next(section for section in section_packet['sections'] if section['sourceId'] == s['id'])
        original = Path(section['cachedPdf'])
        assert sha(original.read_bytes()) == s['sha256']
        pdf = fitz.open(original)
        pix = pdf[pn - 1].get_pixmap(dpi=300, alpha=False)
        with Image.open(page_image) as actual:
            assert actual.convert('RGB').size == (pix.width, pix.height) and actual.convert('RGB').tobytes() == pix.samples
        copy = OUT / f'rossland-{year}-council-original300.png'
        shutil.copyfile(page_image, copy)
        rossland.append({'sourceId': s['id'], 'candidateDataSha256': s['dataSha256'],
                         'approvedBy': '/root', 'approved': True,
                         'reason': 'Root personally viewed the actual full original council table, including literal Remuneration, Taxable Benefit, Expenses and expense-inclusive Total headers. Uniformly adopt the published Remuneration column for every row; exclude separately disclosed benefits and expenses. Kruyse benefit blank remains unknown, never imputed zero. This is a consistent published pay component, not a claim of complete composite compensation.',
                         'originalPageView': {**pin(copy), 'physicalPage': pn, 'sourceSha256': s['sha256'], 'sourcePixelsReproduced': True}})
    supplement_adoption = {'sourceId': NEW_ID, 'candidateDataSha256': source['dataSha256'],
                           'approvedBy': '/root', 'approved': True,
                           'reason': 'Root personally read all11 original row crops and source header. Import the known Remuneration & Payouts component only, explicitly excluding unknown separate Taxable Benefits; expenses stay literal, including two unknown cells. Exact previously held11 are disjoint from old449; complete original has460named rows. Preserve old449composite rows and all old source metadata unchanged. Public notes must distinguish this partial compensation component from complete composite remuneration and disclose the recommendation/adoption limitation.',
                           'boundedDisjointElevenRowSupplementApproved': True,
                           'prior449DataAndMetadataUnchanged': True, 'unknownBenefitsRemainUnknown': True,
                           'priorSourceId': OLD_ID, 'sourceSha256': source['sha256'],
                           'sourceProof': pin(AREA / 'municipal/abbotsford-known-column-supplement.json'),
                           'rootOriginalRowViews': views, 'rootOriginalHeaderView': pin(OUT / 'abbotsford-header.png')}
    receipt = {'approvedBy': '/root', 'approved': True, 'noOutreach': True,
               'qualifiedDefinitionAdoptions': rossland + [supplement_adoption],
               'sourceScope': 'Exactly three Rossland council cohorts,7/7/12observations, and11Abbotsford known-component payments. No salary field changed to balance a control. Source-first independent full peer receipts remain required for every cohort.',
               'reviewCode': pin(Path(__file__))}
    dest = OUT / 'four-qualified-pay-definition-adoptions.json'
    assert not dest.exists()
    dest.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(pin(dest)))


if __name__ == '__main__':
    main()
