"""Converts the six-checkpoint historical research (release 1.0, 1 October 2026) into the queue's
hand-back shape (handback.json, for `npm run research:merge`) and an atlas events file.

Run from the repository root:  python3 research/reviews/historical-checkpoints-2026-10-01/convert.py

What is accepted, following the release's own reading rules (README.md, INTEGRATION.md):
- A sighting: an observation the crosswalk marks eligible, whose printed name matches the body's
  (normalized) or is bridged by a reviewed source, and which names a body or programme. Funds,
  accounts, functional headings and prior-year comparatives are not sightings.
- A label variant ("Corrections" for BC Corrections) is kept as an unresolved check, not a sighting.
- Budget placement is kept as ministry_as_printed on the check, never as a parent.
- Events whose subject is a body the atlas already draws, and which describe something that
  happened (not planned), go to research/atlas/events-historical-checkpoints.json.
Everything else (the 228 unmatched labels, planned events, the matrix) stays here as research.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / 'data'
REPO = HERE.parents[2]
load = lambda name: json.loads((DATA / name).read_text())
CHECKED = '2026-10-01'
BY = 'ChatGPT (six-checkpoint historical research, release 1.0)'

observations = {o['observation_id']: o for o in load('observations.json')}
sources = {s['source_id']: s for s in load('sources.json')}
crosswalk = load('identity_crosswalk.json')
research = json.loads((REPO / 'research/history/sub-agencies-researched.json').read_text())
catalogue = json.loads((REPO / 'research/history/sub-agencies-sources.json').read_text())
by_url = {s['url']: s['id'] for s in catalogue['sources']}
held = {r['id']: r for r in research['records'] + research.get('gone', [])}

SIGHTING_TYPES = {'named_budget_observation', 'named_program_observation'}
evidence_of = lambda sid: 'estimates' if sid.startswith('EST-') else 'official_webpage'
source_id = lambda sid: by_url.get(sources[sid]['url'], 'hc-' + sid.lower())
used = set()

def cite(o):
    used.add(o['source_id'])
    return {'evidence': evidence_of(o['source_id']), 'source': sources[o['source_id']]['url'],
            'source_id': source_id(o['source_id']), 'locator': o['locator'], 'checked': CHECKED}

records = {}
def record(body):
    return records.setdefault(body, {
        'id': body, 'names': [], 'parents': [], 'research_events': [], 'evidence_status': 'documented_partial',
        'note': 'Budget sightings from the six-checkpoint historical research (2002, 2005, 2010, 2015, 2020, 2025). '
                'A sighting is presence in that year\'s Estimates, not a founding date or proof of the years between; '
                'the ministry it was printed under is budget presentation, not a parent.',
        'review': {'checked': CHECKED, 'by': BY, 'scope': 'Six Estimates checkpoints, selected name-bearing passages per ministry',
                   'sources_checked': [], 'full_history_complete': False}})

def already_seen(body, year, name):
    return any(str(n.get('observed_on')) == str(year) and n.get('name') == name for n in held.get(body, {}).get('names', []))

for row in crosswalk:
    o = observations[row['observation_id']]
    body, year = row['current_record_id'], row['checkpoint_year']
    check = {'source': sources[o['source_id']]['url'], 'source_id': source_id(o['source_id']), 'year': str(year),
             'scope': o['locator'], 'name_as_printed': o['name_as_printed'], 'ministry_as_printed': o['ministry_as_printed'],
             'observation_id': o['observation_id']}
    variant = row['mapping_status'] == 'label_variant_requires_identity_review'
    if row['evidence_eligible_for_presence_review'] and not variant and o['claim_type'] in SIGHTING_TYPES:
        r = record(body)
        r['review']['sources_checked'].append({**check, 'listed': True, 'outcome': 'found_name'})
        first = r.get('first_observed')
        if not first or int(first['date']) > year:
            bridge = row['mapping_status'] == 'historical_name_bridge_source_reviewed'
            r['first_observed'] = {'date': str(year), 'precision': 'year', **cite(o),
                                   'meaning': f"Named in the {year} Estimates as \"{o['name_as_printed']}\""
                                              f"{' (earlier name, bridged by a reviewed source)' if bridge else ''}; "
                                              'the earliest of six checkpoints read, not a founding date'}
        if not already_seen(body, year, o['name_as_printed']):
            r['names'].append({'name': o['name_as_printed'], 'observed_on': str(year), 'coverage': 'observation_only', **cite(o)})
    else:
        outcome = 'function_only' if o['claim_type'] not in SIGHTING_TYPES else 'related_label_identity_unresolved'
        r = record(body)
        used.add(o['source_id'])
        r['review']['sources_checked'].append({**check, 'listed': None, 'outcome': outcome,
                                               'note': f"{o['claim_type'].replace('_', ' ')}; {row['mapping_status'].replace('_', ' ')}"})

new_sources = [{'id': source_id(sid), 'url': sources[sid]['url'], 'title': sources[sid]['title'], 'evidence': evidence_of(sid),
                'checked': CHECKED} for sid in sorted(used) if source_id(sid).startswith('hc-')]
(HERE / 'handback.json').write_text(json.dumps({'batch': 'historical-checkpoints-2026-10-01', 'records': list(records.values()),
                                                'gone': [], 'sources': new_sources}, indent=2, ensure_ascii=False) + '\n')

# Events on bodies the atlas already draws. Planned events, and subjects with no atlas body, stay here.
SUBJECT = {
    'EVT-006': 'sub-workers-compensation-appeal-tribunal', 'EVT-007': 'sub-bc-farm-industry-review-board',
    'EVT-008': 'bc-financial-services-authority', 'EVT-009': 'financial-institutions-commission',
    'EVT-010': 'bc-financial-services-authority', 'EVT-012': 'bc-energy-regulator', 'EVT-013': 'skilledtradesbc',
    'EVT-014': 'sub-skilled-trades-bc-appeal-board', 'EVT-015': 'sub-energy-resource-appeal-tribunal',
    'EVT-016': 'sub-bc-timber-sales', 'EVT-017': 'tourism-bc', 'EVT-018': 'destination-bc', 'EVT-019': 'destination-bc',
    'EVT-020': 'royal-bc-museum', 'EVT-021': 'community-living-bc', 'EVT-022': 'provincial-capital-commission',
    'EVT-023': 'bc-human-rights-commission', 'EVT-025': 'bc-human-rights-tribunal'}
events = []
for e in load('events.json'):
    if e['event_id'] not in SUBJECT or e['date_role'] != 'historical_event_date':
        continue
    events.append({'id': f"hc:{e['event_id'].lower()}", 'subject_id': SUBJECT[e['event_id']], 'event_type': e['event_type'],
                   'title': f"{e['subject']}: {e['summary']}",
                   'date': {'start': e['event_date'], 'end': None, 'precision': e['date_precision']},
                   'temporal_status': 'source_reported_past',
                   'evidence': {'source_url': sources[e['source_id']]['url'], 'source_title': sources[e['source_id']]['title'], 'locator': e['locator']},
                   'interpretation_notes': e.get('limitation') or None, 'reviewed_on': CHECKED})
(REPO / 'research/atlas/events-historical-checkpoints.json').write_text(json.dumps({
    'source': 'research/reviews/historical-checkpoints-2026-10-01 (events.json); converted by convert.py',
    'events': events}, indent=1, ensure_ascii=False) + '\n')

sighted = [r for r in records.values() if r.get('first_observed')]
print(f"{len(records)} records, {len(sighted)} with a sighting, {sum(len(r['names']) for r in records.values())} name rows, "
      f"{len(new_sources)} new sources, {len(events)} events")
