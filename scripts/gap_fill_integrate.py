#!/usr/bin/env python3
"""Assemble the exact accepted nine-collection and65-lead integration decisions."""
import copy
import hashlib
import json
from pathlib import Path

from review_salary_gap_fill import freeze_entries, verify_dispositions

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02'
ENTRIES = [
    ('school_native', 'gap-fill-school-native', 'manifest', 'candidateFreeze'),
    ('school_north', 'gap-fill-school-north', 'sourceManifest', 'producerFreeze'),
    ('school_south', 'gap-fill-school-south', 'normalizedManifest', 'producerFreeze'),
    ('municipal', 'gap-fill-municipal', 'acceptedManifest', 'producerFreeze'),
    ('health_employees', 'gap-fill-health-employees', 'manifest', 'freeze'),
    ('health_boards', 'gap-fill-health-boards', 'manifest', 'freeze'),
    ('health_board_supplement', 'gap-fill-health-board-supplement', 'manifest', 'ownedFreeze'),
    ('health_other_history', 'gap-fill-health-other-history', 'manifest', 'freeze'),
    ('phsa_history', 'gap-fill-phsa-history', 'manifest', 'freeze'),
]


def read(path):
    return json.loads(path.read_bytes())


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def norm(reference):
    relative = reference.get('path') or reference['file']
    digest = reference.get('sha256')
    if digest is None:
        assert relative == 'research/salaries/gap-fill-2026-11-02/phsa_history/producer-freeze.json'
        digest = '90a23179ac4cb8c0d528f6a4872985c9a059a5948270dd8a14e423563cbb4fdc'
    return {'path': relative, 'sha256': digest}


def checked(reference):
    path = ROOT / reference['path']
    assert ref(path)['sha256'] == reference['sha256']
    return read(path)


def write(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    handoffs, manifests, freezes, catalog, reports = [], [], [], {}, []
    for area, collection, manifest_key, freeze_key in ENTRIES:
        hp = BASE / area / ('handoff-final.json' if area == 'municipal' else 'handoff.json')
        handoff = read(hp)
        mr, fr = norm(handoff[manifest_key]), norm(handoff[freeze_key])
        manifest, frozen = checked(mr), checked(fr)
        for entry in freeze_entries(frozen):
            path = ROOT / (entry.get('path') or entry['file'])
            assert ref(path)['sha256'] == entry['sha256'], str(path)
        for source in manifest['sources']:
            assert source['status'] in ['accepted', 'verified']
            assert source['id'] not in catalog and source['sourceKind'].startswith('official')
            parent = (ROOT / mr['path']).parent
            for key, digest in [('file', 'dataSha256'), ('provenanceFile', 'provenanceSha256')]:
                assert ref(parent / source[key])['sha256'] == source[digest]
            catalog[source['id']] = {'source': source, 'collection': collection, 'manifest': mr, 'parent': parent}
        handoffs.append(ref(hp)); manifests.append(mr); freezes.append(fr)
        reports.append({'collection': collection, 'cohorts': len(manifest['sources']),
                        'rows': sum(s['rowCount'] for s in manifest['sources'])})
    assert len(catalog) == 227 and sum(v['source']['rowCount'] for v in catalog.values()) == 259336
    draft_path = BASE / 'reviews/integration-north/draft-consolidated-65-leads.json'
    assert ref(draft_path)['sha256'] == '750256cd027f66409454166f2df51e9740a8324b8f3de450c1f5ada2ad56492e'
    ledger = copy.deepcopy(read(draft_path))
    phsa = read(BASE / 'phsa_history/handoff.json')
    new_ids = []
    for ident, item in catalog.items():
        if item['collection'] != 'gap-fill-phsa-history':
            continue
        source, parent = item['source'], item['parent']
        new_ids.append(ident)
        value = {'sourceId': ident, 'collection': item['collection'], 'manifest': item['manifest'],
                 'employerSlug': source['employerSlug'], 'reportingPeriod': source['year'],
                 'scope': source['scope'], 'rowCount': source['rowCount'], 'sourceUrl': source['sourceUrl'],
                 'sourceSha256': source['sha256'], 'status': source['status'],
                 'data': ref(parent / source['file']), 'provenance': ref(parent / source['provenanceFile']),
                 'fullSourceDefinitionInPinnedManifest': True}
        for key in ['periodType', 'periodStart', 'periodEnd', 'sourceKind', 'scopeDescription',
                    'completeEmployeeSchedule', 'retainCompiledPartition', 'publicWarning',
                    'nameDisclosure', 'positionDisclosure', 'notes']:
            value[key] = source.get(key)
        value['sourceQualifications'] = source['validation']
        ledger['acceptedSourceCatalog'][ident] = value
    row = next(r for r in ledger['records'] if r['leadId'] == 'lead-034')
    row.update(disposition='located-nine-employee-originals-accepted-and-integrated',
               remainingPublicProcessingTasks=0, pendingPublicProcessing=[], acceptedSourceIds=new_ids,
               acceptedRowsReferencedMayOverlapOtherLeads=22796,
               currentFinding='All nine located official employee histories2006/07–2014/15 are accepted after complete source processing, bounded independent image reviews and root normalized adoption. All22,796 actual payment observations are retained; source residuals and the2009narrative/2010salary-period conflict remain explicit.',
               nextAction='No public extraction task remains for these located originals. Revisit source-specific clarifications only if corrected originals or issuer explanations appear; no outreach is authorized.')
    row['supplementalClosures'].append({
        'kind': 'complete-nine-source-PHSA-history-release', 'status': 'accepted-verified-and-frozen',
        'handoff': ref(BASE / 'phsa_history/handoff.json'), 'manifest': norm(phsa['manifest']),
        'rootSourceAcceptance': phsa['rootSourceAcceptance'], 'producerFreeze': norm(phsa['freeze']),
        'sourceVerification': phsa['sourceVerification'], 'leadDispositions': phsa['leadDispositions'],
        'acceptedSourceIds': new_ids, 'acceptedRows': 22796, 'sourceClarifications': phsa['sourceClarifications'],
        'remainingPublicProcessingTasks': 0, 'noOutreach': True})
    row['acceptedScopesByPeriod'] = [{'sourceId': i, 'period': catalog[i]['source']['year'],
                                    'scope': catalog[i]['source']['scope'], 'rowCount': catalog[i]['source']['rowCount']}
                                   for i in new_ids]
    row['publicQualifications'] = [{'sourceId': i, 'publicWarning': catalog[i]['source']['publicWarning'],
                                    'completeEmployeeSchedule': True, 'nameDisclosure': None} for i in new_ids]
    ledger.update(schema='salary-gap-fill-consolidated-65-leads-v1',
                  status='Complete bounded public-source processing; accepted observations integrated and genuine acquisition/clarification gaps documented',
                  draft=False, complete=True, workerHandoffs=handoffs, acceptedCollectionManifests=manifests,
                  acceptedInputCohorts=227, acceptedNumericPayRows=259336, remainingPublicProcessingTasks=0,
                  remainingPublicProcessingByLead=[], pendingSupplementalHandoffs=[],
                  allLocatedPublicProcessingComplete=True, sourceDraft=ref(draft_path),
                  finalGateState='All65 exact original lead IDs/owners have substantive outcomes; zero unfinished located-public-source processing tasks. Acquisition and source qualifications are documented without unauthorized outreach.')
    for key in ['acceptedCollectionManifestsExcludingPendingPhsa', 'acceptedInputCohortsReadyForIntegrationExcludingPhsa',
                'acceptedNumericPayRowsReadyForIntegrationExcludingPhsa', 'rootPromotionRequired',
                'allOtherLocatedPublicProcessingComplete']:
        ledger.pop(key, None)
    verify_dispositions(read(BASE / 'input-leads.json'), ledger)
    assert len(ledger['acceptedSourceCatalog']) == 227
    write(BASE / 'lead-dispositions.json', ledger)
    inputs = {'acceptedSourceInputs': True, 'approvedBy': 'root', 'noOutreach': True,
              'collections': [r[1] for r in ENTRIES], 'manifests': manifests, 'workerHandoffs': handoffs,
              'producerFreezes': freezes, 'collectionTotals': reports, 'cohorts': 227, 'rows': 259336,
              'leadDispositions': ref(BASE / 'lead-dispositions.json'),
              'scope': 'All nine independently reviewed and frozen collections; final app reconciliation/root freeze remains the release gate.',
              'integrationCode': ref(Path(__file__))}
    write(BASE / 'integration-inputs.json', inputs)
    archived = read(BASE / 'baseline-collections.json')
    registry = ROOT / 'research/salaries/collections.json'
    assert read(registry) == {**archived, 'collections': archived['collections'] + [r[1] for r in ENTRIES[:7]]}
    registry.write_text(json.dumps({**archived, 'collections': archived['collections'] + inputs['collections']}, indent=2) + '\n')
    print(json.dumps({'collections': reports, 'ledger': ref(BASE / 'lead-dispositions.json'),
                      'integrationInputs': ref(BASE / 'integration-inputs.json'),
                      'totalCohorts': 227, 'totalRows': 259336, 'remainingPublicProcessingTasks': 0}))


if __name__ == '__main__':
    main()
