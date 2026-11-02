#!/usr/bin/env python3
"""Freeze the exact nine held candidates and their independent review inputs.

The later root adoption, active manifest and global integration freeze are
deliberately outside this worker snapshot, so no hash dependency is circular.
"""
import argparse
import gzip
import json
from functools import lru_cache
from pathlib import Path

import finish_salary_phsa_ledger as ledger


ROOT, AREA, COLLECTION = ledger.ROOT, ledger.AREA, ledger.COLLECTION
OUTPUT = AREA/'candidate-freeze.json'
HANDOFF = AREA/'handoff-final.json'
EXCLUDED = {OUTPUT, COLLECTION/'sources.json', ROOT/'research/salaries/collections.json',
            AREA.parent/'parent-acceptance.json'}
TECHNICAL_REVIEWS = [
    ('independent-phsa-history-batches-canonical-money-gates-audit-v3.json','cc2ba3db174e1d30523f7fc43791634771544707e525e72ed4f37be402c0dd1d'),
    ('independent-phsa-history-batches-money-rebase-v2-bounded-audit-addendum.json','6a1b1679c3216144591b7f52e823613d6ebaa315f088f700b0c3c5cd4614a843'),
    ('independent-phsa-history-batches-money023-pointer-correction-bounded-audit-addendum.json','d9d7cece15f1df8ba6418bf5dffc4aa2f196d6c409e37b6dd4f4f245d7ffb25f'),
    ('independent-phsa-history-batches-current-money-v7-code-peer-review.json','abcec5bc55cec7d2aa55bb1b4830342931bcf7e4dd144d08d2fea0ca8744f62e'),
]


def save_new(path, document):
    raw=(json.dumps(document,ensure_ascii=False,indent=2)+'\n').encode()
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Never overwrite a frozen PHSA handoff')
    else:path.write_bytes(raw)
    return ledger.pin(path)


def excluded(path):
    return path in EXCLUDED or path.is_relative_to(AREA.parent/'integration')


@lru_cache(maxsize=None)
def repository_file(raw):
    path=(ROOT/raw).resolve()
    return path if path.is_relative_to(ROOT)and path.is_file()and not excluded(path)else None


@lru_cache(maxsize=None)
def dependency_file(raw,digest):
    path=repository_file(raw)
    if path is not None and not raw.startswith('scripts/')and ledger.sha(path.read_bytes())!=digest:
        raise ValueError('Frozen PHSA dependency changed: '+raw)
    # Historical audits explicitly describe earlier code hashes at the same
    # script path. Preserve those audit bytes and freeze the current code bytes;
    # current source/producer/code-peer checks are separately pinned above.
    return path


def linked_files(value):
    if isinstance(value,dict):
        if 'path'in value and 'sha256'in value:
            raw=value['path']
            if isinstance(raw,str)and raw.startswith(('research/salaries/','scripts/'))and not Path(raw).is_absolute():
                path=dependency_file(raw,value['sha256'])
                # Withdrawn metadata can retain an expressly corrected former
                # filename. Current required inputs are checked separately.
                if path is not None:yield path
        for child in value.values():yield from linked_files(child)
    elif isinstance(value,list):
        for child in value:yield from linked_files(child)
    elif isinstance(value,str)and len(value)<2048 and value.startswith(('research/salaries/','scripts/')):
        path=repository_file(value)
        if path is not None:yield path


def freeze(review_paths):
    inventory={s['id']:s for s in json.loads((AREA/'source-inventory.json').read_text())['sources']}
    peers={};selected=[]
    for raw in review_paths:
        reference=ledger.pin((ROOT/raw).resolve());peer=ledger.pinned(reference);source=peer['sourceId']
        if source not in inventory or source in peers:raise ValueError('Exactly nine unique original source closures are required')
        if peer['frozen']is not True:raise ValueError('Independent source closure must be frozen')
        _check_bytes(peer['script'])
        revision=3 if source in ['phsa-2017-18','phsa-2023-24']else 4
        expected=AREA/'candidates'/f'{source}-source-v{revision}.json'
        if peer['candidateMetadata']!=ledger.pin(expected):raise ValueError('Independent closure does not select the explicit final revision')
        candidate=ledger.pinned(peer['candidateMetadata']);spec=inventory[source]
        if (peer['sourceSha256']!=spec['sourceSha256']or candidate['sha256']!=spec['sourceSha256']
                or peer['checkedLiteralNamedRows']!=candidate['rowCount']or peer['checkedCompletePhysicalPages']!=spec['pdfPages']
                or peer['payload']['sha256']!=candidate['dataSha256']or peer['provenance']['sha256']!=candidate['provenanceSha256']
                or peer['payload']['path']!=str((COLLECTION/candidate['file']).relative_to(ROOT))
                or peer['provenance']['path']!=str((COLLECTION/candidate['provenanceFile']).relative_to(ROOT))
                or peer['literalSourceControlResiduals']!=candidate['validation']['sourceControlResiduals']):
            raise ValueError('Independent closure/source/payload/control scope differs')
        for flag in ['independentRawPlusOnlyExactPinnedOverlayReconstructionEqualsPayload',
                     'allOriginalRowOrderMultiplicityAndNonreviewedFieldsPreserved','everyFieldHasExactlyOneClosedEvidenceRoute']:
            if peer[flag]is not True:raise ValueError('Independent final source replay is incomplete')
        _check_bytes(peer['payload']);_check_bytes(peer['provenance'])
        provenance=json.loads(gzip.decompress((ROOT/peer['provenance']['path']).read_bytes()))
        body=provenance['originalRowsAndPerFieldResolution']
        if body['pendingFields']or body['completePhysicalSource']is not True:raise ValueError('Pending source fields cannot be frozen')
        canonical=peer['canonicalSourceDecisionAndHumanRecordReplay']['closure'];closure=ledger.pinned(canonical)
        if (closure['sourceId'],closure['sourceSha256'],closure['accepted'],closure['closed'],closure['unresolved'])!=(source,spec['sourceSha256'],True,True,[]):
            raise ValueError('Canonical human source closure remains open')
        peers[source]=reference
        selected.append({'sourceId':source,'candidateRevision':revision,'finalCandidate':peer['candidateMetadata'],
                         'independentSourceClosure':reference,'canonicalSourceClosure':canonical,
                         'rows':candidate['rowCount'],'qualifiedNames':len(body['rootAdoptedQualifiedNameCases']),
                         'literalControlResiduals':body['diagnosticControlResiduals']})
    if set(peers)!=set(inventory):raise ValueError('All nine source closures are required together')
    selected.sort(key=lambda row:row['sourceId'])
    if sum(s['rows']for s in selected)!=64912:raise ValueError('Complete original salary row count differs')
    validation=AREA/'validation.json'
    if ledger.pinned(ledger.pin(validation))['allChecksPassed']is not True:raise ValueError('Final worker validation is incomplete')
    canonical_validation=AREA/'canonical-promotion-validation.json'
    if ledger.pinned(ledger.pin(canonical_validation))['allChecksPassed']is not True:raise ValueError('Canonical promotion checks are incomplete')
    technical=[]
    for filename,digest in TECHNICAL_REVIEWS:
        reference={'path':str((ledger.REVIEWS/filename).relative_to(ROOT)),'sha256':digest}
        ledger.pinned(reference);technical.append(reference)
    final_index={'path':str((ledger.REVIEWS/'independent-phsa-history-all-nine-final-canonical-v7-replay-index.json').relative_to(ROOT)),
                 'sha256':'d5ce9b6f5092ab8108a686896e76ff5a6c9d2c5f62ad3ee1b9b9ed5abc683d6a'}
    index=ledger.pinned(final_index)
    if {s['sourceId']:s['independentSourceClosure']for s in index['sources']}!=peers:
        raise ValueError('The final combined independent review index differs from the nine source closures')
    handoff={'frozenOn':'2026-11-02','collection':'queue-completion-phsa','sources':selected,'newSources':9,'newRows':64912,
             'allOriginalPhysicalPages':1480,'allOriginalSalaryPages':1474,'allPendingFields':0,
             'validation':ledger.pin(validation),'canonicalPromotionValidation':ledger.pin(canonical_validation),
             'allNineFinalIndependentReplayIndex':final_index,
             'finalTechnicalPeerReceipts':technical,
             'compiledReplacementAuthority':'Root exact scope adoption only; worker retains compiled partitions.',
             'financialQualification':'Literal residuals remain +31/+28 for 2015/16, 0/-5 for 2016/17, and +5,220/0 for 2019/20; the other six schedules reconcile. No balancing or invented cause.',
             'outreachSent':False,'sourceAndOldFrozenArtifactsRemainUnchanged':True,
             'acceptanceLimit':'Held complete candidates and independent source closures. Later explicit root acceptance and active collection promotion are separate.'}
    save_new(HANDOFF,handoff)
    paths={p.resolve()for folder in [AREA,COLLECTION]for p in folder.rglob('*')
           if p.is_file()and not excluded(p.resolve())and '__pycache__'not in p.parts and p.suffix!='.pyc'}
    paths.update(p.resolve()for p in (ROOT/'scripts').glob('finish_salary_phsa*.py'))
    paths.update(p.resolve()for p in (ROOT/'scripts').glob('test*phsa*.py'))
    # Archive all worker artifacts as historical bytes. Follow and validate
    # dependency claims only from selected final reviews, rather than treating
    # a withdrawn draft's superseded metadata as current authority.
    todo=[p.resolve()for p in [HANDOFF,validation]+[ROOT/ref['path']for ref in peers.values()]]
    visited=set();queued=set(todo)
    while todo:
        path=todo.pop()
        if path in visited or excluded(path):continue
        visited.add(path);paths.add(path)
        try:
            if path.suffix=='.json':document=json.loads(path.read_text())
            elif path.name.endswith('.json.gzip'):document=json.loads(gzip.decompress(path.read_bytes()))
            else:continue
        except json.JSONDecodeError:
            # Historical capture/log bytes can contain multiple JSON events.
            # Pin the opaque original without promoting it to a current review.
            continue
        for dependency in linked_files(document):
            if dependency not in queued:
                queued.add(dependency);todo.append(dependency)
    files=[ledger.pin(p)for p in sorted(paths)]
    result={'frozenOn':'2026-11-02','collection':'queue-completion-phsa','newSources':9,'newRows':64912,
            'includesOnlyCompleteReviewedScopes':True,'selectedSources':selected,'files':files,
            'excludes':['This freeze itself','Later active collection sources.json','Global registries and parent integration/release acceptance artifacts',
                        'Original PDF/model/full-page caches outside the repository','Bytecode and temporary reviewer directories']}
    save_new(OUTPUT,result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--independent-review',action='append',default=[]);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        result=json.loads(OUTPUT.read_text())
        for entry in result['files']:_check_bytes(entry)
    else:
        if OUTPUT.exists():raise ValueError('Already frozen; use --check')
        result=freeze(args.independent_review)
    print(json.dumps({'candidateFreeze':ledger.pin(OUTPUT),'files':len(result['files']),'sources':9,'rows':64912}))


def _check_bytes(reference):
    path=ROOT/reference['path']
    if not path.resolve().is_relative_to(ROOT)or ledger.sha(path.read_bytes())!=reference['sha256']:
        raise ValueError('Frozen PHSA bytes changed: '+reference['path'])


if __name__=='__main__':main()
