#!/usr/bin/env python3
"""Bounded additive audit of four canonical money branches and archive/rebase gates.

Uses actual immutable source receipts and adversarial in-memory copies only.
The reviewer-authored batch016 exhaustive branch is explicitly excluded from
independent financial assessment; its separate tests and H/root replay own that.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from unittest import mock

import finish_salary_phsa_ledger as ledger
import finish_salary_phsa_money_peer as money
import finish_salary_phsa_money_supersessions as rebases


ROOT = ledger.ROOT


def pin(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    checks, replays, inputs = [], [], []
    actual_pinned = ledger.pinned

    def check(label, callback, reject=False):
        try:
            callback()
        except (ValueError, AssertionError, KeyError, TypeError, IndexError, FileNotFoundError) as error:
            if not reject:
                raise
            checks.append({'case': label, 'expected': 'reject', 'passed': True,
                           'errorType': type(error).__name__, 'reason': str(error)})
        else:
            checks.append({'case': label, 'expected': 'reject' if reject else 'accept',
                           'passed': not reject})

    def mutation(label, peer, overlay, changes):
        def changed(reference):
            value = copy.deepcopy(actual_pinned(reference))
            for target, operation in changes:
                if reference == target:
                    operation(value)
            return value
        with mock.patch.object(ledger, 'pinned', side_effect=changed):
            check(label, lambda: money.build(peer, overlay), reject=True)

    for number, expected_count in [(22, 6), (23, 53), (25, 42), (26, 36)]:
        path = ledger.AREA / 'triangulation' / f'money-peer-confirmations-{number:03}.json'
        confirmation = json.loads(path.read_text())
        peer = confirmation['peerInputs'][0]
        overlay = confirmation['confirmations'][0]['effectiveAuthorOverlay']
        review = actual_pinned(peer)
        def exact():
            replayed = money.build(peer, overlay)
            assert (json.dumps(replayed, ensure_ascii=False, indent=2) + '\n').encode() == path.read_bytes()
            assert replayed['confirmedMonetaryFields'] == expected_count
        check(path.name + ' exact pinned derivation bytes', exact)
        replays.append({'confirmation': pin(path), 'fields': expected_count,
                        'sourceReceiptSchema': confirmation['sourceReceiptSchema']})
        inputs.extend([peer, overlay])
        mutation(path.name + ' wrong effective source', peer, overlay,
                 [(overlay, lambda doc: doc.update(sourceSha256='0' * 64))])
        field = confirmation['confirmations'][0]
        def omit(doc):
            row = next(r for r in doc['overlays']
                       if (r['physicalPage'], r['sourceRowOnPage']) ==
                       (field['physicalPage'], field['sourceRowOnPage']))
            row['reviewedFields'].remove(field['field'])
        mutation(path.name + ' missing effective requested money field', peer, overlay, [(overlay, omit)])
        if number == 22:
            raw = review['independentImageFirstTranscript']
            packet = review['sourceOnlyPacket']
            def first(doc):
                next(r for r in doc['rows'] if r['field'] != 'name')['literalPreferred'] += 1
            mutation('017 six money actual first literal', peer, overlay, [(raw, first)])
            mutation('017 raw explicitly unfrozen', peer, overlay, [(raw, lambda doc: doc.update(frozen=False))])
            mutation('017 complete mixed31 target shrink', peer, overlay, [(packet, lambda doc: doc['rows'].pop())])
            mutation('017 false independent source pixel evidence', peer, overlay,
                     [(raw, lambda doc: doc['pixelProofRows'][0].update(allOriginal600FieldAnd300NativeContextRgbExact=False))])
        elif number == 23:
            raw = review['freshColdIndependent394']
            packet = actual_pinned(raw)['sourceOnlyPacket']
            mutation('012394 actual cold value differs', peer, overlay,
                     [(raw, lambda doc: doc['rows'][0].update(literalImageValue=99601))])
            mutation('012394 raw explicitly unfrozen', peer, overlay, [(raw, lambda doc: doc.update(frozen=False))])
            mutation('012394 source-only target missing', peer, overlay, [(packet, lambda doc: doc['rows'].clear())])
            mutation('012394 numeric boolean alias', peer, overlay,
                     [(raw, lambda doc: doc['rows'][0].update(literalImageValue=True))])
        elif number == 25:
            raw = review['rootFirstRaw']
            third_ref = review['independentThird13Final']
            third = actual_pinned(third_ref)
            third_raw = third['inputs'][0]
            mutation('014 root actual cold value differs', peer, overlay,
                     [(raw, lambda doc: doc['rows'][0].update(rootFirstImageReading=1))])
            mutation('014 third raw explicitly unfrozen', peer, overlay,
                     [(third_raw, lambda doc: doc.update(frozen=False))])
            def remove97(doc):
                doc['rows'] = [r for r in doc['rows'] if r['sequence'] != 97]
            mutation('014 third raw and final both shrink against unchanged13packet', peer, overlay,
                     [(third_raw, remove97), (third_ref, remove97)])
            def hidden235(doc):
                next(r for r in doc['sourceOnlyOwnCorrections'] if r['sequence'] == 235)['firstVisualValue'] = 1386
            mutation('014 third235 first visual error must remain explicit', peer, overlay,
                     [(third_raw, hidden235)])
        else:
            raw = review['independentImageFirstTranscript']
            choices = review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']
            correction = review['authorPostPeerAdditiveCorrection']
            proof = review['independentSourcePixelProof']
            mutation('01536 peer actual first value differs', peer, overlay,
                     [(raw, lambda doc: doc['rows'][0].update(literalImageValue=1))])
            mutation('01536 author choice exposure before peer release', peer, overlay,
                     [(choices, lambda doc: doc.update(freshPeerChoicesOpened=True))])
            mutation('01536 author189 original first error hidden', peer, overlay,
                     [(correction, lambda doc: doc.update(ownFirstFrozenAndSecondSourceRereadValue=99883))])
            mutation('01536 source whole600 proof false', peer, overlay,
                     [(proof, lambda doc: doc['rows'][0]['checks'].update(whole600=False))])

        # Simulate absent ephemeral workspaces without deleting a pinned cache.
        original_exists = Path.exists
        external = {Path(row['freshSourceImage']['path']) for row in confirmation['confirmations']
                    if Path(row['freshSourceImage']['path']).is_absolute()}
        def no_workspace(path):
            return False if path in external else original_exists(path)
        with mock.patch.object(Path, 'exists', no_workspace):
            for row in confirmation['confirmations']:
                if Path(row['freshSourceImage']['path']) in external:
                    check(path.name + ' archived bytes replay absent workspace ' +
                          str((row['physicalPage'], row['sourceRowOnPage'], row['field'])),
                          lambda reference=row['freshSourceImage']: money.source_image_check(reference))

    # Rebinding an unchanged financial proof must preserve every amount/source.
    sidecars = sorted((ledger.AREA / 'triangulation/confirmation-supersessions').glob('*.json'))
    assert sidecars, 'expected real immutable confirmation revisions'
    path = sidecars[-1]
    selector = json.loads(path.read_text())
    previous_ref = selector['supersededConfirmation']
    previous = actual_pinned(previous_ref)
    ordinary_ref = selector['ordinaryOverlaySupersession']
    old_overlay = actual_pinned(ordinary_ref)['supersededOverlay']
    check('actual unchanged-money revision selector validates', lambda: rebases.validate(selector))
    def wrong_money():
        doc = copy.deepcopy(previous)
        next(row for row in doc['confirmations']
             if row['effectiveAuthorOverlay'] == old_overlay)['confirmedValue'] += 1
        return rebases.rebase(previous_ref, ordinary_ref, lambda reference: doc)
    check('unchanged-money rebase rejects a changed original confirmed amount', wrong_money, reject=True)

    code = ['finish_salary_phsa_money_peer.py', 'finish_salary_phsa_money_canonical.py',
            'finish_salary_phsa_money_standard.py', 'finish_salary_phsa_money_supersessions.py',
            'finish_salary_phsa_triangulation.py', 'test_finish_salary_phsa.py']
    return {'frozen': True, 'reviewedOn': '2026-11-02', 'reviewer': '/root/recovery_review',
            'scope': 'Additive technical audit of canonical0176,01253/394,01442,01536, exact source archive fallback and one actual unchanged-money rebase. No source-data acceptance.',
            'script': pin(Path(__file__).resolve()),
            'codePins': [pin(ROOT / 'scripts' / name) for name in code],
            'earlierAuditsRemainImmutable': [pin(ledger.REVIEWS / 'independent-phsa-history-batches-canonical-promoter-code-review-002-real-closures.json')],
            'actualMoneyDerivationReplays': replays, 'moneyEvidenceInputs': inputs,
            'checks': checks, 'checkCount': len(checks),
            'failedCases': sum(not case['passed'] for case in checks),
            'initialConcreteFindings': ['014 helper initially accepted an explicitly unfrozen third raw and consistent shrinking of raw/final13 against unchanged source-only13 target packet.',
                                        '012394 helper initially accepted an explicitly unfrozen fresh source-first raw.'],
            'authoredProducerExcluded': {'path': 'scripts/finish_salary_phsa_money_exhaustive.py',
                                        'independentFinancialAssessment': False,
                                        'independentAssessmentOwner': '/root/held_health_review and /root',
                                        'implementationVerificationOnly': 'Actual281positive+1dash replay,44author/4frozenpeer errors;13 original-fixture mutations and health dedicated actual-source regression set separately reported.'},
            'limits': ['Technical code/mutation tests are not another human source transcription or source semantic acceptance.',
                       'Only named implementation pins and exact frozen input receipts are covered; later versions need their own bounded review.',
                       'All mutations and missing-workspace simulations are in memory; no source/review/overlay/archive bytes changed.',
                       'Final nine-source independent provenance/control closure and explicit root promotion remain separate. All four issuer requests remain user-held; no outreach.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = run()
    # Never freeze a successful-sounding artifact while a meaningful negative
    # case is still accepted by the implementation under review.
    if result['failedCases']:
        print(json.dumps({'failedCases': result['failedCases'],
                          'failures': [c for c in result['checks'] if not c['passed']]}))
        raise SystemExit(1)
    path = ROOT / args.out
    with path.open('x') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'receipt': pin(path), 'checks': result['checkCount'], 'failedCases': 0}))
