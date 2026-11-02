"""Independent VCH FY2020/21 reader from the original library PDF."""
import gzip,hashlib,importlib.util,json,re
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('providence_geometry',HERE/'root-providence-pdfminer.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
PDF=Path('/tmp/salary-queue-acquisition/d188294cfedc3ff87cbb.body');SHA='8d2d85205f0c4de6557e39cd8ee21ac2a38c90aa70611f1ca5bfb7c9f030d7ad'

def number(text):
    if text in {'‐','-','–','—',''}:return None
    return base.number(text)

def read():
    assert hashlib.sha256(PDF.read_bytes()).hexdigest()==SHA
    rows=[];board=[];controls=[];issues=[];proof=[]
    for pn,layout in zip([3]+list(range(4,157)),extract_pages(str(PDF),page_numbers=[2]+list(range(3,156)),laparams=LAParams(all_texts=True))):
        cells=list(base.lines(layout));isboard=pn==3
        headers=[c for c in cells if c['text']==('Board Member' if isboard else 'Employee')];assert len(headers)==1,pn
        top=headers[0]['cy']-4;payleft,payright=(230,310) if isboard else (330,405)
        anchors=[c for c in cells if payleft<c['x0']<payright and 40<c['cy']<top and re.fullmatch(r'[\d,().-]+',c['text'])]
        for a in sorted(anchors,key=lambda c:-c['cy']):
            same=[c for c in cells if abs(c['cy']-a['cy'])<3.5]
            def text(left,right):return ' '.join(c['text'] for c in sorted(same,key=lambda c:c['x0']) if left<c['x0']<right)
            name=text(45,230 if isboard else 330);exp=text(320,400) if isboard else text(480,565)
            try:pay=number(a['text']);expense=number(exp)
            except ValueError as e:issues.append({'page':pn,'why':str(e),'lines':same});continue
            if name.startswith('TOTAL') or not name:
                controls.append({'page':pn,'label':name or 'unlabelled printed board subtotal','pay':pay,'expense':expense});continue
            row=['vancouver-coastal-health',name,None,pay,expense,pn];(board if isboard else rows).append(row);proof.append({'physicalPage':pn,'row':row,'sourceLines':same})
    return {'sourceSha256':SHA,'reader':'Independent PDFMiner all_texts=True native geometry','employeeRows':rows,'boardRows':board,'controls':controls,'issues':issues,'rowEvidence':proof}

if __name__=='__main__':
    x=read();p=HERE/'root-vch-pdfminer-first-read.json.gzip';assert not p.exists();p.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));print({'employees':len(x['employeeRows']),'board':len(x['boardRows']),'issues':len(x['issues']),'controlRows':x['controls'],'paySum':sum(r[3] for r in x['employeeRows']),'knownExpenseSum':sum(r[4] or 0 for r in x['employeeRows']),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
