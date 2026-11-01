#!/usr/bin/env python3
"""Recover four historical native Interior Health board schedules.

The independent readers are PyMuPDF coordinate rectangles and Poppler fixed-width
layout rows. The latter never consumes PyMuPDF words, rectangles or row output.
Original bytes stay in /tmp; compressed original-backed evidence permits replay.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/recovery-health'
SCHEMA = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def norm(value):
    return re.sub(r'\s+', ' ', value).strip()


def amount(value):
    value = re.sub(r'\s+', '', value).replace('$', '')
    if not value or value in ('-', '–'):
        return None
    if not re.fullmatch(r'-?(?:\d{1,3}(?:,\d{3})+|\d+)', value):
        raise ValueError(f'Unexpected amount {value!r}')
    return int(value.replace(',', ''))


def pymupdf_evidence(path):
    import fitz
    pages = []
    for page in fitz.open(path):
        words = []
        for word in page.get_text('words'):
            rect = fitz.Rect(word[:4]) * page.rotation_matrix
            words.append([rect.x0, rect.y0, rect.x1, rect.y1, word[4]])
        pages.append(words)
    return pages


def word_cell(words, left, right, top, bottom):
    kept = [w for w in words if left <= (w[0] + w[2]) / 2 < right
            and top <= (w[1] + w[3]) / 2 < bottom]
    groups = []
    for w in sorted(kept, key=lambda x: (x[1], x[0])):
        if groups and abs(w[1] - groups[-1][0][1]) < 2.8:
            groups[-1].append(w)
        else:
            groups.append([w])
    return norm(' '.join(' '.join(w[4] for w in sorted(g)) for g in groups))


def read_pymupdf(pages, spec):
    words = pages[spec['page'] - 1]
    result, evidence = [], []
    for i in range(spec['rows']):
        top = spec['firstRowTop'] + i * spec['rowHeight']
        bottom = top + spec['rowHeight']
        cells = [word_cell(words, l, r, top, bottom)
                 for l, r in zip(spec['pdfColumns'], spec['pdfColumns'][1:])]
        # Portrait schedules have small superscript references in the name/pay
        # columns. Filter using font geometry, independently of expected values.
        if spec['layout'] == 'summary':
            cells = []
            large = [w for w in words if w[3] - w[1] > 9]
            for l, r in zip(spec['pdfColumns'], spec['pdfColumns'][1:]):
                cells.append(word_cell(large, l, r, top, bottom))
        pay = amount(cells[-1])
        components = [amount(cells[c]) for c in spec['componentColumns']]
        row = ['interior-health', cells[0], cells[1], pay, None, spec['page']]
        result.append(row)
        evidence.append({'row': row, 'cells': cells, 'components': components,
                         'rectangle': [spec['pdfColumns'][0], top, spec['pdfColumns'][-1], bottom]})
    return result, evidence


def read_poppler(text, spec):
    """Read plain layout text; line/character columns differ from PDF geometry."""
    lines = text.split('\f')[spec['page'] - 1].splitlines()
    result, evidence = [], []
    if spec['layout'] == 'summary':
        # The summary exposes all fields on one line; annotations are separate
        # lines. This regex allows the original '21, 594' thousands spacing.
        for line in lines:
            match = re.fullmatch(r'(.+?) {3,}(.+?) {3,}(\$\s*[\d, ]+)\s*', line)
            if not match:
                continue
            name, position, value = match.groups()
            row = ['interior-health', norm(name), norm(position), amount(value), None, spec['page']]
            result.append(row)
            evidence.append({'row': row, 'line': line, 'components': []})
    else:
        # Every table body row occupies exactly three text lines. Hard bounds
        # are reviewed on the original, and each complete source row is retained.
        start, size = spec['textFirstLine'], spec['textLinesPerRow']
        for i in range(spec['rows']):
            block = lines[start + size*i:start + size*(i+1)]
            cells = [norm(' '.join(line[l:r] for line in block))
                     for l, r in zip(spec['textColumns'], spec['textColumns'][1:])]
            # A single source row has no text gap between name and title;
            # Poppler's character grid splits the word Director at the boundary.
            # The full two-cell context is locked to the rendered source.
            for correction in spec.get('popplerCellCorrections', []):
                if cells[:2] == correction['rawCells']:
                    cells[:2] = correction['visibleCells']
            row = ['interior-health', cells[0], cells[1], amount(cells[-1]), None, spec['page']]
            components = [amount(cells[c]) for c in spec['componentColumns']]
            result.append(row)
            evidence.append({'row': row, 'lines': block, 'cells': cells, 'components': components})
    if len(result) != spec['rows']:
        raise ValueError(f"{spec['id']}: Poppler row count {len(result)}")
    return result, evidence


def parse_and_compare(evidence, spec):
    a, ae = read_pymupdf(evidence['pymupdfWords'], spec)
    b, be = read_poppler(evidence['popplerLayoutText'], spec)
    if a != b:
        raise ValueError(f"{spec['id']}: independent field disagreement " +
                         repr([(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]))
    if [e['components'] for e in ae] != [e['components'] for e in be]:
        raise ValueError(f"{spec['id']}: independent component disagreement")
    # Independent complete manual review is a third lock for names, titles,
    # amounts, page/row boundaries, unpublished expenses and explicit zeros.
    expected = [['interior-health', *r, None, spec['page']] for r in spec['reviewedRows']]
    if a != expected:
        raise ValueError(f"{spec['id']}: rendered transcription differs")
    if len(a) != spec['rows']:
        raise ValueError('Row boundary count changed')
    year_end = str(int(spec['year'][:4]) + 1)
    page_text = evidence['popplerLayoutText'].split('\f')[spec['page'] - 1]
    if not re.search(r'March\s+31,?\s*' + year_end, page_text, re.I):
        raise ValueError('Printed internal reporting period missing')
    if re.search(r'\bdraft\b', evidence['popplerLayoutText'], re.I):
        raise ValueError('Draft original must be held')
    if spec.get('printedTotal') is not None and f"${spec['printedTotal']:,}" not in page_text:
        raise ValueError('Printed remuneration total missing')
    return a, ae, be


def run(originals=False, check=False):
    sources = []
    for spec in json.loads((OUT / 'source-specs.json').read_text()):
        ep = OUT / 'evidence' / (spec['id'] + '.json.gzip')
        if originals:
            path = Path(spec['cachePath'])
            if sha(path.read_bytes()) != spec['sha256']:
                raise ValueError('Original bytes changed')
            raw = {'sourceSha256': spec['sha256'], 'pymupdfWords': pymupdf_evidence(path),
                   'popplerLayoutText': subprocess.check_output(['pdftotext', '-layout', str(path), '-']).decode()}
            serialized = gzip.compress(compact(raw), mtime=0)
            if check and ep.read_bytes() != serialized:
                raise ValueError('Original-backed evidence changed')
            if not check:
                ep.parent.mkdir(exist_ok=True)
                ep.write_bytes(serialized)
        raw = json.loads(gzip.decompress(ep.read_bytes()))
        if raw['sourceSha256'] != spec['sha256']:
            raise ValueError('Evidence fingerprint changed')
        rows, ae, be = parse_and_compare(raw, spec)
        proof = {'sourceSha256':spec['sha256'], 'rows':[
            {'row':row, 'sourceRowOnPage':i+1, 'physicalPage':spec['page'],
             'pymupdf':ae[i], 'poppler':be[i]}
            for i, row in enumerate(rows)]}
        proof_data = gzip.compress(compact(proof), mtime=0)
        proof_path = OUT / 'evidence' / (spec['id'] + '-rows.json.gzip')
        if check:
            if proof_path.read_bytes() != proof_data:
                raise ValueError('Row-level provenance differs')
        else:
            proof_path.write_bytes(proof_data)
        data = gzip.compress(compact(rows), mtime=0)
        filename = spec['id'] + '.json.gzip'
        if check:
            if (OUT / filename).read_bytes() != data:
                raise ValueError('Normalized data differs')
        else:
            (OUT / filename).write_bytes(data)
        total = sum(r[3] for r in rows)
        component_residuals = [e['row'][3] - sum(v or 0 for v in e['components']) for e in ae] if spec['componentColumns'] else []
        residual = None if spec.get('printedTotal') is None else total - spec['printedTotal']
        source = {k: spec[k] for k in ['id', 'year', 'sourceUrl', 'sourceIndexUrl', 'sha256', 'pdfBytes', 'notes']}
        source.update(employerSlug='interior-health', employerName='Interior Health', sector='Health authorities',
                      title=f"Interior Health board remuneration {spec['year']}",
                      file=filename, dataSha256=sha(data), rowCount=len(rows), totalRemuneration=total,
                      totalExpenses=0, totalDisclosedExpenses=0, status='verified', verifiedOn='2026-11-01',
                      sourceKind='official', category='board-remuneration', scope='board-remuneration',
                      periodType='fiscal', periodStart=spec['year'][:4]+'-04-01',
                      periodEnd=str(int(spec['year'][:4])+1)+'-03-31', currency='CAD', nameDisclosure='named',
                      completeEmployeeSchedule=False, completeBoardSchedule=True,
                      expenseDisclosure='not-published', expenseComparatorAvailable=False,
                      publicationStatus='official-published-unsigned',
                      publicWarning='Expense reimbursements are not published in this board remuneration schedule. All expense fields are unknown, not zero.')
        if residual or any(component_residuals):
            source['publicWarning'] += f' Published remuneration fields disagree: row sum minus printed total = {residual} CAD; row component residuals = {component_residuals}. Published amounts remain literal; no cause is inferred.'
        source['validation'] = dict(independentReaders=['PyMuPDF coordinate-word row reader', 'Poppler fixed-width text row reader'],
                                    independentlyComparedRows=len(rows), completeEmployeeSchedule=False,
                                    completeBoardSchedule=True, physicalPdfPages=[spec['page']],
                                    sourceRowsPerPhysicalPage=[len(rows)], expenseDisclosure='not-published',
                                    missingExpenseRows=len(rows), explicitZeroExpenseRows=0,
                                    explicitZeroRemunerationRows=sum(r[3] == 0 for r in rows),
                                    negativeRemunerationRows=sum(r[3] < 0 for r in rows),
                                    printedRemunerationTotal=spec.get('printedTotal'), remunerationControlResidual=residual,
                                    payComponentResiduals=component_residuals,
                                    originalBackedEvidenceSha256=sha(ep.read_bytes()),
                                    rowProvenanceFile='evidence/'+proof_path.name,
                                    rowProvenanceSha256=sha(proof_data),
                                    renderReview={'physicalPages':[spec['page']], 'allNamedRowsReviewed':True,
                                                  'coverage':'Complete primary summary/table: every name, title, amount, row/page boundary, header, period and relevant footnote reviewed against rendered original.',
                                                  'imagePath':f"/tmp/recovery-health/interior-{int(spec['year'][:4])+1}-summary.png"})
        sources.append(source)
    manifest = json.dumps({'version':1, 'rowSchema':SCHEMA, 'sources':sources}, ensure_ascii=False, indent=2)+'\n'
    if check:
        if (OUT / 'sources.json').read_text() != manifest:
            raise ValueError('Manifest differs')
    else:
        (OUT / 'sources.json').write_text(manifest)
    print(json.dumps({'cohorts':len(sources), 'rows':sum(s['rowCount'] for s in sources)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--originals', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    run(args.originals, args.check)
