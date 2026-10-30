"""Extract selected native PDF drawing paths; never trace raster artwork."""
import fitz, pathlib, math, json, hashlib
from PIL import Image, ImageChops, ImageStat

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'historical-vectors'
OUT.mkdir(exist_ok=True)
JOBS = [
 ('bc-transmission-2009', 'bctc-2009', 0, range(12,44), 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/bctc.pdf'),
 ('partnerships-bc-2012', 'pbc-2012', 0, range(1,28), 'https://www.bcbudget.gov.bc.ca/annual_reports/2012_2013/pdf/agency/pbc.pdf'),
 ('bc-oil-gas-commission-2014', 'ogc-water-2014', 0, range(0,21), 'https://www.bc-er.ca/files/reports/Water-Management/2014-annual-report-water-use-oil-and-gas-activityprint-version.pdf'),
]

def f(v): return format(v, '.8g')
def point(p): return f(p.x)+' '+f(p.y)
def css(c): return 'rgb('+','.join(f(x*100)+'%' for x in c)+')'
def path_data(d):
 out=[]; last=None
 for item in d['items']:
  op=item[0]
  if op in ('l','c'):
   start=item[1]
   if last is None or abs(start.x-last.x)>1e-5 or abs(start.y-last.y)>1e-5:out.append('M '+point(start))
   if op=='l':out.append('L '+point(item[2]));last=item[2]
   else:out.append('C '+' '.join(point(x) for x in item[2:]));last=item[-1]
  elif op=='re':
   r=item[1];out.append(f'M {f(r.x0)} {f(r.y0)} L {f(r.x1)} {f(r.y0)} L {f(r.x1)} {f(r.y1)} L {f(r.x0)} {f(r.y1)} Z');last=None
  elif op=='qu':
   q=item[1];out.append('M '+point(q.ul)+' L '+point(q.ur)+' L '+point(q.lr)+' L '+point(q.ll)+' Z');last=None
  else:raise ValueError(op)
 if d['closePath']:out.append('Z')
 return ' '.join(out)

records=[]
for name,source,pgno,indices,url in JOBS:
 doc=fitz.open(ROOT/'historical-pdfs'/(source+'.pdf'));page=doc[pgno]
 drawing_list=page.get_drawings();paths=[drawing_list[i] for i in indices]
 bounds=fitz.Rect(paths[0]['rect'])
 for p in paths[1:]:bounds|=p['rect']
 crop=fitz.Rect(math.floor(bounds.x0)-1,math.floor(bounds.y0)-1,math.ceil(bounds.x1)+1,math.ceil(bounds.y1)+1)
 overlaps=[i for i in page.get_image_info() if fitz.Rect(i['bbox']).intersects(crop)]
 assert not overlaps, 'Raster image overlaps selected logo'
 elems=[]
 # SVG is sRGB. The Partnerships PDF has print-color definitions whose managed
 # rendering differs from PyMuPDF get_drawings()' simple RGB conversion. These
 # exact opaque fill samples come from the source crop, not an inferred palette.
 color_conversions = []
 if name=='partnerships-bc-2012':
  color_conversions=[{'source_drawing_rgb':list(paths[0]['fill']),'rendered_srgb':[26,124,191]}, {'source_drawing_rgb':list(paths[12]['fill']),'rendered_srgb':[111,192,104]}]
 for p in paths:
  assert p['type']=='f', 'Extraction expects solid filled native paths only'
  color=css(p['fill'])
  for conversion in color_conversions:
   if list(p['fill'])==conversion['source_drawing_rgb']:color='#'+''.join(f'{v:02x}' for v in conversion['rendered_srgb'])
  elems.append('<path d="'+path_data(p)+'" fill="'+color+'" fill-rule="'+('evenodd' if p['even_odd'] else 'nonzero')+'"/>')
 color_note=' PDF print colors converted to the source document rendering in sRGB.' if color_conversions else ''
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(crop.width)}pt" height="{f(crop.height)}pt" viewBox="{f(crop.x0)} {f(crop.y0)} {f(crop.width)} {f(crop.height)}"><title>{name}</title><desc>Native vector paths extracted from {url}, PDF page {pgno+1}. Curve coordinates retained; no raster tracing.{color_note} Date is a document sighting, not adoption date.</desc>'+''.join(elems)+'</svg>'
 path=OUT/(name+'.svg');path.write_text(svg)
 vector=fitz.open(stream=svg.encode(),filetype='svg');pdf=fitz.open('pdf',vector.convert_to_pdf());outpage=pdf[0]
 source_pix=page.get_pixmap(matrix=fitz.Matrix(4,4),clip=crop,alpha=False)
 output_pix=outpage.get_pixmap(matrix=fitz.Matrix(4,4),alpha=False)
 a=Image.frombytes('RGB',(source_pix.width,source_pix.height),source_pix.samples);b=Image.frombytes('RGB',(output_pix.width,output_pix.height),output_pix.samples)
 a.save(OUT/(name+'-source-check.png'));b.save(OUT/(name+'-preview.png'))
 metrics={'source_pixels':list(a.size),'output_pixels':list(b.size)}
 if a.size==b.size:
  diff=ImageChops.difference(a,b);metrics['mean_absolute_channel_difference_0_255']=ImageStat.Stat(diff).mean;metrics['max_channel_difference_0_255']=diff.getextrema()
 records.append({'name':name,'file':str(path),'source_pdf':str(ROOT/'historical-pdfs'/(source+'.pdf')),'source_url':url,'page':pgno+1,'bbox':list(crop),'native_path_indices':list(indices),'native_path_count':len(paths),'raster_images_in_logo_region':len(overlaps),'color_conversions':color_conversions,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_comparison':metrics})
(OUT/'extraction-validation.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
