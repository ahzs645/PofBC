"""Independent visible-table geometry reader; never reads author's candidates."""
import gzip,hashlib,json,re
from decimal import Decimal
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLine,LAParams
ROOT=Path(__file__).resolve().parents[4]
PDF=Path('/tmp/salary-queue-acquisition/cdc461cbb98dda93ede3.body')
SHA='521472f784463bf42626b9c74aeb72252167346b65b8a123031ca59e46ecb5f3'
OUT=Path(__file__).parent

def lines(obj):
    if isinstance(obj,LTTextLine):
        text=' '.join(obj.get_text().split())
        if text:yield {'x0':obj.x0,'x1':obj.x1,'cy':(obj.y0+obj.y1)/2,'text':text}
    elif hasattr(obj,'__iter__'):
        for child in obj:yield from lines(child)

def number(text):
    token=text.strip()
    if token in {'-','–','—'}:return None
    if not re.fullmatch(r'\(?-?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?\)?',token):raise ValueError(('Unparsed money',text))
    return float(Decimal(token.replace(',','').replace('(','-').replace(')','')))

def native_read():
    assert hashlib.sha256(PDF.read_bytes()).hexdigest()==SHA
    rows=[];board=[];proof=[];issues=[];controls=[]
    for page,layout in zip([56]+list(range(58,223)),extract_pages(str(PDF),page_numbers=[55]+list(range(57,222)),laparams=LAParams(all_texts=True))):
        cells=list(lines(layout));pay=[c for c in cells if 325<=c['x0']<440 and 50<c['cy']<580 and re.fullmatch(r'[-–—\d,().]+',c['text'])]
        for anchor in sorted(pay,key=lambda c:-c['cy']):
            same=[c for c in cells if abs(c['cy']-anchor['cy'])<10.5]
            def text(left,right):return ' '.join(c['text'] for c in sorted(same,key=lambda c:(-round(c['cy']/3),c['x0'])) if left<=c['x0']<right)
            surname=text(60,210 if page!=56 else 325);first=text(210,325) if page!=56 else None
            if not surname:issues.append({'page':page,'why':'No name','anchor':anchor,'same':same});continue
            exp=text(445,575)
            try:payvalue=number(anchor['text']);expense=number(exp)
            except ValueError as e:issues.append({'page':page,'why':str(e),'anchor':anchor,'same':same});continue
            if surname.lower().startswith('total'):
                controls.append({'page':page,'label':surname,'pay':payvalue,'expense':expense});continue
            if page!=56 and not first:issues.append({'page':page,'why':'No first name','surname':surname,'anchor':anchor});continue
            row=['providence-health-care',surname if page==56 else surname+', '+first,None,payvalue,expense,page]
            (board if page==56 else rows).append(row);proof.append({'page':page,'row':row,'payAnchor':anchor,'sourceLines':same})
    return {'sourceSha256':SHA,'reader':'PDFMiner LAParams(all_texts=True), independent geometry and literal field parsing','employeeRows':rows,'boardRowsIncludingNonNumericPay':board,'controls':controls,'issues':issues,'rowEvidence':proof}

if __name__=='__main__':
    result=native_read();payload=json.dumps(result,ensure_ascii=False,separators=(',',':')).encode();path=OUT/'root-providence-pdfminer-first-read.json.gzip';assert not path.exists();path.write_bytes(gzip.compress(payload,mtime=0));print({'employees':len(result['employeeRows']),'board':len(result['boardRowsIncludingNonNumericPay']),'issues':len(result['issues']),'controls':result['controls'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
