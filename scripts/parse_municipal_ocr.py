#!/usr/bin/env python3
"""Reproduce visually reviewed municipal schedules from two retained OCR passes.

OCR does not authorize an import. Each accepted table requires a reviewed layout,
all rendered rows checked, explicit cell corrections and fixed source controls.
--check-data is offline; --cache with --fetch also verifies original fingerprints.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-ocr'
PASSES = [(250, 6), (300, 3)]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(data):
    return gzip.compress((json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def amount(text):
    value = text.strip().replace('$', '').strip()
    if value in ('', '-', '—', '–'):
        return None
    if value.lower() == 'nil':
        return 0
    if not re.fullmatch(r'-?\d+(?:,\d{3})*(?:\.\d{1,2})?', value):
        raise ValueError(f'Unreviewed OCR monetary cell {text!r}')
    return int(Decimal(value.replace(',', '')) * 100)


def dollars(cents):
    return None if cents is None else cents // 100 if cents % 100 == 0 else cents / 100


def words_from_tsv(path, dpi):
    words = []
    with path.open() as f:
        for w in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            text = w.get('text', '').strip()
            if not text:
                continue
            left, top, width, height = [float(w[k]) * 72 / dpi for k in ('left', 'top', 'width', 'height')]
            words.append([left, top, left + width, top + height, text])
    return words


def extract(words, section, pass_id, raw_fields=False):
    columns = section['columns']
    selected = [w for w in words if section['y'][0] <= (w[1] + w[3]) / 2 <= section['y'][1]
                and min(v[0] for v in columns.values()) <= (w[0] + w[2]) / 2 < max(v[1] for v in columns.values())]
    pay_bounds = columns[section.get('anchorColumn', 'pay')]
    anchors = []
    for w in selected:
        if pay_bounds[0] <= (w[0] + w[2]) / 2 < pay_bounds[1]:
            if w[4] in section.get('reviewedAnchorTokens', []):
                anchors.append(w)
                continue
            try:
                if amount(w[4]) is not None:
                    anchors.append(w)
            except ValueError:
                pass
    anchors.sort(key=lambda w: (w[1] + w[3]) / 2)
    if len(anchors) != section['rowCount']:
        raise ValueError(f"{pass_id}: expected {section['rowCount']} pay anchors, got {len(anchors)}")
    groups = [{field: [] for field in columns} for _ in anchors]
    for w in selected:
        if w[4] in section.get('ignoreTokens', []):
            continue
        at = min(range(len(anchors)), key=lambda i: abs((anchors[i][1] + anchors[i][3]) / 2 - (w[1] + w[3]) / 2))
        if abs((anchors[at][1] + anchors[at][3]) / 2 - (w[1] + w[3]) / 2) > section.get('maxRowDistance', 10):
            raise ValueError(f'Unassigned OCR table fragment {w[4]!r}')
        field = next((f for f, (a, b) in columns.items() if a <= (w[0] + w[2]) / 2 < b), None)
        if field is None:
            raise ValueError(f'Unassigned OCR column {w[4]!r}')
        groups[at][field].append(w)
    result = []
    used = set()
    for i, group in enumerate(groups):
        row = {}
        for field, cells in group.items():
            # Layouts accepted here contain single-line rows; multiline sources
            # need their own reviewed layout, not a guessed reading order.
            text_fields = section.get('textColumns', ['name', 'position'])
            if field not in text_fields:
                cells = [w for w in cells if w[4] not in section.get('currencyTokens', ['$', 'S', '§', 'S$', '§$', 'iS', '$-'])]
            text = ' '.join(w[4] for w in sorted(cells, key=lambda w: w[0])).strip()
            for at, fix in enumerate(section.get('corrections', [])):
                if fix['pass'] == pass_id and fix['row'] == i and fix['field'] == field:
                    if text != fix['before']:
                        raise ValueError(f'Changed reviewed OCR correction at row {i} {field}: {text!r}')
                    text = fix['after']
                    used.add(at)
            row[field] = (text or None) if raw_fields or field in text_fields else amount(text)
        if not row.get('name') or row.get('pay') is None or (not raw_fields and row['pay'] < 0):
            raise ValueError(f'Invalid OCR person/pay row {i}')
        result.append(row)
    required = {at for at, f in enumerate(section.get('corrections', [])) if f['pass'] == pass_id}
    if used != required:
        raise ValueError('An explicit OCR correction was not consumed')
    return result


def validate_section(report, section, evidence):
    passes = section.get('passes', ['250-6', '300-3'])
    if len(passes) != 2 or len(set(passes)) != 2:
        raise ValueError('Two distinct reviewed OCR passes are required')
    parsed = [extract(evidence['words'][key], section, key) for key in passes]
    compared = [[{f: v for f, v in row.items() if f not in section.get('evidenceOnlyColumns', [])} for row in rows] for rows in parsed]
    if compared[0] != compared[1]:
        differences = [(i, a, b) for i, (a, b) in enumerate(zip(*compared)) if a != b]
        raise ValueError(f"{report['id']} page {section['page']}: OCR passes differ: {differences}")
    rows = parsed[0]
    controls = []
    for field, expected in section['controlsCents'].items():
        actual = sum(r.get(field) or 0 for r in rows)
        residual = actual - expected
        if residual != section.get('reviewedResidualsCents', {}).get(field, 0):
            raise ValueError(f"{report['id']} {field}: unreviewed control difference {residual} cents")
        controls.append({'field': field, 'printedControl': dollars(expected), 'rowSum': dollars(actual), 'residual': dollars(residual)})
    normalized = [[report['employerSlug'], r['name'], r.get('position'), dollars(r['pay']), dollars(r.get('expenses')), section['page']] for r in rows]
    return normalized, controls


def build(config, cache, check_data=False, fetch=False, verify_ocr=False):
    sources = []
    pending = {}
    for report in config['reports']:
        report_rows = {}
        report_sources_start = len(sources)
        if not report.get('allTableRowsVisuallyReviewed'):
            raise ValueError(f"{report['id']}: full visual review required")
        if not check_data:
            path = cache / (report['id'] + '.pdf')
            if not path.exists() and fetch:
                req = urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    path.write_bytes(response.read())
            if sha(path.read_bytes()) != report['sha256']:
                raise ValueError('Original PDF fingerprint changed')
        verified_passes = set()
        for section in report['sections']:
            suffix = f"{report['employerSlug']}-{report['year']}-{section['category']}"
            evidence_path = OUT / 'evidence' / f"{report['id']}-p{section['page']:03}.json.gzip"
            evidence = json.loads(gzip.decompress(evidence_path.read_bytes()))
            if evidence['originalSha256'] != report['sha256'] or evidence['physicalPage'] != section['page']:
                raise ValueError('OCR evidence provenance changed')
            if verify_ocr:
                import fitz
                version = subprocess.check_output(['tesseract', '--version'], text=True).splitlines()[0]
                if version != config['ocrEngine']:
                    raise ValueError(f'OCR engine differs from reviewed version: {version}')
                for pass_id in section.get('passes', ['250-6', '300-3']):
                    pair = (section['page'], pass_id)
                    if pair in verified_passes:
                        continue
                    dpi, psm = map(int, pass_id.split('-'))
                    doc = fitz.open(path)
                    target = cache / f"{report['id']}-p{section['page']:03}-{pass_id}-reproduction"
                    subprocess.run(['tesseract', 'stdin', str(target), '--dpi', str(dpi), '--psm', str(psm), 'txt', 'tsv'],
                                   input=doc[section['page'] - 1].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY).tobytes('png'),
                                   env={**os.environ, 'OMP_THREAD_LIMIT': '1'}, stderr=subprocess.PIPE, check=True, timeout=90)
                    if words_from_tsv(target.with_suffix('.tsv'), dpi) != evidence['words'][pass_id]:
                        raise ValueError(f"{report['id']} p{section['page']}: original OCR words changed")
                    verified_passes.add(pair)
            rows, controls = validate_section(report, section, evidence)
            parsed = extract(evidence['words'][section.get('passes', ['250-6', '300-3'])[0]], section, section.get('passes', ['250-6', '300-3'])[0])
            report_rows.setdefault(section['category'], []).extend(parsed)
            name = f"{suffix}-p{section['page']}.json.gzip"
            data = packed(rows)
            pending[name] = data
            source = {'id': f"municipal-ocr-{suffix}-p{section['page']}", 'employerSlug': report['employerSlug'],
                      'employerName': report['employerName'], 'sector': 'Municipalities', 'year': report['year'],
                      'periodType': 'calendar', 'periodStart': f"{report['year']}-01-01", 'periodEnd': f"{report['year']}-12-31",
                      'category': section['category'], 'scope': section['category'], 'file': name, 'dataSha256': sha(data),
                      'sha256': report['sha256'], 'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['indexUrl'],
                      'title': f"{report['employerName']} {report['year']} SOFI: {section['category']}",
                      'status': 'accepted', 'rowCount': len(rows), 'totalRemuneration': dollars(sum(round(r[3] * 100) for r in rows)),
                      'totalExpenses': dollars(sum(round((r[4] or 0) * 100) for r in rows)),
                      'pages': [section['page']], 'currency': 'CAD', 'amountUnit': 'dollars',
                      'threshold': 75000 if section['category'] == 'employee-remuneration' else None,
                      'thresholdComparison': section.get('thresholdComparison', '>') if section['category'] == 'employee-remuneration' else None,
                      'notes': report.get('notes', []) + section.get('notes', []) + ['Two Tesseract passes use the same OCR engine and are not independent originals. Every accepted rendered row was visually checked; reviewed cell corrections and exact control residuals are retained.'],
                      'validation': {'method': 'Two OCR passes plus complete visual table review', 'physicalPagesVisuallyReviewed': [section['page']],
                                     'ocrPasses': section.get('passes', ['250-6', '300-3']), 'printedControls': controls,
                                     'corrections': section.get('corrections', []), 'evidenceFile': str(evidence_path.relative_to(OUT)),
                                     'evidenceSha256': sha(evidence_path.read_bytes())}}
            if section.get('publicWarning'):
                source['publicWarning'] = section['publicWarning']
            sources.append(source)
        for category, control_config in report.get('aggregateControls', {}).items():
            actual_rows = report_rows[category]
            if len(actual_rows) != control_config['rowCount']:
                raise ValueError('Incomplete multipage OCR cohort')
            controls = []
            for field, expected in control_config['controlsCents'].items():
                actual = sum(r.get(field) or 0 for r in actual_rows)
                residual = actual - expected
                if residual != control_config.get('reviewedResidualsCents', {}).get(field, 0):
                    raise ValueError(f"{report['id']}: multipage {field} residual {residual}")
                controls.append({'field': field, 'printedControl': dollars(expected), 'rowSum': dollars(actual), 'residual': dollars(residual)})
            for source in sources[report_sources_start:]:
                if source['category'] == category:
                    source['validation']['wholeScheduleControls'] = controls
                    source['validation']['wholeScheduleRows'] = len(actual_rows)
    manifest = {'version': 1, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
    if check_data:
        old = json.loads((OUT / 'sources.json').read_text())
        if old != manifest:
            raise ValueError('OCR manifest does not reproduce from reviewed evidence')
        for name, data in pending.items():
            if (OUT / name).read_bytes() != data:
                raise ValueError(f'{name}: normalized OCR data changed')
    else:
        for name, data in pending.items():
            (OUT / name).write_bytes(data)
        (OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cohorts': len(sources), 'rows': sum(s['rowCount'] for s in sources), 'originalHashesVerified': not check_data}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-ocr'))
    parser.add_argument('--check-data', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--verify-ocr', action='store_true', help='Re-run both pinned OCR passes against original PDF pages')
    args = parser.parse_args()
    if args.check_data and (args.fetch or args.verify_ocr):
        parser.error('--check-data is offline and cannot be combined with --fetch or --verify-ocr')
    args.cache.mkdir(parents=True, exist_ok=True)
    build(json.loads((OUT / 'reviewed-layouts.json').read_text()), args.cache, args.check_data, args.fetch, args.verify_ocr)
