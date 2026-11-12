from pathlib import Path
import copy
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

import fitz

ROOT = Path('/workspace/scratch/9f0afc4f8b90')
TMP = ROOT / 'tmp/logo-research'
OUT = ROOT / 'output/health-logos'
OUT.mkdir(parents=True, exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

source = TMP / 'bc-cancer-2015-research-report.pdf'
doc = fitz.open(source)
page = doc[31]
svg = ET.fromstring(page.get_svg_image())
group = next(x for x in svg if x.tag == f'{{{NS}}}g' and x.attrib.get('clip-path') == 'url(#clip_10)')
assert len(group) == 75
assert all(x.tag == f'{{{NS}}}path' for x in group)
drawings = page.get_drawings()
assert len(drawings) == 172

manifest = {
    'research_date': '2026-11-12',
    'method': 'Direct extraction of existing PDF vector paths or embedded raster image data. No tracing, redrawing, upscaling, or generative reconstruction.',
    'sources': [],
    'assets': [],
}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def add_source(path, url, title, notes):
    manifest['sources'].append({'source_file': path.name, 'url': url, 'title': title, 'sha256': digest(path), 'notes': notes})

add_source(source, 'https://www.bccancer.bc.ca/about-site/Documents/ResearchReport2015_Final_Web.pdf', 'BC Cancer Agency 2015 Research Report', 'Vector logo extracted from PDF page 32. Full source is linked, not bundled.')
report_2000 = TMP / 'fraser-valley-2000-project-report.pdf'
add_source(report_2000, 'https://mf.gov.cz/assets/attachments/PPP-Canada-Project-definition-report-Contents.pdf', 'Fraser Valley Health Centre / Eastern Fraser Valley Cancer Centre: Project Definition Report, cover and contents', 'Document dated September 27, 2000; public mirror hosted by the Czech Ministry of Finance. PDF page 1 contains the exact paired logos in the supplied screenshot.')
report_2010 = ROOT / 'tmp/bcca-agent/radiation-therapy-2010.pdf'
add_source(report_2010, 'https://www.bccancer.bc.ca/patient-and-public-info-site/Documents/Radiation_Therapy_What_to_Expect_Chinese_English_2.pdf', 'Radiation Therapy: What to Expect (Chinese/English)', 'PDF metadata dated July 2010. Page 28 contains a second original vector logo; embedded Illustrator metadata and named Pantone colour resources provide additional evidence.')

for stem, indexes, selected, render_width in [
    ('bc-cancer-agency-emblem-2015', range(97,99), list(group)[:2], 1024),
    ('bc-cancer-agency-lockup-2015', range(97,172), list(group), 1800),
]:
    box = fitz.Rect(drawings[97]['rect'])
    for i in indexes:
        box |= drawings[i]['rect']
    box = fitz.Rect(box.x0 - 2, box.y0 - 2, box.x1 + 2, box.y1 + 2)
    height = round(render_width * box.height / box.width, 3)
    out_svg = ET.Element(f'{{{NS}}}svg', {
        'version': '1.1', 'width': str(render_width), 'height': str(height),
        'viewBox': f'{box.x0:.6f} {box.y0:.6f} {box.width:.6f} {box.height:.6f}',
        'role': 'img',
    })
    ET.SubElement(out_svg, f'{{{NS}}}title').text = 'BC Cancer Agency historical logo, extracted from the 2015 Research Report'
    ET.SubElement(out_svg, f'{{{NS}}}desc').text = 'Original PDF vector paths, converted directly to SVG without tracing or redrawing. Source: https://www.bccancer.bc.ca/about-site/Documents/ResearchReport2015_Final_Web.pdf, PDF page 32. Colours are the RGB rendering of the source publication.'
    for element in selected:
        out_svg.append(copy.deepcopy(element))
    svg_path = OUT / (stem + '.svg')
    ET.ElementTree(out_svg).write(svg_path, encoding='utf-8', xml_declaration=True)
    assert not out_svg.findall(f'.//{{{NS}}}image')
    assert len(out_svg.findall(f'.//{{{NS}}}path')) == len(selected)

    crop = fitz.open()
    target = crop.new_page(width=box.width, height=box.height)
    target.show_pdf_page(target.rect, doc, 31, clip=box)
    crop.set_metadata({'title': 'BC Cancer Agency historical logo - original vector excerpt', 'subject': 'Extracted from BC Cancer Agency 2015 Research Report, PDF page 32; no tracing or reconstruction.'})
    pdf_path = OUT / (stem + '.pdf')
    crop.save(pdf_path, garbage=4, deflate=True)

    # Render the delivered SVG itself for a preview and validate against source.
    converted = fitz.open(stream=svg_path.read_bytes(), filetype='svg')
    rendered = fitz.open('pdf', converted.convert_to_pdf())
    rendered[0].get_pixmap(alpha=True).save(OUT / (stem + '.png'))
    # Same-size source crop for internal visual verification, not a deliverable.
    source_crop = fitz.open(pdf_path)
    source_crop[0].get_pixmap(matrix=fitz.Matrix(render_width/box.width, render_width/box.width), alpha=True).save(TMP / (stem + '-source-render.png'))
    manifest['assets'].append({'stem': stem, 'formats': ['svg','pdf','png'], 'source': source.name, 'pdf_page': 32, 'source_bbox_points': list(box), 'vector_paths': len(selected), 'svg_embedded_images': 0, 'png_width': render_width, 'svg_colour_note': 'RGB appearance converted from the published PDF; the PDF crop preserves native PDF artwork/resources.'})

old_doc = fitz.open(report_2000)
for xref, stem, expected_dimensions in [
    (44, 'fraser-valley-health-region-2000-original-78px', (78,78)),
    (43, 'bc-cancer-agency-2000-original-162px', (162,162)),
]:
    info = old_doc.extract_image(xref)
    assert (info['width'], info['height']) == expected_dimensions
    pix = fitz.Pixmap(old_doc, xref)
    if pix.colorspace and pix.colorspace.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(OUT / (stem + '.png'))
    manifest['assets'].append({'filename': stem + '.png', 'source': report_2000.name, 'pdf_page': 1, 'image_xref': xref, 'native_pixels': list(expected_dimensions), 'quality': 'Original embedded raster; no added resolution or enhancement.'})

shutil.copy2(report_2000, OUT / report_2000.name)
shutil.copy2(report_2010, OUT / report_2010.name)
manifest['verification'] = {'2015_lockup': '75 original SVG paths, zero raster images, all lettering outlined.', '2015_emblem': '2 original SVG paths, zero raster images.', '2010_evidence': {'metadata_title': 'BCCA_Template_Horz', 'creator': 'Adobe Illustrator CS2', 'artwork_metadata_created': '2007-06-21', 'named_colours': ['PANTONE 273 U','PANTONE Warm Gray 11 U'], 'limitations': 'Metadata dates are file dates, not logo-introduction dates. Named colours document this publication; a complete historical brand manual was not located.'}}
(OUT / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'output_dir': str(OUT), 'files': [{'name': p.name, 'bytes': p.stat().st_size} for p in sorted(OUT.iterdir())]}, indent=2))
