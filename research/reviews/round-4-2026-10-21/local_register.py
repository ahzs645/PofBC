"""Builds the register of local bodies from Round 4's hospital-district research.

Run from the repository root:  python3 -I research/reviews/round-4-2026-10-21/local_register.py

Writes research/history/local-hospital-districts.json (schema local-bodies/1): the 43 regional
hospital district identities and 25 hospital improvement districts in root/hospital_districts.json
and root/hospital_improvement_districts.json, as the research identifies them. They are local
corporations under provincial statute, not provincial bodies, so no record names a ministry that
answered for it: the build reads them into the atlas's shared identities (search, panels, events,
lineage) and an optional local layer, never into a ministry's group.

As the integration review of 21 October 2026 asks (research/reviews/integration-review-2026-10-21):

- the research's ids are kept, so same-named corporations of different years stay apart;
- an end the research did not trace is `untraced`, drawn only as far as a source shows the district
  standing, and never as survival to today;
- governance is recorded body by body and dated from its instrument: who the trustees were and how
  chosen, who could vote, and, where an instrument says so, that the trustees with a Hospital Act
  appointee were a hospital's board of management. No body is said not to run a hospital, and no
  current-law provision is backdated;
- an asset recipient is a transfer, not a successor.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent / 'root'
RHD = json.loads((HERE / 'hospital_districts.json').read_text())
HID = json.loads((HERE / 'hospital_improvement_districts.json').read_text())
SOURCES = {row['id']: row for row in json.loads((HERE / 'sources.json').read_text())}
CLAIMS = {row['id']: row for row in json.loads((HERE / 'claims.json').read_text())}

# Ids the atlas already gives bodies the research names as transfer recipients.
ATLAS_IDS = {}


def url(source_ids):
    for source_id in source_ids or []:
        found = SOURCES.get(source_id)
        if found and found.get('url'):
            return found['url']
    return None


def names_of(entity):
    rows = sorted(entity.get('names') or [], key=lambda row: row.get('valid_from') or '')
    out = []
    for i, row in enumerate(rows):
        to = rows[i + 1].get('valid_from') if i + 1 < len(rows) else None
        out.append({'name': row['name'], 'from': row.get('valid_from'), 'to': to, 'source': url(row.get('source_ids'))})
    return out


def dated_claims(entity):
    """The entity's own dated claims, for its last sighting."""
    return sorted((CLAIMS[c] for c in entity.get('claim_ids', []) if c in CLAIMS and CLAIMS[c].get('date')), key=lambda c: c['date'])


ELECTORS = ('electors were Canadian citizens of 21 or more, able to register as provincial voters, who owned land in '
            'the district or zone (or a landowning corporation\'s agent, or a landowner\'s legal representative)')


def governance_of(entity):
    rows = []
    for key in sorted(k for k in entity if k.startswith('governance')):
        g = entity[key]
        since = entity['legal_start'] if key == 'governance_at_incorporation' else key.removeprefix('governance_')
        # A later instrument's rules take their day and source from the entity's claim of that year.
        later = next((CLAIMS[c] for c in entity.get('claim_ids', []) if c in CLAIMS and str(CLAIMS[c].get('date', '')).startswith(since)), None) if since != entity['legal_start'] else None
        if later:
            since = later['date']
            g = {**g, 'source_ids': later['source_ids']}
        parts = []
        if g.get('trustee_count'):
            parts.append(f"{g['trustee_count']} trustees" + (f" for {g['zone_count']} zones" if g.get('zone_count') else ''))
        for field in ('seat_allocation', 'initial_selection', 'subsequent_selection', 'selection', 'candidate_rule', 'candidate_exception', 'hospital_board'):
            if g.get(field):
                parts.append(g[field].rstrip('.'))
        if g.get('elector_profile') == 'original_lp_annual_voters_21_citizen_land':
            parts.append(ELECTORS)
        if parts:
            rows.append({'from': since, 'rule': '; '.join(parts) + '.', 'source': url(g.get('source_ids') or entity.get('start_source_ids')),
                         'locator': g.get('board_pinpoint') or g.get('locator') or g.get('elector_pinpoint')})
    # A later instrument that makes the trustees a hospital's board of management (100 Mile House, 1960).
    for claim_id in entity.get('claim_ids', []):
        claim = CLAIMS.get(claim_id)
        if claim and 'board of management' in (claim.get('statement') or '') and not any('board of management' in r['rule'] for r in rows if r['from'] == claim['date']):
            rows.append({'from': claim['date'], 'rule': claim['statement'], 'source': url(claim['source_ids']), 'locator': claim.get('locator')})
    return sorted(rows, key=lambda row: row['from'])


def transfers_of(entity_id, relationships):
    out = []
    for rel in relationships:
        if rel.get('from_id') != entity_id:
            continue
        out.append({'to': rel.get('to_id') or rel.get('to_label'), 'type': rel.get('type'), 'date': rel.get('effective_date') or rel.get('deadline'),
                    'deadline': rel.get('deadline'), 'scope': rel.get('scope'), 'conditions': rel.get('conditions'),
                    'source': url(rel.get('source_ids')), 'locator': rel.get('locator')})
    return out


def record(entity, kind, relationships):
    names = names_of(entity)
    ended = entity.get('legal_end')
    untraced = not ended
    claims = dated_claims(entity)
    last = claims[-1] if claims else None
    rec = {
        'id': entity['id'],
        'name': names[-1]['name'] if names else entity['original_name'],
        'kind': kind,
        'scope': 'local',
        'established': entity['legal_start'],
        'establishedMeaning': 'incorporated by letters patent, in force that day',
        'source': url(entity.get('start_source_ids')),
        'ended': ended,
        **({'endedMeaning': 'dissolved', 'endedSource': url(entity.get('end_source_ids'))} if ended else {}),
        **({'endStatus': 'untraced', 'attestations': [{'date': entity['legal_start'], 'scope': 'letters patent in force', 'source': url(entity.get('start_source_ids'))}]
            + ([{'date': last['date'], 'scope': last['statement'][:160], 'source': url(last['source_ids']), 'locator': last.get('locator')}] if last and last['date'] > entity['legal_start'] else [])} if untraced else {}),
        'names': names,
        'governance': governance_of(entity),
        'transfers': transfers_of(entity['id'], relationships),
        'claims': entity.get('claim_ids', []),
    }
    if kind == 'regional-hospital-district':
        rec['description'] = ('A regional hospital district, incorporated by letters patent under the Hospital District Act. '
                              'Its powers and its board changed by later orders, recorded as events.')
    else:
        statute = entity.get('statutory_authority') or {}
        rec['description'] = (f"A hospital improvement district incorporated under the {statute.get('statute', 'Water Act')}"
                              f"{' (' + statute['citation'] + ', s. ' + statute['section'] + ')' if statute.get('citation') else ''}. "
                              + (entity.get('objects_summary') or ''))
    return rec


records = [record(e, 'regional-hospital-district', RHD['relationships']) for e in RHD['entities']] + \
          [record(e, 'hospital-improvement-district', HID['relationships']) for e in HID['entities']]
assert len({r['id'] for r in records}) == len(records)
(ROOT / 'research/history/local-hospital-districts.json').write_text(json.dumps({
    'schema': 'local-bodies/1',
    'note': ('Local hospital-finance corporations from Round 4 (research/reviews/round-4-2026-10-21/root), generated by its '
             'local_register.py: edit the research and re-run, not this file. Local corporations under provincial statute, '
             'not provincial bodies: none answers to a ministry here.'),
    'identity_policy': RHD.get('identity_policy'),
    'records': records,
}, indent=2, ensure_ascii=False) + '\n')
print(f"{len(records)} local bodies ({sum(1 for r in records if r.get('endStatus') == 'untraced')} with an untraced end)")
