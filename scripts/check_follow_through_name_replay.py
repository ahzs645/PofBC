#!/usr/bin/env python3
"""Replay the immutable name-review generator on its original release context.

Current export reconciliation is independently enforced by the current-preservation
and salary export gates. This wrapper only provides historical generator context;
it never reissues old receipts or changes their validation rules.
"""
import gzip
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from check_salary_current_preservation import ROOT, AREA, BASELINE_SHA256, read, digest, require, observation, inverse_corrections
import review_follow_through_names as review

LINKS_SHA256 = '9dc85ddd0e2ce4d6fb37f169990e0b35cd4d809675d402a7571d4ee40e456d05'


def main():
    require('--check' in sys.argv and '--overlay' not in sys.argv, 'Historical replay is read-only; --check is required')
    raw = (ROOT / AREA / 'baseline.json.gzip').read_bytes()
    require(digest(raw) == BASELINE_SHA256, 'Frozen baseline changed')
    baseline = json.loads(gzip.decompress(raw))
    archive = ROOT / AREA / 'baseline-links.tar.gzip'
    require(digest(archive.read_bytes()) == LINKS_SHA256, 'Original name-link export archive changed')
    index = read(ROOT / 'public/salaries/people/index.json')
    for sid, source in baseline['sourceDefinitions'].items():
        require(index['sources'].get(sid) == source, 'Original source metadata changed')
    corrections = read(ROOT / 'research/salaries/west-vancouver-title-recovery/corrections.json')
    rows = []
    # Keep current dictionary indices: all validators fingerprint decoded strings,
    # not incidental numerical dictionary positions. Filter only approved old IDs.
    for shard in index['shards']:
        rows.extend(row for row in read(ROOT / f'public/salaries/people/{shard}.json.gzip') if row[6] in baseline['sourceDefinitions'])
    decoded = (observation(index['employers'][r[4]][3], index['years'][r[5]], *r[:4], r[6], r[7]) for r in rows)
    restored = inverse_corrections(decoded, corrections)
    for row, old in zip(rows, restored):
        row[0], row[1] = old[2], old[3]
    # Fully consume the generator to enforce its final missing-correction check.
    require(next(restored, None) is None, 'Unexpected inverse observations')
    with tempfile.TemporaryDirectory(prefix='salary-name-replay-') as folder:
        target = Path(folder)
        for name in ('research', 'scripts', 'src'):
            (target / name).symlink_to(ROOT / name, target_is_directory=True)
        people = target / 'public/salaries/people';people.mkdir(parents=True)
        # A single shard is sufficient: unchanged generator/validator iterates
        # every declared shard and recomputes full relevant cohort fingerprints.
        frozen_index = {**index, 'sources': baseline['sourceDefinitions'], 'shards': {'historical': len(rows)}}
        (people / 'index.json').write_text(json.dumps(frozen_index))
        (people / 'historical.json.gzip').write_bytes(gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))
        with tarfile.open(archive, 'r:gz') as stream:
            for member in stream.getmembers():
                require(member.isfile() and member.name.startswith('public/salaries/links/') and target.resolve() in (target/member.name).resolve().parents, 'Unsafe archive entry')
            stream.extractall(target, filter='data')
        review.ROOT = target
        review.OUT = target / 'research/salaries/source-follow-through-2026-11-02'
        review.main()


if __name__ == '__main__':main()
