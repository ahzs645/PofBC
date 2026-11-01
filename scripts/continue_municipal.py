#!/usr/bin/env python3
"""Reproduce reviewed municipal original employee/council schedules.

Each calendar period, table, component definition, count, source hash and control
is fixed by reviewed-layouts.json. --check-data is offline. No discovery lead is
automatically accepted, and no cell is changed to force a total to agree.
"""
import argparse
import csv
import io
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
OUT = ROOT / 'research/salaries/continuation-municipal'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def money(text):
    text = text.strip().replace('$', '').strip()
    if text in ('', '-', '–', '—', '‐'):
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


def cell_text(cells):
    """Join top-to-bottom wrapped lines, keeping horizontal order within each line."""
    lines=[]
    for w in sorted(cells,key=lambda w:((w[1]+w[3])/2,w[0])):
        y=(w[1]+w[3])/2
        if not lines or abs(y-lines[-1][0])>2.5:lines.append([y,[]])
        lines[-1][1].append(w)
    return ' '.join(' '.join(w[4] for w in sorted(line,key=lambda w:w[0])) for y,line in lines).strip()


def extract(words, section, raw_fields=False):
    cols = section['columns']
    # Some PDF extractors retain invisible glyphs clipped by the original table cell.
    # Only exact rendered-reviewed token/rectangle exclusions are permitted.
    words = [w for w in words if not any(w[4]==fix['text'] and abs(w[0]-fix['x'])<fix.get('tolerance',1) and abs(w[1]-fix['y'])<fix.get('tolerance',1) for fix in section.get('ignoredClippedWords',[]))]
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
        distances=sorted((abs((anchor[1]+anchor[3]-w[1]-w[3])/2),i)for i,anchor in enumerate(anchors))
        if len(distances)>1 and abs(distances[0][0]-distances[1][0])<0.5:
            raise ValueError(f'Ambiguous row boundary for {w[4]!r}')
        at=distances[0][1]
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
            text = cell_text(cells)
            for i, fix in enumerate(section.get('corrections', [])):
                if fix['row'] == at and fix['field'] == field:
                    if text not in (fix['before'] if isinstance(fix['before'],list) else [fix['before']]):
                        raise ValueError('Reviewed rendered-source correction changed')
                    text = fix['after']
                    used.add(i)
            row[field] = text or None if raw_fields or field in ('name', 'position') else money(text)
        if section.get('officePrefixInName'):
            office=re.fullmatch(r'(Mayor|Councillor)\s+(.+)',row.get('name') or '')
            if not office:raise ValueError('Original office/name prefix changed')
            row['position'],row['name']=office.groups()
        if section.get('positionValues'):
            row['position'] = section['positionValues'][at]
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
    seen=set()
    for collection in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
        if collection=='continuation-municipal':continue
        for source in json.loads((ROOT/'research/salaries'/collection/'sources.json').read_text())['sources']:
            seen.add((source.get('employerSlug'),str(source.get('year')),source.get('category')))
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
            identity=(report['employerSlug'],report['year'],section['category'])
            if identity in seen:raise ValueError(f'Duplicate registered employer/period/category: {identity}')
            seen.add(identity)
            evidence_file = f"evidence/{report['key']}-{section['category']}.json.gzip"
            if check_data:
                evidence = json.loads(gzip.decompress((OUT / evidence_file).read_bytes()))
                if evidence['originalSha256'] != report['sha256']:
                    raise ValueError('Retained evidence fingerprint mismatch')
            else:
                parts = []
                for part in section.get('parts', [section]):
                    page = doc[part['page'] - 1]
                    if report['year'] not in page.get_text() and not report.get('periodEvidence'):
                        raise ValueError('Reporting-year evidence absent from schedule page')
                    if report.get('sourceKind')=='official-scanned-pdf':
                        png=cache/(report['key']+'-scan-p'+str(part['page'])+'.png')
                        page.get_pixmap(matrix=fitz.Matrix(3,3)).save(png)
                        raw=subprocess.check_output(['tesseract',str(png),'stdout','--psm','6','tsv'],stderr=subprocess.PIPE).decode()
                        scanned=[]
                        for cell in csv.DictReader(io.StringIO(raw),delimiter='\t'):
                            if cell['text'].strip():
                                l,t,wd,ht=[int(cell[k])/3 for k in ['left','top','width','height']]
                                scanned.append([l,t,l+wd,t+ht,cell['text']])
                        parts.append({'originalSha256':report['sha256'],'physicalPage':part['page'],'ocrEngine':'Tesseract 5, psm6, 216dpi','ocrWords':scanned,'manualRows':part['manualRows'],'manualRowsBasis':'Complete independent visual transcription of original rendered page; source cents/fields are explicitly pinned in reviewed layouts.'})
                    else:
                        parts.append({'originalSha256': report['sha256'], 'physicalPage': part['page'],
                                      'mupdfWords': words_mupdf(page), 'popplerWords': words_poppler(path, part['page'])})
                evidence = parts[0] if 'parts' not in section else {'originalSha256': report['sha256'], 'parts': parts}
            if report.get('sourceKind')=='official-pdf-ocr-overlay':
                for part,proof in zip(section.get('parts',[section]),evidence.get('parts',[evidence])):
                    fixes=part.get('corrections',[])
                    if check_data and fixes and proof.get('manualReviewCorrections')!=fixes:raise ValueError('Pinned manual overlay corrections changed')
                    if not check_data and fixes:proof['manualReviewCorrections']=fixes
            parts = section.get('parts', [section])
            retained_parts = evidence.get('parts', [evidence])
            if len(parts) != len(retained_parts):
                raise ValueError('Retained schedule page count changed')
            if report.get('sourceKind')=='official-scanned-pdf':
                if any(proof['manualRows']!=part['manualRows'] for part,proof in zip(parts,retained_parts)):raise ValueError('Pinned manual scan transcript changed')
                a=[row | {'pdfPage':part['page']} for part,proof in zip(parts,retained_parts)for row in extract(proof['ocrWords'],part)]
                b=[row | {'pdfPage':part['page']} for part,proof in zip(parts,retained_parts)for row in proof['manualRows']]
            else:
                a = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                     for row in extract(proof['mupdfWords'], part)]
                b = [row | {'pdfPage': part['page']} for part, proof in zip(parts, retained_parts)
                     for row in extract(proof['popplerWords'], part)]
            if a != b:
                raise ValueError(f"{report['key']}: PDF readers disagree: {[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]}")
            supporting=section.get('supportingControlEvidence')
            if supporting:
                control_bytes=(OUT/supporting['file']).read_bytes()
                if sha(control_bytes)!=supporting['sha256']:raise ValueError('Supporting control evidence fingerprint changed')
                control_proof=json.loads(gzip.decompress(control_bytes))
                if control_proof['originalSha256']!=report['sha256'] or control_proof['physicalPage']!=supporting['physicalPage']:raise ValueError('Supporting control original/page mismatch')
                if not check_data:
                    if control_proof['mupdfWords']!=words_mupdf(doc[supporting['physicalPage']-1]) or control_proof['popplerWords']!=words_poppler(path,supporting['physicalPage']):raise ValueError('Supporting source control readers changed')
                for reader in ['mupdfWords','popplerWords']:
                    for field,expected in supporting['fields'].items():
                        x0,x1=supporting['columns'][field];found=[]
                        for w in control_proof[reader]:
                            if not x0<=(w[0]+w[2])/2<x1:continue
                            try:value=money(w[4])
                            except ValueError:continue
                            if value==expected:found.append(w)
                        if len(found)!=1 or expected!=section['controlsCents'][field]:raise ValueError('Original named source control changed')
            controls = []
            for field, expected in section['controlsCents'].items():
                actual = sum(r.get(field) or 0 for r in a)
                residual = actual - expected
                if residual != section.get('reviewedResidualsCents', {}).get(field, 0):
                    raise ValueError(f"{report['key']} {section['category']} {field}: changed residual {residual}")
                controls.append({'field': field, 'printedOrDerivedControl': dollars(expected), 'rowSum': dollars(actual),
                                 'residual': dollars(residual), 'basis': section.get('controlBasis', 'Printed named subtotal, or total employees less the printed under-threshold aggregate')})
            rows = [[report['employerSlug'], r['name'], r.get('position'), dollars(r['pay']), dollars(r.get('expenses')), r['pdfPage']] for r in a]
            name = f"{report['key']}-{section['category']}.json.gzip"
            data = packed(rows);audit = packed(evidence)
            pending[name] = data;pending[evidence_file] = audit
            source = {'id': f"continuation-municipal-{report['key']}-{section['category']}", 'employerSlug': report['employerSlug'],
                'employerName': report['employerName'], 'sector': 'Municipalities', 'year': report['year'],
                'periodType': 'calendar', 'periodStart': report['year']+'-01-01', 'periodEnd': report['year']+'-12-31',
                'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['indexUrl'], 'sha256': report['sha256'],
                'file': name, 'dataSha256': sha(data), 'category': section['category'], 'scope': section['category'],
                'title': f"{report['employerName']} {report['year']} SOFI: {section['category']}", 'status': 'verified', 'sourceKind': report.get('sourceKind','official-native-pdf'),
                'rowCount': len(rows), 'totalRemuneration': dollars(sum(r['pay'] for r in a)),
                'totalExpenses': dollars(sum(r.get('expenses') or 0 for r in a)), 'pages': [part['page'] for part in parts],
                'currency': 'CAD', 'amountUnit': 'dollars', 'threshold': section.get('threshold', 75000 if section['category']=='employee-remuneration' else None),
                'thresholdComparison': '>' if section.get('threshold',75000) is not None and section['category']=='employee-remuneration' else None,
                'completeEmployeeSchedule': section.get('completeEmployeeSchedule',True) if section['category']=='employee-remuneration' else None,
                'notes': report.get('notes', []) + section.get('notes', []) + [report.get('remunerationDefinition', 'Remuneration is published Salary/Base Salary plus Benefits and Other.') + ' Expenses remain separate. Published blanks and dashes remain missing; explicit zeros stay zero. Names and positions remain as disclosed.'],
                'validation': {'independentPdfReaders': ['PyMuPDF positioned words', 'Poppler bbox-layout words'],
                    'allRowFieldsAgree': True, 'physicalPagesVisuallyReviewed': [part['page'] for part in parts], 'controls': controls,
                    'evidenceFile': evidence_file, 'evidenceSha256': sha(audit), 'corrections': section.get('corrections', []), 'periodEvidence': report.get('periodEvidence',[]), 'completeEmployeeSchedule': section.get('completeEmployeeSchedule',True) if section['category']=='employee-remuneration' else None}}
            if supporting:
                source['validation']['supportingControlEvidence']=supporting
            if section.get('ignoredClippedWords'):
                source['validation']['ignoredClippedWords']=section['ignoredClippedWords']
            if report.get('sourceKind')=='official-scanned-pdf':
                source['validation']['independentPdfReaders']=['Tesseract 5 OCR','Independent complete manual image transcription']
                source['validation']['ocrEngineIndependenceClaimed']=False
                source['validation']['completeRenderedTranscriptionReview']=True
            if report.get('sourceKind')=='official-pdf-ocr-overlay':
                source['validation']['independentPdfReaders']=['PyMuPDF OCR-overlay words','Poppler OCR-overlay words']
                source['validation']['ocrEngineIndependenceClaimed']=False
                source['validation']['completeRenderedTranscriptionReview']=True
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
    p.add_argument('--cache', type=Path, default=Path('/tmp/continuation-municipal'))
    p.add_argument('--fetch', action='store_true');p.add_argument('--check-data', action='store_true')
    args = p.parse_args();args.cache.mkdir(parents=True, exist_ok=True)
    if args.check_data and args.fetch:p.error('--check-data is offline')
    build(json.loads((OUT/'reviewed-layouts.json').read_text()), args.cache, args.check_data, args.fetch)
