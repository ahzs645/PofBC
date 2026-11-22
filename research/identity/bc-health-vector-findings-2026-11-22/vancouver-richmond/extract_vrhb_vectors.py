from pathlib import Path
import fitz, json, hashlib, xml.etree.ElementTree as ET, re, shutil, collections
ROOT=Path(__file__).parent
OUT=ROOT/'recovered-vectors'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'archive-candidates'
source_a=SOURCE/'TakeCareHandBook.pdf'
source_b=SOURCE/'VHRB_Directional_Plan.pdf'
pa=fitz.open(source_a); pb=fitz.open(source_b)
a=pa[0].read_contents().decode('latin1')
b=pb[0].read_contents().decode('latin1').replace('\r','\n')
full_start=a.index('/Cs12 cs 1 scn\n/GS3 gs')
emblem_start=a.index('/Cs12 cs 1 scn\n/GS3 gs\n158.051 123.394 m')
mono_start=b.index('0.83 1 0 0.23 k\n/GS2 gs\n1 i \n129.333 728.228 m')
mono_end=b.index('q\n0 792 612 -792 re\n0 792 m\nW n\n0.06 792 612 -792 re\nW n\n0.114 0 0.494 0 K',mono_start)

def save_vector(name, src, source_content, rect, label):
    doc=fitz.open();doc.insert_pdf(src,from_page=0,to_page=0,links=False,annots=False)
    page=doc[0]
    stream=doc.get_new_xref();doc.update_object(stream,'<<>>');doc.update_stream(stream,source_content.encode('latin1'));page.set_contents(stream)
    resource=int(doc.xref_get_key(page.xref,'Resources')[1].split()[0]);doc.xref_set_key(resource,'Font','null')
    page.set_cropbox(rect)
    doc.set_metadata({'title':label,'subject':'Original vector artwork extracted without tracing from a Vancouver/Richmond Health Board publication','creator':'Source-preserving PDF operator extraction with PyMuPDF'})
    pdf=OUT/(name+'.pdf');doc.save(pdf,garbage=4,deflate=True)
    doc=fitz.open(pdf);page=doc[0]
    svg=page.get_svg_image(text_as_path=True)
    root=ET.fromstring(svg)
    desc=ET.Element('{http://www.w3.org/2000/svg}desc');desc.text=label+'. Original publication vector paths; no tracing, raster image, font substitution or live text. SVG colours are RGB conversions; PDF preserves source colour definitions.';root.insert(0,desc)
    svg=ET.tostring(root,encoding='unicode');(OUT/(name+'.svg')).write_text(svg)
    page.get_pixmap(matrix=fitz.Matrix(7,7),alpha=False).save(str(OUT/(name+'.png')))
    tags=collections.Counter(x.tag.split('}')[-1] for x in root.iter())
    image_tags=[x for x in root.iter() if x.tag.split('}')[-1] in ('image','text','foreignObject')]
    external=[v for x in root.iter() for k,v in x.attrib.items() if 'href' in k and not v.startswith('#')]
    assert not image_tags and not external
    assert page.get_images(full=True)==[] and page.get_fonts()==[]
    return {'name':name,'source_label':label,'source_page':1,'crop_original_page_points':list(rect),'source_path_count_in_extraction':len(page.get_drawings()),'svg_path_count':tags.get('path',0),'svg_image_count':tags.get('image',0),'svg_text_count':tags.get('text',0),'external_references':external,'svg_sha256':hashlib.sha256((OUT/(name+'.svg')).read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}

items=[]
items.append(save_vector('VRHB-original-colour-lockup',pa,'0 J 0 j 2.04 w 10 M []0 d\n'+a[full_start:],fitz.Rect(146.7,454.7,358.1,512.6),'Vancouver/Richmond Health Board original two-colour logo; Take Care, revised 2000, cover'))
items.append(save_vector('VRHB-original-colour-emblem',pa,'0 J 0 j 0.34 w 4 M []0 d\n2.722 i\n'+a[emblem_start:],fitz.Rect(146.7,454.7,180.3,496.3),'Vancouver/Richmond Health Board original two-colour emblem; Take Care, revised 2000, cover'))
items.append(save_vector('VRHB-original-purple-lockup',pb,b[mono_start:mono_end],fitz.Rect(77.3,33.5,279.8,89.1),'Vancouver/Richmond Health Board original single-colour purple logo; Directional Plan 2000–2003, cover'))
# Source crops retain original page including the background behind the logo.
for name,src,rect in [('TakeCare-original-source-crop',pa,fitz.Rect(146.7,454.7,358.1,512.6)),('DirectionalPlan-original-source-crop',pb,fitz.Rect(77.3,33.5,279.8,89.1))]:
    doc=fitz.open();q=doc.new_page(width=rect.width,height=rect.height);q.show_pdf_page(q.rect,src,0,clip=rect);doc.save(OUT/(name+'.pdf'),garbage=4,deflate=True)
    src[0].get_pixmap(matrix=fitz.Matrix(7,7),clip=rect,alpha=False).save(str(OUT/(name+'.png')))
report={
 'result':'Confirmed genuine original vector artwork in two original publication PDFs.',
 'sources':[
 {'file':'TakeCareHandBook.pdf','url':'https://web.archive.org/web/20030426095928id_/http://www.vcn.bc.ca:80/vrhb/Down_Loads/CaregiverSupport/TakeCareHandBook.pdf','title':'Take Care: A handbook for families caring for older adults','publication_date_evidence':'Page 2 states revised in 2000; back cover form code HED2050 00/08.','source_pdf_metadata':pa.metadata,'sha256':hashlib.sha256(source_a.read_bytes()).hexdigest(),'cover_image_objects':len(pa[0].get_images(full=True)),'cover_path_count':len(pa[0].get_drawings()),'spot_colours':['PANTONE 1797 CVC','PANTONE 2627 CVC']},
 {'file':'VHRB_Directional_Plan.pdf','url':'https://web.archive.org/web/20040107163909id_/http://www.vcn.bc.ca:80/vrhb/Down_Loads/VRHB_Health_Plans/Directional_Plan/VHRB_Directional_Plan.pdf','title':'Directional Plan: Working Together for Better Health 2000–2003','source_pdf_metadata':pb.metadata,'sha256':hashlib.sha256(source_b.read_bytes()).hexdigest(),'cover_image_objects':len(pb[0].get_images(full=True)),'cover_path_count':len(pb[0].get_drawings()),'purple_device_cmyk':[0.83,1,0,0.23],'note':'Open heart/negative-space monochrome variant. Original cover background pale cream is preserved in source crop only; logo SVG/PDF have no added background.'}
 ],
 'method':'Isolate original PDF content-stream path operators belonging to logo, preserving original coordinates, Bézier control points, fills, strokes, overprint state and colour resources; copy source page resources, remove unused Font resources, set crop to logo; export isolated PDF through PyMuPDF SVG writer. No tracing, reconstruction, smoothing, recolouring or font substitution. All lettering was already vector outlines in source.',
 'colour_note':'Original named Pantone colours and PDF colour-space definitions remain in colour PDFs. SVG colours are RGB conversions of those definitions and are not a replacement print colour standard. White dry-brush knockout shapes in two-colour source have been preserved as white shapes, not converted to transparency.',
 'artifacts':items
}
(OUT/'vector-provenance.json').write_text(json.dumps(report,indent=2))
print(json.dumps(items,indent=2))
