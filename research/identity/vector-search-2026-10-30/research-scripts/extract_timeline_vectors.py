"""Extract published Canada Starts Here paths, preserving native PDF geometry."""
import hashlib, json, math
from pathlib import Path
import fitz
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent / 'timeline'
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)

def fmt(value): return format(value, '.9g')
def point(p): return fmt(p.x) + ' ' + fmt(p.y)
def data(drawing):
    items = []
    last = None
    for item in drawing['items']:
        op = item[0]
        if op in ('l', 'c'):
            start = item[1]
            if last is None or abs(start.x-last.x)>1e-5 or abs(start.y-last.y)>1e-5:
                items.append('M ' + point(start))
            if op == 'l':
                items.append('L ' + point(item[2])); last = item[2]
            else:
                items.append('C ' + ' '.join(point(p) for p in item[2:])); last = item[-1]
        elif op == 're':
            r = item[1]
            items.append(f'M {fmt(r.x0)} {fmt(r.y0)} L {fmt(r.x1)} {fmt(r.y0)} L {fmt(r.x1)} {fmt(r.y1)} L {fmt(r.x0)} {fmt(r.y1)} Z')
            last = None
        else:
            raise ValueError(op)
    if drawing['closePath']: items.append('Z')
    return ' '.join(items)

records = []
jobs = [
 ('canada-starts-here-2012', 'BC-Jobs-Plan.pdf', 'https://www.amssa.org/wp-content/uploads/2015/05/BC-Jobs-Plan.pdf', 23, '2012-09-11', list(range(140,163)), False),
 ('canada-starts-here-bc-jobs-plan-2012', 'BC-Jobs-Plan.pdf', 'https://www.amssa.org/wp-content/uploads/2015/05/BC-Jobs-Plan.pdf', 23, '2012-09-11', list(range(129,163)), False),
 ('bc-public-service-where-ideas-work-2023-reverse', 'wiw-corporateplan-2023.pdf', 'https://www2.gov.bc.ca/assets/gov/careers/about-the-bc-public-service/corporate-digital/corporateplan_2023.pdf', 10, '2023', list(range(1,52)), True),
]
for stem, filename, url, pgno, date, indices, reversed_ink in jobs:
    source = ROOT / 'sources' / filename
    doc = fitz.open(source)
    page = doc[pgno]
    drawings = page.get_drawings()
    chosen = [drawings[i] for i in indices]
    bounds = fitz.Rect(chosen[0]['rect'])
    for item in chosen[1:]: bounds |= item['rect']
    crop = fitz.Rect(math.floor(bounds.x0)-1, math.floor(bounds.y0)-1, math.ceil(bounds.x1)+1, math.ceil(bounds.y1)+1)
    assert not any(fitz.Rect(image['bbox']).intersects(crop) for image in page.get_image_info())
    assert not page.get_text('text',clip=crop).strip()
    parts=[]
    for d in chosen:
        assert d['type']=='f'
        color='rgb('+','.join(fmt(c*100)+'%' for c in d['fill'])+')'
        rule='evenodd' if d['even_odd'] else 'nonzero'
        parts.append(f'<path d="{data(d)}" fill="{color}" fill-rule="{rule}"/>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(crop.width)}pt" height="{fmt(crop.height)}pt" viewBox="{fmt(crop.x0)} {fmt(crop.y0)} {fmt(crop.width)} {fmt(crop.height)}"><title>{stem}</title><desc>Native paths extracted from the published document, page {pgno+1}, dated {date}. Source: {url}. No raster tracing. The date is a dated specimen, not an adoption date.</desc>'+''.join(parts)+'</svg>'
    target=OUT/(stem+'.svg');target.write_text(svg)
    vector=fitz.open(stream=svg.encode(),filetype='svg')
    pdf=fitz.open('pdf',vector.convert_to_pdf())
    source_pix=page.get_pixmap(matrix=fitz.Matrix(4,4),clip=crop,alpha=False)
    output_pix=pdf[0].get_pixmap(matrix=fitz.Matrix(4,4),alpha=reversed_ink)
    a=Image.frombytes('RGB',(source_pix.width,source_pix.height),source_pix.samples)
    b=Image.frombytes('RGBa' if reversed_ink else 'RGB',(output_pix.width,output_pix.height),output_pix.samples)
    if reversed_ink:
        b=b.convert('RGBA')
        background=Image.new('RGB',b.size,a.getpixel((0,0)))
        background.paste(b,(0,0),b)
        b=background
    a.save(ROOT/(stem+'-source-check.png'));b.save(ROOT/(stem+'-preview.png'))
    metrics={'source_pixels':list(a.size),'output_pixels':list(b.size)}
    if a.size==b.size: metrics['mean_absolute_channel_difference_0_255']=ImageStat.Stat(ImageChops.difference(a,b)).mean
    records.append({'file':str(target),'source_url':url,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'page':pgno+1,'source_date':date,'date_type':'dated_specimen','native_path_indices':indices,'native_path_count':len(chosen),'raster_images_in_logo_region':0,'bbox':list(crop),'reversed':reversed_ink,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'comparison':metrics})
(ROOT/'extraction-validation.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
