"""Import the two reviewed Elections BC final-count tables from a saved HTML page.

Usage: python3 scripts/import-election-final-count.py saved-page.html output.json
The importer records declared election results, not appointments, oaths or caucus changes.
"""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import sys


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.table, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in ('td', 'th') and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def extract(data):
    parser = Tables()
    parser.feed(data.decode('utf-8'))
    totals = next(table for table in parser.tables if table[0] == ['Political Party', 'Candidates Elected'])
    candidates = next(table for table in parser.tables if table[0] == ['Electoral District', 'Candidate Elected', 'Political Party'])
    parties = {party: int(count) for party, count in totals[1:]}
    names = {name.casefold(): name for name in parties}
    records = [dict(district=district.rstrip('*').strip(), candidate=candidate,
                    party=names[party.casefold()], partyAsPrinted=party,
                    judicialRecountRequired=district.endswith('*'))
               for district, candidate, party in candidates[1:]]
    if len(records) != 93 or len({row['district'] for row in records}) != 93:
        raise ValueError('The reviewed source must contain exactly 93 distinct districts')
    if dict(Counter(row['party'] for row in records)) != parties:
        raise ValueError('Candidate rows do not reproduce the source party totals')
    recounts = sorted(row['district'] for row in records if row['judicialRecountRequired'])
    if recounts != ['Kelowna Centre', 'Ladysmith-Oceanside']:
        raise ValueError('Recount footnotes changed: review the source before importing')
    return {
        'schema': 'election-final-count/1', 'electionDate': '2026-10-24', 'parliament': 44,
        'publishedOn': '2026-11-09', 'checkedOn': '2026-11-12', 'totalSeats': 93,
        'status': 'declared_results_subject_to_judicial_recounts',
        'source': {
            'url': 'https://elections.bc.ca/news/final-results-for-the-2026-provincial-general-election-now-available/',
            'title': 'Elections BC — Final Results for the 2026 Provincial General Election Now Available',
            'locator': 'Candidates Elected summary; Electoral District / Candidate Elected / Political Party table; judicial-recount footnote',
            'sha256': sha256(data).hexdigest(),
        },
        'assemblySource': {
            'url': 'https://www.leg.bc.ca/',
            'title': 'Legislative Assembly — Happening at the Legislature',
            'checkedOn': '2026-11-12',
            'note': 'The Assembly says 44th Parliament member information will be available upon receipt of certified results on November 18, 2026.'
        },
        'note': 'The November 9 final count declares 93 candidates elected. Kelowna Centre and Ladysmith-Oceanside are subject to automatic judicial recounts. These results do not establish swearing-in, current caucus affiliation, the Speaker or a new cabinet. Other government office-holder data retains its own review date.',
        'normalization': "Conservative party in the Vancouver-Langara row is normalized to the summary table's Conservative Party; its original spelling is retained. Asterisks are stored as recount flags.",
        'parties': parties, 'candidates': records,
    }


if __name__ == '__main__':
    source, target = map(Path, sys.argv[1:3])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(extract(source.read_bytes()), ensure_ascii=False, indent=2) + '\n')
