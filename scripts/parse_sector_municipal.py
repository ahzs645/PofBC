#!/usr/bin/env python3
"""Reproduce reviewed municipal original employee/council schedules.

Each calendar period, table, component definition, count, source hash and control
is fixed by reviewed-layouts.json. --check-data is offline. No discovery lead is
automatically accepted, and no cell is changed to force a total to agree.
"""
import argparse
from collections import Counter
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
OUT = ROOT / 'research/salaries/sector-municipal'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def money(text):
    text = text.strip().replace('$', '').strip()
    if text in ('', '-', '–', '—'):
        return None
    if not re.fullmatch(r'-?\d+(?:,\d{3})*(?:\.\d{1,2})?', text):
        raise ValueError(f'Unreviewed monetary cell {text!r}')
    return int(Decimal(text.replace(',', '')) * 100)


def dollars(cents):
    return None if cents is None else cents // 100 if cents % 100 == 0 else cents / 100


def words_mupdf(page):
    return [list((*tuple(fitz.Rect(w[:4]) * page.rotation_matrix), w[4])) for w in page.get_text('words')]


def words_poppler(path, number):
    raw = subprocess.check_output(['pdftotext', '-f', str(number), '-l', str(number), '-bbox-layout', str(path), '-'], stderr=subprocess.PIPE)
    root = ET.fromstring(raw)
    return [[float(w.attrib['xMin']), float(w.attrib['yMin']), float(w.attrib['xMax']), float(w.attrib['yMax']), w.text or '']
            for w in root.iter() if w.tag.endswith('}word') or w.tag == 'word']


def extract(words, section, raw_fields=False):
    cols = section['columns']
    selected = [w for w in words if section['y'][0] <= (w[1] + w[3]) / 2 <= section['y'][1]
                and min(c[0] for c in cols.values()) <= (w[0] + w[2]) / 2 < max(c[1] for c in cols.values())]
    salary = cols.get('salary', cols.get('pay'))
    anchors = []
    for w in selected:
        if salary[0] <= (w[0] + w[2]) / 2 < salary[1]:
            try:
                if money(w[4]) is not None:
                    anchors.append(w)
            except ValueError:
                pass
    anchors.sort(key=lambda w: (w[1] + w[3]) / 2)
    if len(anchors) != section['rowCount']:
        raise ValueError(f"Expected {section['rowCount']} salary anchors, got {len(anchors)}")
    groups = [{f: [] for f in cols} for _ in anchors]
    for w in selected:
        if w[4] in section.get('ignoreTokens', []):
            continue
        at = min(range(len(anchors)), key=lambda i: abs((anchors[i][1] + anchors[i][3] - w[1] - w[3]) / 2))
        if abs((anchors[at][1] + anchors[at][3] - w[1] - w[3]) / 2) > section.get('maxRowDistance', 4):
            raise ValueError(f'Unassigned table word {w[4]!r}')
        field = next((f for f, (x0, x1) in cols.items() if x0 <= (w[0] + w[2]) / 2 < x1), None)
        if field is None:
            raise ValueError(f'Unassigned column word {w[4]!r}')
        groups[at][field].append(w)
    rows = []
    used = set()
    for at, group in enumerate(groups):
        row = {}
        for field, cells in group.items():
            if field not in ('name', 'position'):
                cells = [w for w in cells if w[4] not in ('$', 'S')]
            text = ' '.join(w[4] for w in sorted(cells, key=lambda w: w[0])).strip()
            for i, fix in enumerate(section.get('corrections', [])):
                if fix['row'] == at and fix['field'] == field:
                    if text != fix['before']:
                        raise ValueError('Reviewed rendered-source correction changed')
                    text = fix['after']
                    used.add(i)
            row[field] = text or None if raw_fields or field in ('name', 'position') else money(text)
        if not row.get('name') or row.get('salary', row.get('pay')) is None or ('benefits' in cols and row['benefits'] is None):
            raise ValueError(f'Missing disclosed name/remuneration component at row {at}')
        if not raw_fields and 'salary' in cols:
            row['pay'] = row['salary'] + row['benefits']
        rows.append(row)
    if used != set(range(len(section.get('corrections', [])))):
        raise ValueError('A reviewed source correction was not used')
    return rows


def build(config, cache, check_data=False, fetch=False):
    sources = []
    pending = {}
    for report in config['reports']:
        if not report.get('allRowsVisuallyReviewed'):
            raise ValueError('Complete rendered-table review required')
        if report.get('adoptionEvidence'):
            adoption = report['adoptionEvidence']
            if sha(gzip.decompress((OUT / adoption['file']).read_bytes())) != adoption['sha256']:
                raise ValueError('Retained municipal adoption evidence changed')
        path = cache / (report['key'] + '.pdf')
        if not check_data:
            if fetch and not path.exists():
                with urllib.request.urlopen(urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as r:
                    path.write_bytes(r.read())
            if sha(path.read_bytes()) != report['sha256']:
                raise ValueError('Original PDF fingerprint changed')
            doc = fitz.open(path)
        for section in report['sections']:
            evidence_file = f"evidence/{report['key']}-{section['category']}.json.gzip"
            if check_data:
                evidence = json.loads(gzip.decompress((OUT / evidence_file).read_bytes()))
                if evidence['originalSha256'] != report['sha256']:
                    raise ValueError('Retained evidence fingerprint mismatch')
            else:
                parts = []
                for part in section.get('parts', [section]):
                    page = doc[part['page'] - 1]
                    if report['year'] not in page.get_text():
                        raise ValueError('Reporting-year evidence absent from schedule page')
                    parts.append({'originalSha256': report['sha256'], 'physicalPage': part['page'],
                                  'mupdfWords': words_mupdf(page), 'popplerWords': words_poppler(path, part['page'])})
                evidence = parts[0] if 'parts' not in section else {'originalSha256': report['sha256'], 'parts': parts}
            parts = section.get('parts', [section])
            retained_parts = evidence.get('parts', [evidence])
            if len(parts) != len(retained_parts):
                raise ValueError('Retained schedule page count changed')
            a = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                 for row in extract(proof['mupdfWords'], part)]
            b = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                 for row in extract(proof['popplerWords'], part)]
            if a != b:
                raise ValueError(f"{report['key']}: PDF readers disagree: {[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]}")
            controls = []
            for field, expected in section['controlsCents'].items():
                actual = sum(r.get(field) or 0 for r in a)
                residual = actual - expected
                if residual != section.get('reviewedResidualsCents', {}).get(field, 0):
                    raise ValueError(f"{report['key']} {section['category']} {field}: changed residual {residual}")
                controls.append({'field': field, 'printedOrDerivedControl': dollars(expected), 'rowSum': dollars(actual),
                                 'residual': dollars(residual), 'basis': section.get('controlBasis', 'Printed named subtotal, or total employees less the printed under-threshold aggregate')})
            rows = [[report['employerSlug'], r['name'], r.get('position'), dollars(r['pay']), dollars(r['expenses']), r['pdfPage']] for r in a]
            name = f"{report['key']}-{section['category']}.json.gzip"
            data = packed(rows);audit = packed(evidence)
            pending[name] = data;pending[evidence_file] = audit
            source = {'id': f"sector-municipal-{report['key']}-{section['category']}", 'employerSlug': report['employerSlug'],
                'employerName': report['employerName'], 'sector': 'Municipalities', 'year': report['year'],
                'periodType': 'calendar', 'periodStart': report['year']+'-01-01', 'periodEnd': report['year']+'-12-31',
                'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['indexUrl'], 'sha256': report['sha256'],
                'file': name, 'dataSha256': sha(data), 'category': section['category'], 'scope': section['category'],
                'title': f"{report['employerName']} {report['year']} SOFI: {section['category']}", 'status': 'accepted',
                'rowCount': len(rows), 'totalRemuneration': dollars(sum(r['pay'] for r in a)),
                'totalExpenses': dollars(sum(r['expenses'] or 0 for r in a)), 'pages': [part['page'] for part in parts],
                'currency': 'CAD', 'amountUnit': 'dollars', 'threshold': 75000 if section['category']=='employee-remuneration' else None,
                'thresholdComparison': '>' if section['category']=='employee-remuneration' else None,
                'notes': report.get('notes', []) + section.get('notes', []) + [report.get('remunerationDefinition', 'Remuneration is published Salary/Base Salary plus Benefits and Other.') + ' Expenses remain separate. Published blanks and dashes remain missing; explicit zeros stay zero. Names and positions remain as disclosed.'],
                'validation': {'independentPdfReaders': ['PyMuPDF positioned words', 'Poppler bbox-layout words'],
                    'allRowFieldsAgree': True, 'physicalPagesVisuallyReviewed': [part['page'] for part in parts], 'controls': controls,
                    'evidenceFile': evidence_file, 'evidenceSha256': sha(audit), 'corrections': section.get('corrections', [])}}
            if section.get('publicWarning'):
                source['publicWarning'] = section['publicWarning']
            if report.get('adoptionEvidence'):
                source['validation']['adoptionEvidence'] = report['adoptionEvidence']
            sources.append(source)
    manifest = {'version': 1, 'rowSchema': ['employerSlug','name','position','remuneration','expenses','pdfPage'], 'sources': sources}
    if check_data:
        if json.loads((OUT/'sources.json').read_text()) != manifest:
            raise ValueError('Manifest does not reproduce from retained evidence')
        for name, data in pending.items():
            if (OUT/name).read_bytes() != data:
                raise ValueError(f'{name}: data/evidence bytes changed')
    else:
        for name, data in pending.items():
            (OUT/name).parent.mkdir(parents=True, exist_ok=True);(OUT/name).write_bytes(data)
        (OUT/'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'reports': len(config['reports']), 'cohorts': len(sources), 'rows': sum(s['rowCount'] for s in sources), 'originalsVerified': not check_data}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-sector-municipal'))
    p.add_argument('--fetch', action='store_true');p.add_argument('--check-data', action='store_true')
    args = p.parse_args();args.cache.mkdir(parents=True, exist_ok=True)
    if args.check_data and args.fetch:p.error('--check-data is offline')
    build(json.loads((OUT/'reviewed-layouts.json').read_text()), args.cache, args.check_data, args.fetch)
