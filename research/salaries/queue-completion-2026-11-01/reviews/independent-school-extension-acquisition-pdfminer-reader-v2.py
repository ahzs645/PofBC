import json,pathlib,hashlib,gzip,re,decimal,collections,time
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar,LAParams
BASE=pathlib.Path('/tmp/independent-school-extension-acquisition/v2');BASE.mkdir(exist_ok=True);inputs=json.loads(pathlib.Path(__file__).with_name('independent-school-extension-acquisition-source-inputs.json').read_text())['sources']
inputs=[s for s in inputs if s['key'] in ['sd23-2025','sd73-2025']]
# Reader-only post-comparison geometry corrections. v1 transcript and reader remain unchanged.
SCHEMA={
 'sd23-2025':{'employees':[(50,147),(147,394),(394,463),(463,535)],'trustees':[(50,200),None,(200,370),(390,490)],'trusteePages':[55]},
 'sd33-2025':{'employees':[(50,383),None,(383,478),(478,560)],'trustees':[(50,230),None,(230,355),(360,425)],'trusteePages':[81]},
 'sd36-2025':{'employees':[(35,249),(403,610),(249,326),(326,400)],'trustees':[(35,205),(205,373),(373,480),(486,560)],'trusteePages':[56]},
 'sd43-2025':{'employees':[(50,250),(250,435),(435,510),(510,585)],'trustees':[(50,259),(259,400),(400,515),(515,585)],'trusteePages':[60]},
 'sd61-2025':{'employees':[(90,202.3),(202.3,426),(426,490),(490,545)],'trustees':[(90,202.3),(202.3,426),(426,490),(490,545)],'trusteePages':[],'sharedPage':7,'sharedCut':250},
 'sd68-2025':{'employees':[(55,245),(245,445),(445,533),(533,585)],'trustees':[(55,245),(245,445),(445,533),(533,585)],'trusteePages':[],'sharedPage':55,'sharedCut':420},
 'sd73-2025':{'employees':[(45,237),(237,414),(414,495),(495,550)],'trustees':[(95,209),(209,379),(379,484),(484,560)],'trusteePages':[73]}}
def sha(b):return hashlib.sha256(b).hexdigest()
def chars(node):
 out=[]
 def go(x):
  if isinstance(x,LTChar):out.append({'text':x.get_text(),'x0':x.x0,'x1':x.x1,'y0':x.y0,'y1':x.y1,'baseline':x.matrix[5],'size':x.size});return
  if hasattr(x,'__iter__'):
   for z in x:go(z)
 go(node);return out
def text(cs):
 s='';prev=None
 for c in sorted(cs,key=lambda c:c['x0']):
  if prev and c['x0']-prev['x1']>max(.7,prev['size']*.16) and not s.endswith(' ') and not c['text'].isspace():s+=' '
  s+=c['text'];prev=c
 return ' '.join(s.split())
def amount(raw):
 token=''.join(raw.split()).replace('$','').replace(',','').replace('−','-').replace('‐','-').strip('*')
 if token in ['-','–','—','--']:return None,'explicit-source-dash'
 if not token:return None,'missing-source-token'
 if token.startswith('(') and token.endswith(')'):token='-'+token[1:-1]
 if not re.fullmatch(r'-?\d+(?:\.\d{1,2})?',token):raise ValueError(raw)
 d=decimal.Decimal(token);return (float(d) if '.' in token else int(d)),'literal-number'
def run():
 allsources=[]
 for s in inputs:
  assert sha(pathlib.Path(s['originalPath']).read_bytes())==s['originalSha256'];cfg=SCHEMA[s['key']];records=[];controls=[];issues=[];pg=[];start=time.time()
  for pn,layout in zip(s['completePhysicalSalaryPages'],extract_pages(s['originalPath'],page_numbers=[i-1 for i in s['completePhysicalSalaryPages']],laparams=LAParams(char_margin=.6,line_margin=.15))):
   cs=chars(layout);baselines=[]
   for c in sorted(cs,key=lambda c:-c['baseline']):
    if not baselines or abs(baselines[-1][0]['baseline']-c['baseline'])>.9:baselines.append([c])
    else:baselines[-1].append(c)
   count=0
   for group in baselines:
    y=layout.height-group[0]['baseline'];scope='trustees' if pn in cfg['trusteePages'] or (pn==cfg.get('sharedPage') and y<cfg.get('sharedCut',0)) else 'employees';bounds=cfg[scope]
    if not (50 if s['key']=='sd23-2025' else 95)<y<layout.height-35:continue
    fields=[text([c for c in group if b[0]<=c['x0']<b[1]]) if b else '' for b in bounds];n,title,pay,exp=fields
    if not n or '$' in n or n.upper().startswith(('TOTAL','SUBTOTAL','JULY','EMPLOYEES,','WHOSE','A. LIST','FOR ','SCHOOL ','STATEMENT ','SCHEDULE ','PREPARED ')):
     if n and pay.strip():controls.append({'physicalPage':pn,'sourceBaselineFromTop':y,'fields':fields})
     continue
    try:pv,pk=amount(pay)
    except ValueError:
     if ',' in n and any(c.isdigit() for c in pay):issues.append({'physicalPage':pn,'name':n,'field':'remuneration','raw':pay,'reason':'unparsed-pay-cell'})
     continue
    if not n or ',' not in n:
     if n and (pk=='literal-number' or exp.strip()):controls.append({'physicalPage':pn,'sourceBaselineFromTop':y,'fields':fields})
     continue
    try:ev,ek=amount(exp)
    except ValueError:issues.append({'physicalPage':pn,'name':n,'field':'expenses','raw':exp});continue
    if pk!='literal-number':issues.append({'physicalPage':pn,'name':n,'field':'remuneration','kind':pk,'raw':pay});continue
    if ek=='missing-source-token':issues.append({'physicalPage':pn,'name':n,'field':'expenses','kind':ek})
    n=re.sub(r'\s*,\s*',',',n);row=['school-district-'+s['key'][2:4],n,title or None,pv,ev,pn];records.append({'row':row,'scope':scope,'rawCells':fields,'remunerationKind':pk,'expensesKind':ek,'sourceBaselineFromTop':y,'fieldBounds':bounds});count+=1
   pg.append({'physicalPage':pn,'width':layout.width,'height':layout.height,'sourceCharacters':len(cs),'salaryRows':count,'topSourceText':' | '.join(text(g) for g in baselines if layout.height-g[0]['baseline']<120)})
  result={'key':s['key'],'originalPath':s['originalPath'],'sourceSha256':s['originalSha256'],'reader':'Independently built PDFMiner LTChar matrix-baseline grouping and geometric character columns. v2 corrects only source-image-verified SD23 name/title separator and SD73 visible left annotations after candidate comparison; original v1 remains frozen.','records':records,'controls':controls,'readerIssues':issues,'pages':pg};allsources.append(result);print(s['key'],'rows',len(records),'scopes',dict(collections.Counter(r['scope'] for r in records)),'issues',len(issues),issues[:6],flush=True)
  (BASE/(s['key']+'-stage.json.gzip')).write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 (BASE/'reader-stage-summary.json').write_text(json.dumps([{'key':s['key'],'records':len(s['records']),'issues':s['readerIssues']} for s in allsources],ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':run()
