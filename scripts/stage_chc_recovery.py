#!/usr/bin/env python3
"""Stage CHC employee candidates from attributed official-report text captures.

This is deliberately NOT a publication/acceptance command. It cannot alter PofBC's
public outputs or its accepted collections. Run from any directory; stdlib only.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/chc-recovery'
MONEY = r'(?:0|[1-9]\d{0,2}(?:,\d{3})*|[1-9]\d*)'
ROW = re.compile(rf'(?P<initials>[A-Z]{{1,5}}) (?P<surname>[^\d]+?) (?P<rem>{MONEY}) (?P<exp>{MONEY})')
STATUS = 'text-extracted-awaiting-pdf-verification'

class ValidationError(ValueError):
    """The capture is incomplete, malformed, or semantically inconsistent."""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n').encode()

def parse_row(text: str) -> tuple[str, int, int]:
    match = ROW.fullmatch(text.strip())
    if not match:
        raise ValidationError(f'Unparsed employee row: {text!r}')
    surname = match['surname'].strip()
    if not surname or any(t in surname.lower() for t in ('supplier', 'receiver general', 'total')):
        raise ValidationError(f'Not an employee name: {text!r}')
    rem, exp = (int(match[k].replace(',', '')) for k in ('rem', 'exp'))
    if rem <= 75_000:
        raise ValidationError(f'Unexpected named payment at/below threshold: {text!r}')
    return f"{match['initials']} {surname}", rem, exp

def stage_capture(capture: dict[str, Any]) -> tuple[list[dict], dict]:
    year = capture.get('fiscalYear', '')
    if not re.fullmatch(r'\d{4}/\d{2}', year):
        raise ValidationError('Invalid fiscal year')
    end = int(year[:4]) + 1
    if str(end)[-2:] != year[-2:]:
        raise ValidationError('Non-consecutive fiscal-year label')
    if capture.get('periodStart') != f'{end-1}-04-01' or capture.get('periodEnd') != f'{end}-03-31':
        raise ValidationError('Period dates do not match fiscal-year label')
    if capture.get('currency') != 'CAD' or capture.get('amountPrecision') != 'whole-dollar':
        raise ValidationError('This adapter is for CAD whole-dollar CHC tables only')
    if capture.get('threshold') != 75000 or capture.get('thresholdRule') != 'over':
        raise ValidationError('Unexpected disclosure threshold')
    pages = capture.get('pages', [])
    if not pages:
        raise ValidationError('No schedule pages')
    count = pages[0]['sheets']
    if count != len(pages) or [p['sheet'] for p in pages] != list(range(1, count+1)):
        raise ValidationError('Incomplete or duplicate schedule sheet sequence')
    if any(p['sheets'] != count for p in pages):
        raise ValidationError('Inconsistent sheet count')
    physical = [p['pdfPage'] for p in pages]
    if any(type(p) is not int or p < 1 for p in physical):
        raise ValidationError('Invalid physical page')
    if physical != list(range(physical[0], physical[0] + count)):
        raise ValidationError('Physical pages must be contiguous and unique')
    if capture['controlsPdfPage'] != physical[-1]:
        raise ValidationError('Summary page is not the final schedule page')
    controls = capture['controls']
    for key in ('totalRemuneration','totalExpenses','belowThresholdRemuneration','belowThresholdExpenses','employerCppEi'):
        if type(controls.get(key)) is not int or controls[key] < 0:
            raise ValidationError(f'Invalid control: {key}')
    if controls['totalRemuneration'] < controls['belowThresholdRemuneration'] or controls['totalExpenses'] < controls['belowThresholdExpenses']:
        raise ValidationError('Below-threshold aggregate exceeds overall aggregate')
    rows = []
    for p in pages:
        if p['employerHeader'] != 'COLUMBIA HYDRO CONSTRUCTORS LTD.':
            raise ValidationError('Employer header mismatch; do not merge subsidiaries')
        if p['periodHeader'] != f'on Behalf of Employees During the Year Ended March 31, {end}':
            raise ValidationError('Fiscal header mismatch')
        if p['scheduleHeader'] != 'Schedule of Remuneration Paid to Employees and Expenses Paid to or':
            raise ValidationError('Not an employee schedule')
        lines = p['rowsText'].splitlines()
        if lines and (type(p['firstSourceTextLine']) is not int or p['firstSourceTextLine'] < 0):
            raise ValidationError('Missing source-text line locator')
        for offset, text in enumerate(lines):
            if not text.strip():
                raise ValidationError('Unexpected blank within captured row block')
            name, rem, exp = parse_row(text)
            rows.append({'sourceId':capture['sourceId'],'fiscalYear':year,'employer':capture['employer'],
                'proposedEmployerSlug':capture['proposedEmployerSlug'],'rawName':name,
                'nameOrdering':'initials-then-surname','position':None,'remuneration':rem,'expenses':exp,
                'currency':'CAD','pdfPage':p['pdfPage'],'sourceTextLine':p['firstSourceTextLine']+offset,
                'sourceUrl':capture['sourceUrl'],'sourcePageUrl':capture['sourceUrl']+f"#page={p['pdfPage']}",
                'status':STATUS})
    aggregate_only = capture.get('captureType') == 'aggregate-only-employee-schedule'
    if aggregate_only and rows:
        raise ValidationError('Aggregate-only evidence contains named rows')
    if not aggregate_only and not rows:
        raise ValidationError('Named-employee capture is empty')
    named_rem = sum(r['remuneration'] for r in rows)
    named_exp = sum(r['expenses'] for r in rows)
    rem_residual = named_rem - (controls['totalRemuneration']-controls['belowThresholdRemuneration'])
    exp_residual = named_exp - (controls['totalExpenses']-controls['belowThresholdExpenses'])
    # Hypothetical maximum of independently rounded whole-dollar rows and two aggregates.
    # Compatibility is a diagnostic, NOT evidence that rounding caused the residual.
    bound = (len(rows)+2)/2
    compatible = abs(rem_residual) <= bound and abs(exp_residual) <= bound
    if aggregate_only and (rem_residual or exp_residual):
        raise ValidationError('Aggregate-only declaration conflicts with totals')
    repeated = Counter((r['rawName'],r['remuneration'],r['expenses']) for r in rows)
    result = {'sourceId':capture['sourceId'],'fiscalYear':year,
        'status':'aggregate-only-awaiting-pdf-verification' if aggregate_only else STATUS,
        'coverageMeaning':'No named rows disclosed in the captured employee schedule; not no employees or no payroll.' if aggregate_only else 'Named disclosed payment records; not verified individual identities or total headcount.',
        'rowCount':len(rows),'namedRemuneration':named_rem,'namedExpenses':named_exp,
        'rowsByPhysicalPage':{str(p['pdfPage']):sum(r['pdfPage']==p['pdfPage'] for r in rows) for p in pages},
        'sourceControls':controls,'remunerationResidual':rem_residual,'expenseResidual':exp_residual,
        'hypotheticalWholeDollarRoundingBound':bound,'withinHypotheticalRoundingBound':compatible,
        'exactAggregateReconciliation':rem_residual==0 and exp_residual==0,
        'residualExplanation':'Unknown. Values are unchanged; compatibility does not establish rounding as the cause.',
        'duplicateLookingExtraRows':sum(n-1 for n in repeated.values()),
        'zeroExpenseRows':sum(r['expenses']==0 for r in rows),'missingExpenseRows':0,
        'originalPdfBytesValidated':False,'visualReviewCompleted':False,'acceptedForPublication':False,
        'expectedPdfSha256FromEarlierPackage':capture['expectedPdfSha256FromEarlierPackage'],
        'sourceUrl':capture['sourceUrl'],'controlsInterpretationStatus':capture['controlsInterpretationStatus']}
    return rows,result

def csv_bytes(rows: list[dict]) -> bytes:
    fields=['sourceId','fiscalYear','employer','proposedEmployerSlug','rawName','nameOrdering','position',
            'remuneration','expenses','currency','pdfPage','sourceTextLine','sourceUrl','sourcePageUrl','status']
    buff=io.StringIO(newline=''); writer=csv.DictWriter(buff,fieldnames=fields,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return buff.getvalue().encode('utf-8')

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures',type=Path,default=BASE/'captures')
    parser.add_argument('--output',type=Path,default=BASE/'candidates')
    args=parser.parse_args()
    try:
        files=sorted(args.captures.glob('*.json'))
        if not files: raise ValidationError('No capture files found')
        staged=[];allrows=[];seen=set()
        # Validate every input before creating any outputs.
        for f in files:
            raw=f.read_bytes();capture=json.loads(raw);rows,result=stage_capture(capture)
            if capture['sourceId'] in seen: raise ValidationError('Duplicate sourceId')
            seen.add(capture['sourceId']);result['captureSha256']=digest(raw)
            staged.append((f.stem,rows,result));allrows.extend(rows)
        artifacts={};reports=[]
        for stem,rows,result in staged:
            data=json_bytes(rows); compressed=gzip.compress(data,mtime=0)
            result.update(candidateDataSha256=digest(data),candidateGzipSha256=digest(compressed))
            artifacts[stem+'.json']=data;artifacts[stem+'.json.gzip']=compressed
            artifacts[stem+'.csv']=csv_bytes(rows);artifacts[stem+'.validation.json']=json_bytes(result)
            reports.append(result)
        artifacts['all-candidates.csv']=csv_bytes(allrows)
        summary={'version':1,'candidateRows':len(allrows),'acceptedRows':0,'publishedRowsAdded':0,
                 'reports':reports,'commandPurpose':'staging only; no production collections or outputs are edited'}
        artifacts['summary.json']=json_bytes(summary)
        args.output.mkdir(parents=True,exist_ok=True)
        for filename,data in artifacts.items():
            target=args.output/filename;tmp=target.with_name('.'+target.name+'.tmp');tmp.write_bytes(data);tmp.replace(target)
        print(json.dumps({'candidateRows':len(allrows),'acceptedRows':0,'publishedRowsAdded':0,
            'periods':[{k:r[k] for k in ('fiscalYear','rowCount','namedRemuneration','namedExpenses','remunerationResidual','expenseResidual')} for r in reports]},indent=2))
        return 0
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':
    raise SystemExit(main())
