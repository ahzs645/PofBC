#!/usr/bin/env python3
"""Reproduce reviewed northern municipal disclosures from two native-text readers."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-wave-north'
CONFIG = OUT / 'reviewed-inputs.json'

def money(text):
    text = text.replace('$', '').replace(' ', '')
    if text in ('', '-', '–', '—'):
        return None
    if not re.fullmatch(r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?', text):
        raise ValueError('Unreviewed monetary cell: ' + text)
    return int(Decimal(text.replace(',', '')) * 100)


def join(words):
    groups = []
    for word in sorted(words, key=lambda w: (w[1], w[0])):
        if groups and abs(word[1] - groups[-1][0][1]) < 4:
            groups[-1].append(word)
        else:
            groups.append([word])
    return ' '.join(' '.join(w[4] for w in sorted(group, key=lambda w: w[0])) for group in groups)


def extract(words, config, section):
    page, y0, y1 = section
    columns = config['columns']
    name_column = columns.get('name', columns.get('combined'))
    words = [w for w in words if y0 <= w[1] < y1]
    anchors = sorted([w for w in words if name_column[0] <= w[0] < min(name_column[1], 165)
                      and (',' in w[4] or w[4] == 'ESTATE')], key=lambda w: w[1])
    rows = []
    for i, anchor in enumerate(anchors):
        low = anchor[1] - 1.5
        high = anchors[i + 1][1] - 1.5 if i + 1 < len(anchors) else y1
        cells = {key: [] for key in columns}
        for word in words:
            if low <= word[1] < high:
                field = next((key for key, (left, right) in columns.items()
                              if left <= (word[0] + word[2]) / 2 < right), None)
                if field:
                    cells[field].append(word)
        text = {key: join(value).strip() for key, value in cells.items()}
        if 'combined' in text:
            name, position = text['combined'].split(' - ', 1)
        else:
            name, position = text['name'], text['position']
        rows.append([name, position, money(text['pay']), money(text['expenses']), page])
    return rows

def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(data):
    raw = (json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    return gzip.compress(raw, mtime=0)


def dollars(cents):
    return None if cents is None else cents // 100 if cents % 100 == 0 else cents / 100


def read_original(path, report):
    import fitz
    doc = fitz.open(path)
    xml = subprocess.run(['pdftotext', '-bbox', str(path), '-'], capture_output=True, check=True).stdout
    pages = ET.fromstring(xml).findall('.//{*}page')
    assert report['periodEvidencePages'], report['id'] + ': no internal date evidence'
    assert any(re.search(rf"(?i)(?:ended|end:?)\s*,?\s*December\s+31,?\s*{report['year']}", doc[i - 1].get_text()) for i in report['periodEvidencePages'])
    primary, secondary = [], []
    for section in report['sections']:
        pn = section[0]
        fw = [list(w[:5]) for w in doc[pn - 1].get_text('words')]
        pw = [[float(w.attrib[k]) for k in ('xMin', 'yMin', 'xMax', 'yMax')] + [''.join(w.itertext())]
              for w in pages[pn - 1].findall('.//{*}word')]
        primary.extend(extract(fw, report, section))
        secondary.extend(extract(pw, report, section))
    assert primary == secondary, report['id'] + ': independent text readers disagree'
    assert len(primary) == report['rowCount'], report['id'] + ': named row count changed'
    assert all(r[0] and r[1] and r[2] is not None for r in primary), (report['id'], [r for r in primary if not (r[0] and r[1] and r[2] is not None)])
    assert max(r[2] for r in primary) <= report['controlsCents'][0]
    return primary


def build(cache, fetch=False, check_data=False):
    reports = json.loads(CONFIG.read_text())['reports']
    sources = []
    for report in reports:
        source_id = 'municipal-wave-north-' + report['id']
        evidence_file = 'evidence/' + report['id'] + '.json.gzip'
        if check_data:
            evidence = json.loads(gzip.decompress((OUT / evidence_file).read_bytes()))
            assert evidence['originalSha256'] == report['sha256']
            assert evidence['bothReadersAgree'] is True
            raw_rows = evidence['rows']
        else:
            path = cache / report['originalFile']
            if fetch and not path.exists():
                req = urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    path.write_bytes(response.read())
            assert sha(path.read_bytes()) == report['sha256'], report['id'] + ': original changed'
            raw_rows = read_original(path, report)
            evidence = {'originalSha256': report['sha256'], 'bothReadersAgree': True,
                        'readers': ['PyMuPDF positioned words', 'Poppler pdftotext -bbox XML words'],
                        'rowSchema': ['name', 'department' if report.get('departmentOnly') else 'position', 'remunerationCents', 'expensesCents', 'pdfPage'],
                        'rows': raw_rows}
            (OUT / evidence_file).write_bytes(packed(evidence))
        assert len(raw_rows) == report['rowCount']
        rows = [[report['employerSlug'], r[0], None if report.get('departmentOnly') else r[1], dollars(r[2]), dollars(r[3]), r[4]] for r in raw_rows]
        totals = [sum(r[j] for r in raw_rows if r[j] is not None) for j in (2, 3)]
        controls = [{'field': field, 'printedControl': dollars(control), 'rowSum': dollars(actual), 'residual': dollars(actual - control),
                     'missingCells': sum(r[idx] is None for r in raw_rows)}
                    for field, idx, control, actual in zip(['remuneration', 'expenses'], [2, 3], report['controlsCents'], totals)]
        filename = report['id'] + '.json.gzip'
        data = packed(rows)
        if check_data:
            assert (OUT / filename).read_bytes() == data
        else:
            (OUT / filename).write_bytes(data)
        warning = None
        if any(c['residual'] for c in controls):
            pay, exp = [dollars(total - control) for total, control in zip(totals, report['controlsCents'])]
            warning = (f'Known named-row sums minus source controls: remuneration ${pay:+,.2f}; expenses ${exp:+,.2f}. '
                       'Published cells are unchanged and residual causes remain unresolved. Missing expense dashes stay missing.')
        source = {'id': source_id, 'employerSlug': report['employerSlug'], 'employerName': report['employerName'], 'sector': 'Municipalities',
                  'year': report['year'], 'periodType': 'calendar', 'periodStart': report['year'] + '-01-01', 'periodEnd': report['year'] + '-12-31',
                  'category': report['category'], 'scope': report['category'], 'file': filename, 'sha256': report['sha256'], 'dataSha256': sha(data),
                  'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['sourceIndexUrl'],
                  'title': report['employerName'] + ' ' + report['year'] + ' SOFI: ' + report['category'],
                  'status': 'accepted', 'rowCount': len(rows), 'totalRemuneration': dollars(totals[0]), 'totalExpenses': dollars(totals[1]),
                  'pages': sorted({r[4] for r in raw_rows}), 'currency': 'CAD', 'amountUnit': 'dollars',
                  'threshold': 75000 if report['category'] == 'employee-remuneration' else None,
                  'thresholdComparison': report.get('thresholdComparison', '>') if report['category'] == 'employee-remuneration' else None,
                  'verifiedOn': '2026-10-31',
                  'notes': report['notes'], 'validation': {'method': 'Complete name/position-or-department/pay/expense/page agreement between two native-text readers',
                  'bothReadersAgree': True, 'renderedEdgeAndControlPagesReviewed': sorted(set([s[0] for s in report['sections']] + report['controlPages'])),
                  'internalPeriodEvidencePages': report['periodEvidencePages'], 'printedControls': controls,
                  'controlPages': report['controlPages'], 'evidenceFile': evidence_file, 'evidenceSha256': sha((OUT / evidence_file).read_bytes())}}
        if warning:
            source['publicWarning'] = warning
        if report['category'] == 'employee-remuneration':
            source['completeEmployeeSchedule'] = True
        if report['employerSlug'] == 'city-of-dawson-creek' and report['category'] == 'employee-remuneration':
            source['notes'].append('Printed threshold wording refers to remuneration and expenses exceeding $75,000. All accepted named employees also have remuneration above $75,000; threshold text is not silently generalized to other years.')
        sources.append(source)
    manifest = {'version': 1, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
    target = OUT / 'sources.json'
    if check_data:
        assert json.loads(target.read_text()) == manifest
    else:
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sources': len(sources), 'rows': sum(s['rowCount'] for s in sources),
                      'employees': sum(s['rowCount'] for s in sources if s['category'] == 'employee-remuneration'),
                      'council': sum(s['rowCount'] for s in sources if s['category'] == 'elected-officials')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-wave-north'))
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--check-data', action='store_true')
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    build(args.cache, args.fetch, args.check_data)
