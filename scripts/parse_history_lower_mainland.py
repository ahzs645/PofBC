#!/usr/bin/env python3
"""Reproduce reviewed municipal original employee/council schedules.

Each calendar period, table, component definition, count, source hash and control
is fixed by reviewed-layouts.json. --check-data is offline. No discovery lead is
automatically accepted, and no cell is changed to force a total to agree.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-history-lower-mainland'
INPUT = OUT


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def money(text):
    text = text.strip().replace('$', '').strip()
    if text in ('', '-', '–', '—', '‐'):
        return None
    if text.startswith('(') and text.endswith(')'):
        text = '-' + text[1:-1].strip()
    text = text.replace('−','-')
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


def ocr_words(raw, offset=(0, 0), dpi=300):
    result = []
    for word in csv.DictReader(io.StringIO(raw), delimiter='\t'):
        if not word['text'].strip():
            continue
        x, y, width, height = map(float, (word['left'], word['top'], word['width'], word['height']))
        result.append([x*72/dpi+offset[0], y*72/dpi+offset[1],
                       (x+width)*72/dpi+offset[0], (y+height)*72/dpi+offset[1], word['text']])
    return result


def independent_ocr(page, part, cache):
    """Reproduce pinned OCR from rendered ink, not the PDF's embedded OCR layer."""
    from PIL import Image
    recipe = part['independentOcr']
    base = cache / recipe['cacheKey']
    base.mkdir(parents=True, exist_ok=True)
    stem = base / f"p{part['page']}"
    png = stem.with_suffix('.png')
    rendered = page.get_pixmap(dpi=recipe['dpi']).tobytes('png')
    if sha(rendered) != recipe['renderedOriginalSha256']:
        raise ValueError('Pinned OCR rendered original changed')
    png.write_bytes(rendered)
    raw = {}
    words = []
    for field, (left, right) in part['columns'].items():
        target = base / f"p{part['page']}-{field}"
        tsv = target.with_suffix('.tsv')
        if not tsv.exists():
            scale = recipe['dpi']/72
            image = Image.open(png)
            image.crop((round(left*scale), round(recipe['cropY'][0]*scale),
                        round(right*scale), round(recipe['cropY'][1]*scale))).save(target.with_suffix('.png'))
            command = ['tesseract', str(target.with_suffix('.png')), str(target), '--psm', '6']
            if field != 'name':
                # This restriction applies only to actual monetary columns; names
                # and initials are never filtered through a monetary alphabet.
                command += ['-c', 'tessedit_char_whitelist=0123456789,.-()$']
            subprocess.run(command + ['tsv'], env=dict(os.environ, OMP_THREAD_LIMIT='1'),
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raw[field] = tsv.read_text()
        if sha(raw[field].encode()) != recipe['tsvSha256'][field]:
            raise ValueError('Pinned independent OCR input changed')
        words += ocr_words(raw[field], (left, recipe['cropY'][0]), recipe['dpi'])
    return words, raw


def reader_layout(part, reader):
    return part | {'corrections': part.get('corrections', []) + part.get('readerCorrections', {}).get(reader, [])}


def extract(words, section, raw_fields=False):
    cols = section['columns']
    selected = [w for w in words if section['y'][0] <= (w[1] + w[3]) / 2 <= section['y'][1]
                and not any(a <= (w[1]+w[3])/2 <= b for a,b in section.get('ignoreYRanges', []))
                and min(c[0] for c in cols.values()) <= (w[0] + w[2]) / 2 < max(c[1] for c in cols.values())]
    salary = cols[section['anchorField']] if section.get('anchorField') else cols.get('salary', cols.get('pay'))
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
        if 'rowBounds' in section:
            matching = [i for i,(lower,upper) in enumerate(section['rowBounds']) if lower <= (w[1]+w[3])/2 < upper]
            if len(matching) != 1: raise ValueError(f'Unassigned/ambiguous table word {w[4]!r}')
            at = matching[0]
        else:
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
            ordered = sorted(cells, key=lambda w: (round((w[1]+w[3])/2/2),w[0])) if field in ('name','position') and field not in section.get('singleLineTextFields', []) else sorted(cells, key=lambda w: w[0])
            text = ' '.join(w[4] for w in ordered).strip()
            for i, fix in enumerate(section.get('corrections', [])):
                if fix['row'] == at and fix['field'] == field:
                    if text != fix['before']:
                        raise ValueError('Reviewed rendered-source correction changed')
                    text = fix['after']
                    used.add(i)
            if field == 'name' and section.get('normalizeCommaWhitespace'):
                text = re.sub(r'\s*,\s*', ', ', text)
            row[field] = text or None if raw_fields or field in ('name', 'position') else money(text)
        if not row.get('name') or (row.get('salary', row.get('pay')) is None and not section.get('holdMissingSalary')):
            raise ValueError(f'Missing disclosed name/remuneration component at row {at}')
        if not raw_fields and 'salary' in cols:
            row['pay'] = None if row['benefits'] is None or row['salary'] is None else row['salary'] + row['benefits']
        if not raw_fields and section.get('nameRoleSeparator'):
            chunks = row['name'].split(section['nameRoleSeparator'],1)
            row['name'] = chunks[0].strip()
            if len(chunks)==2: row['position']=chunks[1].strip()
        for field in section.get('currencyFreeTextFields', []):
            if '$' in (row.get(field) or ''):
                raise ValueError(f'Currency token leaked into reviewed {field} field')
        if not raw_fields and row.get('total') is not None and row.get('pay') is not None and row.get('expenses') is not None:
            if row['total'] != row['pay'] + row['expenses']:
                raise ValueError('Published row total disagrees without an explicit reviewed exception')
        if not raw_fields and section.get('rowTotalField'):
            difference = row[section['rowTotalField']] - row['pay'] - row['expenses']
            if difference != section.get('reviewedRowTotalResidualsCents',{}).get(str(at),0):
                raise ValueError('Reviewed expense-inclusive row-total difference changed')
        rows.append(row)
    if used != set(range(len(section.get('corrections', [])))):
        raise ValueError('A reviewed source correction was not used')
    return rows


def build(config, cache, check_data=False, fetch=False):
    sources = []
    pending = {}
    for report in config['reports']:
        if not report.get('tablesAndEdgeFieldsVisuallyReviewed'):
            raise ValueError('Rendered table layout and edge-field review required')
        if report.get('adoptionEvidence'):
            adoption = report['adoptionEvidence']
            adoption_data = (INPUT / adoption['file']).read_bytes()
            if sha(gzip.decompress(adoption_data)) != adoption['sha256']:
                raise ValueError('Retained municipal adoption evidence changed')
            pending[adoption['file']] = adoption_data
        path = cache / (report['key'] + '.pdf')
        if not check_data:
            if fetch and not path.exists():
                with urllib.request.urlopen(urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as r:
                    path.write_bytes(r.read())
            if sha(path.read_bytes()) != report['sha256']:
                raise ValueError('Original PDF fingerprint changed')
            doc = fitz.open(path)
            for proof in report['periodEvidence']:
                if 'visualText' in proof:
                    rendered = doc[proof['page']-1].get_pixmap(dpi=proof['renderDpi']).tobytes('png')
                    if sha(rendered) != proof['renderedPageSha256']:
                        raise ValueError('Rendered calendar-period evidence changed')
                elif proof['text'] not in ' '.join(doc[proof['page']-1].get_text().split()):
                    raise ValueError('Reviewed calendar-period evidence changed')
            for proof in report.get('columnAndControlEvidence', []):
                if proof['text'] not in ' '.join(doc[proof['page']-1].get_text().split()):
                    raise ValueError('Reviewed column/control evidence changed')
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
                    proof = {'originalSha256': report['sha256'], 'physicalPage': part['page'],
                             'mupdfWords': words_mupdf(page), 'popplerWords': words_poppler(path, part['page'])}
                    if part.get('independentOcr'):
                        proof['independentOcrWords'], proof['independentOcrRawTsv'] = independent_ocr(page, part, cache)
                    parts.append(proof)
                evidence = parts[0] if 'parts' not in section else {'originalSha256': report['sha256'], 'parts': parts}
            parts = section.get('parts', [section])
            retained_parts = evidence.get('parts', [evidence])
            if len(parts) != len(retained_parts):
                raise ValueError('Retained schedule page count changed')
            a = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                 for row in extract(proof['mupdfWords'], reader_layout(part, 'embedded-ocr'))]
            b = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                 for row in extract(proof['popplerWords'], reader_layout(part, 'embedded-ocr'))]
            if a != b:
                raise ValueError(f"{report['key']}: PDF readers disagree: {[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]}")
            if any(part.get('independentOcr') for part in parts):
                c = []
                for part, proof in zip(parts, retained_parts):
                    recipe = part['independentOcr']
                    recomputed = []
                    for field, (left, right) in part['columns'].items():
                        raw = proof['independentOcrRawTsv'][field]
                        if sha(raw.encode()) != recipe['tsvSha256'][field]:
                            raise ValueError('Retained independent OCR input fingerprint changed')
                        recomputed += ocr_words(raw, (left, recipe['cropY'][0]), recipe['dpi'])
                    if recomputed != proof['independentOcrWords']:
                        raise ValueError('Retained independent OCR word coordinates changed')
                    c += [row | {'pdfPage': part['page']} for row in extract(recomputed, reader_layout(part, 'independent-ocr'))]
                if a != c:
                    raise ValueError(f"{report['key']}: independent OCR fields disagree: {[(i,x,y) for i,(x,y) in enumerate(zip(a,c)) if x!=y]}")
            held = [row for row in a if row['pay'] is None]
            if held and not (section.get('holdMissingBenefits') or section.get('holdMissingSalary')):
                raise ValueError('Missing remuneration component without a reviewed partial-cohort decision')
            if len(held) != section.get('expectedHeldRows', 0):
                raise ValueError('Reviewed held-component count changed')
            controls = []
            for field, expected in section['controlsCents'].items():
                actual = sum(r.get(field) or 0 for r in a)
                residual = actual - expected
                if residual != section.get('reviewedResidualsCents', {}).get(field, 0):
                    raise ValueError(f"{report['key']} {section['category']} {field}: changed residual {residual}")
                controls.append({'field': field, 'sourceColumnLabel': section.get('sourceColumnLabels', {}).get(field, field),
                                 'printedOrDerivedControl': dollars(expected), 'knownCellSum': dollars(actual),
                                 'residual': dollars(residual), 'basis': section.get('controlBasis', 'Printed named subtotal, or total employees less the printed under-threshold aggregate')})
            accepted_rows = [row for row in a if row['pay'] is not None]
            evidence['componentRows'] = a
            evidence['componentAmountUnit'] = 'integer-cents'
            rows = [[report['employerSlug'], r['name'], r.get('position'), dollars(r['pay']), dollars(r['expenses']), r['pdfPage']] for r in accepted_rows]
            name = f"{report['key']}-{section['category']}.json.gzip"
            data = packed(rows);audit = packed(evidence)
            pending[name] = data;pending[evidence_file] = audit
            source = {'id': f"history-lower-mainland-{report['key']}-{section['category']}", 'employerSlug': report['employerSlug'],
                'employerName': report['employerName'], 'sector': 'Municipalities', 'year': report['year'],
                'periodType': 'calendar', 'periodStart': report['year']+'-01-01', 'periodEnd': report['year']+'-12-31',
                'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['indexUrl'], 'sha256': report['sha256'],
                'file': name, 'dataSha256': sha(data), 'category': section['category'], 'scope': section['category'],
                'title': f"{report['employerName']} {report['year']} SOFI: {section['category']}", 'status': 'accepted',
                'rowCount': len(rows), 'totalRemuneration': dollars(sum(r['pay'] for r in accepted_rows)),
                'totalExpenses': dollars(sum(r['expenses'] or 0 for r in accepted_rows)), 'pages': [part['page'] for part in parts],
                'currency': 'CAD', 'amountUnit': 'dollars', 'threshold': 75000 if section['category']=='employee-remuneration' else None,
                'thresholdComparison': '>' if section['category']=='employee-remuneration' else None,
                'notes': report.get('notes', []) + section.get('notes', []) + [section.get('remunerationDefinition', report['remunerationDefinition']) + ' Expenses remain separate. Published blanks and dashes remain missing; explicit zeros stay zero. Names and positions remain as disclosed.'],
                'validation': {'independentPdfReaders': ['PyMuPDF positioned words', 'Poppler bbox-layout words'],
                    'allRowFieldsAgree': True, 'physicalPagesVisuallyReviewed': sorted(set(report.get('visualPagesReviewed', [part['page'] for part in parts])) & {part['page'] for part in parts}), 'controls': controls,
                    'evidenceFile': evidence_file, 'evidenceSha256': sha(audit), 'corrections': section.get('corrections', []),
                    'periodEvidence': report['periodEvidence'], 'namedControlUnavailable': not section['controlsCents'],
                    'sourceNamedRows': len(a), 'acceptedRows': len(accepted_rows), 'heldMissingBenefitRows': len(held),
                    'sourceRowCountsByPhysicalPage': [{'page': p['page'], 'rows': p['rowCount']} for p in parts],
                    'columnAndControlEvidence': report.get('columnAndControlEvidence', []),
                    'heldRows': [{'name':r['name'],'position':r.get('position'),'pdfPage':r['pdfPage'],
                        'knownRemunerationColumn':dollars(r.get('salary')),'benefits':None,'expenses':dollars(r.get('expenses'))} for r in held]}}
            if section.get('publicWarning'):
                source['publicWarning'] = section['publicWarning']
            if section.get('printedAggregateControls'):
                source['validation']['printedAggregateControls'] = section['printedAggregateControls']
            if section.get('independentCrossReview'):
                source['validation']['independentCrossReview'] = section['independentCrossReview']
            if any(part.get('independentOcr') for part in parts):
                source['validation']['independentOcr'] = {'reader': 'Tesseract 5 column OCR from original 300-dpi ink',
                    'pdfTextLayer': 'Pre-existing OCR; PyMuPDF/Poppler alone are not independent OCR readings.',
                    'allAcceptedAndHeldRowFieldsAgreeAfterRenderedCorrections': True,
                    'pageCorrections': [{'physicalPage': part['page'], 'readers': part['readerCorrections']} for part in parts]}
            if section['category']=='employee-remuneration':
                source['completeEmployeeSchedule'] = not bool(held)
                source['validation']['completeEmployeeSchedule'] = not bool(held)
            if held:
                source['publicWarning'] = ((source.get('publicWarning') or '') + ' Partial employee cohort: '
                    + str(len(held)) + ' named rows with an unpublished/dash taxable-benefit component remain held; '
                    + 'their known remuneration cells and raw dashes remain in evidence, and are not substituted for composite remuneration. '
                    + 'Accepted-subset totals differ in scope from full named-cohort controls. Held names/pages: '
                    + '; '.join(r['name']+' (p'+str(r['pdfPage'])+')' for r in held)).strip()
                if section.get('holdMissingSalary'):
                    source['validation']['heldMissingBenefitRows'] = sum(r['benefits'] is None for r in held)
                    source['validation']['heldMissingPayComponentRows'] = len(held)
                    source['validation']['heldRows'] = [{'name': r['name'], 'position': r.get('position'),
                        'pdfPage': r['pdfPage'], 'knownBaseSalary': dollars(r.get('salary')),
                        'knownBenefitsAndOther': dollars(r.get('benefits')), 'expenses': dollars(r.get('expenses')),
                        'missingPayComponents': [field for field in ['salary', 'benefits'] if r.get(field) is None]} for r in held]
                    source['publicWarning'] = ((section.get('publicWarning') or '') + ' Partial employee cohort: '
                        + str(len(held)) + ' named rows have a blank/dash pay component and no numeric row remuneration total. '
                        + 'Their known component cells and raw missing cells remain in evidence; no zero component or composite remuneration is inferred. '
                        + 'Held names/pages: ' + '; '.join(r['name']+' (p'+str(r['pdfPage'])+')' for r in held)).strip()
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
    p.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-history-lower-mainland'))
    p.add_argument('--fetch', action='store_true');p.add_argument('--check-data', action='store_true')
    p.add_argument('--output-dir', type=Path, default=OUT)
    args = p.parse_args();args.cache.mkdir(parents=True, exist_ok=True)
    if args.check_data and args.fetch:p.error('--check-data is offline')
    config = json.loads((OUT/'reviewed-layouts.json').read_text())
    OUT = args.output_dir
    OUT.mkdir(parents=True, exist_ok=True)
    build(config, args.cache, args.check_data, args.fetch)
