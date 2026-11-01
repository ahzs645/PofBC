#!/usr/bin/env python3
"""Reproduce reviewed northern municipal history with two independent PDF readers."""
import argparse
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-history-north'
CONFIG = OUT / 'reviewed-layouts.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def money(text):
    text = text.strip().replace('$', '').replace(' ', '')
    if text in ('', '-', '—', '–', '‐'):
        return None
    if text.startswith('(') and text.endswith(')'):
        text = '-' + text[1:-1]
    if not re.fullmatch(r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?', text):
        raise ValueError('Unreviewed monetary cell: ' + text)
    return int(Decimal(text.replace(',', '')) * 100)


def dollars(value):
    return None if value is None else value // 100 if value % 100 == 0 else value / 100


def join(words):
    lines = []
    for word in sorted(words, key=lambda w: (w[1], w[0])):
        if lines and abs(word[1] - lines[-1][0][1]) < 4:
            lines[-1].append(word)
        else:
            lines.append([word])
    return ' '.join(' '.join(w[4] for w in sorted(line, key=lambda w: w[0])) for line in lines)


def extract(words, section):
    columns = section['columns']
    y0, y1 = section['y']
    selected = [w for w in words if y0 <= w[1] < y1 and min(c[0] for c in columns.values()) <= (w[0] + w[2]) / 2 < max(c[1] for c in columns.values())]
    bounds = columns['pay']
    anchors = []
    for w in selected:
        if bounds[0] <= (w[0] + w[2]) / 2 < bounds[1]:
            try:
                if money(w[4]) is not None:
                    anchors.append(w)
            except ValueError:
                pass
    anchors.sort(key=lambda w: w[1])
    assert len(anchors) == section['rowCount'], ('row count', section['page'], len(anchors), section['rowCount'])
    groups = [{field: [] for field in columns} for _ in anchors]
    for word in selected:
        cy = (word[1] + word[3]) / 2
        field = next(k for k, (left, right) in columns.items() if left <= (word[0] + word[2]) / 2 < right)
        if section.get('rowAssignment') == 'starts':
            # In these reviewed tables names/pay start each row, and wrapped
            # titles continue below that line, sometimes nearer the next row.
            at = max(i for i, anchor in enumerate(anchors) if word[1] >= anchor[1] - 1.5)
        else:
            at = min(range(len(anchors)), key=lambda i: abs(cy - (anchors[i][1] + anchors[i][3]) / 2))
        for override in section.get('reviewedRowOverrides', []):
            if field == override['field'] and override['y'][0] <= word[1] < override['y'][1]:
                at = override['row']
        distance = abs(cy - (anchors[at][1] + anchors[at][3]) / 2)
        if distance > section.get('maxRowDistance', 5):
            raise ValueError(('unassigned table word', section['page'], word[4], distance))
        groups[at][field].append(word)
    rows = []
    for i, group in enumerate(groups):
        row = {}
        for field, cells in group.items():
            text = join(cells)
            for fix in section.get('cellCorrections', []):
                if fix['row'] == i and fix['field'] == field:
                    assert text == fix['before'], ('reviewed correction changed', text, fix)
                    text = fix['after']
            if field in ('name', 'position', 'department'):
                if '$' in text or re.search(r'\b(?:Consolidated|Subtotal|CITY OF|Remuneration)\b', text, re.I):
                    raise ValueError(('non-person text entered row', field, text))
                row[field] = text or None
            else:
                row[field] = money(text)
        assert row['pay'] is not None
        row['pdfPage'] = section['page']
        rows.append(row)
    return rows


def read_original(path, report):
    doc = fitz.open(path)
    for proof in report['periodEvidence']:
        if 'text' in proof:
            assert proof['text'] in ' '.join(doc[proof['page'] - 1].get_text().split())
        else:
            png = doc[proof['page'] - 1].get_pixmap(dpi=proof['dpi']).tobytes('png')
            assert sha(png) == proof['renderedSha256']
    assert report['periodEvidence'], 'No reviewed reporting-period proof'
    # Read only reviewed salary pages. Unrelated financial-statement pages in
    # some originals contain invalid XML control characters in their text layer.
    pages = {}
    for number in sorted({s['page'] for s in report['sections']}):
        xml = subprocess.check_output(['pdftotext', '-f', str(number), '-l', str(number), '-bbox-layout', str(path), '-'], stderr=subprocess.PIPE)
        pages[number] = ET.fromstring(xml).find('.//{*}page')
    first, second = [], []
    for section in report['sections']:
        page = section['page']
        a = [list((*tuple(fitz.Rect(w[:4]) * doc[page - 1].rotation_matrix), w[4])) for w in doc[page - 1].get_text('words')]
        b = [[float(w.attrib[k]) for k in ('xMin', 'yMin', 'xMax', 'yMax')] + [w.text or ''] for w in pages[page].findall('.//{*}word')]
        first += extract(a, section)
        second += extract(b, section)
    assert first == second, report['key'] + ': independent PDF readers disagree'
    return first


def build(cache, check_data=False, fetch=False, inspect=False):
    reports = json.loads(CONFIG.read_text())['reports']
    sources = []
    for report in reports:
        key = report['key']
        evidence_file = 'evidence/' + key + '.json.gzip'
        if check_data:
            evidence = json.loads(gzip.decompress((OUT / evidence_file).read_bytes()))
            assert evidence['originalSha256'] == report['sha256']
            raw = evidence['rows']
        else:
            path = cache / report['originalFile']
            if fetch and not path.exists():
                request = urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'})
                path.write_bytes(urllib.request.urlopen(request, timeout=45).read())
            assert sha(path.read_bytes()) == report['sha256'], key + ': original fingerprint changed'
            raw = read_original(path, report)
            evidence = {'originalSha256': report['sha256'], 'independentReaders': ['PyMuPDF positioned words', 'Poppler bbox-layout words'], 'allRowFieldsAgree': True, 'rows': raw}
        assert len(raw) == report['rowCount']
        if report['nameDisclosure'] == 'not-published':
            assert all('name' not in r and r.get('position') for r in raw)
        else:
            assert all(r.get('name') for r in raw)
        controls = []
        for field, expected in report['controlsCents'].items():
            actual = sum(r.get(field) for r in raw if r.get(field) is not None)
            residual = actual - expected
            if not inspect:
                assert residual == report.get('reviewedResidualsCents', {}).get(field, 0), (key, field, actual, expected, residual)
            controls.append({'field': field, 'printedOrDerivedControl': dollars(expected), 'knownCellSum': dollars(actual), 'residual': dollars(residual), 'missingCells': sum(r.get(field) is None for r in raw)})
        broader = []
        for field, expected in report.get('broaderControlsCents', {}).items():
            actual = sum(r.get(field) for r in raw if r.get(field) is not None)
            if not inspect:
                assert actual - expected == report['reviewedBroaderDifferencesCents'][field], (key, field, 'broader scope difference changed')
            broader.append({'field': field, 'scope': 'All employees including under-threshold aggregate; compared with known published named-position cohort only',
                            'printedAllEmployeeControl': dollars(expected), 'knownDisclosedCohortSum': dollars(actual),
                            'difference': dollars(actual - expected), 'underThresholdComponent': None,
                            'namedOnlyControlAvailable': False})
        if inspect:
            print(json.dumps({'key': key, 'rows': len(raw), 'first': raw[0], 'last': raw[-1], 'controls': controls}, ensure_ascii=False))
            continue
        normalized = [[report['employerSlug'], r.get('name'), r.get('position'), dollars(r['pay']), dollars(r.get('expenses')), r['pdfPage']] for r in raw]
        data = packed(normalized)
        evidence_bytes = packed(evidence)
        filename = key + '.json.gzip'
        warning = report.get('publicWarning')
        if any(c['residual'] for c in controls):
            label = 'council' if report.get('category') == 'elected-officials' else 'employee'
            warning = (warning + ' ' if warning else '') + 'Known printed ' + label + ' cells minus source controls: ' + '; '.join(f"{c['field']} {c['residual']:+g} CAD" for c in controls) + '. Published values are unchanged and the cause remains unconfirmed. Expense dashes stay missing.'
        for comparison in broader:
            warning = (warning + ' ' if warning else '') + (f"Named employee expenses have no issuer subtotal: known disclosed cells total ${comparison['knownDisclosedCohortSum']:,.2f}; "
                f"the printed all-employee expense control is ${comparison['printedAllEmployeeControl']:,.2f} (difference {comparison['difference']:+g} CAD). "
                'The under-threshold expense cell is blank, so the scope differs and no named-only reconciliation or zero under-threshold amount is inferred.')
        source = {'id': 'history-north-' + key, 'employerSlug': report['employerSlug'], 'employerName': report['employerName'], 'sector': 'Municipalities', 'year': report['year'], 'periodType': 'calendar', 'periodStart': report['year'] + '-01-01', 'periodEnd': report['year'] + '-12-31', 'category': report.get('category', 'employee-remuneration'), 'scope': report.get('category', 'employee-remuneration'), 'file': filename, 'dataSha256': sha(data), 'sha256': report['sha256'], 'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['sourceIndexUrl'], 'title': report['employerName'] + ' ' + report['year'] + ' SOFI employee schedule', 'status': 'accepted', 'rowCount': len(normalized), 'totalRemuneration': dollars(sum(r['pay'] for r in raw)), 'totalExpenses': dollars(sum(r.get('expenses') or 0 for r in raw)), 'pages': sorted({r['pdfPage'] for r in raw}), 'nameDisclosure': report['nameDisclosure'], 'sourceScopeDescription': report.get('scopeDescription', 'Complete published employee schedule; this threshold disclosure is not a workforce roster or an annual salary-rate table.'), 'completeEmployeeSchedule': True, 'currency': 'CAD', 'amountUnit': 'dollars', 'threshold': 75000, 'thresholdComparison': report.get('thresholdComparison'), 'verifiedOn': '2026-10-31', 'notes': report['notes'], 'validation': {'completeEmployeeSchedule': True, 'independentReaders': evidence['independentReaders'], 'everyRowFieldAgreement': True, 'periodEvidence': report['periodEvidence'], 'printedControls': controls, 'printedControlCells': report.get('printedControlCells'), 'renderedEdgesAndControlsReviewed': report['renderedEdgesAndControlsReviewed'], 'evidenceFile': evidence_file, 'evidenceSha256': sha(evidence_bytes)}}
        if warning:
            source['publicWarning'] = warning
        source['validation']['namedExpenseControlAvailable'] = 'expenses' in report['controlsCents']
        source['validation']['broaderControlComparisons'] = broader
        source['scopeDescription'] = source['sourceScopeDescription']
        if report.get('category') == 'elected-officials':
            source['title'] = report['employerName'] + ' ' + report['year'] + ' SOFI council remuneration schedule'
            source['threshold'] = None
            source.pop('completeEmployeeSchedule')
            source['validation'].pop('completeEmployeeSchedule')
            source['completeCouncilSchedule'] = True
            source['validation']['completeCouncilSchedule'] = True
        sources.append(source)
        if check_data:
            assert (OUT / filename).read_bytes() == data
            assert (OUT / evidence_file).read_bytes() == evidence_bytes
        else:
            (OUT / filename).write_bytes(data)
            (OUT / evidence_file).write_bytes(evidence_bytes)
    if inspect:
        return
    manifest = {'version': 1, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
    if check_data:
        assert json.loads((OUT / 'sources.json').read_text()) == manifest
    else:
        (OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cohorts': len(sources), 'records': sum(s['rowCount'] for s in sources)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-history-north'))
    parser.add_argument('--check-data', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--supplemental', action='store_true', help='Reproduce the separately reviewed small-village supplement')
    parser.add_argument('--council', action='store_true', help='Reproduce the separate historical council supplement')
    args = parser.parse_args()
    if args.supplemental:
        OUT = OUT / 'supplemental'
        CONFIG = OUT / 'reviewed-layouts.json'
    if args.council:
        assert not args.supplemental
        OUT = OUT / 'council'
        CONFIG = OUT / 'reviewed-layouts.json'
    args.cache.mkdir(parents=True, exist_ok=True)
    build(args.cache, args.check_data, args.fetch, args.inspect)
