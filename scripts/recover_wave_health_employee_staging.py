#!/usr/bin/env python3
"""Freeze a fully image-transcribed PHSA page without accepting a partial cohort."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/recovery-wave-2026-11-01/health'
PDF = Path('/tmp/sector-health/phsa-2025.pdf')
IMAGE = Path('/tmp/sector-health/phsa-2025-page-1.png')
OCR = Path('/tmp/sector-health/phsa-2025-page-1.txt')
SOURCE_SHA = '809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c'
# All 49 names, amounts and row boundaries were independently read from the
# complete rendered original. No source position is disclosed. '-' stays null.
TRANSCRIPTION = '''Aarbo,Trevor|177599|1348
Abacan,Maria Celita|86695|-
Abad,Anna|118714|708
Abadi,Shirin|141292|163
Abarca Matus,Maria Eloisa|75644|1347
Abaunza,Danessa Rebecca|92096|3933
Abaya,Alejandro Luis|100351|-
Abbas,Aya|82568|-
Abbas,Harun Nisha|108744|-
Abbasi,Jahangir|101575|-
Abbott,Matthew James William|95391|-
Abbott,Robb James Prosser|150402|708
Abbott,Stephen John|118291|3442
Abdallah,Mohammed Omar Elsiddieg|120433|-
Abdelmoaty,Mai|130716|366
Abdi,Mariam|79102|645
Abdjalieva,Feruza|116424|840
Abdoh,Nora|120613|44
Abdollahi,Mohammad-Sharif|113912|-
Abdollahzadeh,Nian|118769|645
Abdulla,Salima|144371|4618
Abdulla,Shaiza|124130|673
Abdulmenan,Jalud|156246|15118
Abdulwahab,Yosuf|86884|-
Abed,Abeer|263998|6857
Abedrabbo,Randy|152025|3179
Abelardo,Marita|169688|708
Abendanio,Angela|100887|2525
Abia,Jo-Ann|122090|771
Abou Mourad,Yasser Rifaat|578869|14977
Abozaid,Wisam|78311|-
Abraham,Anju Mary|84890|-
Abraham,Hadassah|80388|-
Abraham,Rohan|76889|-
Abrahams,Bethina|138531|2443
Abrahams,Kristy Belle|127445|1876
Abreo,Lebert|138540|3518
Abriel,Danica|101753|708
Abril,Lorraine|95929|-
Absolon,Nancy|111436|1758
Abu Salim,Wael|99460|392
Abubakar,Ibrahim|110360|-
Abu-Remaileh,Haneen|188684|7547
Abustan,Priscilla|98855|-
Accili,Laura|75691|-
Achen,Melanie Wynne|126780|1353
Ackerman,Jacob|183250|5568
Ackerman,Jennifer|107892|-
Ackley,Emily|84464|37'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(raw, image_sha):
    body = raw.split('Name Remuneration Expenses\n', 1)[1].split('\nThis statement', 1)[0]
    parsed = []
    for line in body.splitlines():
        match = re.fullmatch(r'(.*?) (\d[\d,]*) (\S+)', line)
        if not match:
            raise ValueError('Unrecognized raw OCR row: ' + line)
        parsed.append(match.groups())
    if len(parsed) != 49:
        raise ValueError('Raw OCR row boundaries changed')
    rows, evidence = [], []
    for i, (line, ocr) in enumerate(zip(TRANSCRIPTION.splitlines(), parsed)):
        name, pay, expense = line.split('|')
        pay = int(pay)
        expense = None if expense == '-' else int(expense)
        row = ['provincial-health-services-authority', name, None, pay, expense, 1]
        rows.append(row)
        evidence.append(dict(physicalPage=1, sourceRowOnPage=i+1, visibleName=name,
                             visibleRemuneration=pay, visibleExpense=expense,
                             visibleExpenseToken='-' if expense is None else f'{expense:,}',
                             rawTesseractName=ocr[0], rawTesseractRemuneration=ocr[1],
                             rawTesseractExpense=ocr[2], row=row,
                             manualImageReview='Every name, remuneration, expense and complete row boundary compared to rendered original; no position is published.'))
    e = dict(status='staged-partial-employee-page-not-for-import',
             sourceId='phsa-2024-25-employee-page-1-staged',
             employerSlug='provincial-health-services-authority', year='2024/25',
             periodType='fiscal', periodStart='2024-04-01', periodEnd='2025-03-31',
             sourceUrl='https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf',
             sourceIndexUrl='https://www.phsa.ca/about/accountability/budget-financials',
             sourceSha256=SOURCE_SHA, sourceBytes=54160556, sourceCachePath=str(PDF),
             pdfPages=284, nativeTextCharacters=0, scope='employee-remuneration',
             completeEmployeeSchedule=False, acceptedRows=0, stagedRows=49,
             physicalPagesManuallyReviewed=[1],
             physicalPagesNotReviewed={'first':2, 'last':284, 'count':283},
             sourceDefinition='Alphabetical list of employees who received remuneration exceeding $75,000 for the year ended March 31, 2025 and their expenses paid during this period. Expenses may have been reimbursed directly to employees and/or paid to a third party supplier.',
             publicationStatus='Official published scan, unsigned; no draft wording visible on reviewed page. Remaining source pages were not visually reviewed in this tranche.',
             reviewImage={'path':str(IMAGE), 'sha256':image_sha, 'dimensions':[1224,1584],
                          'render':'PyMuPDF matrix (2,2), physical page1'},
             ocr={'engine':'Tesseract 5.5.0, eng, --psm 6', 'textSha256':sha(raw.encode()),
                  'text':raw, 'independentOcrEngines':1,
                  'independentAcceptance':'Manual full-page image transcription is an independent reader for this staged page only; it does not verify the remaining original.'},
             rows=rows, rowEvidence=evidence,
             blocker='283 original pages remain without complete independent row verification. No full-cohort acceptance or compiled replacement follows from this staged page.',
             nextAction='Peer-review all 49 staged rows; use this guarded page fixture for a complete independent OCR/manual workflow, or obtain the existing electronic schedule using the prior unsent ordinary-copy request. Verify every remaining image page before proposing a full cohort.')
    return e


def run(originals=False, check=False):
    path = OUT / 'phsa-2024-25-page-1-staged.json.gzip'
    if originals:
        if sha(PDF.read_bytes()) != SOURCE_SHA:
            raise ValueError('Original source changed')
        raw, image_sha = OCR.read_text(), sha(IMAGE.read_bytes())
    else:
        old = json.loads(gzip.decompress(path.read_bytes()))
        raw, image_sha = old['ocr']['text'], old['reviewImage']['sha256']
    e = build(raw, image_sha)
    data = gzip.compress(json.dumps(e, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)
    summary = {k:v for k,v in e.items() if k not in ['rows','rowEvidence','ocr']}
    summary.update(stagedEvidenceSha256=sha(data),
                   stagedTotalRemuneration=sum(r[3] for r in e['rows']),
                   stagedTotalDisclosedExpenses=sum(r[4] or 0 for r in e['rows']),
                   missingExpenseRows=sum(r[4] is None for r in e['rows']),
                   ocrFullRowMismatchCount=sum((x['rawTesseractName'] != x['visibleName']) or
                                              (x['rawTesseractRemuneration'] != f"{x['visibleRemuneration']:,}") or
                                              (x['rawTesseractExpense'] != x['visibleExpenseToken']) for x in e['rowEvidence']),
                   specialCorrection={'name':'Abia,Jo-Ann','rawOcrExpense':'™m','visibleExpense':771,
                                      'reason':'Both existing Tesseract configurations failed; the rendered source visibly shows 771.'})
    receipt = json.dumps(summary, ensure_ascii=False, indent=2)+'\n'
    if check:
        if path.read_bytes() != data or (OUT/'employee-staging-receipt.json').read_text() != receipt:
            raise ValueError('Frozen employee staging differs')
    else:
        path.write_bytes(data)
        (OUT/'employee-staging-receipt.json').write_text(receipt)
    print(json.dumps({k:summary[k] for k in ['acceptedRows','stagedRows','stagedTotalRemuneration','stagedTotalDisclosedExpenses','missingExpenseRows','ocrFullRowMismatchCount']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--originals', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    run(args.originals, args.check)
