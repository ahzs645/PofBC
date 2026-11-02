#!/usr/bin/env python3
"""Activate only the exact root-accepted PHSA candidate and freeze owned files."""
import copy
import json
from pathlib import Path
import subprocess
import sys

from gap_phsa_history_build import COLLECTION, decode, main as rebuild, pinned, ref, sha, validate_retention
from gap_phsa_history_fetch import AREA, ROOT

ROOT_ACCEPTANCE = {
    'path': 'research/salaries/gap-fill-2026-11-02/reviews/root-nine-phsa-history-source-acceptance.json',
    'sha256': '0ac2f26bd907c1d46fd93fed52a35ab4ccd4d7e895bb98a47e2c6b5fadf7481a',
}
PROJECTION = {
    'path': 'research/salaries/gap-fill-2026-11-02/municipal/reviews/phsa-history/five-final-normalized-projection-review.json',
    'sha256': '7dfa3f4bc9957427c58ebdc028d29db490eac6620860732c41e7a0ce2242ff94',
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def owned_files():
    paths = list(AREA.rglob('*')) + list(COLLECTION.rglob('*'))
    paths += list((ROOT / 'scripts').glob('gap_phsa_history*.py'))
    paths += [ROOT / 'scripts/test_gap_phsa_history.py']
    return sorted({p for p in paths if p.is_file() and '__pycache__' not in p.parts and p.name not in ['producer-freeze.json', 'producer-freeze-replay.json']})


def main():
    assert not (AREA / 'producer-freeze.json').exists(), 'Already frozen; use read-only hash replay'
    acceptance = pinned(ROOT_ACCEPTANCE)
    assert acceptance['accepted'] is True and acceptance['approvedBy'] == 'root'
    candidate = pinned(acceptance['candidateManifest'])
    index = pinned(acceptance['sourceAcceptanceIndex'])
    pinned(PROJECTION)
    assert not index['pendingPeerScopes']
    assert len(candidate['sources']) == 9 and sum(s['rowCount'] for s in candidate['sources']) == 22796
    before = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in COLLECTION.iterdir() if p.is_file()}
    rebuild()
    after = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in COLLECTION.iterdir() if p.is_file()}
    assert before == after, 'Second offline build changed normalized candidate bytes'
    assert ref(COLLECTION / 'sources-candidate.json') == acceptance['candidateManifest']
    approved = {s['sourceId']: s for s in acceptance['sources']}
    final = copy.deepcopy(candidate)
    final['status'] = 'verified with explicit literal source qualifications'
    final['rootSourceAcceptance'] = ROOT_ACCEPTANCE
    final['independentFiveSourceNormalizedProjection'] = PROJECTION
    sources = []
    for source in final['sources']:
        exact = approved[source['id']]
        assert source['sha256'] == exact['sourceSha256']
        for field in ['dataSha256', 'provenanceSha256', 'rowCount']:
            assert source[field] == exact[field]
        validate_retention(source)
        source['status'] = 'verified'
        source['verifiedOn'] = '2026-11-02'
        source['validation'].update(candidateOnly=False, independentPeerVerified=True, rootSourceAcceptance=ROOT_ACCEPTANCE, pendingGates=[])
        sources.append({
            'sourceId': source['id'], 'year': source['year'], 'sourceSha256': source['sha256'],
            'dataSha256': source['dataSha256'], 'provenanceSha256': source['provenanceSha256'],
            'numericRows': source['rowCount'], 'employerSlug': source['employerSlug'],
            'literalNamedControlResiduals': source['validation']['literalNamedControlResiduals'],
            'completeEmployeeSchedule': True, 'retainCompiledPartition': True,
        })
    dump(COLLECTION / 'sources.json', final)
    (COLLECTION / 'README.md').write_text(
        '# Earlier PHSA employee disclosures\n\n'
        'Nine official Legislative Library originals add 22,796 named employee payment observations for fiscal 2006/07–2014/15. The original schedules publish no job titles. All existing compiled observations remain retained, with possible overlap disclosed.\n\n'
        'The [methods and source qualifications](../gap-fill-2026-11-02/phsa_history/METHODS.md) explain the two-reader/native or raster extraction, complete payment censuses, bounded personal source review, explicit unknown expense dashes, original period/count contradictions and literal control residuals. The [source clarification ledger](../gap-fill-2026-11-02/phsa_history/remaining-source-clarifications.json) lists issues for possible later issuer clarification; no requests were sent.\n\n'
        'Offline reconstruction: `python scripts/gap_phsa_history_build.py`. Regression checks: `python -m unittest discover -s scripts -p test_gap_phsa_history.py -v`. Both use committed evidence without live retrieval, OCR models or original PDF caches. Original processing scripts and exact source/model fingerprints are retained separately. Re-run processing only in an isolated research checkout; the producer evidence is frozen.\n'
    )
    inventory = pinned(index['inventory'])
    originals = []
    for original in inventory['sources']:
        path = Path(original['cachePath'])
        assert sha(path.read_bytes()) == original['sourceSha256']
        originals.append({'key': original['key'], 'sourceSha256': original['sourceSha256'], 'physicalPages': original['pageCount']})
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_gap_phsa_history.py', '-v'], cwd=ROOT, capture_output=True, text=True)
    assert tests.returncode == 0, tests.stdout + tests.stderr
    assert 'Ran 12 tests' in tests.stderr
    log = AREA / 'offline-validation.log'
    log.write_text(tests.stdout + tests.stderr)
    validation = {
        'offlineRegressionTests': 12, 'passed': True, 'log': ref(log),
        'secondNormalizedBuildByteIdentical': True, 'normalizedFilesBeforeAndAfter': before,
        'allNineDeliveredOriginalPdfHashesRechecked': originals,
        'originalPdfCachesNeededForOfflineTestsOrBuild': False, 'noOutreach': True,
    }
    dump(AREA / 'validation-results.json', validation)
    closure = {
        'status': 'nine earlier PHSA employee schedules fully processed and root accepted',
        'employeeOriginals': 9, 'employeeCohorts': 9, 'numericRows': 22796,
        'physicalPagesCensused': 602, 'nativePhysicalPages': 121, 'scannedPhysicalPagesIncludingCovers': 481,
        'scanBodyPagesCapturedThroughBothOcrReaders': 475, 'salaryPages': 583,
        'allTrueSourceFlagsAndAdaptiveChallengesClosed': True,
        'allOriginalPaymentBandsAccountedFor': True, 'allScanExpenseCellsSourceCalibrated': True,
        'noAllRowManualTranscriptionClaim': True, 'compiledRowsRemoved': 0,
        'rootSourceAcceptance': ROOT_ACCEPTANCE, 'sourceAcceptanceIndex': acceptance['sourceAcceptanceIndex'],
        'independentNormalizedProjection': PROJECTION, 'manifest': ref(COLLECTION / 'sources.json'),
        'sourceClarifications': ref(AREA / 'remaining-source-clarifications.json'),
        'validationResults': ref(AREA / 'validation-results.json'), 'noOutreach': True,
    }
    dump(AREA / 'source-verification-closure.json', closure)
    disposition = {
        'leadId': 'lead-034', 'disposition': 'accepted-official-history; all nine newly identified earlier original salary schedules processed',
        'periods': [s['year'] for s in final['sources']], 'employeeOriginalsImported': 9,
        'employeeCohorts': 9, 'numericRows': 22796, 'unlocatedOriginalsInThisFiniteBatch': 0,
        'unprocessedOcrInThisFiniteBatch': 0, 'unresolvedIndividualFields': 0,
        'issuerClarificationNotesRemainQualified': ref(AREA / 'remaining-source-clarifications.json'),
        'compiledRowsRemoved': 0, 'noOutreach': True,
    }
    dump(AREA / 'lead-dispositions.json', disposition)
    handoff = {
        'candidateReady': True, 'accepted': True, 'status': 'complete; frozen owned evidence', 'noOutreach': True,
        'originalReportsProcessed': 9, 'employeeOriginalsImported': 9, 'supportingOnlyOriginals': 0,
        'sourceCohortsWithNumericPay': 9, 'numericRows': 22796, 'compiledRowsRemoved': 0,
        'physicalPagesCensused': 602, 'scannedBodyPagesCaptured': 475, 'salaryPages': 583,
        'allRawReaderFlagsClosed': True, 'allIndependentPeerScopesClosed': True,
        'testCount': 12, 'rootSourceAcceptance': ROOT_ACCEPTANCE,
        'manifest': ref(COLLECTION / 'sources.json'), 'sourceVerification': ref(AREA / 'source-verification-closure.json'),
        'leadDispositions': ref(AREA / 'lead-dispositions.json'), 'sources': sources,
        'sourceClarifications': ref(AREA / 'remaining-source-clarifications.json'),
        'validationCommands': ['python -m unittest discover -s scripts -p test_gap_phsa_history.py -v', 'python scripts/gap_phsa_history_build.py'],
        'pending': [], 'freeze': {'path': str((AREA / 'producer-freeze.json').relative_to(ROOT))},
    }
    dump(AREA / 'handoff.json', handoff)
    handoff['frozenInputCount'] = len(owned_files())
    dump(AREA / 'handoff.json', handoff)
    files = owned_files()
    frozen = {'schemaVersion': 1, 'status': 'frozen', 'date': '2026-11-02', 'scope': ['phsa_history/**', 'gap-fill-phsa-history/**', 'scripts/gap_phsa_history*.py', 'scripts/test_gap_phsa_history.py'], 'inputs': [{**ref(p), 'bytes': p.stat().st_size} for p in files], 'frozenInputCount': len(files), 'noOutreach': True}
    dump(AREA / 'producer-freeze.json', frozen)
    for record in frozen['inputs']:
        assert sha((ROOT / record['path']).read_bytes()) == record['sha256']
    dump(AREA / 'producer-freeze-replay.json', {'passed': True, 'inputsChecked': len(files), 'producerFreeze': ref(AREA / 'producer-freeze.json'), 'noOutreach': True})
    print(json.dumps({'handoff': ref(AREA / 'handoff.json'), 'manifest': ref(COLLECTION / 'sources.json'), 'freeze': ref(AREA / 'producer-freeze.json'), 'frozenInputs': len(files), 'rows': 22796, 'cohorts': 9}))


if __name__ == '__main__':
    main()
