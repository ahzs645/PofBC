#!/usr/bin/env python3
"""Freeze the complete reviewed22-scope school handoff and exact queue changes."""
import argparse
import collections
import gzip
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'
COLLECTION = ROOT/'research/salaries/queue-completion-schools'
NEW_ROOT = ROOT/'research/salaries/queue-completion-2026-11-01'
QUEUE_KEYS = {'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
OUTBOX = [
    ('research/salaries/queue-completion-2026-11-01/acquisition/outbox/outbox-sd10-declaration-approval.md', '911c77da5fe7652f02d8d45b4abf007ce420c305bb461961bef75f9a11ade130'),
    ('research/salaries/queue-completion-2026-11-01/acquisition/outbox/outbox-sd08-heading-controls-approval.md', 'b32b22c9fe60b3f7efc3722d3a056d467f3968f444e25b234a95e8582d9fe10a'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def linked_files(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from linked_files(child)
    elif isinstance(value, list):
        for child in value:
            yield from linked_files(child)
    elif isinstance(value, str) and value.startswith('research/salaries/queue-completion-2026-11-01/'):
        path = ROOT/value
        if path.is_file():
            yield path


def freeze():
    manifest_path = COLLECTION/'sources.json'
    manifest = json.loads(manifest_path.read_text())
    sources = manifest['sources']
    assert manifest['reviewed'] and len(sources) == 22 and sum(s['rowCount'] for s in sources) == 15138
    assert all(s['status'] == 'verified' and not s['validation']['independentPeerReviewPending'] and s['retainCompiledPartition'] for s in sources)
    for source in sources:
        assert sha(COLLECTION/source['file']) == source['dataSha256']
        assert sha(COLLECTION/source['provenanceFile']) == source['provenanceSha256']
    employers = collections.defaultdict(list)
    for source in sources:
        employers[source['employerSlug']].append(source)
    queue = []
    for slug, scopes in sorted(employers.items()):
        first = scopes[0]
        number = first['id'].split('-sd')[-1].split('-')[0]
        predecessors = [f'continuation-schools-sd{number}-2025-processing']
        if number == '50':
            predecessors.append('recovery-schools-sd50-2025-scan-processing')
        queue.append({'id': f'queue-completion-schools-sd{number}-2025-integration', 'employerSlug': slug,
                      'employerName': first['employerName'], 'sector': 'School districts', 'reportingPeriods': ['2024/25'],
                      'sourceUrl': first['sourceUrl'], 'sourceIndexUrl': first['sourceIndexUrl'],
                      'status': 'complete-independent-reviewed-scopes-ready-for-integration', 'route': 'processing',
                      'nextAction': 'Integrate both complete named scopes from the new manifest, preserving exact source qualifications and all compiled partitions until the root comparison. SD50/SD61 unamended employee v1 artifacts are revision evidence and are not registered.',
                      'reason': 'Completes located processing for '+', '.join(predecessors)+f'; {sum(s["rowCount"] for s in scopes)} literal observations across separate employee/trustee scopes. '+('Published control qualifications remain literal, with no balancing.' if any(s['validation']['summaryReconciles'] is not True for s in scopes) else 'Both named monetary controls reconcile exactly.')})
    old_queue = json.loads((ROOT/'research/salaries/held-resolution-2026-11-01/schools/work-queue.json').read_text())
    for old_id, suffix, draft in [('held-resolution-schools-sd10-2025-approval-clarification','sd10-2025',OUTBOX[0]),
                                  ('held-resolution-schools-sd08-2026-issuer-clarification','sd08-2026',OUTBOX[1])]:
        old = next(item for item in old_queue if item['id'] == old_id)
        queue.append({**old, 'id': 'queue-completion-schools-'+suffix+'-issuer-clarification',
                      'status': 'public-routes-checked-existing-record-request-drafted-unsent',
                      'nextAction': 'Review the concrete unsent existing-record draft '+draft[0]+'. An issuer response or specifically corrected existing public record is still needed; no institution contact is authorized by this research closure.',
                      'reason': 'Continues '+old_id+'. Fresh original/index/board/public-search evidence is pinned in clarification-public-route-closure.json. Qualified existing398observations remain unchanged. The conflicting printed facts and missing SOFI-specific adoption evidence remain unresolved; no typo or cause is asserted.'})
    assert all(set(item) == QUEUE_KEYS for item in queue)
    write(AREA/'work-queue.json', queue)
    for filename, digest in OUTBOX:
        assert sha(ROOT/filename) == digest
    commands = [
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_finish_salary_schools.py', '-v'],
        [sys.executable, 'scripts/finish_salary_schools_native.py', '--check'],
        [sys.executable, 'scripts/finish_salary_schools_scan.py', '--check-amendments'],
        [sys.executable, 'scripts/finish_salary_schools_revisions.py', '--check'],
        [sys.executable, 'scripts/finish_salary_schools.py', '--check'],
        [sys.executable, 'scripts/finish_salary_schools_clarifications.py', '--check'],
        [sys.executable, 'scripts/finish_salary_schools_discover.py', '--verify-receipts'],
    ]
    validation = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, (shlex.join(command), result.stdout, result.stderr)
        validation.append({'command': shlex.join(command), 'exitCode': result.returncode,
                           'stdout': result.stdout, 'stderr': result.stderr})
    write(AREA/'validation.json', {'reviewedOn': '2026-11-01', 'allChecksPassed': True, 'checks': validation,
                                  'sourceManifestSha256': sha(manifest_path), 'newScopes': 22, 'newRows': 15138})
    baseline = json.loads((AREA/'registered-gap-inventory.json').read_text())
    baseline_missing = {e['employerSlug'] for e in baseline['employers'] if 'employee-remuneration' in e['current2024_25MissingCategories']}
    new_slugs = set(employers)
    controls = json.loads((AREA/'native-controls-and-context.json').read_text())
    handoff = {'frozenOn': '2026-11-01', 'collection': 'queue-completion-schools', 'scope': '22 complete published named scopes across11 additional official district employers; all observation periods explicitly2024/25.',
               'sourceManifest': {'file': str(manifest_path.relative_to(ROOT)), 'sha256': sha(manifest_path)},
               'newRows': 15138, 'newEmployeeRows': sum(s['rowCount'] for s in sources if s['category'] == 'employee-remuneration'),
               'newTrusteeRows': sum(s['rowCount'] for s in sources if s['category'] == 'school-trustees'),
               'nullExpenseRows': sum(s['validation']['nullExpenseRows'] for s in sources),
               'explicitZeroExpenseRows': sum(s['validation']['zeroExpenseRows'] for s in sources),
               'allCompiledPartitionsRetained': True, 'compiledReplacementOrCalendarRelabellingAuthorized': False,
               'priorAccepted398SchoolObservationsUnchanged': True,
               'sourceScopes': [{'id': s['id'], 'rows': s['rowCount'], 'sourceSha256': s['sha256'], 'file': s['file'], 'dataSha256': s['dataSha256'],
                                 'normalizedSha256': s['normalizedSha256'], 'provenanceFile': s['provenanceFile'], 'provenanceSha256': s['provenanceSha256'],
                                 'computedTotals': s['validation']['computedComponentTotals'], 'printedControls': s['validation']['printedControlTotals'],
                                 'residuals': s['validation']['controlResiduals'], 'independentPeerReview': s['validation']['independentPeerReview']} for s in sources],
               'literalControlsAndDefinitions': {'file': str((AREA/'native-controls-and-context.json').relative_to(ROOT)), 'sha256': sha(AREA/'native-controls-and-context.json')},
               'publicClarificationClosure': {'file': str((AREA/'clarification-public-route-closure.json').relative_to(ROOT)), 'sha256': sha(AREA/'clarification-public-route-closure.json'),
                                              'issuerItemsStillUnresolved': 2, 'outboxDrafts': [{'file': p, 'sha256': h} for p,h in OUTBOX], 'outreachSent': False},
               'revisionHistory': {'sd50FirstEmployeeDataSha256': '8ef567c55c22e061658f7eaca221edba46f73277d4aa2f2dfc139c88ef6ef161',
                                   'sd50AcceptedEmployeeV2Sha256': '0e21b24b559974668171a77e7f0e2cfe6c2d01c3929cd097ca8c3abf01a67502',
                                   'sd50NameAmendment': 'Exactly one shared OCR I/l error, Keir, lan J. → Keir, Ian J.; old proof/data/raw bytes remain unchanged. No generic capitalization.',
                                   'sd61AcceptedEmployeeV2Sha256': '4ef497c0aecb94b4857868df4ffc1b34ee2147b8570973721ed3957f0f67eedb',
                                   'sd61PositionAmendments': 'Exactly20 page-final TEACHER position fields exclude separate centred printed footer numbers5–24, as independently image-verified. All v1 bytes and all money/name/page/multiplicity fields remain unchanged.',
                                   'sd61ProvenanceWordingCorrection': 'Supporting native crop Matrix3 is216dpi, not the erroneous300dpi-equivalent phrase in its frozen amendment reason. Additive bounded-source-image-receipts.json qualifies that wording; no source/proof/data bytes changed.'},
               'coverageLimits': {'baselineAllPeriodOfficialSchoolEmployers': 25, 'additionalOfficialEmployers': len(new_slugs), 'prospectiveAllPeriodOfficialEmployers': 36,
                                  'baselineCurrent2024_25EmployeeDistricts': 60-len(baseline_missing),
                                  'prospectiveCurrent2024_25EmployeeDistricts': 60-len(baseline_missing-new_slugs),
                                  'locatedCurrentEmployeeGapsRemaining': len(baseline_missing-new_slugs),
                                  'remainingScope': 'The25 remaining current district gaps and earlier historical runs are not claimed accepted or complete. Located scan/native processing is not treated as a procurement/FOI blocker. Two additionally retrieved SD10 historical attachments remain discovery-only; no historical observations imported.'},
               'specialChecks': ['All10 complete native originals replay from exact PDF bytes through independent Poppler and MuPDF readers; third-reader/source-context peer receipts pin all15,080 native rows.',
                                 'SD50 actual-PDF-rendered complete image transcript independently checked against both OCR engines and final58rows. Four source dashes are null; missing OCR detection was unresolved until image review.',
                                 'The SD23 Canada Revenue Agency expense-only organization row is excluded from individual observations and retained as a printed aggregate component.',
                                 'All four leading-asterisk source-footnoted SD73 staff are included: three explicit reimbursement notes and one role definition. The literal negative expense−$590 is retained.',
                                 'Low-paid elected official638 is retained; no employee disclosure threshold was applied to trustees.',
                                 'No board adoption motion or visible signature authentication is inferred. Explicit Unaudited labels and all source-control residuals remain literal.'],
               'validation': {'file': str((AREA/'validation.json').relative_to(ROOT)), 'sha256': sha(AREA/'validation.json')},
               'finalPeerSnapshots': json.loads((AREA/'peer-final-snapshots.json').read_text()) if (AREA/'peer-final-snapshots.json').exists() else [],
               'globalFilesChangedByWorker': [], 'oldFrozenFilesChangedByWorker': [], 'branchActions': [], 'institutionContacts': []}
    write(AREA/'handoff.json', handoff)
    paths = set(p for folder in [AREA, COLLECTION] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != 'candidate-freeze.json')
    paths.update(ROOT/'scripts'/name for name in ['finish_salary_schools.py','finish_salary_schools_native.py','finish_salary_schools_scan.py','finish_salary_schools_ocr.py','finish_salary_schools_discover.py','finish_salary_schools_clarifications.py','finish_salary_schools_freeze.py','finish_salary_schools_revisions.py','test_finish_salary_schools.py'])
    paths.update(ROOT/p for p,h in OUTBOX)
    peers = json.loads((AREA/'peer-receipts.json').read_text())
    todo = [ROOT/v['file'] for v in peers.values()]
    if (AREA/'peer-final-snapshots.json').exists():
        todo.extend(linked_files(json.loads((AREA/'peer-final-snapshots.json').read_text())))
    visited = set()
    while todo:
        path = todo.pop()
        if path in visited:
            continue
        visited.add(path)
        paths.add(path)
        if path.suffix == '.json':
            linked = list(linked_files(json.loads(path.read_text())))
            paths.update(linked)
            todo.extend(p for p in linked if p.suffix == '.json' and p not in visited and p.parent != AREA)
    files = [{'path': str(path.relative_to(ROOT)), 'sha256': sha(path)} for path in sorted(paths)]
    frozen = {'frozenOn': '2026-11-01', 'collection': 'queue-completion-schools', 'newSources': 22, 'newRows': 15138,
              'includesOnlyCompleteReviewedScopes': True, 'files': files,
              'excludes': ['this candidate-freeze.json', 'original PDF/model/image caches under/tmp', 'bytecode', 'mutable global registries/generated exports']}
    write(AREA/'candidate-freeze.json', frozen)
    return frozen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = AREA/'candidate-freeze.json'
    if args.check:
        frozen = json.loads(path.read_text())
        for item in frozen['files']:
            assert sha(ROOT/item['path']) == item['sha256'], item['path']
    else:
        if path.exists():
            raise ValueError('Already frozen; use --check')
        frozen = freeze()
    print(json.dumps({'candidateFreezeSha256': sha(path), 'files': len(frozen['files']), 'sources': frozen['newSources'], 'rows': frozen['newRows']}))


if __name__ == '__main__':
    main()
