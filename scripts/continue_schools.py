#!/usr/bin/env python3
"""Pinned school SOFI parser. Poppler lines are checked against MuPDF columns.

Default verification replays committed extraction evidence without PDF/OCR/network.
--originals requires the pinned PDFs and runs both readers independently.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / 'research/salaries/continuation-schools'
INVENTORY = ROOT / 'research/salaries/continuation-2026-11-01/schools'
MONEY = re.compile(r'(?<![\w.,])\(?-?\d[\d,]*(?:\.\d{2})?\)?-?(?![\d.])')

def clean(s):
    return re.sub(r'\s+', ' ', s).strip()

def decimal(s):
    if s:s=s.replace('*','').strip()
    if not s or s.replace('$','').strip() in ['', '-', '‐', '–', '—']:
        return None
    value=s.replace(',', '').replace('$', '').replace('(', '-').replace(')', '').strip()
    if value.endswith('-'):value='-'+value[:-1]
    return str(Decimal(value))

def cents_sum(rows, field):
    return str(sum((Decimal(r[field]) for r in rows if r[field] is not None), Decimal(0)))

def parse_poppler(text, config):
    """Use only explicitly reviewed physical pages and report scope boundaries."""
    pages = text.split('\f')
    out = []
    mode = None
    controls = {}
    for pno in config['pages']:
        ptext = pages[pno-1]
        position_col = None
        if config['positions']:
            heads = [l for l in ptext.splitlines() if re.search(r'\b(?:POSITION|ROLE)\b', l, re.I) and re.search(r'\b(?:REMUNERATION|RENUMERATION)\b', l, re.I)]
            position_col = config.get('popplerPositionColumns',{}).get(str(pno))
            if position_col is None:
                if not heads:
                    raise ValueError(f'Missing position heading on physical page {pno}')
                position_col = re.search(r'\b(?:POSITION|ROLE)\b', heads[0], re.I).start()
        if str(pno) in config.get('pageModes', {}):
            mode = config['pageModes'][str(pno)]
        for line in ptext.splitlines():
            s = clean(line)
            upper = s.upper()
            if re.search(r'^(?:A\. )?(?:LIST OF )?ELECTED OFFICIALS(?:\s*:?$| REMUNERATION)', upper):
                mode = 'school-trustees'
                continue
            vals = MONEY.findall(line)
            for category,pattern in config.get('modeSwitchPatterns',{}).items():
                if re.fullmatch(pattern,s):mode=category
            for category,pattern in config.get('controlLinePatterns',{}).items():
                if re.search(pattern,line):controls[category]=[decimal(x) for x in vals[-2:]]
            if re.match(r'(?:\d\. )?DETAILED EMPLOYEES|(?:A\. )?LIST OF EMPLOYEES|EMPLOYEES, OTHER THAN|SCHEDULE OF EMPLOYEES PAID', upper) and len(vals)<3:
                mode = 'employee-remuneration'
                continue
            if re.match(r'DETAILED VENDORS|(?:A\. )?SUPPLIERS', upper):
                mode=None
            if upper.startswith(('TOTAL','WHOSE REMUNERATION','$75,000','DETAILED EMPLOYEES')):
                elected_control='ELECTED' in upper and 'OTHER THAN' not in upper and 'INCLUDING ELECTED' not in upper
                if len(vals) >= 1 and not any(x in upper for x in ['LESS THAN',' OR LESS','BELOW','<=']) and (elected_control or 'DETAILED' in upper or 'AT LEAST' in upper or re.search(r'>\s*=?\s*\$?75,000',upper) or 'EXCEED' in upper or 'WHOSE' in upper or (upper.startswith('$75,000') and 'employee-remuneration' not in controls)):
                    cat = 'school-trustees' if elected_control else 'employee-remuneration'
                    control_vals=[decimal(x) for x in vals]
                    if control_vals and Decimal(control_vals[0])==75000:control_vals=control_vals[1:]
                    if control_vals:
                        controls[cat]=control_vals[-2:] if len(control_vals)>1 else [control_vals[0],None]
                        if mode==cat:mode=None
                # Total-only lines are controls/aggregates, never individuals.
                continue
            if upper.startswith(('FISCAL ','CONSOLIDATED ', 'REMUNERATION TO ', 'C. REMUNERATION','B. REMUNERATION','D. EMPLOYER')):
                continue
            literal_name=next((n for n in config.get('literalNamesWithoutComma',[]) if s.startswith(n)),None)
            valid_named_prefix=bool(re.search(r'^[A-Za-zÀ-ž][^\d]*'+(',' if config.get('namesRequireComma',True) else ''), s)) or literal_name is not None
            if mode and vals and not valid_named_prefix and re.match('[A-Za-zÀ-ž]',s) and any(Decimal(decimal(v))>=75000 for v in vals) and not re.match(r'(?:SCHOOL|FISCAL|YEAR|SCHEDULE|STATEMENT|PREPARED|THE |NOTES|DATE|NAME|TOTAL|CONSOLIDATED|[ABCD]\. |REMUNERATION|EMPLOYEE|DETAILED|WHOSE|FOR THE|PAID TO|CANADA|AND )',upper):
                raise ValueError(f'Unparsed potential named row on physical page {pno}: {line}')
            if not mode or not vals or not valid_named_prefix:
                continue
            matches=[m for m in MONEY.finditer(line) if Decimal(decimal(m.group()))>=config.get('minimumRemuneration',1000)]
            if not matches:continue
            first=matches[0]
            vals=MONEY.findall(line[first.start():])
            pay = decimal(vals[0])
            if Decimal(pay) < config.get('minimumRemuneration',1000):
                raise ValueError(f'Unexpected pay amount on {pno}: {line}')
            if len(vals) > 2:
                raise ValueError(f'Unexpected monetary components: {line}')
            prefix = line[:first.start()].rstrip().rstrip('$').rstrip()
            if position_col is not None:
                row_position_col=config.get('popplerPositionColumnsByCategory',{}).get(str(pno),{}).get(mode,position_col)
                name = clean(prefix[:row_position_col])
                position = clean(prefix[row_position_col:]) or None
                for exception in config.get('explicitJoinedNameTitleRows',[]):
                    if pno==exception['pdfPage'] and clean(prefix)==exception['sourcePrefix']:
                        name,position=exception['name'],exception['position']
            else:
                name, position = clean(prefix), None
            if not name or (config.get('namesRequireComma',True) and ',' not in name and name not in config.get('literalNamesWithoutComma',[])):
                raise ValueError(f'Name boundary invalid: {line}')
            out.append({'name': name, 'position': position, 'remuneration': pay,
                        'expenses': decimal(vals[1]) if len(vals) == 2 else None,
                        'pdfPage': pno, 'category': mode, 'sourceLine': line})
    return out, controls

def mupdf_rows(pdf_path, config):
    """Independent row grouping and fixed geometric table columns, not Poppler order."""
    import fitz
    out = []
    doc = fitz.open(pdf_path)
    for pno in config['pages']:
        page = doc[pno-1]
        groups = []
        for w in sorted(page.get_text('words'), key=lambda w: ((w[1]+w[3])/2, w[0])):
            center = (w[1]+w[3])/2
            group = next((g for g in reversed(groups[-3:]) if abs(g['y']-center)<2.0), None)
            if group is None:
                group = {'y': center, 'words': []}; groups.append(group)
            group['words'].append(w)
        bounds = config['geometry'][str(pno)]
        for group in groups:
            if str(pno) in config.get('regions',{}):
                lo,hi=config['regions'][str(pno)]
                if not lo<=group['y']<=hi:continue
            ws = sorted(group['words'], key=lambda w:w[0])
            fields = [[] for _ in range(4)]
            for w in ws:
                if w[4]=='$':continue
                if str(pno) in config.get('commentsStart',{}) and w[0]>=config['commentsStart'][str(pno)]:continue
                idx = sum(w[0] >= x for x in bounds)
                fields[idx].append(w[4])
            name, pos, pay, exp = map(lambda f:clean(' '.join(f)), fields)
            name_prefix_valid=bool(re.match(r'^[A-Za-zÀ-ž][^\d]*'+(',' if config.get('namesRequireComma',True) else ''), name)) or name in config.get('literalNamesWithoutComma',[])
            if not name_prefix_valid or name.lower().startswith(('total', 'detailed employees','consolidated ', 'paid ','whose ','c. ','b. ','remuneration ')) or not MONEY.fullmatch(pay.replace('$','').strip()):
                continue
            if not config['positions']:
                if pos:
                    raise ValueError(f'Unexpected position data: {pno} {pos}')
                pos = None
            else:
                pos = pos or None
            pay = decimal(pay)
            if pay is None or Decimal(pay)<config.get('minimumRemuneration',1000):
                continue
            try:expense_value=decimal(exp)
            except Exception as e:raise ValueError(f'Invalid geometric expense {pno}: {name} | {pos} | {pay} | {exp}') from e
            out.append({'name':name, 'position':pos, 'remuneration':pay,
                        'expenses':expense_value, 'pdfPage':pno,
                        'mupdfWords': [{'x0':round(w[0],3), 'y0':round(w[1],3), 'x1':round(w[2],3), 'y1':round(w[3],3), 'text':w[4]} for w in ws]})
    return out

def sha(data):
    return hashlib.sha256(data).hexdigest()

def pack_json(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    return gzip.compress(raw, mtime=0), raw

def scanned_ocr_rows(text,page):
    rows=[]
    for line in text.splitlines():
        if not re.match(r'^[A-Za-zÀ-ž][^\d]*,',line):continue
        matches=list(MONEY.finditer(line))
        if not matches:continue
        if len(matches)>2:raise ValueError('Unexpected scan monetary components')
        rows.append({'name':clean(line[:matches[0].start()]),'position':None,'remuneration':decimal(matches[0].group()),'expenses':decimal(matches[1].group()) if len(matches)>1 else None,'pdfPage':page,'ocrSourceLine':line})
    return rows

def read_report(pdf_path,config,rerun_ocr=False):
    text=subprocess.check_output(['pdftotext','-layout',str(pdf_path),'-']).decode()
    rows,controls=parse_poppler(text,config);independent=mupdf_rows(pdf_path,config)
    cols=['name','position','remuneration','expenses','pdfPage']
    for supplement in config.get('scannedSupplements',[]):
        proof_bytes=(COLLECTION/supplement['file']).read_bytes()
        assert sha(proof_bytes)==supplement['sha256']
        proof=json.loads(gzip.decompress(proof_bytes))
        assert proof['sourceSha256']==sha(pdf_path.read_bytes())
        page=supplement['pdfPage']
        assert not any(r['pdfPage']==page for r in rows), 'Native and scan rows overlap'
        ocr_text=proof['ocrText']
        if rerun_ocr:
            import fitz
            from PIL import Image,ImageDraw
            import tempfile
            doc=fitz.open(pdf_path);pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(2,2))
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pixels=im.load()
            horizontal=[y for y in range(70,1490) if sum(max(pixels[x,y])<80 for x in range(37,936))>800]
            vertical=[x for x in range(37,936) if sum(max(pixels[x,y])<80 for y in range(300,1488))>1000]
            draw=ImageDraw.Draw(im)
            for y in horizontal:draw.line([(35,y),(938,y)],fill='white',width=3)
            for x in vertical:draw.line([(x,70),(x,1490)],fill='white',width=3)
            with tempfile.TemporaryDirectory(prefix='continuation-schools-ocr-') as tmp:
                image=Path(tmp)/'page.png';im.save(image)
                ocr_text=subprocess.check_output(['tesseract',str(image),'stdout','--psm','6'],stderr=subprocess.PIPE).decode()
        a=proof['manualRows'];b=scanned_ocr_rows(ocr_text,page)
        assert [[r[k] for k in cols] for r in a]==[[r[k] for k in cols] for r in b], 'Manual transcript and independent OCR differ'
        rows.extend(a);independent.extend(b)
    rows.sort(key=lambda r:r['pdfPage']);independent.sort(key=lambda r:r['pdfPage'])
    return rows,independent,controls,text

def verify_evidence(source, evidence):
    rows = evidence['rows']
    cols = ['name','position','remuneration','expenses','pdfPage']
    a = [[r[k] for k in cols] for r in rows]
    b = [[r[k] for k in cols] for r in evidence['independentRows']]
    assert a == b, f"Independent-reader field mismatch: {source['id']}"
    assert len(rows) == source['rowCount']
    assert evidence['sourceSha256'] == source['sha256']
    acceptance=source['validation'].get('independentQualificationAcceptance')
    if acceptance:
        assert acceptance['originalSha256']==source['sha256']
        assert acceptance['dataSha256']==source['dataSha256']
        assert acceptance['provenanceSha256']==source['provenanceSha256']
        assert acceptance['rowCount']==source['rowCount']
        assert acceptance['approvedControlResiduals']==source['validation']['controlResiduals']
        for review_file in acceptance['reviewFiles']:
            assert sha((ROOT/review_file['file']).read_bytes())==review_file['sha256']
    for supplement in source['validation'].get('scannedSupplementEvidence',[]):
        assert sha((COLLECTION/supplement['file']).read_bytes())==supplement['sha256']
    totals = [cents_sum(rows,k) for k in ['remuneration','expenses']]
    assert totals == source['validation']['computedComponentTotals']
    assert [str(Decimal(a)-Decimal(b)) if b is not None else None for a,b in zip(totals,evidence['printedControlTotals'])] == source['validation']['controlResiduals']
    expected = [[source['employerSlug'],r['name'],r['position'],float(r['remuneration']),None if r['expenses'] is None else float(r['expenses']),r['pdfPage']] for r in rows]
    packed,raw = pack_json(expected)
    assert sha(packed) == source['dataSha256']
    assert packed == (COLLECTION/source['file']).read_bytes()
    return expected

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--originals',action='store_true')
    parser.add_argument('--include-held',action='store_true',help='Audit held transcripts without accepting their unresolved scope/period/control qualifications')
    parser.add_argument('--rerun-ocr',action='store_true',help='With --originals, rerender the hybrid page and rerun Tesseract; offline replay never needs OCR')
    parser.add_argument('--cache-dir',type=Path,default=Path('/tmp/pofbc-schools'))
    args = parser.parse_args()
    manifest = json.loads((COLLECTION/'sources.json').read_text())
    if args.include_held:manifest['sources']+=json.loads((INVENTORY/'held-candidates.json').read_text())
    configs = json.loads((INVENTORY/'parser-config.json').read_text())
    count = 0
    for source in manifest['sources']:
        packed = (COLLECTION/source['provenanceFile']).read_bytes()
        assert sha(packed)==source['provenanceSha256']
        evidence = json.loads(gzip.decompress(packed))
        verify_evidence(source,evidence)
        if args.originals:
            config = configs[source['inputKey']]
            path = Path(config.get('cacheDir',args.cache_dir))/config['cacheFile']
            assert sha(path.read_bytes()) == source['sha256']
            rows,independent,controls,text=read_report(path,config,args.rerun_ocr)
            rows = [r for r in rows if r['category']==source['category']]
            assert rows==evidence['rows']
            ps = {(r['pdfPage'],r['name']) for r in rows}
            independent = [r for r in independent if (r['pdfPage'],r['name']) in ps]
            assert independent==evidence['independentRows']
            assert controls[source['category']]==evidence['printedControlTotals']
        count += source['rowCount']
    print(f"Verified {len(manifest['sources'])} school cohorts, {count} observations" + (' against pinned original PDFs and independent readers' if args.originals else ' by offline evidence replay'))

if __name__=='__main__':
    main()
