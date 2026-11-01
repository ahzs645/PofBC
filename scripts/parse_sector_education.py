#!/usr/bin/env python3
"""Reproduce SFU employee schedules from hash-pinned official SOFI PDFs.

Only the six accepted source cohorts enter sector-education/sources.json.
The three held candidates are verified for reproducibility but remain outside it.
Requires PyMuPDF and Poppler pdftotext. No OCR or source-row corrections are applied.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import fitz
ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = ROOT / "research/salaries/sector-education"
HELD = ROOT / "research/salaries/sector-search-2026-10-31/education/held"
MONEY = re.compile(r"^-?\d{1,3}(?:,\d{3})*$")


def core(words, pageno):
 words=[w for w in words if 40<w[0]<566 and 45<w[1]<742]
 out=[];wrapped=[];layouts=[]
 for x0,x1 in [(40,306),(308,566)]:
  w=[v for v in words if x0<=v[0]<x1]
  cutoff=min([v[1] for v in w if v[4]=='Earnings'] or [742])
  heads=[v[1] for v in w if v[4]=='Remuneration' and v[1]<150];head=max(heads or [98])
  w=[v for v in w if head+2<v[1]<cutoff-1]
  candidates=[v for v in w if 150+x0-40<v[0]<250+x0-40 and MONEY.fullmatch(v[4]) and 75000<=int(v[4].replace(',',''))<1000000]
  if not candidates:
   assert not [v for v in w if v[4] not in ['Name','Expenses']],(pageno,w)
   continue
  payright=collections.Counter(round(v[2],1) for v in candidates).most_common(1)[0][0]
  epc=[v for v in w if 255+x0-40<v[0]<306+x0-40 and (v[4]=='-' or MONEY.fullmatch(v[4]))]
  expright=collections.Counter(round(v[2],1) for v in epc).most_common(1)[0][0] if epc else 300
  anchors=sorted([v for v in w if abs(v[2]-payright)<1 and MONEY.fullmatch(v[4])],key=lambda a:a[1])
  layouts.append([pageno,x0,payright,expright,head,cutoff])
  used=set()
  names=[(i,v) for i,v in enumerate(w) if v[0]<payright-35]
  lines=[]
  for i,v in sorted(names,key=lambda q:(round(q[1][1]),q[1][0])):
   if not lines or abs(lines[-1][0]-v[1])>1:lines.append([v[1],[]])
   lines[-1][1].append((i,v))
  groups=[]
  for yy,line in lines:
   line.sort(key=lambda q:q[1][0]);st=' '.join(v[4] for i,v in line)
   if ',' in st:groups.append([yy,st,line,1])
   else:
    assert groups,(pageno,'name continuation without first line',st)
    groups[-1][1]+= ('' if groups[-1][1].endswith('-') else ' ')+st
    groups[-1][2].extend(line);groups[-1][3]+=1
  assert len(groups)==len(anchors),(pageno,len(groups),len(anchors))
  for j,(yy,namestr,name,lc) in enumerate(groups):
   nxt=groups[j+1][0] if j+1<len(groups) else cutoff
   row=[(i,v) for i,v in enumerate(w) if yy-.75<=v[1]<nxt-.75]
   rowanchors=[v for i,v in row if abs(v[2]-payright)<1 and MONEY.fullmatch(v[4])]
   assert len(rowanchors)==1,(pageno,namestr,rowanchors)
   a=rowanchors[0]
   exp=[(i,v) for i,v in row if abs(v[2]-expright)<1]
   assert len(exp)<=1,(pageno,namestr,exp)
   expt=exp[0][1][4] if exp else '-'
   assert expt=='-' or MONEY.fullmatch(expt) or expt=='(0)',(pageno,namestr,expt)
   pay=int(a[4].replace(',',''));assert pay>=75000,(pageno,namestr,pay)
   assert ',' in namestr and not any(z in namestr for z in ['Expenses','Earnings','Total']),(pageno,namestr)
   if lc>1:wrapped.append((pageno,namestr,pay))
   out.append([namestr,None,pay,None if expt=='-' else int(expt.replace(',','').strip('()')),pageno])
   for i,v in row:
    if v==a or any(i==k for k,z in name+exp):used.add(i)
   leftovers=[v for i,v in row if i not in used]
   assert not leftovers,(pageno,namestr,leftovers)
  unmatched=[v for i,v in enumerate(w) if i not in used and v[1]>=groups[0][0]-.75]
  assert not unmatched,(pageno,'unmatched',unmatched)
 return out,wrapped,layouts


def poppler_words(path):
    run = subprocess.run(["pdftotext", "-bbox-layout", str(path), "-"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Poppler emits XML-forbidden U+0007 in a separator outside employee cells.
    xml = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", run.stdout)
    tree = ET.fromstring(xml)
    ns = {"x": "http://www.w3.org/1999/xhtml"}
    return [[(float(w.attrib["xMin"]), float(w.attrib["yMin"]), float(w.attrib["xMax"]), float(w.attrib["yMax"]), w.text) for w in page.findall(".//x:word", ns)] for page in tree.findall(".//x:page", ns)]


def control_values(words):
    labels = [w for w in words if w[4] == "Earnings"]
    assert len(labels) == 2, ("missing named/under-threshold control labels", labels)
    labels.sort(key=lambda w: w[1])
    first, second = labels
    xmin, xmax = (40, 306) if first[0] < 306 else (308, 566)
    pay_min = xmin + 100
    selected = [w for w in words if xmin <= w[0] < xmax and first[1] - 1 <= w[1] < second[1] - 1 and w[0] > pay_min and MONEY.fullmatch(w[4])]
    selected.sort(key=lambda w: w[0])
    assert len(selected) == 2, ("ambiguous named controls", selected)
    return tuple(int(w[4].replace(",", "")) for w in selected)


def reproduce(source, pdf):
    original = pdf.read_bytes()
    assert hashlib.sha256(original).hexdigest() == source["sha256"], (source["id"], "original fingerprint changed")
    doc = fitz.open(pdf)
    alternate = poppler_words(pdf)
    rows, wrapped = [], []
    for physical_page in source["pages"]:
        page = doc[physical_page - 1]
        primary, wrap, layout = core([w[:5] for w in page.get_text("words")], physical_page)
        secondary, _, _ = core(alternate[physical_page - 1], physical_page)
        assert primary == secondary, (source["id"], physical_page, "reader disagreement")
        rows.extend([[source["employerSlug"]] + row for row in primary])
        wrapped.extend(wrap)
    last = source["pages"][-1]
    primary_controls = control_values([w[:5] for w in doc[last - 1].get_text("words")])
    secondary_controls = control_values(alternate[last - 1])
    assert primary_controls == secondary_controls == (source["validation"]["publishedNamedRemuneration"], source["validation"]["publishedNamedExpenses"])
    text = "\n".join(p.get_text() for p in doc)
    end_year = int(source["periodEnd"][:4])
    assert re.search(r"March\s+31,?\s+" + str(end_year), text), (source["id"], "period heading changed")
    assert "Employee Remuneration and Expenses" in text
    assert re.search(r"equal\s+to\s+\$75,000", text), (source["id"], "threshold changed")
    body = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    assert hashlib.sha256(body).hexdigest() == source["normalizedSha256"], (source["id"], "normalized rows changed")
    assert len(rows) == source["rowCount"]
    assert sum(r[3] for r in rows) == source["totalRemuneration"]
    assert sum(r[4] or 0 for r in rows) == source["totalDisclosedExpenses"]
    assert len(wrapped) == source["validation"]["wrappedNameCells"]
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=Path("/tmp/pofbc-sector-education"))
    parser.add_argument("--download", action="store_true", help="retrieve missing originals from pinned official URLs")
    parser.add_argument("--verify", action="store_true", help="verify source originals and committed normalized bytes (default)")
    args = parser.parse_args()
    args.pdf_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for folder in [ACCEPTED, HELD]:
        for source in json.loads((folder / "sources.json").read_text())["sources"]:
            year = source["periodEnd"][:4]
            pdf = args.pdf_dir / f"sfu-{year}.pdf"
            if not pdf.exists() and args.download:
                request = urllib.request.Request(source["sourceUrl"], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=60) as response:
                    pdf.write_bytes(response.read())
            rows = reproduce(source, pdf)
            normalized = folder / source["file"]
            compressed = normalized.read_bytes()
            assert hashlib.sha256(compressed).hexdigest() == source["dataSha256"]
            assert json.loads(gzip.decompress(compressed)) == rows
            results.append({"id": source["id"], "status": source["status"], "rows": len(rows), "remunerationResidual": source["validation"]["remunerationResidual"], "expensesResidual": source["validation"]["expensesResidual"]})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
