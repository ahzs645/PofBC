"""Assemble the reviewed branding artwork and its evidence into a portable collection.

The SVGs are the deliverables. Construction scripts are retained as research
records; their original relative source paths are documented in the README.
"""
from pathlib import Path
import json, csv, shutil, hashlib, html, re, concurrent.futures
from collections import Counter
from lxml import etree
import cairosvg

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'branding_rebuild'
OUT=ROOT/'output'
PKG=OUT/'branding_collection'
ASSETS=[]
NS='http://www.w3.org/2000/svg'
GROUPS={
 'symbols':'Core symbols and colour treatments',
 'related_emblems':'Associated emblems',
 'report_dividers':'Annual-report section dividers',
 'branch_lockups':'Reusable department and branch bands',
 'cover_headers':'Annual-report cover branding',
 'cover_stacks':'Back-cover symbol stacks',
 'wordmarks':'Outlined report lettering',
 'handbook_emblems':'Museum handbook subject emblems',
 'handbook_labels':'Outlined handbook lettering',
 'handbook_templates':'Museum handbook branding panels',
 'park_symbols':'Proposed park pictograms',
 'supporting_arms':'Supporting period coat of arms'
}

def copyfile(src,dst):
 src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)
 return str(dst.relative_to(PKG))

def add(src,group,title=None,meta=None):
 src=Path(src);r=etree.fromstring(src.read_bytes());v=list(map(float,r.get('viewBox').split()))
 title=title or r.findtext('{'+NS+'}title') or src.stem.replace('_',' ')
 meta=meta or {}
 id=group+'/'+src.stem
 rec={**meta,'id':id,'title':title,'group':group,'group_title':GROUPS[group],
      'svg':copyfile(src,PKG/'vectors'/group/src.name),
      'preview':f'previews/{group}/{src.stem}.png',
      'pdf':f'pdf/{group}/{src.stem}.pdf','viewBox':v,
      'font_dependency':False,'embedded_raster':False}
 ASSETS.append(rec)
 return rec

def collect_assets():
 root=json.loads((WORK/'collection/manifest.json').read_text())
 for item in root['assets']:
  metadata={k:v for k,v in item.items() if k not in ['id','svg','preview','title','group']}
  add(WORK/'collection'/item['svg'],item['group'],item['title'],metadata)
 for p in sorted((ROOT/'output/package/svg/reversed').glob('*.svg')):
  add(p,'symbols',p.stem.replace('_',' '),{'treatment':'transparent_white','status':'Reusable white treatment of the reconstructed historical symbol.'})
 for m in json.loads((WORK/'related_emblems/manifest.json').read_text()):
  add(WORK/'related_emblems'/m['svg'],'related_emblems',m['title'],{k:v for k,v in m.items() if k not in ['svg','preview','id','title']})
 phrases=json.loads((WORK/'type/specimen_manifest.json').read_text())['phrases']
 for p,t in zip(sorted((WORK/'type/wordmarks').glob('*.svg')),phrases):
  meta={'status':'Fixed-wording Corporatus comparison outlines; final report layouts retain page-specific spacing. Not font software or recovered historical production outlines.', 'source_url':'https://www.myfonts.com/collections/corporatus-font-alex-rosario-type'}
  if t in ['General Administration','Department of Recreation and Conservation']:
   # The two principal wordmarks are extracted from their final, measured
   # report layout, so standalone use retains that finished page's spacing.
   layout=next(m for m in root['assets'] if m['id']=='1973_general_divider')
   spec=next(s for s in layout['typography'] if s['text']==t)
   source=etree.fromstring((WORK/'collection'/layout['svg']).read_bytes())
   wanted=t.replace(' ','')
   g=next(e for e in source if etree.QName(e).localname=='g' and ''.join(q.get('data-character','') for q in e)==wanted)
   x0,y0,x1,y1=spec['source_ink_bbox_frame_normalized'];v=[x0-4,y0-4,x1-x0+8,y1-y0+8]
   temp=WORK/'root/final_wordmarks'/p.name;temp.parent.mkdir(exist_ok=True)
   temp.write_text(f'<svg xmlns="{NS}" viewBox="'+ ' '.join(map(str,v))+f'" width="{v[2]}" height="{v[3]}"><title>{html.escape(t)}</title><desc>Outlined label extracted from the measured 1973 General Administration reconstruction.</desc>'+etree.tostring(g,encoding='unicode')+'</svg>')
   p=temp;meta.update({'status':'Outlined standalone label with the final measured 1973 page spacing.','source_url':layout['source_url'],'typography':spec})
  add(p,'wordmarks',t,meta)
 for m in json.loads((WORK/'handbooks/subject_emblems.json').read_text()):
  add(WORK/'handbooks'/m['svg'],'handbook_emblems',m['name'],{k:v for k,v in m.items() if k!='svg'})
 for m in json.loads((WORK/'handbooks/label_sources.json').read_text()):
  add(WORK/'handbooks'/m['svg'],'handbook_labels',m['text'],{'status':m['status'],'source_url':m['url'],'typeface':'Neue Helvetica Pro 43 Extended Light; closest inspected comparison, exact historical face unconfirmed.'})
 manifest_path=WORK/'handbooks/templates/all24/manifest.json'
 if manifest_path.exists():
  data=json.loads(manifest_path.read_text())
  items=data if isinstance(data,list) else data.get('templates',data.get('assets',[]))
  for m in items:
   val=m.get('svg') or m.get('file');p=Path(val)
   if not p.is_absolute():
    possibilities=[manifest_path.parent/p,WORK/'handbooks'/p]
    p=next((q for q in possibilities if q.exists()),possibilities[0])
   add(p,'handbook_templates',m.get('title') or m.get('name'),{k:v for k,v in m.items() if k not in ['svg','preview','id','title','name']})
 else:
  raise RuntimeError('Handbook templates are not ready.')
 parks=json.loads((WORK/'park_symbols/manifest.json').read_text())
 for m in parks['symbols']:
  add(WORK/'park_symbols'/m['svg'],'park_symbols',m['name'],{'source_url':parks['source_pdf']+'#page=68','source_pdf_page':68,'printed_page':'DD67','status':parks['status'],'whole_ink_IoU':m['whole_ink_iou'],'interior_ink_IoU':m['interior_ink_iou']})
 add(WORK/'reused_arms/BC_Arms_1960_Museum_Refined.svg','supporting_arms','Period coat of arms / 1960 Museum engraving reconstruction',{'status':'Reused supporting artwork from the user’s refined BC arms collection. Similar period treatment; not the exact engraving master in the 1971–1973 cover scans.'})

def render(rec):
 p=PKG/rec['svg'];png=PKG/rec['preview'];pdf=PKG/rec['pdf']
 png.parent.mkdir(parents=True,exist_ok=True);pdf.parent.mkdir(parents=True,exist_ok=True)
 w,h=rec['viewBox'][2:];scale=min(1100/w,1400/h)
 cairosvg.svg2png(url=str(p),write_to=str(png),output_width=max(1,round(w*scale)),output_height=max(1,round(h*scale)))
 cairosvg.svg2pdf(url=str(p),write_to=str(pdf))
 return rec['id']

def tree(src,dst,ignore=None):
 if Path(src).exists():shutil.copytree(src,dst,dirs_exist_ok=True,ignore=ignore)

def collect_evidence():
 # Source/reconstruction comparisons are deliberately separate from production vectors.
 tree(WORK/'collection/review',PKG/'review/report_layouts')
 for f in (WORK/'root').glob('*_art_source.png'):copyfile(f,PKG/'sources/report_dividers'/f.name)
 copyfile(WORK/'root/layout_geometry.json',PKG/'sources/report_dividers/layout_geometry.json')
 for sub in ['related_emblems','handbooks','type','park_symbols']:
  base=WORK/sub
  for f in base.glob('*.png'):
   if f.name.endswith('_native_page.png') or f.name=='native_page.png' or f.name.endswith('_grid.png') or f.name.endswith('_reference_large.png'):continue
   if 'Review' in f.name or 'Comparison' in f.name or 'Overview' in f.name:copyfile(f,PKG/'review'/sub/f.name)
  for f in base.glob('*_source.png'):copyfile(f,PKG/'sources'/sub/f.name)
  for f in base.glob('*_native_reference.png'):copyfile(f,PKG/'sources'/sub/f.name)
  for f in base.glob('*_construction.svg'):copyfile(f,PKG/'construction'/sub/f.name)
  for f in base.glob('*.py'):
   if f.name not in ['fit_divider_labels.py','patch_divider.py']:copyfile(f,PKG/'construction'/sub/f.name)
  for f in base.glob('*.json'):
   if not f.name.startswith('divider_'):copyfile(f,PKG/'construction'/sub/f.name)
  if (base/'README.md').exists():copyfile(base/'README.md',PKG/'notes'/f'{sub}.md')
 for f in (WORK/'root').glob('*.py'):copyfile(f,PKG/'construction/root'/f.name)
 copyfile(WORK/'root/layout_geometry.json',PKG/'construction/root/layout_geometry.json')
 tree(WORK/'park_symbols/sources',PKG/'sources/park_symbols')
 tree(WORK/'park_symbols/overlays',PKG/'review/park_symbols/individual')
 tree(WORK/'handbooks/templates/review',PKG/'review/handbook_templates')
 for f in (WORK/'handbooks/templates/all24').glob('*_source_*.jpg'):copyfile(f,PKG/'sources/handbook_panels'/f.name)
 for f in (WORK/'handbooks/templates/all24').glob('Source_Comparison_*.jpg'):copyfile(f,PKG/'review/handbook_templates'/f.name)
 copyfile(WORK/'handbooks/templates/all24/All_24_Handbook_Branding_Templates.png',PKG/'review/handbook_templates/All_24_Handbook_Branding_Templates.png')
 for f in (WORK/'handbooks/templates/all24').glob('*.json'):copyfile(f,PKG/'construction/handbook_templates'/f.name)
 copyfile(WORK/'handbooks/templates/all24/README.md',PKG/'notes/Handbook_24_Templates.md')
 for f in (WORK/'handbooks/templates').glob('*.py'):copyfile(f,PKG/'construction/handbook_templates'/f.name)
 for f in (WORK/'handbooks/templates').glob('*.json'):copyfile(f,PKG/'construction/handbook_templates'/f.name)
 for f in (WORK/'handbooks/templates').glob('*.png'):
  if 'Review' in f.name or 'Overview' in f.name:copyfile(f,PKG/'review/handbook_templates'/f.name)
 for f in (WORK/'handbooks/templates').glob('*.md'):copyfile(f,PKG/'notes'/f.name)
 for ext in ['svg','pdf','png']:
  copyfile(WORK/'park_symbols'/f'Park_Symbols_1971_Reconstructed.{ext}',PKG/'sheets'/f'Park_Symbols_1971_Reconstructed.{ext}')
 # Preserve the five-symbol construction records and earlier source inventory.
 tree(OUT/'package/construction',PKG/'construction/core_family')
 tree(OUT/'package/review',PKG/'review/core_family')
 copyfile(OUT/'package/manifest.json',PKG/'notes/Core_Family_Manifest.json')
 for f in ['BC_Typeface_and_Variants_Atlas.pdf','BC_Handbook_Variants_Inventory.csv','BC_Typeface_Variants_Inventory.csv','BC_Handbook_Variants_Contact_Sheet.jpg','BC_Corporatus_Spacing_Study.pdf','BC_Corporatus_Spacing_Settings.json','BC_Corporatus_Spacing.css','BC_Corporatus_Spacing_README.md']:
  copyfile(OUT/f,PKG/'reference'/f)
 for f in ['handbook_variants.json','report_variants_matrix.csv','report_variants_findings.md']:
  candidates=[ROOT/'variant_research/handbooks'/f,ROOT/'variant_research/reports'/f]
  src=next((p for p in candidates if p.exists()),None)
  if src:copyfile(src,PKG/'reference'/f)
 hb=json.loads((ROOT/'variant_research/handbooks/handbook_variants.json').read_text())
 for m in hb:
  p=Path(m['image_path'])
  if p.exists():copyfile(p,PKG/'sources/handbook_covers'/p.name)
 for f in ['page2_image1.jpeg','page2_image3.jpeg']:
  p=ROOT/'variant_research/handbooks'/f
  if p.exists():copyfile(p,PKG/'sources/handbook_covers'/f)
 copyfile(WORK/'reused_arms/README.md',PKG/'notes/Supporting_Coat_of_Arms.md')

def validate():
 issues=[]
 for m in ASSETS:
  p=PKG/m['svg'];r=etree.fromstring(p.read_bytes());ids=set();refs=[]
  for e in r.iter():
   tag=etree.QName(e).localname
   if tag in ['text','image','foreignObject','script']:issues.append([m['id'],'forbidden element',tag])
   if e.get('id'):ids.add(e.get('id'))
   for k,v in e.attrib.items():
    if etree.QName(k).localname=='href':
     if v.startswith('#'):refs.append(v[1:])
     elif tag not in ['a']:issues.append([m['id'],'external SVG dependency',v])
    refs.extend(re.findall(r'url\(#([^)]*)\)',v))
  for ref in refs:
   if ref not in ids:issues.append([m['id'],'unresolved reference',ref])
  if r.get('data-pending') or b'data-pending' in p.read_bytes():issues.append([m['id'],'pending placeholder'])
  m['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 report={'production_svg_count':len(ASSETS),'all_svg_parse':True,'no_live_text_or_embedded_raster':not issues,'issues':issues,'scope':'Production vectors only; reference photos and review sheets are intentionally raster.'}
 (PKG/'validation.json').write_text(json.dumps(report,indent=2))
 if issues:raise RuntimeError(issues)

def docs():
 counts=Counter(m['group'] for m in ASSETS)
 data={'title':'British Columbia Recreation and Conservation — reconstructed branding collection','created':'2026-11-21','status':'Historical reconstructions and clearly marked derived templates; not recovered original production masters.','production_svg_count':len(ASSETS),'category_counts':dict(counts),'assets':ASSETS}
 (PKG/'manifest.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
 fields=['id','title','group','svg','pdf','preview','source_url','source_report','source_pdf_page','printed_page','status']
 with (PKG/'asset_index.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(ASSETS)
 table='\n'.join(f'| {GROUPS[k]} | {v} |' for k,v in counts.items())
 readme=f'''# British Columbia Recreation and Conservation
## Reconstructed branding collection

This collection recreates the branding documented in the checked 1970–1973 annual reports and the photographed Provincial Museum handbook series. It includes **{len(ASSETS)} production SVG files**, plus matching vector PDFs, PNG previews, source evidence, overlays and construction records. Colour treatments and fixed lettering components are counted separately; this is not a claim of {len(ASSETS)} different historical logos.

Open **index.html** for the searchable visual catalogue. Open **BC_Recreation_Conservation_Branding_Catalogue.pdf** for the illustrated guide. The SVG masters are in **vectors/**; the matching PDF and PNG folders use the same category and basename.

| Category | SVG files |
|---|---:|
{table}

## What is reconstructed

The five original square emblems cover the department, Fish and Wildlife, Provincial Parks, the Provincial Museum, and Commercial Fisheries / Marine Resources. They include black, report-green, pale, reversed-on-dark and transparent-white treatments. Colours approximate the scanned copies; they are not official printing specifications.

Three associated designs are supplied as four assets: the 1973 F&W oval emblem and its paired name panel; the Parks dogwood/province shield visible in the 1973 organisation chart; and the department’s earlier 1970 oval dogwood badge.

The report section dividers preserve the two documented layout generations. The 1971 family also occurs in 1972; duplicate artwork is indexed in the research inventory rather than presented as an invented third design. The 1973 interior uses the newer F&W panel while its back cover retains the earlier square. Both fisheries name arrangements are included.

The museum handbook components and normalized branding-panel templates follow the photographed title, number, emblem and publisher-panel variants. Open illustration fields are intentional: these assets reconstruct the branding framework, while the cover’s natural-history illustration remains separate artwork. Photographed printing dates are verified only where a visible edition notice is recorded; seller dates do not establish a design’s introduction date.

All 22 signs from the 1971 sheet headed “Proposed Park Symbols” are included. The source’s proposal status is preserved; it does not establish approval or installation.

## Type and spacing

The report wordmarks use a restricted set of Corporatus comparison outlines reconstructed from public specimens. The supplied wording is already paths and needs no installed font. This is fixed artwork, not an installable font or recovered historical font master. For new wording, use Corporatus in your design application and refer to the included spacing study.

The earlier live-specimen study gives starting settings of 100% horizontal scale and tracking around −45 to −50 per 1000 em for General Administration; the long department line fits near 97% horizontal scale and −22 to −25 tracking. The finished path-based pages fit each line’s measured bounds, and their internal reconstructed glyph advances differ from live font metrics. Do not transfer their JSON tracking values directly into a commercial font. The two principal standalone wordmarks retain the finished 1973 page spacing. None of these measurements proves that the original typesetter applied a particular scaling command.

Handbook lettering uses the closest inspected modern comparison, Neue Helvetica Pro 43 Extended Light. The exact historical handbook face is unconfirmed. The small captions in the F&W panel and Parks shield use close outlined substitutes, documented in their notes.

## Using the artwork

Import an SVG into Illustrator, Affinity Designer, Inkscape or Figma to edit paths, fills and groups. Standalone black/green/white symbols have transparent backgrounds. Report pages and handbook panels include their paper/background shapes as editable vector objects. Reverse samples include a dark field; transparent-white masters are provided separately.

The five department-and-branch bands are reusable arrangements derived from the full report dividers. Handbook panels normalize photographed proportions and colours. The cover branding blocks exclude the photographic image area and reuse a separately reconstructed period coat of arms, rather than claiming the exact cover engraving. These distinctions are recorded in the manifest.

## Evidence and limitations

The review folders show source, reconstruction and overlay comparisons. Pixel overlap scores measure registration against small printed scans, not a percentage of historical authenticity. The largest remaining interpretation is in the 1970 botanical engraving, small serif lettering, tiny handbook emblem details, and complex park-sign figures/ropes/snowflake details.

The supplied reports document the designs’ use, but no original identity manual or credited designer was established for this family. The Parks Branch logo proposal mentioned on printed AA105 / PDF 106 describes a submission without showing its drawing; it is not identified here with the spiral mark or shield.

The construction scripts are preserved as working research records, with their original workspace-relative paths. They use the source PDFs identified in their manifests; those full reports and font software are not bundled. The production vectors and their PDF exports are self-contained.

## Primary sources

- 1970 report: https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1970.pdf
- 1971 report: https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf
- 1972 colour report: https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1972.pdf
- 1973 report: https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf
- Report colour scans and archive: https://rbcm.ca/corporate-information/reports-policies/annual-report-archive/
- Corporatus: https://www.myfonts.com/collections/corporatus-font-alex-rosario-type
- Handbook photographs: individual seller-page URLs and visible-date qualifications in reference/BC_Handbook_Variants_Inventory.csv.

Created 21 November 2026. Historical reconstruction for review and reuse; no claim of official endorsement or recovered original master artwork.
'''
 (PKG/'README.md').write_text(readme)
 cards=[]
 for m in ASSETS:
  white='dark' if m.get('treatment')=='transparent_white' else ''
  source=m.get('source_url') or m.get('seller_page_url') or ''
  source_link=f'<a href="{html.escape(source,quote=True)}" target="_blank" rel="noopener">Source</a>' if source else ''
  cards.append(f'<article data-group="{m["group"]}" data-search="{html.escape((m["title"]+" "+m["group_title"]).lower(),quote=True)}"><a class="art {white}" href="{m["svg"]}"><img loading="lazy" src="{m["preview"]}" alt="{html.escape(m["title"],quote=True)}"></a><div class="info"><small>{html.escape(m["group_title"])}</small><h2>{html.escape(m["title"])}</h2><p>{html.escape(str(m.get("status","Historical vector reconstruction.")))}</p><nav><a href="{m["svg"]}" download>SVG</a><a href="{m["pdf"]}" download>PDF</a><a href="{m["preview"]}" download>PNG</a>{source_link}</nav></div></article>')
 opts=''.join(f'<option value="{k}">{GROUPS[k]} ({v})</option>' for k,v in counts.items())
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Recreation & Conservation — Branding Collection</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece2;color:#173c35;font-family:Arial,sans-serif;line-height:1.5}header{background:#163b33;color:#f4f1e6;padding:52px max(28px,5vw)}h1{font-size:clamp(30px,4vw,60px);line-height:1.05;margin:12px 0}header p{max-width:900px;color:#e1e6d9}a{color:inherit}header a{margin-right:24px}main{padding:30px max(24px,4vw)}.controls{display:flex;gap:16px;flex-wrap:wrap;position:sticky;top:0;background:#eeece2ed;padding:14px 0;z-index:1}input,select{font:inherit;padding:12px;border:1px solid #a6b2a7;border-radius:8px;background:#fffdf5;color:#173c35}input{min-width:260px;flex:1}#count{align-self:center;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:22px}article{background:#fffdf5;border:1px solid #d2d7c9;border-radius:12px;overflow:hidden}article[hidden]{display:none}.art{height:260px;padding:22px;display:flex;align-items:center;justify-content:center;background:linear-gradient(45deg,#f4f3eb 25%,transparent 25%),linear-gradient(-45deg,#f4f3eb 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#f4f3eb 75%),linear-gradient(-45deg,transparent 75%,#f4f3eb 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}.art.dark{background:#163b33}.art img{max-width:100%;max-height:100%;object-fit:contain}.info{padding:20px}.info small{color:#60786c;font-size:11px;text-transform:uppercase;letter-spacing:.08em}h2{font-size:18px;line-height:1.25;margin:8px 0}.info p{font-size:12px;color:#53665b;max-height:110px;overflow:auto}nav{display:flex;gap:15px;font-size:13px;font-weight:bold}footer{padding:30px;text-align:center;font-size:12px;color:#60786c}</style></head><body><header><small>BRITISH COLUMBIA · HISTORICAL RECONSTRUCTION</small><h1>Recreation &amp; Conservation</h1><p>Symbols, report layouts, outlined lettering, museum handbook branding and the 22 proposed park signs. Each item links to its SVG master, vector PDF and PNG preview.</p><a href="BC_Recreation_Conservation_Branding_Catalogue.pdf">Illustrated catalogue</a><a href="README.md">Methods and limitations</a><a href="asset_index.csv">Asset index</a></header><main><div class="controls"><input id="q" type="search" placeholder="Find a symbol, title or category" aria-label="Search assets"><select id="category" aria-label="Filter category"><option value="">All categories</option>'''+opts+'''</select><span id="count"></span></div><div class="grid">'''+''.join(cards)+'''</div></main><footer>Historical reconstructions and derived templates. Colours are approximations of scanned copies. Source records and review overlays are included in the collection.</footer><script>const q=document.querySelector('#q'),sel=document.querySelector('#category'),cards=[...document.querySelectorAll('article')];function filter(){let n=0;for(const c of cards){const show=(!sel.value||c.dataset.group===sel.value)&&c.dataset.search.includes(q.value.trim().toLowerCase());c.hidden=!show;if(show)n++}document.querySelector('#count').textContent=n+' assets'}q.addEventListener('input',filter);sel.addEventListener('change',filter);filter();</script></body></html>'''
 (PKG/'index.html').write_text(page)

def run():
 PKG.mkdir(parents=True,exist_ok=True)
 collect_assets();validate()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  done=list(pool.map(render,ASSETS))
 collect_evidence();docs()
 print(json.dumps({'assets':len(ASSETS),'counts':dict(Counter(m['group'] for m in ASSETS)),'package':str(PKG),'renders':len(done)},indent=2))

if __name__=='__main__':run()
