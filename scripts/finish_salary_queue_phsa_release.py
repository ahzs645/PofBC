#!/usr/bin/env python3
"""Apply the exact compiled-partition metadata qualification to nine PHSA sources.

The frozen promoter/candidates and every salary/provenance byte remain inputs.
Default preview and --check never write. Only the explicit --write action may
replace the active manifest, after the immutable archive/adoption validate.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

import finish_salary_phsa_promote as promoter


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATH = 'research/salaries/queue-completion-phsa/sources.json'
ARCHIVE_PATH = 'research/salaries/queue-completion-2026-11-01/integration/phsa-base-promoted-sources.json'
ADOPTION_PATH = 'research/salaries/queue-completion-2026-11-01/integration/phsa-release-metadata-adoption.json'
BASE_ROOT_ACCEPTANCE = {
    'path': 'research/salaries/queue-completion-2026-11-01/reviews/root-phsa-history-all-nine-source-acceptance.json',
    'sha256': '89272a31d2898741efbced563cf577788f8537170a1279096813c1c13b7cf447',
}
BASE_MANIFEST_SHA = 'c510c1375723288e174f2ea28232a7f4ba460cf491d73c168b4e9af6d2f04e8a'
FROZEN_PROMOTER = {
    'path': 'scripts/finish_salary_phsa_promote.py',
    'sha256': 'cc68a5e0ee7799e5024da401d4c3e11307071ff283e311e4ca623d0cd62ffc70',
}
RETENTION_REASON = (
    'Complete-copy equivalence with the existing compiled partition has not been proved; '
    'the compiled observations are retained without assuming identity or reporting-period equivalence.'
)
WARNING_APPEND = (
    'Existing compiled observations are retained and may overlap this official schedule; '
    'no identity or reporting-period equivalence is assumed.'
)


def packed(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _root_reference(reference):
    if reference is None:
        #One explicit immutable selection, never a latest-file search.
        reference = json.loads((ROOT / ADOPTION_PATH).read_bytes())['baseRootAcceptance']
    _require(type(reference) is dict and reference == BASE_ROOT_ACCEPTANCE,
             'Release requires the exact pinned base all-nine root acceptance')
    _require(sha((ROOT / reference['path']).read_bytes()) == reference['sha256'],
             'Base root acceptance bytes changed')
    return copy.deepcopy(reference)


def _metadata_only(base, release):
    """Inverse ONLY the three permitted fields; every other byte must replay."""
    _require(isinstance(base, dict) and isinstance(release, dict), 'Manifest must be an object')
    _require(type(base.get('sources')) is list and len(base['sources']) == 9
             and type(release.get('sources')) is list and len(release['sources']) == 9,
             'Release must contain exactly the nine base sources')
    ids = [s['id'] for s in base['sources']]
    _require(len(set(ids)) == 9 and [s['id'] for s in release['sources']] == ids,
             'Release source identities/order differ')
    restored = copy.deepcopy(release)
    changes = []
    for index, (before, after, undo) in enumerate(zip(base['sources'], release['sources'], restored['sources'])):
        _require(before['status'] == after['status'] == 'verified'
                 and before['retainCompiledPartition'] is True and after['retainCompiledPartition'] is True,
                 'Only the verified retained base partitions may receive metadata qualification')
        old_validation, new_validation = before['validation'], after['validation']
        _require(type(old_validation) is dict and type(new_validation) is dict,
                 'Source validation must be an object')
        for field, wanted in [('compiledPartitionRetained', True),
                              ('compiledPartitionRetentionReason', RETENTION_REASON)]:
            _require(field not in old_validation, 'Base unexpectedly contains release-only retention guards')
            _require(field in new_validation and type(new_validation[field]) is type(wanted)
                     and new_validation[field] == wanted, 'Exact compiled-partition guard differs')
            changes.append({'sourceId': before['id'], 'path': f'/sources/{index}/validation/{field}',
                            'before': {'present': False},
                            'after': {'present': True, 'value': new_validation[field]}})
            del undo['validation'][field]
        warning = before['publicWarning']
        _require(type(warning) is str and warning.strip()
                 and type(after['publicWarning']) is str
                 and after['publicWarning'] == warning + ' ' + WARNING_APPEND,
                 'Existing public warning must be preserved and receive exactly the retention append')
        changes.append({'sourceId': before['id'], 'path': f'/sources/{index}/publicWarning',
                        'before': {'present': True, 'value': warning},
                        'after': {'present': True, 'value': after['publicWarning']}})
        undo['publicWarning'] = warning
    _require(packed(restored) == packed(base),
             'Release changed a field outside the exact 27 permitted metadata paths')
    _require(len(changes) == 27 and len({c['path'] for c in changes}) == 27,
             'Release must declare exactly 27 distinct metadata changes')
    return changes


def _make_release(base):
    result = copy.deepcopy(base)
    for source in result['sources']:
        source['validation']['compiledPartitionRetained'] = True
        source['validation']['compiledPartitionRetentionReason'] = RETENTION_REASON
        source['publicWarning'] += ' ' + WARNING_APPEND
    return result


def _expected_adoption(reference, base, release, changes):
    return {
        'schema': 'queue-phsa-release-metadata-adoption-v1',
        'frozen': True,
        'reviewedOn': '2026-11-02',
        'metadataOnly': True,
        'baseRootAcceptance': reference,
        'frozenPromoter': FROZEN_PROMOTER,
        'baseManifest': {'path': ACTIVE_PATH, 'sha256': BASE_MANIFEST_SHA},
        'baseManifestArchive': {'path': ARCHIVE_PATH, 'sha256': BASE_MANIFEST_SHA},
        'releaseManifestPath': ACTIVE_PATH,
        'releaseManifestSHA': sha(packed(release)),
        'sourceCount': 9,
        'changedFieldCount': 27,
        'changes': changes,
        'decision': (
            'Retain the existing compiled observations because complete-copy equivalence has not been proved. '
            'Add only the two explicit validation retention guards and the public overlap/identity/period '
            'qualification to each of the nine already verified official source entries.'
        ),
        'preserved': (
            'All salary data and provenance files/bytes/hashes, source identities, reporting periods/years, '
            'definitions, original root/peer pins, source control amounts, existing warnings and all other '
            'manifest metadata are unchanged. No identity or reporting-period equivalence is inferred.'
        ),
    }


def prepare(root_reference):
    """Pure proposal for staging the two new immutable review inputs; no writes."""
    reference = _root_reference(root_reference)
    _require(sha(Path(promoter.__file__).read_bytes()) == FROZEN_PROMOTER['sha256'],
             'Frozen promoter implementation changed')
    base = promoter.build(reference)
    base_raw = packed(base)
    _require(sha(base_raw) == BASE_MANIFEST_SHA, 'Frozen promoter no longer reproduces the exact base manifest')
    release = _make_release(base)
    changes = _metadata_only(base, release)
    adoption = _expected_adoption(reference, base, release, changes)
    return base_raw, release, adoption


def _current_allowed(base_raw, release_raw):
    current = (ROOT / ACTIVE_PATH).read_bytes()
    _require(current == base_raw or current == release_raw,
             'Active manifest is neither the exact frozen base nor the exact adopted release')
    return current


def build(root_reference=None):
    """Replay the frozen promoter and validate both immutable release inputs."""
    base_raw, release, expected_adoption = prepare(root_reference)
    archive_raw = (ROOT / ARCHIVE_PATH).read_bytes()
    _require(archive_raw == base_raw and sha(archive_raw) == BASE_MANIFEST_SHA,
             'Base archive does not replay the exact frozen promoted bytes')
    adoption_raw = (ROOT / ADOPTION_PATH).read_bytes()
    adoption = json.loads(adoption_raw)
    #Canonical exact bytes reject extra keys, reordered/duplicate/hidden changes,
    #present-null substitutions, and JSON bool/int equality ambiguities.
    _require(type(adoption) is dict and adoption_raw == packed(expected_adoption),
             'Metadata adoption is not the exact generated 27-field before/after decision')
    _current_allowed(base_raw, packed(release))
    return release


def _atomic_release(raw):
    target = ROOT / ACTIVE_PATH
    mode = stat.S_IMODE(target.stat().st_mode)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.phsa-release-', dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run(root_reference=None, *, write=False, check=False):
    _require(type(write) is bool and type(check) is bool and not (write and check),
             'Choose only one explicit write/check action')
    guarded_inputs = ({path: (ROOT / path).read_bytes() for path in [ARCHIVE_PATH, ADOPTION_PATH]}
                      if write else None)
    release = build(root_reference)
    raw = packed(release)
    if check:
        _require((ROOT / ACTIVE_PATH).read_bytes() == raw, 'Active PHSA release metadata does not replay')
    elif write:
        #Recheck immediately before an atomic replace; never overwrite another state.
        _require(all((ROOT / path).read_bytes() == previous for path, previous in guarded_inputs.items())
                 and sha(guarded_inputs[ARCHIVE_PATH]) == BASE_MANIFEST_SHA,
                 'Immutable release inputs changed during validation')
        current = _current_allowed(guarded_inputs[ARCHIVE_PATH], raw)
        if current != raw:
            _atomic_release(raw)
    return {
        'previewOnly': not write and not check,
        'activeManifest': {'path': ACTIVE_PATH, 'sha256': sha((ROOT / ACTIVE_PATH).read_bytes())},
        'baseManifestArchive': {'path': ARCHIVE_PATH, 'sha256': BASE_MANIFEST_SHA},
        'metadataAdoption': {'path': ADOPTION_PATH, 'sha256': sha((ROOT / ADOPTION_PATH).read_bytes())},
        'releaseManifestSHA': sha(raw),
        'sources': len(release['sources']),
        'changedMetadataFields': 27,
        'rows': sum(source['rowCount'] for source in release['sources']),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-adoption', help='PATH=SHA; omitted only by the exact baseRootAcceptance in the adoption artifact')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--write', action='store_true', help='ROOT ONLY after review: atomically write the exact adopted active metadata')
    action.add_argument('--check', action='store_true', help='Read-only replay of the exact already-written release')
    args = parser.parse_args(argv)
    reference = None
    if args.root_adoption is not None:
        try:
            path, digest = args.root_adoption.rsplit('=', 1)
        except ValueError:
            parser.error('--root-adoption must be PATH=SHA')
        reference = {'path': path, 'sha256': digest}
    result = run(reference, write=args.write, check=args.check)
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == '__main__':
    main()
