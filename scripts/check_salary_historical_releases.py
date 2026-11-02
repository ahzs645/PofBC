#!/usr/bin/env python3
"""Rebuild the frozen pre-expansion release in an isolated, verified checkout."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/source-follow-through-2026-11-02'
COMMANDS = [
    ['npm', 'run', 'compare:municipal-periods'],
    ['npm', 'run', 'build:salaries'],
    ['npm', 'run', 'check:salaries'],
    ['npm', 'run', 'audit:municipal-salaries'],
    ['npm', 'run', 'follow-up:municipal-salaries'],
    ['npm', 'run', 'review:sector-salaries'],
    ['npm', 'run', 'review:municipal-wave'],
    ['npm', 'run', 'review:municipal-history'],
    ['npm', 'run', 'review:salary-continuation'],
    ['npm', 'run', 'review:salary-recovery'],
    ['npm', 'run', 'review:salary-held-resolution'],
    ['npm', 'run', 'review:salary-queue-completion'],
    ['npm', 'run', 'review:salary-gap-fill'],
    ['python3', 'scripts/review_name_connection_evidence.py', '--write-reviewed', '--check'],
    ['python3', 'scripts/review_name_connection_continuation.py', '--check'],
    ['python3', 'scripts/assess_salary_name_queue.py', '--check'],
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root, area, target):
    root, target = root.resolve(), target.resolve()
    if root == target or root in target.parents or target in root.parents:
        raise ValueError('Historical replay target must not overlap the live checkout')
    if target.exists() and any(target.iterdir()):
        raise ValueError('Historical replay requires an empty isolated directory')
    target.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(gzip.decompress((area / 'baseline.json.gzip').read_bytes()))
    archive = area / 'baseline-code.tar.gz'
    if sha(archive) != manifest['baselineCodeSha256']:
        raise ValueError('Historical code archive changed')
    with tarfile.open(archive, 'r:gz') as stream:
        # These are our own frozen repository files, nevertheless reject paths/links outside target.
        for member in stream.getmembers():
            path = (target / member.name).resolve()
            if target.resolve() not in path.parents or not member.isfile():
                raise ValueError('Unsafe historical archive member')
        stream.extractall(target, filter='data')
        overrides = {m.name for m in stream.getmembers()}
    for pin in manifest['researchInputs']:
        if root not in (root / pin['path']).resolve().parents or target not in (target / pin['path']).resolve().parents:
            raise ValueError('Unsafe historical input path')
        source = target / pin['path'] if pin['path'] in overrides else root / pin['path']
        if sha(source) != pin['sha256']:
            raise ValueError('Historical input changed: ' + pin['path'])
        destination = target / pin['path']
        if source != destination:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    (target / 'src/government').mkdir(parents=True, exist_ok=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if args.prepare_only and args.out is None:
        parser.error('--prepare-only requires --out to retain the isolated checkout')
    with tempfile.TemporaryDirectory(prefix='salary-historical-') as folder:
        target = args.out.resolve() if args.out else Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        manifest = prepare(ROOT, AREA, target)
        if args.prepare_only:
            print('Prepared frozen release at', target)
            return
        for number, command in enumerate(COMMANDS, 1):
            result = subprocess.run(command, cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if result.returncode:
                raise RuntimeError('Historical command failed: ' + ' '.join(command) + '\n' + result.stdout[-7000:])
            print(f'Historical gate {number}/{len(COMMANDS)} passed: {" ".join(command)}', flush=True)
        expected = {p['path']: p['sha256'] for p in manifest['exportFiles']}
        actual = {str(p.relative_to(target)): sha(p) for p in (target / 'public/salaries').rglob('*') if p.is_file()}
        if actual != expected:
            differences = [p for p in set(actual) | set(expected) if actual.get(p) != expected.get(p)]
            raise ValueError('Historical exports changed: ' + ', '.join(sorted(differences)[:12]))
        for pin in manifest['researchInputs']:
            if sha(target / pin['path']) != pin['sha256']:
                raise ValueError('A historical receipt was rewritten: ' + pin['path'])
        print(f'Historical release reproduced: {len(actual)} byte-identical exports; all {len(COMMANDS)} gates passed')


if __name__ == '__main__':
    main()
