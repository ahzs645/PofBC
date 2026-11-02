#!/usr/bin/env python3
"""Correct only the documented53-peer transcript-pointer metadata defect."""
import copy
import finish_salary_phsa_ledger as ledger

ORIGINAL={'path':'research/salaries/queue-completion-2026-11-01/phsa/triangulation/money-peer-confirmations-023.json',
          'sha256':'34fd632d9beca3d6c5c13860dfe723ac85c6c3709d8513eed667fb8696dc542c'}


def build(previous_reference,read_previous=None):
    if previous_reference!=ORIGINAL:raise ValueError('Unknown source-first pointer correction')
    if read_previous is None:
        from finish_salary_phsa_triangulation import verified_confirmation
        read_previous=verified_confirmation
    previous=read_previous(previous_reference)
    review=ledger.pinned(previous['peerInputs'][0]);original_ref=review['originalRootFirstRaw'];fresh_ref=review['freshColdIndependent394']
    original=ledger.pinned(original_ref);fresh=ledger.pinned(fresh_ref)
    identity=lambda row:(row['physicalPage'],row['sourceRowOnPage'],row['field'])
    roots={identity(row):row for row in original['rows']};cold={identity(row):row for row in fresh['rows']}
    targets={identity(row):row for row in review['rows']}
    if (len(roots)!=53 or len(roots)!=len(original['rows'])or set(roots)!=set(targets)
            or set(cold)!={(88,13,'remuneration')}or len(fresh['rows'])!=1
            or original['frozen']is not True or fresh['frozen']is not True
            or original['candidateOrAuthorValuesOpened']is not False or fresh['correspondingAuthorOrPeerAmountsOpened']is not False
            or original['sourceId']!=fresh['sourceId']or original['sourceSha256']!=fresh['sourceSha256']):
        raise ValueError('Source-first pointer correction lacks complete root53/singlecold394 inputs')
    result=copy.deepcopy(previous);changed=0
    for row in result['confirmations']:
        key=identity(row)
        if (key not in roots or row['sourceId']!=original['sourceId']or row['sourceSha256']!=original['sourceSha256']
                or row['imageFirstTranscript']!=fresh_ref):
            raise ValueError('Original documented pointer defect differs from its exact53 source scope')
        current=targets[key]
        if roots[key]['rootFirstImageReading']!=current['rootFirstImageReading']:
            raise ValueError('Root source-first pointer would hide an original literal reading')
        if key in cold:
            if cold[key]['literalImageValue']!=row['confirmedValue']:raise ValueError('Cold394 first literal differs')
            row['imageFirstTranscript']=fresh_ref
        else:row['imageFirstTranscript']=original_ref;changed+=1
    if changed!=52 or len(result['confirmations'])!=53:raise ValueError('Source-first pointer correction widens/removes fields')
    result['adapter']='source-first-provenance-correction-v1'
    result['supersededAdapter']=previous['adapter'];result['previousConfirmationLedger']=previous_reference
    result['sourceFirstPointerCorrections']=changed
    result['originalRoot53FirstTranscript']=original_ref;result['independentCold394FirstTranscript']=fresh_ref
    result['peerInputs']=previous['peerInputs']+[previous_reference]
    result['provenanceCorrectionReason']='Only52 misleading imageFirstTranscript pointers are corrected to the actual original root53 raw. Field394 retains its genuine independent cold-one-field raw. All53 values, original reading errors, scope, source images and effective overlays remain identical.'
    return result
