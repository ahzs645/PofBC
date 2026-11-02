#!/usr/bin/env python3
"""Root's complete normalized-row adoption of65 reviewed health originals."""
import copy
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

from gap_fill_health_context_review import control

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    candidate = ROOT / 'research/salaries/gap-fill-health-employees/sources-candidate.json'
    assert sha(candidate.read_bytes()) == 'ad82f4dba33d6322715c0bb7e278d6ecccf2a27e263e5658eb3fee2f2886bbb6'
    sources = read(candidate)['sources']
    indices = {s['key']: s for s in read(AREA / 'health_employees/native-primary-candidate-index.json')}
    contexts = {s['key']: s for s in read(AREA / 'health_employees/source-context-review-packet.json')['sources']}
    closure_path = AREA / 'health_employees/source-verification-closure.json'
    closure = read(closure_path)
    assert sha(closure_path.read_bytes()) == 'c24031a6158a9cdac9b9c3f0174b664b805fe218041714eec777e8701cb22087'
    assert len(closure['sourceImageTargetDecisions']) == 352 and len(closure['readerFlagDecisions']) == 93
    assert all(s['allDifferencesExplicitlyImageCovered'] for s in closure['rowDifferenceCoverage'])
    for ref in closure['proofRefs']:
        assert sha((ROOT / ref['path']).read_bytes()) == ref['sha256']
    adoption_path = AREA / 'reviews/root-seven-health-clipped-name-adoptions.json'
    nulls = read(adoption_path)['adoptions']
    selected = []
    for source in sources:
        key = source['id'].removeprefix('gap-health-employees-')
        index = indices[key]
        assert index['sourceSha256'] == source['sha256']
        primary_path = ROOT / index['file']
        assert sha(primary_path.read_bytes()) == index['sha256']
        primary = read(primary_path)['rows']
        expected = []
        for item in primary:
            row = copy.deepcopy(item['row'])
            matches = [a for a in nulls if a['sourceKey'] == key and a['physicalPage'] == row[5] and a['sourceRowOnPage'] == item['sourceRowOnPage']]
            assert len(matches) <= 1
            if matches:
                a = matches[0]
                assert [row[3], row[4]] == [a['remuneration'], a['expenses']]
                row[1] = None
            if key == 'island-health-2005-06' and row[1] == 'STEVEN,LOIS' and row[5] == 17:
                assert expected[-1][1] == 'STEEN,SARAH'
                expected.append(['island-health', 'M.S.', None, 88941, 0, 17])
            expected.append(row)
        path = candidate.parent / source['file']
        assert sha(path.read_bytes()) == source['dataSha256']
        actual = read(path)
        assert actual == expected and len(actual) == source['rowCount']
        provenance = candidate.parent / source['provenanceFile']
        assert sha(provenance.read_bytes()) == source['provenanceSha256']
        context = contexts[key]
        printed = control(context)
        assert source['validation']['printedNamedControls'] == printed
        pay = sum((Decimal(str(r[3])) for r in actual), Decimal())
        expense = sum((Decimal(str(r[4])) for r in actual if r[4] is not None), Decimal())
        residuals = [pay - Decimal(str(printed['remuneration'])), expense - Decimal(str(printed['expenses'] or 0))] if printed else None
        declared = source['validation']['literalNamedControlResiduals']
        assert (None if declared is None else list(map(Decimal, declared))) == residuals
        if residuals and any(residuals):
            assert 'differing from the printed named controls' in source['publicWarning']
        assert all(r[2] is None and r[0] == source['employerSlug'] for r in actual)
        assert source['validation']['unavailableNamesDueOriginalClipping'] == sum(r[1] is None for r in actual)
        assert source['year'] == context['candidateYear']
        selected.append({'sourceId': source['id'], 'sourceSha256': source['sha256'],
                         'dataSha256': source['dataSha256'], 'provenanceSha256': source['provenanceSha256'],
                         'rowCount': source['rowCount'], 'accepted': True,
                         'exactReconstructionFromOriginalPrimaryAndPinnedAdoptions': True,
                         'remunerationSum': str(pay), 'knownExpenseSum': str(expense),
                         'literalNamedControlResiduals': None if residuals is None else list(map(str, residuals))})
    visibility_path = AREA / 'health_employees/native-visibility-flag-dispositions.json'
    visibility = read(visibility_path)
    assert visibility['count'] == 192 and visibility['salaryHiddenWhiteTransparentLaterOverpaintOrOutsidePageFlags'] == 0
    assert len(sources) == 65 and sum(s['rowCount'] for s in sources) == 207001
    assert sum(s['validation']['unavailableNamesDueOriginalClipping'] for s in sources) == 7
    fraser = next(s for s in sources if s['employerSlug'] == 'fraser-health' and s['year'] == '2010/11')
    assert 'equivalence of their counting scopes is not established' in fraser['publicWarning']
    assert 'does not supply missing observations or inferred positions' in fraser['publicWarning']
    receipt = {'accepted': True, 'approvedBy': 'root', 'noOutreach': True,
               'candidateManifest': pin(candidate), 'sourceVerificationClosure': pin(closure_path),
               'sourceContextAcceptance': pin(AREA / 'reviews/root-health-source-context-acceptance.json'),
               'nativeVisibilityDispositions': pin(visibility_path), 'sevenNullNameAdoption': pin(adoption_path),
               'exactSevenFieldOnlyChangeCheck': pin(AREA / 'health_employees/normalized-seven-clipped-name-change-check.json'),
               'fraserAdditionalContextQualification': pin(AREA / 'health_employees/fraser-2010-11-contract-context-qualification.json'),
               'sources': selected,
               'scope': 'All65actual fiscal-year employee originals,207001published payment observations, complete native reader/physical-page/monetary-anchor census and352independent original-image exception targets. Root personally reviewed65source headers/56named controls and critical context images, independently replayed131source contexts and exact normalized rows; this is not a claim of personal transcription of207001rows. Initial reader artifacts and peer first-reading mistakes are preserved and finite source-image corrections are pinned.',
               'qualifications': 'Literal residuals, Island2022/23narrative count disagreement, Fraser2010/11 separate contract-count context, below-threshold source observations, partial M.S. name and exact seven clipped names remain public/provenance-qualified. No source value is balanced or missing field imputed. These65cohorts exclude the separately delegated earlier employee histories, found board tables and financial-appendix audit. No claim that all29discovery leads are already closed.',
               'reviewCode': pin(Path(__file__))}
    output = AREA / 'reviews/root-sixty-five-health-source-acceptance.json'
    assert not output.exists(), 'Keep acceptance immutable and issue additive revisions'
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(output), 'sources': 65, 'rows': 207001}))


if __name__ == '__main__':
    main()
