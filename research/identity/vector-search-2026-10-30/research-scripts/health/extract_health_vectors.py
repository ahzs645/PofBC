"""Extract source vector geometry without tracing or redrawing.

Input PHSA artwork: GSC public brand archive 1.0.4, 15 July 2026.
Input Interior Health artwork: official IH Wayfinding Signage Guideline PDF.
The FNHA SVGs are originals and do not need conversion.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import fitz
from lxml import etree

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'vectors'
OUT.mkdir(exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
records = []

def info(path):
    data=path.read_bytes()
    root=etree.fromstring(data)
    return {'file': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'paths': len(root.findall('.//{%s}path'%NS)), 'images': len(root.findall('.//{%s}image'%NS)),
            'texts': len(root.findall('.//{%s}text'%NS)), 'viewBox':root.get('viewBox')}

for color in ['black', 'white']:
    source=ROOT/'gsc/gsc-logo/1.0.4/rgb/svg'/f'phsa-gsc-logo-{color}-combinationmark-vc-rgb.svg'
    original=etree.parse(str(source)).getroot()
    groups=original.findall('{%s}g'%NS)
    assert len(groups[-1])==45
    root=etree.Element('{%s}svg'%NS,nsmap={None:NS})
    root.set('viewBox','12.0992 17.0589 128.5033 34.9387')
    title=etree.SubElement(root,'{%s}title'%NS);title.text=f'PHSA — {color} wordmark, extracted original vectors'
    desc=etree.SubElement(root,'{%s}desc'%NS)
    desc.text='Intact PHSA group extracted from the public PHSA/GSC combination mark, GSC logo archive v1.0.4 (15 July 2026). No paths redrawn or recoloured. Source: https://mk.bcgsc.ca/branding/files/logo/gsc-logo-1.0.4.zip . This derivative is a faithful extraction, not a separately supplied standalone master.'
    definitions=original.find('{%s}defs'%NS)
    if definitions is not None:
        root.append(deepcopy(definitions))
    root.append(deepcopy(groups[-1]))
    path=OUT/f'phsa-{color}-source-extraction.svg'
    path.write_bytes(etree.tostring(root,xml_declaration=True,encoding='UTF-8'))
    row=info(path);row.update({'bodyId':'provincial-health-services-authority','method':'isolated original SVG group; new tight viewBox only','sourceFile':str(source),'sourcePage':'https://mk.bcgsc.ca/branding/','sourceUrl':f'https://mk.bcgsc.ca/branding/files/logo/1.0.4/rgb/svg/phsa-gsc-logo-{color}-combinationmark-vc-rgb.svg','publishedDate':'2026-07-15','dateMeaning':'asset bundle version date, not logo adoption date'})
    records.append(row)

source=ROOT/'ih-wayfinding.pdf'
d=fitz.open(source)
page=d[0]
clip=fitz.Rect(998,34,1173,127.5)
assert len(page.get_images())==0
selected=[x for x in page.get_drawings() if clip.contains(x['rect'])]
# Remove non-logo page contents before export rather than merely hiding them.
# The enclosing title-block rules cross the left/right removal zones and are
# therefore removed as whole paths. Keep the text's font metrics to y=136
# while removing content; the final visible crop is the tighter ink boundary.
keep=fitz.Rect(998,32,1173,136)
for outside in [fitz.Rect(0,0,1224,keep.y0),fitz.Rect(0,keep.y0,keep.x0,792),
                fitz.Rect(keep.x1,keep.y0,1224,792),fitz.Rect(keep.x0,keep.y1,keep.x1,792)]:
    page.add_redact_annot(outside,fill=None,cross_out=False)
page.apply_redactions(images=2,graphics=2,text=0)
page=d.reload_page(page)
assert all(keep.contains(x['rect']) or x['rect'].is_empty for x in page.get_drawings())
sub=fitz.open();p=sub.new_page(width=clip.width,height=clip.height)
p.show_pdf_page(p.rect,d,0,clip=clip)
pdfpath=OUT/'interior-health-black-stacked-source-extraction.pdf'
sub.save(pdfpath,garbage=4,deflate=True)
svgpath=OUT/'interior-health-black-stacked-source-extraction.svg'
svgpath.write_text(p.get_svg_image(text_as_path=True),encoding='utf-8')
row=info(svgpath);row.update({'bodyId':'interior-health','method':'isolate original vector PDF title-block logo by removing all non-logo content before cropping; embedded font outlined by MuPDF, no traced geometry','sourceFile':str(source),'sourcePage':'https://www.interiorhealth.ca/about-ih/business-centre/construction','sourceUrl':'https://www.interiorhealth.ca/sites/default/files/PDFS/ih-wayfinding-signage-guideline.pdf','sourcePdfPage':1,'cropBox':list(clip),'originalVectorDrawingsInRegion':len(selected),'sourceDate':'2024-06-07 guideline; drawing sheet date 04.05.2026','dateMeaning':'document/sheet dates, not logo adoption date','caveat':'Published CAD/signage specimen rendered as hatched vector geometry. Stronger stand-alone curve master is still preferred. The enclosing title-block rules and other page contents were removed, not merely clipped.'})
records.append(row)

# The climate roadmap has a much cleaner full-colour original: the final
# page consists of one background rectangle and the 17 outlined logo paths.
source=ROOT/'ih-climate-roadmap.pdf'
doc=fitz.open(source);page=doc[21]
assert len(page.get_images())==0
original=etree.fromstring(page.get_svg_image(text_as_path=True).encode())
groups=original.findall('{%s}g'%NS)
assert len(groups)==1 and len(groups[0])==17
root=etree.Element('{%s}svg'%NS,nsmap={None:NS})
root.set('viewBox','47 739.5 134 29.5')
title=etree.SubElement(root,'{%s}title'%NS);title.text='Interior Health — blue horizontal original vector specimen'
desc=etree.SubElement(root,'{%s}desc'%NS);desc.text='The 17 original logo paths from PDF page 22 of Interior Health Climate Change and Sustainability Roadmap 2023–2028. Converted to SVG via MuPDF with original geometry and colour retained; no tracing or redrawing. The yellow page background is excluded.'
root.append(deepcopy(original.find('{%s}defs'%NS)))
root.append(deepcopy(groups[0]))
path=OUT/'interior-health-blue-horizontal-source-extraction.svg'
path.write_bytes(etree.tostring(root,xml_declaration=True,encoding='UTF-8'))
row=info(path);row.update({'bodyId':'interior-health','method':'retain only the original 17-path logo group from converted PDF page 22; no tracing, redrawing or recolouring','sourceFile':str(source),'sourcePage':'https://www.interiorhealth.ca/about-ih/climate-change-and-sustainability/climate-change-and-sustainability-roadmap-2023-2028','sourceUrl':'https://www.interiorhealth.ca/sites/default/files/PDFS/interior-health-climate-change-sustainability-roadmap-2023-2028.pdf','sourcePdfPage':22,'cropBox':[47,739.5,181,769],'originalVectorDrawingsInRegion':17,'sourceDate':'2023','dateMeaning':'report period starts in 2023; this is not an adoption date','caveat':'Faithful extraction from a published report, not a separate standalone master. Source PDF colours rendered to sRGB by MuPDF.'})
records.append(row)

for name in ['fnha-logo-colour.svg','fnha-logo-white.svg','fnha-icon.svg']:
    source=ROOT/name;out=OUT/name;out.write_bytes(source.read_bytes())
    url=('https://annualreport.fnha.ca/wp-content/uploads/2024/12/fnha-icon.svg' if name=='fnha-icon.svg' else 'https://annualreport.fnha.ca/wp-content/themes/fnhaimpactreport/images/'+('fnha-logo-vector.svg' if name=='fnha-logo-colour.svg' else name))
    row=info(out);row.update({'bodyId':'first-nations-health-authority','method':'byte-for-byte original SVG download','sourceFile':str(source),'sourcePage':'https://annualreport.fnha.ca/','sourceUrl':url,'dateMeaning':'retrieved 2026-10-30; no first-use date implied'})
    records.append(row)

for row in records:
    assert row['images']==0
    row['sourceSha256']=hashlib.sha256(Path(row['sourceFile']).read_bytes()).hexdigest()
    row['retrievedDate']='2026-10-30'
    path=Path(row['file'])
    doc=fitz.open(path);pdf=fitz.open('pdf',doc.convert_to_pdf())
    pdf[0].get_pixmap(matrix=fitz.Matrix(3,3),alpha=True).save(OUT/(path.stem+'.png'))

(ROOT/'vector-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['bodyId','file','paths','images','bytes']} for r in records],indent=2))
