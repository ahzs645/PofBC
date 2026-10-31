#!/usr/bin/env python3
"""Compare a local, checksum-pinned CHC source PDF with staged row captures.

Requires PyMuPDF and Poppler's pdftotext. No downloads or OCR. Never accepts or
publishes records; aggregate column interpretation and visual review stay pending.
The two readers share row-reconstruction logic, so agreement is not independent
proof of correctness. This command was not run against original PDFs in this pass.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from stage_chc_recovery import ValidationError, digest, json_bytes, parse_row, stage_capture


def reconstruct(words: list[tuple], width: float, page_number: int) -> tuple[list[tuple], list[str]]:
    """Read two side-by-side table blocks; never infer columns from amount size."""
    found=[]; suspicious=[]
    for half in (0,1):
        selected=sorted((w for w in words if (w[0] >= width/2)==bool(half)),key=lambda w:(w[1],w[0]))
        groups=[]
        for word in selected:
            match=next((g for g in reversed(groups[-3:]) if abs(g[0]-word[1])<=2.0),None)
            if match is None: groups.append([word[1],[word]])
            else: match[1].append(word)
        for _,group in groups:
            text=' '.join(w[4] for w in sorted(group,key=lambda w:w[0])).replace('\u00a0',' ')
            try:
                name,rem,exp=parse_row(text)
                found.append((name,rem,exp,page_number))
            except ValidationError:
                if re.search(r'\d[\d,]*\s+\d[\d,]*\s*$',text):
                    suspicious.append(text)
    return found,suspicious


def ensure_headers(text: str, capture: dict, page_number: int) -> None:
    normalized=' '.join(text.split()).upper()
    if 'COLUMBIA HYDRO CONSTRUCTORS LTD.' not in normalized:
        raise ValidationError(f'Wrong/missing employer header on physical page {page_number}')
    if 'SCHEDULE OF REMUNERATION PAID TO EMPLOYEES' not in normalized:
        raise ValidationError(f'Wrong/missing employee schedule on physical page {page_number}')
    end=capture['periodEnd'][:4]
    if f'YEAR ENDED MARCH 31, {end}' not in normalized:
        raise ValidationError(f'Wrong/missing year on physical page {page_number}')


def compare(reader: str, pages: dict, capture: dict, expected_rows: list[dict]) -> dict:
    wanted=Counter((r['rawName'],r['remuneration'],r['expenses'],r['pdfPage']) for r in expected_rows)
    actual=[];unparsed=[];summaries=[]
    for p in capture['pages']:
        number=p['pdfPage'];data=pages[number]
        ensure_headers(data['text'],capture,number)
        rows,suspicious=reconstruct(data['words'],data['width'],number)
        if p['rowsText']:
            actual.extend(rows);unparsed.extend({'pdfPage':number,'text':s} for s in suspicious)
        else:
            # Include any unexpectedly named row on a nominal summary page.
            actual.extend(rows)
            summaries.append({'pdfPage':number,'text':data['text']})
    observed=Counter(actual)
    missing=list((wanted-observed).elements());extra=list((observed-wanted).elements())
    return {'reader':reader,'parsedNamedRows':len(actual),'missingRows':missing,'extraRows':extra,
        'unparsedMonetaryLines':unparsed,'allNamedRowsMatch':not missing and not extra and not unparsed,
        'summaryPagesForManualReview':summaries}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capture',type=Path,required=True)
    p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:
        capture=json.loads(args.capture.read_text());expected,_=stage_capture(capture)
        data=args.pdf.read_bytes()
        if not data.startswith(b'%PDF-'): raise ValidationError('Input is not a PDF')
        sha=digest(data)
        if sha!=capture['expectedPdfSha256FromEarlierPackage']:
            raise ValidationError('PDF checksum differs from earlier reviewed source manifest; do not silently re-pin it')
        import pymupdf
        document=pymupdf.open(args.pdf)
        selected=[p['pdfPage'] for p in capture['pages']]
        if max(selected)>len(document): raise ValidationError('Source PDF is missing required pages')
        mup={}
        for n in selected:
            page=document[n-1]
            mup[n]={'width':page.rect.width,'text':page.get_text(),
                'words':[tuple(w[:5]) for w in page.get_text('words')]}
        proc=subprocess.run(['pdftotext','-bbox-layout','-enc','UTF-8',str(args.pdf),'-'],
            check=True,capture_output=True,timeout=180)
        # Poppler copies control characters from the PDF's text into its XML (the 2013/14 return has a
        # BEL on its cover page), which XML forbids. They are never part of a name or an amount.
        tree=ET.fromstring(re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]',b'',proc.stdout))
        elements=[x for x in tree.iter() if x.tag.rsplit('}',1)[-1]=='page']
        if len(elements)!=len(document): raise ValidationError('PDF reader page counts disagree')
        pop={}
        for n in selected:
            node=elements[n-1];words=[]
            for w in node.iter():
                if w.tag.rsplit('}',1)[-1]=='word':
                    words.append((float(w.attrib['xMin']),float(w.attrib['yMin']),
                                  float(w.attrib['xMax']),float(w.attrib['yMax']),w.text or ''))
            pop[n]={'width':float(node.attrib['width']),'text':' '.join(w[4] for w in words),'words':words}
        results=[compare('PyMuPDF',mup,capture,expected),compare('Poppler',pop,capture,expected)]
        passed=all(r['allNamedRowsMatch'] for r in results)
        report={'sourceId':capture['sourceId'],'pdfSha256':sha,'pdfSha256MatchesExpected':True,
            'captureSha256':digest(args.capture.read_bytes()),'readerResults':results,
            'namedRowComparisonPassed':passed,'aggregateColumnInterpretationVerified':False,
            'visualReviewCompleted':False,'acceptedForPublication':False,
            'nextStep':'Review rendered employee and summary pages, resolve flagged lines and source residuals, then use the existing publication review process.'}
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(json_bytes(report))
        print(json.dumps({k:v for k,v in report.items() if k!='readerResults'},indent=2))
        return 0 if passed else 2
    except (ImportError,OSError,ValueError,KeyError,subprocess.SubprocessError,ET.ParseError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())
