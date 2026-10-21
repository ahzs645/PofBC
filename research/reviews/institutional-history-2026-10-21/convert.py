"""Converts the health-authority lineage of the institutional-history research (21 October 2026)
into the history's own shapes: body records for every named predecessor of the five geographic
health authorities, and an atlas events file for the dated changes around them.

Run from the repository root:  python3 -I research/reviews/institutional-history-2026-10-21/convert.py

Writes research/history/bodies-health-lineage.json and research/atlas/events-health-lineage.json.

What is accepted, and how:

- The 44 constituents in Schedule A of B.C. Reg. 293/2001 become bodies that amalgamated into
  their authority on 12 December 2001 (deposited that day; signed 11 December). The regulation says
  amalgamated, so `becameId` is used.
- The seven community health services societies are not in Schedule A. They are bodies whose
  services passed to the authorities (listed as predecessors of each successor, never `becameId`),
  ending as independent bodies on 12 December 2001, when M298-M305 replaced their boards. When each
  society was dissolved or its assets conveyed is not known, and the record says so.
- No start of any council or board is guessed. A body is drawn from the earliest day a source shows
  it (`firstSeen`): the December 1996 orders for the boards they continued, B.C. Reg. 76/2000 for
  the council areas and societies, the 1994 board-composition order for Northern Interior. Only
  Prince George's council (designated 24 March 1995) and Simon Fraser/Burnaby (designated 16
  December 1996) have a start.
- The 43 councils that the December 1996 orders provided would amalgamate into a board are bodies
  ending in 1997 (the orders rescind them only "on amalgamation", and the transactions' days are
  not recovered). With no start they are not drawn; they are what each board came from.
- A board's December 1996 name and its 2001 "Health Region" name are treated as one body, as the
  research recommends.

The primary-evidence follow-up (research/reviews/primary-evidence-2026-10-21) is then applied on
top, and wins where it gives a fact: original designation dates replace `firstSeen`, express
renaming orders become `names` periods, the follow-up's ministry intervals become `responsible`,
the societies end on their 15 February 2002 registry dissolution, and the Nisga'a council and the
predecessors of the four 1997 councils are added.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAP = json.loads((HERE / 'health_lineage_map.json').read_text())

URL = {
    'HL01': 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001',
    'HL02': 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002HLTH0009-000402.htm',
    'HL07': 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2001resume38',
    'HL08': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0051_2002',
    'HL09': 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/regulationbulletin/2002cumulati',
    'HL11': 'https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf',
    'HL13': 'https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/93047',
    'HL14': 'https://www.bclaws.gov.bc.ca/civix/document/id/regulationbulletin/regulationbulletin/r0076_2000',
    'HL15': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0432_1996',
    'HL16': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0441_1996',
    'HL17': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0444_1996',
    'HL18': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0007_1997',
    'HL19': 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0178_1995',
    'HL20': 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1298_1994',
    'HL21': 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1999resume27',
    'HL22': 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/regulationbulletin/1999cumulati',
    'HL25': 'https://fnha.ca/about/about-us/transition-and-transformation/',
    'HL26': 'https://fnha.ca/wp-content/uploads/FNHA-Annual-Report-2014-2015.pdf',
    'HL41': 'https://lims.leg.bc.ca/hdms/file/Debates/35th3rd/19940606pm-Hansard-v16n3.htm',
}

AUTHORITY = {
    'Fraser Health Authority': 'fraser-health',
    'Interior Health Authority': 'interior-health',
    'Northern Health Authority': 'northern-health',
    'Vancouver Coastal Health Authority': 'vancouver-coastal-health',
    'Vancouver Island Health Authority': 'vancouver-island-health',
}


def slug(name):
    name = name.replace('’', '').replace("'", '')
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


# The eleven boards: the 2001 name, the name the December 1996 orders gave it, and where the orders
# show it. Northern Interior is shown earlier, by the 1994 board-composition order.
BOARDS = {
    'Fraser Valley Health Region': ('Fraser Valley Regional Health Board', '1996-12-19', 'HL16', 'M441/1996, section 2: continued'),
    'Simon Fraser Health Region': ('Simon Fraser/Burnaby Health Board', None, 'HL15', 'M432/1996, section 4: designated, effective 16 December 1996'),
    'South Fraser Health Region': ('South Fraser Valley Regional Health Board', '1996-12-19', 'HL16', 'M441/1996, section 3: continued'),
    'Thompson Health Region': ('Thompson Regional Health Board', '1996-12-19', 'HL16', 'M441/1996, section 4: continued'),
    'Okanagan Similkameen Health Region': ('South Okanagan Similkameen Health Board', '1996-12-16', 'HL15', 'M432/1996, section 5: continued'),
    'North Okanagan Health Region': ('North Okanagan Regional Health Board', '1996-12-19', 'HL17', 'M444/1996, section 3: continued'),
    'Central Vancouver Island Health Region': ('Central Vancouver Island Regional Health Board', '1996-12-19', 'HL16', 'M441/1996, section 5: continued'),
    'Capital Health Region': ('Capital Health Board', '1996-12-19', 'HL16', 'M441/1996, section 7: continued'),
    'Northern Interior Regional Health Board': ('Northern Interior Regional Health Board', '1994-10-13', 'HL20', 'OIC 1298/1994, Schedule section 9: in the Health Board Regulation, with members appointed by the Lakes District, Omineca, Mackenzie, Robson Valley and Prince George councils. Evidence of existence by that day, not of its creation'),
    'North Shore Health Region': ('North Shore Health Region', '1996-12-16', 'HL15', 'M432/1996: the North Shore board continued'),
    'Vancouver/Richmond Health Board': ('Vancouver Health Board', '1997-01-09', 'HL18', 'M7/1997, sections 1-2: the Vancouver Health Board continued and known as the Vancouver/Richmond Health Board'),
}
BOARD_OF_1996 = {old: new for new, (old, *_rest) in BOARDS.items()}

# The councils whose designating regulation M444/1996 names, so a source shows them by that year.
COUNCIL_REGULATION = {
    'Lakes District Health Council': ('1995', 'B.C. Reg. 89/95'),
    'Omineca Health Council': ('1995', 'B.C. Reg. 161/95'),
    'MacKenzie and Area Health Council': ('1994', 'B.C. Reg. 458/94'),
    'Robson Valley Health Council': ('1994', 'B.C. Reg. 314/94'),
}

ABOUT_2001 = ('Amalgamated into the {authority} on 12 December 2001 under the Regional Health Boards '
              'Regulation, B.C. Reg. 293/2001, which names it in Schedule A (signed 11 December, deposited 12 December).')


def board(name, authority):
    old, seen, source, locator = BOARDS[name]
    earlier = [r['predecessor'] for r in MAP['council_to_board_1996_1997'] if BOARD_OF_1996.get(r['successor']) == name]
    record = {
        'id': slug(name),
        'name': name,
        'kind': 'health-authority',
        'established': None,
        'ended': '2001-12-12',
        'becameId': AUTHORITY[authority],
        'predecessorIds': [],
        'responsible': [],
        'description': ' '.join(filter(None, [
            f'Regional health board under the Health Authorities Act. The December 1996 orders call it the {old}.' if old != name else 'Regional health board under the Health Authorities Act.',
            f'Those orders provided for {len(earlier)} community health councils to amalgamate into it.' if earlier else None,
            ABOUT_2001.format(authority=authority),
            'That the 1996 and 2001 names are one body rests on the orders continuing it; the renaming instrument is not yet found.' if old != name and name != 'Vancouver/Richmond Health Board' else None,
            'When it was first designated is not yet found.' if seen else None,
        ])),
        'source': URL['HL01'],
        'otherSources': [URL[source], URL['HL11']],
    }
    if seen:
        record['firstSeen'] = {'date': seen, 'source': URL[source], 'locator': locator}
    else:
        record['established'] = '1996-12-16'
        record['establishedMeaning'] = 'designated by M432/1996, combining the Simon Fraser and Burnaby health boards'
    return record


def council(name, authority, society):
    record = {
        'id': slug(name),
        'name': name,
        'kind': 'health-authority',
        'established': None,
        'ended': '2001-12-12',
        'becameId': AUTHORITY[authority],
        'predecessorIds': [],
        'responsible': [],
        'description': ' '.join([
            'Community health council under the Health Authorities Act.' if 'Transitional' not in name else 'Transitional health authority, on the council side of the Health Authorities Act framework.',
            f'Its area was one of those served by the {society}.' if society else '',
            ABOUT_2001.format(authority=authority),
            'When it was first designated is not yet found; it is drawn from February 2000, when B.C. Reg. 76/2000 shows its area.',
        ]).replace('  ', ' '),
        'source': URL['HL01'],
        'firstSeen': {'date': '2000-02-28', 'source': URL['HL14'], 'locator': f'B.C. Reg. 76/2000, Schedule A: the council area associated with the {society}' if society else 'B.C. Reg. 76/2000, Schedule A'},
    }
    return record


def bare(name):
    return re.sub(r'\b(Community )?Health Council$|Transitional Health Authority$', '', name).strip()


societies = MAP['societies_2000_2001']
society_of = {}
for s in societies:
    for area in s['corresponding_chc_areas_2000']:
        society_of[area] = s['name']

records = []
for row in MAP['statutory_amalgamation_2001']:
    name, authority = row['predecessor'], row['successor']
    if name in BOARDS:
        records.append(board(name, authority))
    else:
        match = next((s for area, s in society_of.items() if bare(area) == bare(name)), None)
        records.append(council(name, authority, match))

SERVICE_NOTE = {
    'Cariboo Community Health Services Society': 'Its territory was split: the Quesnel council went to Northern Health, the others to Interior Health; Bella Coola moved on to Vancouver Coastal in March 2002.',
    'Upper Island/Central Coast Community Health Services Society': 'Its Central Coast territory moved to Vancouver Coastal in March 2002.',
    'Kootenay Boundary Community Health Services Society': 'The 2001 announcement calls it "Central Kootenay"; this is the name in B.C. Reg. 76/2000, section 7.',
}
for s in societies:
    successors = [AUTHORITY[name] for name in s['service_successors_2001']]
    records.append({
        'id': slug(s['name']),
        'name': s['name'],
        'kind': 'health-authority',
        'established': None,
        'ended': '2001-12-12',
        'becameId': None,
        'predecessorIds': [],
        'serviceSuccessorIds': successors,
        'responsible': [],
        'description': ' '.join(filter(None, [
            f"Community health services society serving the areas of {len(s['corresponding_chc_areas_2000'])} community health councils.",
            f"Its services passed to the {' and the '.join(s['service_successors_2001'])} in the December 2001 reorganization, when its board was replaced by the new authority's appointees (M298-M305/2001, effective 12 December).",
            SERVICE_NOTE.get(s['name']),
            'It is not in Schedule A of B.C. Reg. 293/2001: this is a passing of services, not an amalgamation, and when the society was dissolved or its assets conveyed is not yet found.',
        ])),
        'source': URL['HL14'],
        'otherSources': [URL['HL07'], URL['HL01']],
        'firstSeen': {'date': '2000-02-28', 'source': URL['HL14'], 'locator': 'B.C. Reg. 76/2000, section 7 and Schedule A'},
    })

# The councils the December 1996 orders provided would amalgamate into a board, and the boards they
# combined or rescinded.
ORDER = {'HL15': 'M432/1996', 'HL16': 'M441/1996', 'HL17': 'M444/1996'}
for row in MAP['council_to_board_1996_1997']:
    name = row['predecessor']
    target = BOARD_OF_1996[row['successor']]
    source = next(s for s in row['sources'] if s in ORDER)
    record = {
        'id': slug(name) if name != 'South Cariboo Health Council' else 'south-cariboo-health-council-1996',
        'name': name,
        'kind': 'health-authority',
        'established': None,
        'ended': '1997',
        'becameId': slug(target),
        'predecessorIds': [],
        'responsible': [],
        'description': ' '.join(filter(None, [
            f"Community health council. {ORDER[source]} (December 1996) provided for it to amalgamate into the {row['successor']}, rescinding its designation on amalgamation.",
            'The day the amalgamation was carried out is not yet found; the regional reform took effect through 1997.',
            'Not the South Cariboo Community Health Council of 2001 (100 Mile House): similar names are not proof of one body.' if name == 'South Cariboo Health Council' else None,
        ])),
        'source': URL[source],
        'otherSources': [URL['HL11']],
    }
    if name == 'Prince George Health Council':
        record['established'] = '1995-03-24'
        record['establishedMeaning'] = 'designated by M178/1995; a 1994 board-composition order already names a council of this name'
        record['otherSources'].insert(0, URL['HL19'])
    elif name in COUNCIL_REGULATION:
        year, reg = COUNCIL_REGULATION[name]
        record['firstSeen'] = {'date': year, 'source': URL['HL17'], 'locator': f'M444/1996, section 2(g): names {reg} as its regulation'}
    records.append(record)

for name, target, source, note in [
    ('Simon Fraser Health Board', 'Simon Fraser Health Region', 'HL15', 'M432/1996 designated the Simon Fraser/Burnaby Health Board from it and the Burnaby Health Board, rescinding the old designations on amalgamation.'),
    ('Burnaby Health Board', 'Simon Fraser Health Region', 'HL15', 'M432/1996 designated the Simon Fraser/Burnaby Health Board from it and the Simon Fraser Health Board, rescinding the old designations on amalgamation.'),
    ('Richmond Health Board', 'Vancouver/Richmond Health Board', 'HL18', 'M7/1997 (9 January 1997) rescinded its designation, continuing the Vancouver Health Board as the Vancouver/Richmond Health Board.'),
]:
    records.append({
        'id': slug(name),
        'name': name,
        'kind': 'health-authority',
        'established': None,
        'ended': '1997-01-09' if name == 'Richmond Health Board' else '1997',
        'becameId': slug(target),
        'predecessorIds': [],
        'responsible': [],
        'description': f'Regional health board. {note} When it was first designated is not yet found.',
        'source': URL[source],
    })


# ── The primary-evidence follow-up (research/reviews/primary-evidence-2026-10-21) ─────────────────
#
# The original designation orders, the express renaming orders, the ministry each body answered to,
# and the societies' registry lives. Where it gives a fact, it replaces the earlier stand-in: a
# designation's effective day replaces `firstSeen`, a renaming order replaces "continuity unproved",
# and the registry's 15 February 2002 dissolution replaces the 12 December 2001 governance change as
# a society's end. Order-made dates of renamings are kept as such: their deposit is mostly not found.

FOLLOWUP = json.loads((HERE.parent / 'primary-evidence-2026-10-21' / 'PofBC-primary-evidence-followup-2026-10-21.json').read_text())
FSRC = {source['id']: source for source in FOLLOWUP['sources']}
HD = FOLLOWUP['health_designations']
HT = FOLLOWUP['health_transactions_and_accountability']


def fu(source_id):
    return FSRC[source_id]['url']


def order_url(order):
    """The BC Laws address of a ministerial order such as M357/1994."""
    number, year = order[1:].split('/')
    return f'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m{int(number):04d}_{year}'


by_id = {record['id']: record for record in records}
council_of = {c['name_2001']: c for c in HD['councils'] if c['name_2001']}
board_of = {b['name_in_2001_schedule']: b for b in HD['boards']}
name_events = HD['council_name_events'] + HD['board_name_events']
accountability = {e['entity']: e for e in HT['accountability_entities_2001']}
SUPERSEDED_ORDERS = {'M88/1997'}  # rescinded by M111/1997, which named the Region; kept as an interim name


def chain(final, first):
    """Each name a body held, oldest first, from its first name to its 2001 name, by the renaming orders."""
    names = [{'name': final}]
    current = final
    while current != first:
        step = next((e for e in name_events if e['to_name'] == current and e['from_name'] != current
                     and not (e['order'] == 'M111/1997')), None)
        if not step:
            break
        names[0]['from'] = step['order_made_date'] or step['order'].split('/')[1]
        names[0]['source'] = order_url(step['order'])
        names[0]['locator'] = f"{step['order']}, made {step['order_made_date']}; its deposit is not recovered" if step['order_made_date'] else f"{step['order']} ({step['order'].split('/')[1]}); the day is not recovered"
        names.insert(0, {'name': step['from_name']})
        current = step['from_name']
    for earlier, later in zip(names, names[1:]):
        earlier['to'] = later['from']
    return names


def periods(entity, start, end):
    """The ministry a body answered to, from the follow-up's intervals, from its own start."""
    rows = []
    for interval in accountability[entity]['ministry_intervals']:
        frm = interval.get('valid_from') or start
        rows.append({
            'ministry': interval['ministry'],
            'from': max(frm, start) if start and frm else (frm or start),
            'to': min(interval['valid_until_exclusive'], end) if end else interval['valid_until_exclusive'],
            'source': fu(interval['source_ids'][0]),
            'locator': FSRC[interval['source_ids'][0]].get('pinpoint'),
            'note': interval.get('from_rule') or interval.get('note'),
        })
    return rows


MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def human(day):
    """A date as the descriptions write it: 17 November 1994, March 1997, 1994."""
    parts = str(day).split('-')
    if len(parts) == 3:
        return f'{int(parts[2])} {MONTHS[int(parts[1]) - 1]} {parts[0]}'
    if len(parts) == 2:
        return f'{MONTHS[int(parts[1]) - 1]} {parts[0]}'
    return parts[0]


def set_names(record, names):
    if len(names) > 1:
        record['names'] = names


for record in list(records):
    name = record['name']
    if name in board_of:
        b = board_of[name]
        first = b['original_designations'][0] if len(b['original_designations']) == 1 else None
        record.pop('firstSeen', None)
        if name == 'Simon Fraser Health Region':
            record['established'] = '1996-12-16'
            record['establishedMeaning'] = 'designated by M432/1996, combining the Simon Fraser and Burnaby health boards'
            set_names(record, [
                {'name': 'Simon Fraser/Burnaby Health Board', 'to': '1997-02-26'},
                {'name': 'Simon Fraser Health Board', 'from': '1997-02-26', 'to': '1997-03-17', 'source': order_url('M88/1997'), 'locator': 'M88/1997, made 26 February 1997 (Reg. 56/97); rescinded by M111/1997'},
                {'name': name, 'from': '1997-03-17', 'source': order_url('M111/1997'), 'locator': 'M111/1997, made 17 March 1997, rescinding Reg. 56/97 and substituting the Region name; its deposit is not recovered'},
            ])
        elif name == 'Vancouver/Richmond Health Board':
            record['established'] = '1994-12-06'
            record['establishedMeaning'] = 'designated as the Vancouver Health Board by M411/1994, effective that day'
            set_names(record, [
                {'name': 'Vancouver Health Board', 'to': '1997-01-09'},
                {'name': name, 'from': '1997-01-09', 'source': URL['HL18'], 'locator': 'M7/1997, sections 1-2: continued and known as the Vancouver/Richmond Health Board'},
            ])
        else:
            record['established'] = first['stated_effective_date']
            record['establishedMeaning'] = f"designated as the {first['name']} by {first['order']}, effective that day"
            names = chain(name, first['name'])
            if name == 'Fraser Valley Health Region':
                # M597/1995 designates the twenty-board set under the Fraser Valley name.
                names = [{'name': 'Upper Fraser Valley Health Board', 'to': '1995-12-06'},
                         {'name': 'Fraser Valley Regional Health Board', 'from': '1995-12-06', 'to': names[-1]['from'], 'source': fu('HDS053'), 'locator': 'M597/1995, made 6 December 1995 (Reg. 521/95), designating the twenty-board set under this name'},
                         names[-1]]
            set_names(record, names)
        record['source'] = order_url((first or b['original_designations'][0])['order'])
        record['otherSources'] = [URL['HL01'], order_url(b['reconstitution_order'])]
        old = BOARDS[name][0]
        earlier = [r['predecessor'] for r in MAP['council_to_board_1996_1997'] if BOARD_OF_1996.get(r['successor']) == name]
        record['description'] = ' '.join(filter(None, [
            f"Regional health board under the Health Authorities Act, designated {record['establishedMeaning'].split(' by ')[0].replace('designated ', '')} on {human(record['established'])}." if name != 'Simon Fraser Health Region' else 'Regional health board under the Health Authorities Act, designated on 16 December 1996 by combining the Simon Fraser and Burnaby health boards.',
            f"{b['reconstitution_order']} continued it in the December 1996 reconstitution." if b['reconstitution_event'] == 'continued' else None,
            f'Those orders provided for {len(earlier)} community health councils to amalgamate into it.' if earlier else None,
            'Renamed by express amending orders, each dated by the day it was made.' if record.get('names') else None,
            ABOUT_2001.format(authority=next(k for k, v in AUTHORITY.items() if v == record['becameId'])),
        ]))
        if name == 'Northern Interior Regional Health Board':
            record['description'] += ' A board-composition order of 13 October 1994 (OIC 1298/1994) names it before its designation took effect; that is not its start.'
        record['responsible'] = periods(name, record['established'], record['ended'])
    elif name in council_of:
        c = council_of[name]
        record.pop('firstSeen', None)
        if c['original_stated_effective_date']:
            record['established'] = c['original_stated_effective_date']
            record['establishedMeaning'] = f"designated by {c['original_designation_order']}, effective that day"
            record['source'] = order_url(c['original_designation_order'])
        elif c['original_designation_order']:
            record['established'] = c['original_designation_order'].split('/')[1]
            record['establishedMeaning'] = f"designated by {c['original_designation_order']}; the effective day is not confirmed"
            record['source'] = order_url(c['original_designation_order'])
        else:
            trigger = next(t for t in HT['new_council_amalgamation_triggers_1997'] if t['new_council'].replace("'", '’') == c['designation_name_1997'] or t['new_council'] == c['designation_name_1997'])
            if c['1997_order'] == 'M96/1997':
                record['established'] = '1997-03'
                record['establishedMeaning'] = f"designated by M96/1997 (March 1997: the day in its date line is unclear); its members were appointed by {trigger['appointment_order']} effective {trigger['appointment_effective_date']}"
            else:
                record['established'] = trigger['appointment_effective_date']
                record['establishedMeaning'] = f"designated by {c['1997_order']} (made that day) and its members appointed by {trigger['appointment_order']} effective that day, which under Reg. 338/96 s. 3 brings the amalgamation of its predecessors into effect"
            record['source'] = order_url(c['1997_order'])
            for old_name in trigger['predecessors']:
                records.append({
                    'id': slug(old_name),
                    'name': old_name.replace("'", '’'),
                    'kind': 'health-authority',
                    'established': None,
                    'ended': record['established'],
                    'becameId': record['id'],
                    'predecessorIds': [],
                    'responsible': [],
                    'description': f"Community health council, combined into the {c['designation_name_1997']} in 1997: the appointment of the new council's members ({trigger['appointment_order']}) brought the amalgamation into effect under Reg. 338/96 s. 3, where its area lay within the new council's. When it was designated is not in this research.",
                    'source': order_url(trigger['appointment_order']),
                })
        set_names(record, chain(name, c['designation_name_1997']) if c['designation_name_1997'] != name else [])
        if name == 'Columbia Valley Health Council':
            set_names(record, chain(name, 'Upper Columbia Health Council'))
        record['otherSources'] = [URL['HL01'], order_url(c['1997_order'])]
        society = next((s for area, s in society_of.items() if bare(area) == bare(name)), None)
        record['description'] = ' '.join(filter(None, [
            'Community health council under the Health Authorities Act.' if 'Transitional' not in name else 'Community health council under the Health Authorities Act, renamed a transitional health authority in 1998.',
            f"Its designation took effect on {human(record['established'])} ({c['original_designation_order']})." if c['original_stated_effective_date'] else None,
            f"{c['1997_order']} continued it in the 1997 framework." if c['1997_event_type'] == 'continuation' else f"A new council of 1997, combining {len(next(t for t in HT['new_council_amalgamation_triggers_1997'] if t['designation_order'] == c['1997_order'] and bare(t['new_council'].replace(chr(39), '’')) == bare(c['designation_name_1997']))['predecessors'])} earlier councils.",
            f'Its area was one of those served by the {society}.' if society else None,
            ABOUT_2001.format(authority=next(k for k, v in AUTHORITY.items() if v == record['becameId'])),
        ]))
        record['responsible'] = periods(name, record['established'], record['ended'])

registry = {s['name']: s for s in HT['registry_society_lifespans']}
for record in records:
    s = registry.get(record['name'])
    if not s:
        continue
    record.pop('firstSeen', None)
    record['established'] = s['registration_date']
    record['establishedMeaning'] = f"registered as a society ({s['registration_number']})"
    record['ended'] = s['dissolution_date']
    record['source'] = fu(s['source_ids'][0])
    names = s['historical_names']
    if len(names) > 1:
        record['names'] = [{'name': n['name'].title().replace('/C', '/C'), 'from': n['valid_from'], 'to': n['valid_until_exclusive'], 'source': fu(s['source_ids'][0]), 'locator': 'BC Corporate Registry name history'} for n in names]
        record['names'][-1]['name'] = record['name']
        record['names'][0]['name'] = 'Central Kootenay Community Health Services Society'
        del record['names'][0]['from']
    record['description'] = ' '.join(filter(None, [
        f"Community health services society, registered on {human(s['registration_date'])} ({s['registration_number']}), serving the areas of several community health councils where no regional board was formed.",
        f"Known as the Central Kootenay Community Health Services Society until 21 January 1998." if len(names) > 1 else None,
        f"On 12 December 2001 its governors were replaced by the new authority's appointees (M298-M305/2001) and its services passed to the {' and the '.join(next(x['service_successors_2001'] for x in societies if x['name'] == record['name']))}.",
        SERVICE_NOTE.get(record['name']) if 'Kootenay' not in record['name'] else None,
        'The corporate registry records its dissolution on 15 February 2002. It is not in Schedule A of B.C. Reg. 293/2001, so this is a passing of services, not an amalgamation; how and when its assets were conveyed is not found.',
    ]))
    record['otherSources'] = [fu('HT16'), URL['HL07'], URL['HL01']]
    record['responsible'] = periods(record['name'], s['registration_date'], s['dissolution_date'])

# The three boards of 1994 that the December 1996 and January 1997 orders folded into others.
for name, order in [('Simon Fraser Health Board', 'M199/1994'), ('Burnaby Health Board', 'M344/1994'), ('Richmond Health Board', 'M334/1994')]:
    record = by_id[slug(name)]
    designation = next(o for b in HD['boards'] for o in b['original_designations'] if o['name'] == name)
    record['established'] = designation['stated_effective_date']
    record['establishedMeaning'] = f'designated by {order}, effective that day'
    record['description'] = record['description'].replace(' When it was first designated is not yet found.', '')
    record['otherSources'] = [order_url(order)]

# The councils and boards folded into others before 1997 answered to the minister under the 1993
# Act as the later ones did: from their designation, or from the first sight of them, to their end.
for record in records:
    if record['responsible'] or record.get('serviceSuccessorIds') or not record.get('becameId'):
        continue
    start = record.get('established') or (record.get('firstSeen') or {}).get('date')
    if start:
        record['responsible'] = [{'ministry': 'Ministry of Health', 'from': start, 'to': record['ended'], 'source': fu('HT32'),
                                  'locator': FSRC['HT32'].get('pinpoint'), 'note': 'Boards and councils answer to the minister under the Health Authorities Act, SBC 1993 c. 47.'}]

# Nisga'a: a council of the 1997 framework whose designation was removed in 1999. Not an end of
# Nisga'a health services, and not a predecessor of Northern Health.
nisgaa = next(c for c in HD['councils'] if c['name_2001'] is None)
records.append({
    'id': 'nisgaa-community-health-council',
    'name': nisgaa['designation_name_1997'],
    'kind': 'health-authority',
    'established': nisgaa['original_stated_effective_date'],
    'establishedMeaning': f"designated by {nisgaa['original_designation_order']}, effective that day",
    'ended': '1999-10-18',
    'becameId': None,
    'predecessorIds': [],
    'responsible': [{'ministry': 'Ministry of Health', 'from': nisgaa['original_stated_effective_date'], 'to': '1999-10-18', 'source': URL['HL13'], 'locator': 'Health Authorities Act: councils answer to the minister'}],
    'description': ('Community health council for the Nass Valley, designated in 1995 and continued in the 1997 framework (M191/1997). '
                    'M366/1999 removed its designation from the council regulation (Reg. 333/99, deposited 18 October 1999), which is why '
                    '1997 had 34 councils and 2001 had 33. Nisga’a health services did not end: the Nisga’a Valley Health Board kept a '
                    'distinct status through the 2001 restructuring.'),
    'source': order_url(nisgaa['original_designation_order']),
    'otherSources': [order_url('M191/1997'), URL['HL22']],
})

ids = [record['id'] for record in records]
assert len(ids) == len(set(ids)), 'duplicate ids'
assert len(records) == 44 + 7 + 43 + 3 + 9 + 1, len(records)

bodies = {
    'note': ('Predecessors of the five geographic health authorities, from the institutional-history research of '
             '21 October 2026 (research/reviews/institutional-history-2026-10-21). Generated by its convert.py: edit '
             'the research and re-run, not this file. `firstSeen` is the earliest day a source shows a body whose start '
             'is unknown; `serviceSuccessorIds` names the bodies a society\'s services passed to, which is not an amalgamation.'),
    'records': records,
}
(ROOT / 'research/history/bodies-health-lineage.json').write_text(json.dumps(bodies, indent=2, ensure_ascii=False) + '\n')


def event(id, subject, type, title, start, precision, source, locator, notes=None, related=None):
    return {
        'id': f'atlas:health-lineage-{id}',
        'subject_id': subject,
        'related_subject_ids': related or [],
        'event_type': type,
        'title': title,
        'date': {'start': start, 'end': None, 'precision': precision, 'range_end_inclusive': False},
        'temporal_status': 'source_reported_past',
        'certainty': 'documented',
        'evidence': {'source_url': URL[source], 'locator': locator, 'observed_on': '2026-10-21'},
        'interpretation_notes': notes,
        'reviewed_on': '2026-10-21',
    }


events = []
# The diagram's own id for an authority, where it differs from the research record's.
DIAGRAM_ID = {'vancouver-island-health': 'island-health'}
for authority, research_id in AUTHORITY.items():
    subject = DIAGRAM_ID.get(research_id, research_id)
    constituents = [r['predecessor'] for r in MAP['statutory_amalgamation_2001'] if r['successor'] == authority]
    events.append(event(f'{subject}-amalgamation', subject, 'amalgamation',
                        f'{authority} formed by amalgamating {len(constituents)} boards and councils',
                        '2001-12-12', 'day', 'HL01', 'B.C. Reg. 293/2001, sections 2-4 and Schedule A',
                        'Signed 11 December 2001 (M297), deposited and announced 12 December.',
                        [slug(name) for name in constituents]))
events += [
    event('new-directions', 'ministry-of-health-1976', 'policy_announced', 'New Directions for a Healthy British Columbia announced, beginning regionalization',
          '1993-02', 'month', 'HL41', 'Hansard, 6 June 1994, printed p. 11445 (minister Paul Ramsey)',
          'The Auditor General\'s 1998 review assigns it to 1992; the contemporaneous testimony is preferred.'),
    event('act-1993', 'ministry-of-health-1976', 'legislation_assented', 'Health Authorities Act receives assent: regional health boards and community health councils, with community representation and public meetings',
          '1993-07-29', 'day', 'HL13', 'SBC 1993 c. 47, sections 4, 6, 8',
          'The original framework: councils sent members to regional boards, ministerial appointees were capped at a third, and meetings were public with stated exceptions.'),
    event('better-teamwork', 'ministry-of-health-1976', 'policy_announced', 'Better Teamwork, Better Care resets regionalization to 11 regional boards, 34 councils and 7 societies',
          '1996-11-29', 'day', 'HL11', 'Auditor General 1998 review, printed pp. 1, 6, 22-24'),
    event('devolution-1997', 'ministry-of-health-1976', 'functions_transferred', 'Health services devolve to the regional boards, councils and societies (1 April to 1 October 1997)',
          '1997-04-01', 'day', 'HL11', 'Auditor General 1998 review, implementation timeline, printed p. 28',
          'The remaining council transfers completed by 1 October 1997.'),
    event('nisgaa-1999', 'ministry-of-health-1976', 'designation_removed', 'Nisga\'a Community Health Council designation removed from the council regulation',
          '1999-10-18', 'day', 'HL22', '1999 cumulative regulation bulletin, Health Authorities Act, Reg. 333/99 (M366/1999)',
          'Not the end of Nisga\'a health services: the Nisga\'a Valley Health Board kept a distinct status through the 2001 restructuring.'),
    event('central-coast-2002', 'vancouver-coastal-health', 'territory_transferred', 'Bella Coola and Central Coast areas move to Vancouver Coastal Health from Interior and Vancouver Island',
          '2002-03-18', 'day', 'HL09', '2002 cumulative regulation bulletin: B.C. Reg. 52/2002 (M51/2002), deposited 18 March 2002',
          'A boundary change after the 2001 amalgamation; the two bodies amalgamated into Interior and Vancouver Island, and only their areas moved.',
          ['bella-coola-and-district-transitional-health-authority', 'central-coast-transitional-health-authority', 'interior-health', 'island-health']),
]
events_file = {
    'metadata': {
        'title': 'Health-authority lineage: regionalization, the 2001 amalgamation and later transfers',
        'as_of': '2026-10-21',
        'produced_by': 'research/reviews/institutional-history-2026-10-21/convert.py',
        'conventions': {'date_precision': 'kept as stated by the source; a year is never 1 January'},
    },
    'events': events,
}
(ROOT / 'research/atlas/events-health-lineage.json').write_text(json.dumps(events_file, indent=2, ensure_ascii=False) + '\n')
print(f'{len(records)} bodies, {len(events)} events')

# ── Beyond the regional authorities: PHSA's agencies, the ministry's functions, Crown ownership ──
#
# Only events the diagram does not already hold (BC Cancer's 1938 and 1974, FNHA's two transfers,
# BCCDC's 2018 amalgamation and BC Housing's PRHC are there already). Each says what it dates.

MORE = {
    'PM02': 'https://www.phsa.ca/about-site/Documents/PHSA%20Consolidated%20FS.pdf',
    'PM03': 'https://www.phsa.ca/about-site/Documents/Mental%20Health.pdf',
    'PM06': 'https://www.bccdc.ca/About-Site/Documents/Annual-Reports/BCCDCReport2013V4.pdf',
    'PM08': 'https://www.bcwomens.ca/about/who-we-are/our-unique-role/our-story',
    'PM29': 'https://free.bcpublications.ca/civix/document/id/corpreg/corpreg/soc0409soc0526',
    'PM30': 'https://hsabc.org/BCSHS_townhall_questions',
    'PM36': 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1217607539',
    'PM38': 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/681611917',
    'PM41': 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2004resume03',
    'PM44': 'https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz1/bcgaz1/1335172506',
    'PM46': 'https://www2.gov.bc.ca/assets/gov/health/practitioner-pro/medical-services-plan/bluebook2002.pdf',
    'PM48': 'https://www2.gov.bc.ca/assets/gov/health/health-drug-coverage/pharmacare/pharmacare_trends_2022_2023.pdf',
    'CB-008': 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-transportation-financing-authority-fs-2025-26.pdf',
    'CB-014': 'https://archive.news.gov.bc.ca/releases/news_releases_2009-2013/2010hsd0024-000212.htm',
    'CB-026': 'https://news.gov.bc.ca/releases/2024AG0027-000679',
}
URL.update(MORE)


def more(id, subject, type, title, start, precision, source, locator, notes=None, related=None):
    record = event(id, subject, type, title, start, precision, source, locator, notes, related)
    record['id'] = f'atlas:institutional-history-{id}'
    return record


institutional = [
    # BC Centre for Disease Control, from its own 2013 annual report (History, p. 7).
    more('bccdc-1955', 'sub-bc-centre-for-disease-control', 'co_location', 'Special Health and Treatment Services divisions in Vancouver brought under one roof, each keeping its own operations',
         '1955', 'year', 'PM06', 'BCCDC Annual Report 2013, History, printed p. 7', 'Co-location, not a merger or an incorporation.'),
    more('bccdc-1977', 'sub-bc-centre-for-disease-control', 'administrative_consolidation', 'The divisions brought under one administration as the Vancouver Bureau',
         '1977', 'year', 'PM06', 'BCCDC Annual Report 2013, History, printed p. 7'),
    more('bccdc-1986', 'sub-bc-centre-for-disease-control', 'name_change', 'The Vancouver Bureau becomes the BC Centre for Disease Control',
         '1986', 'year', 'PM06', 'BCCDC Annual Report 2013, History, printed p. 7'),
    more('bccdc-1997', 'sub-bc-centre-for-disease-control', 'governance_transferred', 'BCCDC becomes a society, its governance moving from the ministry to the Vancouver/Richmond Health Board',
         '1997', 'year', 'PM06', 'BCCDC Annual Report 2013, History, printed p. 7', 'Incorporation and the governance transfer are two claims; neither day is known.',
         ['vancouver-richmond-health-board']),
    more('bccdc-2001', 'sub-bc-centre-for-disease-control', 'governance_transferred', 'BCCDC becomes part of the Provincial Health Services Authority',
         '2001-12', 'month', 'PM06', 'BCCDC Annual Report 2013, History, printed p. 7', None, ['provincial-health-services-authority']),
    # BC Women's, from its own chronology.
    more('grace-1927', 'sub-bc-womens-hospital', 'operational_start', 'Grace Hospital opens in Vancouver, run by the Salvation Army',
         '1927-10-02', 'day', 'PM08', 'Our Story: milestones and memories, 1927', 'A Grace Hospital founded in 1904 was in Winnipeg, not this one.'),
    more('grace-1994-02', 'sub-bc-womens-hospital', 'governance_transferred', 'The Salvation Army transfers responsibility for Grace Hospital to the provincial government; an interim board is set up',
         '1994-02', 'month', 'PM08', 'Our Story: milestones and memories, 1994'),
    more('womens-1994-03', 'sub-bc-womens-hospital', 'legal_establishment', 'British Columbia\'s Women\'s Hospital and Health Centre Society formed, joining the hospital and the Women\'s Health Centre',
         '1994-03-31', 'day', 'PM08', 'Our Story: milestones and memories, 1994', 'The society\'s formation, not the hospital\'s opening.'),
    # PHSA's corporate layer.
    more('phsa-2001', 'provincial-health-services-authority', 'legal_establishment', 'Provincial Health Services Authority created under the Society Act',
         '2001-12-12', 'day', 'PM02', 'PHSA consolidated financial statements, nature of operations, printed pp. 6-8',
         'A society coordinating provincial agencies, not a successor of the regional boards.'),
    more('phsa-branches-2001', 'provincial-health-services-authority', 'amalgamation', 'The agencies\' societies amalgamate as PHSA branch societies (cancer, disease control, mental health, transplant, Children\'s and Women\'s among them)',
         '2001-12-31', 'day', 'PM03', 'BC Mental Health Society Branch financial statements, printed p. 5, introductory notes',
         'Five branch names are evidenced; that there were seven is not. HSSBC and BCEHS were not among them.',
         ['sub-bc-cancer', 'sub-bc-centre-for-disease-control']),
    more('bcshs-2026', 'bc-shared-health-services', 'legal_establishment', 'BC Shared Health Services incorporated as a society (S0085000)',
         '2026-04-01', 'day', 'PM29', 'BC Registries society filings, 1 April 2026 entry S0085000',
         'A stand-alone society and a member of HEABC, not part of it. Functions move to it in waves after this date (HSA\'s published BCSHS answers).'),
    # Direct ministry programs.
    more('msc-1968', 'sub-medical-services-commission', 'legal_establishment', 'Medical Services Commission established under the Medical Service Act',
         '1968-07-01', 'day', 'PM46', 'MSC financial statements 2002 (Blue Book), printed p. 6, Note 1',
         'The commission administers the Medical Services Plan; the two have related but separate histories.'),
    more('pharmacare-1974', 'sub-bc-pharmacare', 'operational_start', 'PharmaCare begins under the Ministry of Human Resources',
         '1974', 'year', 'PM48', 'PharmaCare Trends 2022/23, history, printed pp. 7-9'),
    more('pharmacare-1987', 'sub-bc-pharmacare', 'functions_transferred', 'PharmaCare\'s administration moves from Human Resources to Health',
         '1987', 'year', 'PM48', 'PharmaCare Trends 2022/23, history, printed pp. 7-9'),
    # The ministry, by its functions rather than its names.
    more('health-welfare-1946', 'department-of-health-and-welfare-1946', 'legislation_assented', 'Department of Health and Welfare Act assented: Public Health and Social Welfare branches; Provincial Board of Health references redirected; Provincial Secretary functions may transfer',
         '1946-04-11', 'day', 'PM36', 'SBC 1946 c. 31, sections 2-4, 7-12',
         'It came into force by proclamation on 1 October 1946 (see the primary-evidence follow-up).'),
    more('hshi-1959', 'department-of-health-services-and-hospital-insurance-1959', 'functions_transferred', 'Health Services and Hospital Insurance brings together the Health Branch, Mental Health Services (from the Provincial Secretary) and the BC Hospital Insurance Service',
         '1959-03-20', 'day', 'PM38', 'Department of Health Services and Hospital Insurance Act, RS 1960 c. 102 (from 1959 c. 38), sections 5-11'),
    more('health-planning-2004', 'ministry-of-health-planning-2001', 'functions_transferred', 'Health Planning disestablished; all its functions transferred to Health Services',
         '2004-01-26', 'day', 'PM41', 'OIC 37/2004, Appendix A, paragraphs 4-5', None, ['ministry-of-health-services-2001']),
    more('healthy-living-2010', 'ministry-of-healthy-living-and-sport-2008', 'functions_transferred', 'Healthy Living and Sport disestablished, its functions split three ways: sport to Community, Sport and Cultural Development, air and water human-health policy to Environment, the rest to Health Services',
         '2010-10-25', 'day', 'PM44', 'OIC 652/2010 (BC Gazette, 4 November 2010), Appendix A, paragraphs 14-15, 21, 35-37',
         'Not a merger back into Health: three ministries received its functions.', ['ministry-of-health-services-2008']),
    # Crown ownership, apart from ministerial responsibility.
    more('bctfa-build-bc-1993', 'bc-transportation-financing-authority', 'legal_establishment', 'BC Transportation Financing Authority established under the Build BC Act',
         '1993', 'year', 'CB-008', 'BCTFA financial statements 2025/26, Note 1, PDF p. 11', 'The Transportation Act replaced the Build BC Act as its basis on 31 December 2004.'),
    more('bctfa-transportation-act-2004', 'bc-transportation-financing-authority', 'legal_basis_change', 'The Transportation Act replaces the Build BC Act as BCTFA\'s legal basis',
         '2004-12-31', 'day', 'CB-008', 'BCTFA financial statements 2025/26, Note 1, PDF p. 11'),
    more('bctfa-bcrc-2010', 'bc-transportation-financing-authority', 'ownership_started', 'BC Railway Company becomes a wholly owned subsidiary of BCTFA',
         '2010-04-01', 'day', 'CB-008', 'BCTFA financial statements 2025/26, Note 1, PDF p. 11',
         'Ownership, not ministerial responsibility, which is a separate relation. BCRC continues to exist, holding the corridor leased to CN.', ['bc-railway-company']),
    more('bctfa-ticorp-2018', 'bc-transportation-financing-authority', 'ownership_started', 'Transportation Investment Corporation becomes a wholly owned subsidiary of BCTFA',
         '2018-04-01', 'day', 'CB-008', 'BCTFA financial statements 2025/26, Note 1, PDF p. 11', None, ['transportation-investment-corporation']),
    more('hpo-2010', 'bc-housing', 'functions_transferred', 'The Homeowner Protection Office\'s licensing, owner-builder authorization, research and education move to BC Housing; its Reconstruction Program goes to Finance',
         '2010-04-01', 'day', 'CB-014', 'Information Bulletin 2010HSD0024-000212, 3 March 2010, transfer list',
         'A split between two receivers, not a rename of the office.', ['sub-bc-housing-licensing-and-consumer-services']),
    more('sheriffs-1974', 'sub-bc-sheriff-services', 'amalgamation', 'Nine county sheriff offices amalgamated into one provincial Sheriff Service',
         '1974', 'year', 'CB-026', 'Information Bulletin 2024AG0027-000679, 6 May 2024, paragraph beginning "The event coincided"',
         'The first sheriff was appointed in 1857. Which nine offices, and the day, are not yet found.'),
]
institutional_file = {
    'metadata': {
        'title': 'Institutional history: PHSA agencies, health ministry functions and programs, Crown ownership and branch consolidations',
        'as_of': '2026-10-21',
        'produced_by': 'research/reviews/institutional-history-2026-10-21/convert.py',
        'conventions': {'date_precision': 'kept as stated by the source; a year is never 1 January'},
    },
    'events': institutional,
}
(ROOT / 'research/atlas/events-institutional-history.json').write_text(json.dumps(institutional_file, indent=2, ensure_ascii=False) + '\n')
print(f'{len(institutional)} further events')
