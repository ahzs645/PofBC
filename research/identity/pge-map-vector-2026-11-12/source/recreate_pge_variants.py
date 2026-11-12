"""Additional PGE variants using the existing map and wordmark geometry.

The original path data remain unchanged. Variant transforms and palette are
separate from the shared assets. No contour extraction or font substitution.
"""
from pathlib import Path
import hashlib
import io
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
import fitz
from reportlab.pdfgen import canvas

import reconstruct_pge as base

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output' / 'pge-solid-variant'
ANALYSIS = ROOT / 'analysis' / 'solid'
OUT.mkdir(parents=True, exist_ok=True)
ANALYSIS.mkdir(parents=True, exist_ok=True)
REFERENCES = list((ROOT / 'upload').glob('Screenshot*11.21.07*'))
REFERENCE = REFERENCES[0] if REFERENCES else None

INK = '#000000'
WHITE = '#ffffff'
UPPER_GREEN = '#728b76'
LOWER_GREEN = '#345135'
IDENTITY = (1,0,0,1,0,0)
MAP_MATRIX = (0.104,0,0,0.109,-1,14.6)
TYPE_MATRIX = (0.1232,0,0.00673,0.11699,-18.949,14.856)

# A presentation-specific white separator follows the continuous coastal gap
# visible in this reference. It overlays, but never changes, the shared map.
COAST_CHANNEL = '''M59.3 61.2
C62.1 62.3 63.9 63.7 65.5 65.1
C67.4 67.0 68.8 69.2 70.2 71.2
L74 74.1 V77 H70.4 V76.0
C69.0 73.2 67.5 71.0 65.6 69.1
C64.1 67.3 62.0 65.5 59.4 63.7 Z'''

# The same folded-panel construction, with its lean and width adapted to the
# new reference. The reusable map and letter path data are not changed.
PANEL_POINTS = [(13.5,17.5),(110,17.5),(130.5,84.5),
                (109.5,150.5),(13.5,150.5),(34,84.5)]
SOLID_PANEL = 'M' + ' L'.join(f'{x:g} {y:g}' for x,y in PANEL_POINTS) + ' Z'
ISOLATED_VIEWBOX = (5.5,9.5,133,149)
LIVERY_VIEWBOX = (0,0,151,167)

def rect(x,y,w,h):
    return f'M{x:g} {y:g} h{w:g} v{h:g} h{-w:g} Z'

def matrix_text(m):
    return 'matrix(' + ' '.join(f'{n:.8g}' for n in m) + ')'

def path_hash(d):
    return hashlib.sha256(base.clean(d).encode()).hexdigest()

ASSETS = {
    'bc-mainland': base.MAINLAND,
    'bc-western-island': base.WEST_ISLAND,
    **{f'bc-coastal-cutout-{i+1}':d for i,d in enumerate(base.COAST_CUTOUTS)},
    'letter-P': base.LETTER_P,
    'letter-G': base.LETTER_G,
    'letter-E': base.LETTER_E,
}

def artwork_shapes():
    return [('white-panel',WHITE,SOLID_PANEL,IDENTITY),
            ('bc-mainland',INK,base.MAINLAND,MAP_MATRIX),
            ('bc-western-island',INK,base.WEST_ISLAND,MAP_MATRIX),
            *[(f'bc-coastal-cutout-{i+1}',WHITE,d,MAP_MATRIX)
              for i,d in enumerate(base.COAST_CUTOUTS)],
            ('solid-coastal-channel',WHITE,COAST_CHANNEL,IDENTITY),
            ('letter-P',INK,base.LETTER_P,TYPE_MATRIX),
            ('letter-G',INK,base.LETTER_G,TYPE_MATRIX),
            ('letter-E',INK,base.LETTER_E,TYPE_MATRIX)]

def livery_shapes():
    return [('upper-green',UPPER_GREEN,rect(0,0,151,83),IDENTITY),
            ('lower-green',LOWER_GREEN,rect(0,83,151,84),IDENTITY),
            ('white-livery-band',WHITE,rect(0,79.5,151,7.5),IDENTITY),
            *artwork_shapes()]

def svg_start(viewbox,title,desc,display_scale=8):
    x,y,w,h=viewbox
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="{w*display_scale:g}" height="{h*display_scale:g}" viewBox="{x:g} {y:g} {w:g} {h:g}"
     role="img" aria-labelledby="title description">
  <title id="title">{title}</title>
  <desc id="description">{desc}</desc>
  <metadata>Reference-based reconstruction, 2026-11-12. The original BC and PGE path data are reused unchanged from the earlier striped version. No automatic tracing, embedded images or live lettering. Green colors are approximate samples from the supplied screenshot, not verified historical paint specifications.</metadata>
'''

def path_element(sid,fill,d,matrix=None,indent='    '):
    tr='' if matrix is None or matrix==IDENTITY else f' transform="{matrix_text(matrix)}"'
    return f'{indent}<path id="{sid}" fill="{fill}" fill-rule="evenodd"{tr} d="{base.clean(d)}"/>'

def make_svg(name,viewbox,with_livery):
    title='PGE - two-green livery' if with_livery else 'PGE - solid white panel'
    desc='Solid white folded panel with black British Columbia silhouette and custom PGE outlines, using the same vector assets as the earlier striped mark.'
    if with_livery:desc+=' Two green fields and a horizontal white band reproduce the reference presentation.'
    else:desc+=' The exterior is transparent; the white panel is opaque artwork.'
    lines=[svg_start(viewbox,title,desc)]
    if with_livery:
        lines.append('  <g id="livery-background" inkscape:groupmode="layer" inkscape:label="Green livery and white band">')
        for sid,fill,d,m in livery_shapes()[:3]:lines.append(path_element(sid,fill,d,m))
        lines.append('  </g>')
    lines.extend(['  <g id="panel" inkscape:groupmode="layer" inkscape:label="White folded panel">',
                  path_element('white-panel',WHITE,SOLID_PANEL),'  </g>',
                  f'  <g id="bc-map" inkscape:groupmode="layer" inkscape:label="Shared BC map" transform="{matrix_text(MAP_MATRIX)}">',
                  path_element('bc-mainland',INK,base.MAINLAND),
                  path_element('bc-western-island',INK,base.WEST_ISLAND)])
    for i,d in enumerate(base.COAST_CUTOUTS):lines.append(path_element(f'bc-coastal-cutout-{i+1}',WHITE,d))
    lines.extend(['  </g>',
                  '  <g id="solid-coastal-treatment" inkscape:groupmode="layer" inkscape:label="Solid variant coastal separator">',
                  path_element('solid-coastal-channel',WHITE,COAST_CHANNEL),'  </g>',
                  f'  <g id="pge-wordmark" inkscape:groupmode="layer" inkscape:label="Shared PGE outlines" transform="{matrix_text(TYPE_MATRIX)}">'])
    for letter,d in [('P',base.LETTER_P),('G',base.LETTER_G),('E',base.LETTER_E)]:
        lines.append(path_element('letter-'+letter,INK,d))
    lines.extend(['  </g>','</svg>\n'])
    path=OUT/name
    path.write_text('\n'.join(lines))
    return path

def make_pdf(name,viewbox,shapes):
    x,y,w,h=viewbox
    scale=(200*72/25.4)/h
    path=OUT/name
    c=canvas.Canvas(str(path),pagesize=(w*scale,h*scale),pageCompression=1)
    c.setTitle(name.removesuffix('.pdf').replace('-',' '))
    c.setAuthor('Reference-based PGE reconstruction')
    c.setSubject('Shared map and letter paths; vector fills only')
    c.scale(scale,scale)
    c.translate(-x,h+y)
    c.scale(1,-1)
    for sid,fill,d,m in shapes:
        c.saveState()
        c.transform(*m)
        base.add_rl_path(c,d,fill)
        c.restoreState()
    c.showPage();c.save()
    doc=fitz.open(path)
    page=doc[0]
    contents=page.read_contents().replace(b'BT /F1 12 Tf 14.4 TL ET',b'')
    assert b'BT' not in contents
    xref=doc.get_new_xref();doc.update_object(xref,'<<>>')
    doc.update_stream(xref,contents);page.set_contents(xref)
    doc.xref_set_key(page.xref,'Resources','<</ProcSet[/PDF]>>')
    data=doc.tobytes(garbage=4,deflate=True);doc.close();path.write_bytes(data)
    return path

def render(svg,width):
    return base.render_svg(svg,width)

def shared_template():
    """One file, one definition of each map/letter path, three instances."""
    lines=[svg_start((0,0,3600,1400),'PGE - shared vector template',
                     'Three compositions share a single set of map and PGE letter definitions: the original striped mark, the solid white panel, and the green livery.',1),
           '  <defs>']
    for sid,d in ASSETS.items():
        lines.append(f'    <path id="asset-{sid}" fill-rule="evenodd" d="{base.clean(d)}"/>')
    lines.append(f'    <path id="asset-panel-striped" d="{base.clean(base.BACK)}"/>')
    lines.append(f'    <path id="asset-panel-solid" d="{SOLID_PANEL}"/>')
    lines.append(f'    <path id="asset-solid-coastal-channel" d="{base.clean(COAST_CHANNEL)}"/>')
    lines.append('    <g id="asset-stripe-grid">')
    for i in range(base.STRIPE_COUNT):
        lines.append(f'      <path d="{base.stripe_path(i)}"/>')
    lines.extend(['    </g>','  </defs>',
                  '  <path id="preview-background" fill="#e7ebee" d="M0 0H3600V1400H0Z"/>'])
    def use(asset,color,indent='    '):
        return f'{indent}<use xlink:href="#asset-{asset}" fill="{color}"/>'
    def bc(positive,negative,transform=None):
        tr='' if transform is None else f' transform="{matrix_text(transform)}"'
        a=[f'    <g data-name="Shared BC map"{tr}>',use('bc-mainland',positive,'      '),use('bc-western-island',positive,'      ')]
        a += [use(f'bc-coastal-cutout-{i+1}',negative,'      ') for i in range(6)]
        return a+['    </g>']
    def letters(color,transform=None):
        tr='' if transform is None else f' transform="{matrix_text(transform)}"'
        return [f'    <g data-name="Shared PGE lettering"{tr}>']+[use(f'letter-{q}',color,'      ') for q in 'PGE']+['    </g>']
    old_scale=1056/1104
    lines.append(f'  <g id="variant-striped" inkscape:groupmode="layer" inkscape:label="Original striped version" transform="translate({600-674*old_scale:.6f} {150-46*old_scale:.6f}) scale({old_scale:.8f})">')
    lines.extend([use('panel-striped',INK),use('stripe-grid',WHITE),*bc(WHITE,INK),*letters(WHITE),'  </g>'])
    solid_scale=1056/133
    for label,tx,green in [('solid',1800-72*solid_scale,False),('green-livery',3000-75.5*solid_scale,True)]:
        ty=150-17.5*solid_scale
        lines.append(f'  <g id="variant-{label}" inkscape:groupmode="layer" inkscape:label="{label}" transform="translate({tx:.6f} {ty:.6f}) scale({solid_scale:.8f})">')
        if green:
            for sid,fill,d,m in livery_shapes()[:3]:lines.append(path_element('template-'+sid,fill,d))
        lines.extend([use('panel-solid',WHITE),*bc(INK,WHITE,MAP_MATRIX),use('solid-coastal-channel',WHITE),*letters(INK,TYPE_MATRIX),'  </g>'])
    lines.extend(['</svg>\n'])
    path=OUT/'PGE-shared-template.svg';path.write_text('\n'.join(lines))
    geometry={
        'source':'Earlier PGE striped reconstruction in this conversation',
        'assets':{sid:{'path':base.clean(d),'sha256':path_hash(d)} for sid,d in ASSETS.items()},
        'variants':{
            'striped':{'map_transform':IDENTITY,'type_transform':IDENTITY,'panel':base.BACK,'stripe_count':38,'stripe_pitch':14.55},
            'solid':{'map_transform':MAP_MATRIX,'type_transform':TYPE_MATRIX,'panel':SOLID_PANEL,'stripe_count':0,'coastal_channel_overlay':base.clean(COAST_CHANNEL)},
            'green_livery':{'map_transform':MAP_MATRIX,'type_transform':TYPE_MATRIX,'panel':SOLID_PANEL,'upper_green':UPPER_GREEN,'lower_green':LOWER_GREEN,'band':[0,79.5,151,7.5]}
        }
    }
    (OUT/'PGE-shared-geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    return path

def build_preview(solid_svg,livery_svg):
    W,H=1800,1130
    board=Image.new('RGB',(W,H),'#e7ebee');d=ImageDraw.Draw(board)
    d.text((58,38),'PGE / SHARED-ASSET VARIANTS',font=base.font(34,True),fill='#202f3f')
    d.text((58,92),'The same BC outline and PGE lettering, in the solid-panel treatment.',font=base.font(22),fill='#586573')
    d.text((58,160),'ISOLATED EMBLEM',font=base.font(20,True),fill='#26364a')
    d.text((942,160),'TWO-GREEN LIVERY',font=base.font(20,True),fill='#26364a')
    for x,path,width in [(58,solid_svg,732),(942,livery_svg,732)]:
        im=render(path,width)
        if path==solid_svg:
            im=Image.alpha_composite(Image.new('RGBA',im.size,'#d2d9df'),im)
        board.paste(im.convert('RGB'),(x,204))
    d.text((58,1065),'Transparent exterior; opaque white panel.',font=base.font(20),fill='#586573')
    d.text((942,1065),'Green tones sampled approximately from the reference.',font=base.font(20),fill='#586573')
    board.save(OUT/'PGE-solid-variants-preview.png')

def comparison(livery_svg):
    if REFERENCE is None:return
    ref=Image.open(REFERENCE).convert('RGB')
    rebuilt=render(livery_svg,906).convert('RGB')
    native=rebuilt.resize((151,167),Image.Resampling.LANCZOS)
    a=np.asarray(ref);b=np.asarray(native)
    # Restrict the proof to map/type interior; exclude the dark green livery.
    yy,xx=np.indices((167,151))
    map_roi=(xx>=40)&(xx<=98)&(yy>=22)&(yy<=77)
    type_roi=(yy>=90)&(yy<=146)&(xx>40-.34*(yy-92)-3)&(xx<122-.32*(yy-92)+2)
    roi=map_roi|type_roi
    ref_ink=(a.mean(axis=2)<120)&((a.max(axis=2).astype(int)-a.min(axis=2).astype(int))<35)&roi
    vec_ink=(b.mean(axis=2)<120)&((b.max(axis=2).astype(int)-b.min(axis=2).astype(int))<35)&roi
    overlay=np.full((167,151,3),244,dtype=np.uint8)
    overlay[ref_ink&vec_ink]=[32,46,65]
    overlay[ref_ink&~vec_ink]=[202,44,116]
    overlay[vec_ink&~ref_ink]=[0,153,185]
    over=Image.fromarray(overlay).resize((755,835),Image.Resampling.NEAREST)
    W,H=2500,1250
    board=Image.new('RGB',(W,H),'#f3f5f6');d=ImageDraw.Draw(board)
    d.text((50,35),'PGE / SOLID-VARIANT COMPARISON',font=base.font(34,True),fill='#202f3f')
    d.text((50,90),'Shared map and letter paths; composition adjusted to the supplied 151 x 167 px reference.',font=base.font(22),fill='#586573')
    for x,label,im in [(50,'SUPPLIED REFERENCE',ref.resize((755,835),Image.Resampling.NEAREST)),
                       (875,'REBUILT VECTOR',rebuilt.resize((755,835),Image.Resampling.LANCZOS)),
                       (1700,'ALIGNED MAP / TYPE OVERLAY',over)]:
        d.text((x,155),label,font=base.font(21,True),fill='#26364a');board.paste(im,(x,200))
    d.line((50,1080,2455,1080),fill='#cbd3da',width=2)
    d.text((50,1108),'The original P, G, E and BC paths are reused unchanged.',font=base.font(21),fill='#465465')
    d.text((50,1145),'The continuous coastal gap is a separate white overlay.',font=base.font(21),fill='#465465')
    for i,(color,txt) in enumerate([('#202e41','Shared ink'),('#ca2c74','Reference only'),('#0099b9','Reconstruction only')]):
        x=1700;y=1100+i*34
        d.rectangle((x,y+5,x+19,y+25),fill=color);d.text((x+32,y),txt,font=base.font(19),fill='#465465')
    d.text((50,1204),'Green colors are approximate screenshot samples. Shared geometry remains editable independently of the coastal overlay.',font=base.font(18),fill='#637080')
    board.save(OUT/'PGE-solid-reference-comparison.png')
    # Internal enlarged side-by-side map crop for inspection.
    crop_ref=ref.crop((40,22,99,78)).resize((590,560),Image.Resampling.NEAREST)
    crop_vec=native.crop((40,22,99,78)).resize((590,560),Image.Resampling.NEAREST)
    detail=Image.new('RGB',(1180,560),'white');detail.paste(crop_ref,(0,0));detail.paste(crop_vec,(590,0))
    detail.save(ANALYSIS/'map-comparison.png')

def validate(svg_paths,pdf_paths,template):
    ns={'s':'http://www.w3.org/2000/svg'}
    reports=[]
    for p in svg_paths:
        root=ET.parse(p).getroot()
        assert not root.findall('.//s:image',ns)
        assert not root.findall('.//s:text',ns)
        assert not root.findall('.//s:filter',ns)
        for sid,d in ASSETS.items():
            actual=root.find(f'.//s:path[@id="{sid}"]',ns)
            assert actual is not None and actual.attrib['d']==base.clean(d),sid
        reports.append({'file':p.name,'paths':len(root.findall('.//s:path',ns)),'shared_asset_paths_unchanged':len(ASSETS)})
    tr=ET.parse(template).getroot()
    for sid,d in ASSETS.items():
        matches=tr.findall(f'.//s:path[@id="asset-{sid}"]',ns)
        assert len(matches)==1 and matches[0].attrib['d']==base.clean(d)
    for p in pdf_paths:
        doc=fitz.open(p);page=doc[0]
        assert not page.get_images() and not page.get_fonts()
        reports.append({'file':p.name,'vector_drawings':len(page.get_drawings()),'images':0,'fonts':0})
        pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=True)
        pix.save(ANALYSIS/(p.stem+'-render.png'))
    (OUT/'PGE-asset-validation.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps(reports,indent=2))

def readme():
    (OUT/'README.txt').write_text('''PGE - SHARED-ASSET SOLID VARIANTS
================================

Recreated from the supplied green-livery reference, 12 November 2026.
This is a reference-based reconstruction, not an original archival master.

MAIN FILES
PGE-solid-white-panel.svg / .pdf
  Isolated white folded panel with black BC and PGE artwork.
  Exterior is transparent in SVG and PNG; the white panel is opaque artwork.

PGE-green-livery.svg / .pdf
  The same emblem on two green fields separated by a white horizontal band.

PGE-shared-template.svg
  Original striped version, new solid emblem and green livery together.
  Every BC and PGE shape is defined once in <defs> and reused through <use>.
  Editing a shared path in this template updates all its instances.

PGE-shared-geometry.json
  Canonical path data, hashes, and variant transforms/colors.

PGE-striped-original.svg
  Unchanged copy of the earlier standalone striped SVG.

PNG exports, a preview, a source comparison, validation results, and the
construction scripts are also included.

WHAT IS SHARED
The BC mainland, western island, six coastal cutouts, and P, G and E letter
paths are identical to the earlier vector. The new standalone SVGs contain
those exact paths directly, for portability; the family template defines
each asset once. There are no embedded images or live font dependencies.

WHAT CHANGES
The upper stripe grid is omitted, the panel becomes white, and the map and
lettering become black. Map size/placement and one shared wordmark affine
transform match the new reference. The panel uses the same folded-polygon
construction with a slightly reduced lean. No individual letter was redrawn.
The solid version also has a separate white coastal separator to match the
continuous gap beside Vancouver Island in this reference. This editable
overlay leaves every shared map path unchanged. Hide the solid-coastal-
treatment group to show only the exact shared coastal cutouts.

COLOR AND REFERENCE LIMITS
Upper green: #728B76. Lower green: #345135. White: #FFFFFF. Ink: #000000.
The greens are approximate screenshot samples, not verified paint standards.
The screenshot is only 151 x 167 px. The overall map follows the shared asset,
with a separate coastal-gap treatment. The small yellow curve and photographic artifacts are not
part of the isolated emblem or the clean livery presentation.

EDITING
The standalone SVG groups are named for the panel, map and lettering. Keep
the map's black shapes and white coastal cutouts together when transforming.
The letters are outlined, with a true even-odd compound counter in the P.
The template's neutral background is a separate preview-background object.

REGENERATION
Run recreate_pge_variants.py with reconstruct_pge.py beside it.
Dependencies: Pillow, NumPy, svgpathtools, ReportLab and PyMuPDF.
Primary artwork is generated from paths alone. Reference images are optional
and only used for comparisons; place them under upload/ if needed.
''')

def package():
    originals=ROOT/'output'/'pge-vector'/'PGE-reconstructed.svg'
    if originals.exists():
        dest=OUT/'PGE-striped-original.svg'
        shutil.copy2(originals,dest)
        assert dest.read_bytes()==originals.read_bytes()
    shutil.copy2(ROOT/'reconstruct_pge.py',OUT/'reconstruct_pge.py')
    shutil.copy2(__file__,OUT/'recreate_pge_variants.py')
    zip_path=OUT.parent/'PGE-shared-assets-package.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():z.write(p,arcname='PGE-shared-assets/'+p.name)
    print('Package:',zip_path)

def main():
    solid=make_svg('PGE-solid-white-panel.svg',ISOLATED_VIEWBOX,False)
    livery=make_svg('PGE-green-livery.svg',LIVERY_VIEWBOX,True)
    pdfs=[make_pdf('PGE-solid-white-panel.pdf',ISOLATED_VIEWBOX,artwork_shapes()),
          make_pdf('PGE-green-livery.pdf',LIVERY_VIEWBOX,livery_shapes())]
    template=shared_template()
    render(solid,2800).save(OUT/'PGE-solid-white-panel.png')
    render(livery,2800).convert('RGB').save(OUT/'PGE-green-livery.png')
    render(template,2400).save(OUT/'PGE-shared-template-preview.png')
    build_preview(solid,livery)
    comparison(livery)
    validate([solid,livery],pdfs,template)
    readme();package()

if __name__=='__main__':main()
