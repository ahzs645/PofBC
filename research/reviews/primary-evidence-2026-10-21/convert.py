"""Converts the primary-evidence follow-up (21 October 2026) into the history's own shapes: the
dated events it recovers, and the two bodies it adds (the Homeowner Protection Office and the
Provincial Rental Housing Corporation).

Run from the repository root:  python3 -I research/reviews/primary-evidence-2026-10-21/convert.py

Writes research/atlas/events-primary-evidence.json and research/history/bodies-primary-evidence.json.
The health bodies themselves (designations, names, ministries, the societies' registry lives) are
written by research/reviews/institutional-history-2026-10-21/convert.py, which reads this package
as well, so one generator owns that file.

Every date keeps the role its source gives it: an order's approval, a statute's commencement, a
Gazette's publication, a registry's effective date. A year stays a year. An order-made date is not
called a commencement, and a registry dissolution is not called an asset transfer.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / 'PofBC-primary-evidence-followup-2026-10-21.json').read_text())
SRC = {source['id']: source for source in DATA['sources']}


def url(source_id):
    return SRC[source_id]['url']


def pin(source_id):
    return SRC[source_id].get('pinpoint') or SRC[source_id].get('title')


def event(id, subject, type, title, start, precision, source, locator=None, notes=None, related=None):
    return {
        'id': f'atlas:primary-evidence-{id}',
        'subject_id': subject,
        'related_subject_ids': related or [],
        'event_type': type,
        'title': title,
        'date': {'start': start, 'end': None, 'precision': precision, 'range_end_inclusive': False},
        'temporal_status': 'source_reported_past',
        'certainty': 'documented',
        'evidence': {'source_url': url(source), 'locator': locator or pin(source), 'observed_on': '2026-10-21'},
        'interpretation_notes': notes,
        'reviewed_on': '2026-10-21',
    }


HEALTH_1976 = 'ministry-of-health-1976'
events = [
    # The regional health system, 1995-2002.
    event('twenty-boards-1995', HEALTH_1976, 'designation', 'M597/1995 designates a set of twenty regional health boards, repealing their individual regulations',
          '1995-12-06', 'day', 'HDS053', 'M597/1995, made 6 December 1995 (Reg. 521/95)',
          'The order-made day. The boards\' earlier individual designations keep their own dates; nine rural boards of this set were not continued in 1997.'),
    event('hierarchy-1997', HEALTH_1976, 'legislation_in_force', 'Health Authorities Amendment Act, 1997: councils\' regional-service budgets go straight to the minister, councils stop reporting to boards, and the minister approves bylaws',
          '1997-08-25', 'day', 'HT30', None,
          'Councils and boards answered to the minister throughout; this changes the line between council and board, not the ministry.'),
    event('cfm-programs-1997', 'ministry-for-children-and-families-1996', 'program_accountability_observed', 'Health authorities deliver child and youth programs (public-health nursing, child and youth mental health, infant development) under the Ministry for Children and Families\' policy direction',
          '1997', 'year', 'HT24', 'Auditor General 1998 review, printed pp. 1 and 33-34',
          'Observed in the April-July 1997 review; it does not say which of the 52 bodies delivered each program.'),
    event('health-planning-2001', 'ministry-of-health-planning-2001', 'functions_transferred', 'Health becomes Health Services, which keeps the Health Authorities Act; Health Planning takes strategic planning, policy, resource allocation, capital planning and evaluation',
          '2001-06-05', 'day', 'HT26', 'OIC 565/2001, Appendix A ss. 37-43; Schedule B ss. 11-12',
          'A split of functions: the authorities answered to Health Services, with Health Planning setting system policy beside it.', ['ministry-of-health-services-2001']),
    event('society-governors-2001', 'ministry-of-health-services-2001', 'appointment', 'The seven community health services societies\' governors replaced by the new authorities\' appointees (M298-M305/2001)',
          '2001-12-12', 'day', 'HT01', 'M298/2001 to M305/2001, single-page orders',
          'Appointments only: not a dissolution, a conveyance of assets or an amalgamation.'),
    event('societies-dissolved-2002', 'ministry-of-health-services-2001', 'dissolution', 'The seven community health services societies dissolved, as the corporate registry records',
          '2002-02-15', 'day', 'HT16', 'OrgBook BC: Conversion Society Dissolution (Event:CONVSDIS) for S0036593-S0036599',
          'How and to whom their assets passed is not found.'),
    # The health department, 1893-1977.
    event('health-act-1893', 'department-of-health-and-welfare-1946', 'function_origin', 'Health Act provides for a Provincial Board of Health and local boards of health',
          '1893-04-18', 'day', 'RF11', None, 'An antecedent of the provincial health function, not the start of the department.'),
    event('social-welfare-1934', 'department-of-the-provincial-secretary-1872', 'unit_observed', 'A Social Welfare Section in the Provincial Secretary\'s department',
          '1934-10-22', 'day', 'RF12', None, 'Known by this day (an appointment to it took effect 12 November 1934); not its creation.'),
    event('health-welfare-commencement-1946', 'department-of-health-and-welfare-1946', 'statutory_commencement', 'The Department of Health and Welfare Act comes into force',
          '1946-10-01', 'day', 'RF01', 'OIC 2060/1946, approved 10 September 1946; proclaimed in the British Columbia Gazette, 3 October 1946, p. 2905',
          'Assented 11 April 1946; proclamation authorized 10 September; published 3 October.'),
    event('provincial-secretary-transfer-1946', 'department-of-health-and-welfare-1946', 'functions_transferred', 'Order transferring listed health and welfare functions from the Provincial Secretary to the new department',
          '1946-09-28', 'day', 'RF03', None, 'The order\'s approval; when each transfer took effect is not separately recovered.', ['department-of-the-provincial-secretary-1872']),
    event('reversal-1947', 'department-of-the-provincial-secretary-1872', 'functions_transferred', 'Physiotherapists and Massage Practitioners Act and Welfare Institutions Licensing Act duties return to the Provincial Secretary',
          '1947-04-23', 'day', 'RF05', None, None, ['department-of-health-and-welfare-1946']),
    event('split-1959', 'department-of-health-and-welfare-1946', 'department_split', 'Health and Welfare splits into Health Services and Hospital Insurance and Social Welfare, both in force',
          '1959-03-20', 'day', 'RF07', 'OIC 558/1959 and OIC 559/1959',
          'The same day Provincial Secretary mental-health responsibilities moved to Health Services and Hospital Insurance.',
          ['department-of-health-services-and-hospital-insurance-1959', 'department-of-social-welfare-1959']),
    event('rename-1973', 'department-of-health-services-and-hospital-insurance-1959', 'statutory_rename', 'Renamed the Department of Health by statute',
          '1973-11-07', 'day', 'RF13', None, 'The statute\'s date; its commencement is not separately recovered.', ['department-of-health-1973']),
    event('health-act-title-1977', HEALTH_1976, 'legislative_title_amendment', 'Ministerial Titles Act amends the Department of Health Act to the Ministry of Health Act',
          '1977-09-27', 'day', 'RF26', None,
          'Assent. Proclamation was authorized on 21 October 1977; the proclamation itself is not retrieved. The ministry had been named by OIC 3199/1976 a year before.'),
    # PHSA's registered identities.
    event('phsa-amalgamation-2018-04', 'provincial-health-services-authority', 'amalgamation', 'PHSA and five branch societies (cancer, disease control, mental health, transplant, Children\'s and Women\'s) amalgamate as one society (S0069120)',
          '2018-04-01', 'day', 'RF15', 'Registrar notice, 1 April 2018 entry',
          'Predecessors S0044011, S0044073, S0044074, S0044076, S0044077, S0044078.',
          ['sub-bc-cancer', 'sub-bc-centre-for-disease-control', 'sub-bc-mental-health-and-substance-use-services', 'sub-bc-transplant', 'sub-bc-childrens-hospital', 'sub-bc-womens-hospital']),
    event('phsa-amalgamation-2018-06', 'provincial-health-services-authority', 'amalgamation', 'PHSA and BC Clinical and Support Services Society amalgamate (S0069572)',
          '2018-06-29', 'day', 'RF16', 'Registrar notice, 29 June 2018 entry', 'Predecessors S0069120 and S0054278.'),
    event('cancer-society-1974', 'sub-bc-cancer', 'registration', 'Cancer Control Agency of British Columbia registered as a society (S0011125)',
          '1974-09-09', 'day', 'RF17', 'BC Corporate Registry credential history',
          'The society\'s registration, before the 31 October 1974 provincial takeover of cancer care.'),
    event('cancer-name-1990', 'sub-bc-cancer', 'registry_name_change', 'The registry records the society\'s new name, British Columbia Cancer Agency',
          '1990-02-14', 'day', 'RF17', 'BC Corporate Registry credential history', 'The day for the 1990 rename already recorded by year.'),
    event('transplant-society-1986', 'sub-bc-transplant', 'registration', 'British Columbia Transplant Society registered (S0021154)',
          '1986-04-01', 'day', 'RF19', 'BC Corporate Registry credential history'),
    event('mental-health-society-1987', 'sub-bc-mental-health-and-substance-use-services', 'registration', 'British Columbia Mental Health Society registered (S0023123), to operate Riverview',
          '1987-12-11', 'day', 'RF18', 'BC Corporate Registry credential history'),
    event('cw-amalgamation-1997', 'sub-bc-childrens-hospital', 'amalgamation', 'Children\'s and Women\'s Health Centre of British Columbia formed by amalgamation (S0037131)',
          '1997-07-15', 'day', 'RF20', 'BC Corporate Registry credential history',
          'Which societies were its parties is not recovered.', ['sub-bc-womens-hospital']),
    event('bccdc-society-1997', 'sub-bc-centre-for-disease-control', 'registration', 'British Columbia Centre for Disease Control Society registered (S0037212)',
          '1997-08-06', 'day', 'RF21', 'BC Corporate Registry credential history'),
    event('bccdc-amalgamation-2001', 'sub-bc-centre-for-disease-control', 'amalgamation', 'British Columbia Centre for Disease Control and Prevention Society formed by amalgamation (S0042940)',
          '2001-04-02', 'day', 'RF23', 'BC Corporate Registry credential history',
          'The 1997 society (S0037212) and a January 2001 society of the same new name (S0042656) end that day; the full list of parties is not recovered.'),
    # Crown and branch histories.
    event('sheriffs-1973', 'sub-bc-sheriff-services', 'roster_observed', 'Nine sheriffs, one for each bailiwick: the counties of Westminster, Cariboo (outside the Peace River districts), Kootenay, Victoria, Nanaimo, Yale, Vancouver and Prince Rupert, and the Peace River portion of Cariboo',
          '1973-07-05', 'day', 'CS01', None,
          'A Gazette roster (notice dated 21 February 1972): the offices as they stood before the 1974 reorganization, not the days they were established.'),
    event('sheriffs-jurisdiction-1974', 'sub-bc-sheriff-services', 'legislation_assented', 'Statute Law Amendment Act, 1974 gives sheriffs province-wide jurisdiction',
          '1974-06-20', 'day', 'CS04', 'SBC 1974 c. 87, s. 35',
          'The jurisdictional statute; the administrative amalgamation of the nine offices is dated only to 1974.'),
    event('ferry-authority-2003', 'bc-ferry-corporation', 'related_body_origin', 'B.C. Ferry Authority established under the Coastal Ferry Act, as the sole voting shareholder of the company the corporation became',
          '2003-04-01', 'day', 'CS07', 'Coastal Ferry Act, SBC 2003 c. 14, ss. 2 and 89',
          'Not the British Columbia Ferry Authority of 1964 (the renamed Toll Highways and Bridges Authority).'),
    event('bc-housing-responsibility-1999', 'bc-housing', 'responsibility_changed', 'Ministerial responsibility for BC Housing and PRHC moves from Employment and Investment to Social Development and Economic Security',
          '1999-07-21', 'day', 'CS16', None, None, ['provincial-rental-housing-corporation', 'ministry-of-social-development-and-economic-security-1999']),
]

# OIC 3199/1976: the departments' new names as ministries, one event on each resulting ministry.
EPISODE = {
    'Ministry of the Provincial Secretary and Travel Industry': 'ministry-of-the-provincial-secretary-and-travel-industry-1976',
    'Ministry of Finance': 'ministry-of-finance-1976',
    'Ministry of the Attorney-General': 'ministry-of-the-attorney-general-1976',
    'Ministry of Agriculture': 'ministry-of-agriculture-1976',
    'Ministry of Education': 'ministry-of-education-1976',
    'Ministry of Municipal Affairs and Housing': 'ministry-of-municipal-affairs-and-housing-1976',
    'Ministry of Mines and Petroleum Resources': 'ministry-of-mines-and-petroleum-resources-1976',
    'Ministry of Forests': 'ministry-of-forests-1976',
    'Ministry of Labour': 'ministry-of-labour-1976',
    'Ministry of Health': 'ministry-of-health-1976',
    'Ministry of Highways and Public Works': 'ministry-of-highways-and-public-works-1976',
    'Ministry of Economic Development': 'ministry-of-economic-development-1976',
    'Ministry of Energy, Transport and Communications': 'ministry-of-energy-transport-and-communications-1976',
    'Ministry of Human Resources': 'ministry-of-human-resources-1976',
    'Ministry of the Environment': 'ministry-of-the-environment-1976',
    'Ministry of Consumer and Corporate Affairs': 'ministry-of-consumer-and-corporate-affairs-1976',
    'Ministry of Recreation and Conservation': 'ministry-of-recreation-and-conservation-1976',
}
for row in DATA['ministry_name_changes_1976']:
    subject = EPISODE[row['resulting_name']]
    events.append(event(f"oic-3199-{subject}", subject, 'executive_names_directive',
                        f"OIC 3199/1976 names the {' and the '.join(row['former_names'])} the {row['resulting_name']}",
                        '1976-10-28', 'day', 'RF25', 'Two-page order; approval stamp 28 October 1976 and complete operative list',
                        'An executive naming order: it does not by itself move assets or functions. The statutory titles followed in 1977.'))
assert len(events) == len({e['id'] for e in events}), 'duplicate event ids'

(ROOT / 'research/atlas/events-primary-evidence.json').write_text(json.dumps({
    'metadata': {
        'title': 'Primary-evidence follow-up: health designations and ministries, the health department 1893-1977, PHSA registry identities, sheriffs, ferries and housing',
        'as_of': '2026-10-21',
        'produced_by': 'research/reviews/primary-evidence-2026-10-21/convert.py',
        'conventions': {'date_precision': 'kept as stated by the source; a year is never 1 January'},
    },
    'events': events,
}, indent=2, ensure_ascii=False) + '\n')

# The two bodies the follow-up adds.
bodies = [
    {
        'id': 'homeowner-protection-office',
        'name': 'Homeowner Protection Office',
        'shortName': 'HPO',
        'kind': 'agency',
        'established': '1998-09-21',
        'establishedMeaning': 'established by section 3 of the Homeowner Protection Act, in force that day (OIC 1188/1998, B.C. Reg. 309/98); it opened on 1 October 1998',
        'ended': '2010-04-01',
        'becameId': None,
        'predecessorIds': [],
        'serviceSuccessorIds': ['bc-housing'],
        'responsible': [{'ministry': 'Ministry of Municipal Affairs', 'from': '1998-09-21', 'to': '2001-06-05', 'source': url('CS22'),
                         'locator': 'OIC 1146/1998, approved 16 September 1998: administration of the Act assigned to the Minister of Municipal Affairs',
                         'note': 'Ends with that ministry; who answered for the office from 2001 is not in this research.'}],
        'description': ('Provincial office created in 1998, after the leaky-condo crisis, to license residential builders, protect buyers of new homes and run the '
                        'Reconstruction Program of loans to owners of failed buildings. On 1 April 2010 it was folded into others: licensing, owner-builder '
                        'authorization, research and education went to BC Housing, and the Reconstruction Program to the Ministry of Finance.'),
        'source': url('CS09'),
        'otherSources': [url('CS22'), url('CS11'), url('CS20')],
    },
    {
        'id': 'provincial-rental-housing-corporation',
        'name': 'Provincial Rental Housing Corporation',
        'shortName': 'PRHC',
        'kind': 'crown-corporation',
        'established': '1973',
        'establishedMeaning': 'acquired by the Province; the company itself was incorporated as Pemco Holdings Ltd. on 13 December 1961 (No. 52129)',
        'ended': None,
        'becameId': None,
        'predecessorIds': [],
        'names': [
            {'name': 'Pemco Holdings Ltd.', 'to': '1976-05-07'},
            {'name': 'British Columbia Housing Corporation', 'from': '1976-05-07', 'to': '1976-12-21', 'source': url('CS13'), 'locator': pin('CS13')},
            {'name': 'Provincial Rental Housing Corporation', 'from': '1976-12-21', 'source': url('CS14'), 'locator': pin('CS14')},
        ],
        'responsible': [],
        'description': ('The Province\'s holding company for social and low-cost rental housing. One corporation throughout (BC0052129): incorporated '
                        'privately as Pemco Holdings Ltd. in 1961, acquired by the Province in 1973, and renamed twice in 1976. BC Housing administers it, '
                        'came to control it through board-appointment changes on 26 January 2024, and consolidated it in its accounts from 31 March 2024. '
                        'No share transfer is shown, and administration is not ownership.'),
        'source': url('CS12'),
        'otherSources': [url('CS15'), url('CS16'), url('CS19')],
    },
]
body_events = [
    event('hpo-opening-1998', 'homeowner-protection-office', 'operational_start', 'Homeowner Protection Office opens', '1998-10-01', 'day', 'CS11',
          notes='The opening, after its legal establishment on 21 September.'),
    event('pemco-1961', 'provincial-rental-housing-corporation', 'incorporation', 'Pemco Holdings Ltd. incorporated (No. 52129)', '1961-12-13', 'day', 'CS12',
          notes='A private company; the incorporation certificate itself is not obtained.'),
    event('pemco-1973', 'provincial-rental-housing-corporation', 'ownership_started', 'The Province acquires Pemco Holdings Ltd.', '1973', 'year', 'CS16',
          notes='The day and instrument are not found.'),
    event('prhc-control-2024', 'provincial-rental-housing-corporation', 'control_started', 'BC Housing gains control of PRHC through governance and board-appointment changes', '2024-01-26', 'day', 'CS19',
          notes='Control, not a share transfer. BC Housing consolidated PRHC in its accounts from 31 March 2024.', related=['bc-housing']),
]
data = json.loads((ROOT / 'research/atlas/events-primary-evidence.json').read_text())
data['events'] += body_events
(ROOT / 'research/atlas/events-primary-evidence.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

(ROOT / 'research/history/bodies-primary-evidence.json').write_text(json.dumps({
    'note': ('Bodies added by the primary-evidence follow-up of 21 October 2026 (research/reviews/primary-evidence-2026-10-21). '
             'Generated by its convert.py: edit the research and re-run, not this file.'),
    'records': bodies,
}, indent=2, ensure_ascii=False) + '\n')
print(f'{len(data["events"])} events, {len(bodies)} bodies')
