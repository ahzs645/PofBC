from pathlib import Path
from lxml import etree
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json,re,subprocess,hashlib
from pypdf import PdfReader
from pypdf.generic import ContentStream
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'vector-validation.json'
NS='http://www.w3.org/2000/svg'
def px(v):
 m=re.fullmatch(r'\s*([0-9.]+)\s*(in|mm|cm|pt|px)?\s*',v or '')
 if not m:return None
 return float(m[1])*{None:1,'px':1,'in':96,'mm':96/25.4,'cm':96/2.54,'pt':96/72}[m[2]]
def svg_check(p):
 data=p.read_bytes();r=etree.fromstring(data);els=list(r.iter());tags=Counter(etree.QName(e).localname for e in els if isinstance(e.tag,str));ids=Counter(e.get('id') for e in els if isinstance(e.tag,str) and e.get('id'));links=[];scripts=[]
 for e in els:
  if not isinstance(e.tag,str):continue
  for k,v in e.attrib.items():
   loc=etree.QName(k).localname
   if loc=='href' and not v.startswith('#'):links.append({'element':etree.QName(e).localname,'attribute':k,'value':v[:150]})
   if loc.startswith('on'):scripts.append({'element':etree.QName(e).localname,'attribute':k})
   for target in re.findall(r'url\([\s\"\']*([^\)\"\']+)',v):
    if not target.startswith('#'):links.append({'element':etree.QName(e).localname,'attribute':k,'value':target[:150]})
 style_external=[]
 for e in els:
  if isinstance(e.tag,str) and etree.QName(e).localname=='style':
   s=e.text or ''
   if '@import' in s or re.search(r'url\(\s*[\"\']?(?!#)',s):style_external.append(s[:150])
 res={'file':p.name,'sha256':hashlib.sha256(data).hexdigest(),'elements':dict(tags),'ids':len(ids),'duplicate_ids':[k for k,n in ids.items() if n>1],'forbidden_tags':{k:tags[k] for k in ['image','text','tspan','textPath','foreignObject','script','iframe','video','audio','canvas'] if tags[k]},'external_links':links,'event_handlers':scripts,'external_styles':style_external,'width_px':px(r.get('width')),'height_px':px(r.get('height'))}
 q=subprocess.run(['inkscape',str(p),'--query-all'],capture_output=True,text=True,timeout=45)
 res['inkscape_query_returncode']=q.returncode
 bounds=[]
 for s in q.stdout.splitlines():
  a=s.rsplit(',',4)
  try:
   if len(a)==5:bounds.append((a[0],*[float(v) for v in a[1:]]))
  except ValueError:pass
 res['queried_objects']=len(bounds)
 W,H=res['width_px'],res['height_px'];tol=.12
 outside=[]
 if W and H:
  for id,x,y,w,h in bounds:
   if x < -tol or y < -tol or x+w > W+tol or y+h > H+tol:outside.append({'id':id,'bbox':[x,y,w,h],'overflow':[max(0,-x),max(0,-y),max(0,x+w-W),max(0,y+h-H)]})
 res['objects_outside_canvas']=outside
 if q.returncode:res['query_error']=q.stderr[-1000:]
 return res

def pdf_check(p):
 data=p.read_bytes();reader=PdfReader(p);image_objs=[];inline_images=[];seen=set();forms=0;operators=Counter()
 def visitresources(resources,page):
  nonlocal forms
  if not resources:return
  resources=resources.get_object()
  xobjs=resources.get('/XObject')
  if not xobjs:return
  for name,ref in xobjs.get_object().items():
   key=(getattr(ref,'idnum',None),getattr(ref,'generation',None))
   if key[0] is not None and key in seen:continue
   if key[0] is not None:seen.add(key)
   obj=ref.get_object();sub=str(obj.get('/Subtype'))
   if sub=='/Image':image_objs.append({'page':page,'name':str(name),'width':obj.get('/Width'),'height':obj.get('/Height')})
   if sub=='/Form':
    forms+=1
    try:
     cs=ContentStream(obj,reader)
     for operands,op in cs.operations:
      operators[op.decode(errors='replace')]+=1
      if op==b'INLINE IMAGE':inline_images.append({'page':page,'form':str(name)})
    except Exception as exc:pass
    visitresources(obj.get('/Resources'),page)
 for i,page in enumerate(reader.pages,1):
  visitresources(page.get('/Resources'),i)
  cs=page.get_contents()
  if cs:
   for operands,op in cs.operations:
    operators[op.decode(errors='replace')]+=1
    if op==b'INLINE IMAGE':inline_images.append({'page':i})
 return {'file':p.name,'sha256':hashlib.sha256(data).hexdigest(),'pages':len(reader.pages),'image_xobjects':image_objs,'inline_images':inline_images,'form_xobjects':forms,'path_move_operators':operators['m'],'path_curve_operators':operators['c'],'text_show_operators':sum(operators[x] for x in ['Tj','TJ',"'",'"'])}
svgfiles=sorted((ROOT/'svg').glob('*.svg'));pdffiles=sorted((ROOT/'pdf').glob('*.pdf'))
with ThreadPoolExecutor(max_workers=4) as pool:sres=list(pool.map(svg_check,svgfiles))
pres=[pdf_check(p) for p in pdffiles]
report={'scope':'26 production SVG assets and their individual PDF exports. Guide and original reference photographs excluded. Read-only validation.',
'svg_count':len(sres),'pdf_count':len(pres),'matching_stems':{p.stem for p in svgfiles}=={p.stem for p in pdffiles},'svg':sres,'pdf':pres}
report['summary']={'svg_image_elements':sum(x['elements'].get('image',0) for x in sres),'live_text_elements':sum(x['elements'].get('text',0)+x['elements'].get('tspan',0)+x['elements'].get('textPath',0) for x in sres),'svg_path_elements':sum(x['elements'].get('path',0) for x in sres),'svg_external_links':sum(len(x['external_links'])+len(x['external_styles']) for x in sres),'svg_scripts_or_event_handlers':sum(x['elements'].get('script',0)+len(x['event_handlers']) for x in sres),'svg_foreignobjects':sum(x['elements'].get('foreignObject',0) for x in sres),'svg_files_with_duplicate_ids':[x['file'] for x in sres if x['duplicate_ids']],'svg_files_with_canvas_overflow':[x['file'] for x in sres if x['objects_outside_canvas']],'inkscape_query_failures':[x['file'] for x in sres if x['inkscape_query_returncode']],'pdf_image_xobjects':sum(len(x['image_xobjects']) for x in pres),'pdf_inline_images':sum(len(x['inline_images']) for x in pres),'pdf_pages':sum(x['pages'] for x in pres),'pdf_text_show_operators':sum(x['text_show_operators'] for x in pres)}
REPORT.write_text(json.dumps(report,indent=2));print(json.dumps(report['summary'],indent=2))
for x in sres:
 if x['duplicate_ids'] or x['objects_outside_canvas']:print(json.dumps({k:x[k] for k in ['file','duplicate_ids','objects_outside_canvas']}))
