"""Normalized, source-derived branding panels for the 24 photographed handbooks.

This is deliberately a reusable branding system, not an illustrated-cover facsimile.
Source wording and observed mark presence are retained; illustrations/authors omitted.
"""
from pathlib import Path
import ast,copy,json,sys,re,html
from xml.etree import ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cairosvg
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OUT=P/'templates/all24';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(P));from label_engine import label_group
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
# Reuse the explicitly registered four source layouts, without executing that builder.
src=P/'build_templates.py';nodes=[]
for n in ast.parse(src.read_text()).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='records' for t in n.targets):break
 nodes.append(n)
ns={'__file__':str(src)};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(src),'exec'),ns)
component,rect=ns['component'],ns['rect'];representatives={c['file']:copy.deepcopy(c) for c in ns['CASES']}
inventory=json.loads((ROOT/'variant_research/handbooks/handbook_variants.json').read_text())
# Each rectangle describes a normalized top-left position and ink target width/height.
# These are visible photographed line breaks, including the bird-volume topic labels.
T=[
 ('Freshwater_Fishes', [('The Fresh-water',80,88,639,70),('Fishes',94,160,264,70),('of British Columbia',373,203,377,34)]),
 ('Birds_Woodpeckers_Crows', [('The Birds',80,84,458,72),('of British Columbia',100,159,546,44),('1) The Woodpeckers',100,205,419,37),('2) The Crows and Their Allies',100,246,641,37)]),
 ('Barnacles', [('The Barnacles',77,85,682,74),('of British Columbia',98,163,608,47)]),
 ('Birds_Shorebirds', [('The Birds',80,84,458,72),('of British Columbia',100,159,546,44),('3) The Shorebirds',100,207,405,38)]),
 ('Birds_Upland_Game', [('The Birds',80,84,458,72),('of British Columbia',100,159,546,44),('4) Upland Game Birds',100,207,494,38)]),
 ('Ferns', [('The Ferns',80,83,475,69),('and Fern-allies',95,153,626,68),('of British Columbia',96,224,590,46)]),
 ('Birds_Gulls', [('The Birds',80,84,458,72),('of British Columbia',100,159,546,44),('5) Gulls, Terns, Jaegers and Skua',100,207,684,38)]),
 ('Birds_Waterfowl', [('The Birds',80,84,458,72),('of British Columbia',100,159,546,44),('6) Waterfowl',100,207,321,38)]),
 ('Orchids', [('The Orchids',80,88,608,73),('of British Columbia',100,169,594,45)]),
 ('Intertidal_Bivalves', [('The Intertidal',80,86,596,69),('Bivalves',96,157,415,69),('of British Columbia',96,228,595,46)]),
 ('Edible_Plants_1972_copy', []),
 ('Edible_Plants_second_copy', [('Guide to Common',80,87,638,52),('Edible Plants',82,149,620,71),('of British Columbia',83,226,590,45)]),
 ('Marine_Life', [('Guide to',80,87,292,51),('Marine Life',80,146,595,74),('of British Columbia',82,228,569,44)]),
 ('Birds_Chickadees', [('The Birds',80,80,458,72),('of British Columbia',97,153,546,44),('8) Chickadees, Thrushes, Kinglets,',97,200,695,38),('Pipits, Waxwings and Shrikes',97,242,661,38)]),
 ('Marine_Fishes', []),
 ('Mushrooms', [('Guide to Common',80,84,620,53),('Mushrooms',80,146,601,73),('of British Columbia',82,229,591,45)]),
 ('Intertidal_Univalves', [('The Intertidal',80,85,613,73),('Univalves',100,161,486,70),('of British Columbia',100,236,567,44)]),
 ('Mosses', [('Some Mosses',80,89,684,76),('of British Columbia',81,174,608,47)]),
 ('Birds_Diving', []),
 ('Pea_Family', [('The Pea Family',80,91,682,73),('of British Columbia',99,174,598,46)]),
 ('Figwort_Family', [('The Figwort',80,85,562,67),('Family',80,153,315,65),('of British Columbia',397,191,365,29)]),
 ('Dragonflies', []),
 ('Food_Plants_Interior_Peoples', [('Food Plants of',80,85,501,54),('British Columbia Indians',80,146,730,55),('Part 2/Interior Peoples',82,224,567,44)]),
 ('Birds_Goatsuckers', [('The Birds',80,85,425,65),('of British Columbia',80,160,524,44),('(10) Goatsuckers, Swifts, Hummingbirds and Swallows',80,231,816,31)]),
]
# Medians/colour clusters measured in each uncalibrated photographed header.
# Ground and panel values are deliberately smooth, with no photographic wear.
PALETTES=[
 ('#89a0af','#b7c5c6','#263335','#8e9e9e'),('#e3c15c','#efd389','#3c2b0d','#d1b166'),
 ('#93aec2','#c8d3d4','#234f70','#93aec2'),('#d3b25f','#dcbe79','#3c2a10','#c8aa65'),
 ('#dfbe65','#eccf8e','#3b290e','#d5b978'),('#979758','#bbbe8e','#303315','#969d68'),
 ('#e5c056','#eace8e','#3a280b','#aa8f50'),('#dcb446','#e3c47e','#39260b','#c3a360'),
 ('#8a9150','#b6ba8e','#293315','#8a9350'),('#8eb1ca','#c9d7df','#244254','#89aabd'),
 ('#b8bd8e','#c8cbc0','#677066','#aeb58b'),('#969b59','#bcc194','#303b1b','#99a263'),
 ('#8199ac','#a8b8bf','#23313a','#8398a4'),('#d5b152','#dcc390','#3b280d','#8f7543'),
 ('#91b0c5','#c2d0d1','#252e2e','#798485'),('#93954f','#ced0a9','#2a3318','#505936'),
 ('#96aebf','#cbd8dc','#263c4b','#263c4b'),('#a0a432','#c3c59c','#283413','#a0a66c'),
 ('#ebc75b','#f6dea4','#392a0c','#947d50'),('#9fa66b','#cad2c1','#5b6d53','#788c68'),
 ('#a6aa61','#cdd3bf','#5b6d53','#7b8b68'),('#b64317','#d48f80','#370401','#280100'),
 ('#a1a73f','#b2be5f','#26320c','#26320c'),('#f2cd5a','#f9dd93','#392b0b','#392b0b'),
]
assert len(T)==len(inventory)==24
records=[]
for idx,(r,(slug,headings),pal) in enumerate(zip(inventory,T,PALETTES),1):
 num=str(r['handbook_no']);filename=Path(r['image_path']).name;stem=f'{idx:02d}_HB{int(num):02d}_{slug}'
 em='Ram_Head' if 'ram' in r['subject_emblem'] else 'Flower' if 'flower' in r['subject_emblem'] else 'Crab' if 'crab' in r['subject_emblem'] else None
 has_bcpm=r['bcpm_monogram']!='absent'
 c=dict(header=(45,55,910,300),art=(45,395,910,765),footer=(45,1200,910,140),radius=34,
        headings=headings,number=(num,819,92,94,94,72 if len(num)>1 else 42,51),emblem=(em,819,219,94) if em else None,
        museum=(72,1224,730,38),victoria=(73,1288,130,33),canada=(664,1288,138,33),bcpm=(826,1225,96) if has_bcpm else None)
 if filename in representatives:
  c.update(representatives[filename]);c['headings']=headings or c['headings']
 if num in ['36','37']:
  c.update(footer=(45,1210,910,122),museum=(78,1232,815,36),victoria=(79,1283,164,34),canada=(714,1283,178,34),bcpm=None)
 # No. 5 and later no. 24 use dark numbering, despite pale category marks elsewhere.
 bg,panel,ink,accent=pal;number_ink=ink if num in ['5','24','26','35','36','37'] else accent
 body=[f'<rect id="cover-ground" width="1000" height="1400" fill="{bg}"/>',rect(c['header'],panel,ink,c['radius'],'header-panel'),rect(c['art'],panel,ink,c['radius'],'illustration-panel'),rect(c['footer'],panel,ink,c['radius'],'footer-panel')]
 for j,(text,x,y,w,h) in enumerate(c['headings']):body.append(f'<g id="heading-line-{j+1}">'+label_group(text,x,y,w,h,ink)+'</g>')
 n,x,y,w,h,tw,th=c['number'];body.append(rect((x,y,w,h),panel,number_ink,17,'handbook-number-panel'));body.append(label_group(n,x+(w-tw)/2,y+(h-th)/2,tw,th,number_ink))
 if c['emblem']:
  e,x,y,size=c['emblem'];body.append(component(P/'svg'/f'{e}.svg',x,y,size,accent,'category-emblem'))
 for text,key in [('British Columbia Provincial Museum','museum'),('Victoria','victoria'),('Canada','canada')]:
  x,y,w,h=c[key];body.append(label_group(text,x,y,w,h,ink))
 if c['bcpm']:
  x,y,size=c['bcpm'];body.append(component(ROOT/'output/package/svg/04_BC_Provincial_Museum.svg',x,y,size,accent,'bcpm-monogram'))
 title=f'Handbook {num}: {r["title_visible"]}'
 svg=f'<svg xmlns="{NS}" width="1000" height="1400" viewBox="0 0 1000 1400"><title>{html.escape(title)} — normalized branding-panel template</title><desc>Source-derived fixed wording, observed category-emblem presence and publisher treatment. Illustration field intentionally open and authors omitted. Panel geometry is normalized; this is not an exact illustrated-cover facsimile. Lettering is the closest inspected modern Helvetica43ExtendedLight comparison, not a confirmed historical font. Colours are approximate samples from uncalibrated photographs. No raster images or fonts embedded.</desc>'+''.join(body)+'</svg>'
 (OUT/f'{stem}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/f'{stem}.png'))
 source=Image.open(r['image_path']).convert('RGB');w,h=source.size
 source.crop((0,0,w,round(h*.35))).save(OUT/f'{stem}_source_header.jpg',quality=94)
 source.crop((0,round(h*.78),w,h)).save(OUT/f'{stem}_source_footer.jpg',quality=94)
 records.append(dict(index=idx,slug=stem,handbook_number=int(num),title=title,source_title=r['title_visible'],svg=stem+'.svg',png=stem+'.png',
  source_file=filename,source_url=r['seller_page_url'],source_image_url=r['image_url'],printed_date_visible=r['printed_date_visible_in_this_image'],date_status=r['date_status'],
  heading_lines=[h[0] for h in c['headings']],canvas=[1000,1400],panel_rectangles={k:c[k] for k in ['header','art','footer']},
  category_emblem=em,bcpm=has_bcpm,palette=dict(zip(['ground','panel','ink','accent'],pal)),
  source_mark_status={'subject_emblem':r['subject_emblem'],'bcpm_monogram':r['bcpm_monogram']},
  geometry_status='Source-specific normalized panel positions for this representative cover.' if filename in representatives else 'Normalized panel geometry shared within the photographed series; source title line breaks and observed symbol presence retained.',
  type_status='Closest inspected modern Neue Helvetica Pro43ExtendedLight specimen; exact historical typeface unconfirmed.',
  palette_status='Approximate RGB from uncalibrated photographed header colour clusters/dark samples; no official ink standard implied.',
  scope='Reusable branding-panel template. Illustration field open; illustration artwork, authors, paper wear and incidental handwriting omitted.'))
manifest={'title':'All 24 photographed handbook branding variants','template_count':24,'distinct_handbook_numbers':23,'scope':'Normalized source-derived reusable branding-panel templates, not exact illustrated-cover facsimiles.','templates':records}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Compact index with editorial labelling outside production artwork.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
cols=6;cellw=330;cellh=520;margin=30;sheet=Image.new('RGB',(cols*cellw+2*margin,4*cellh+160),'#f4f1e8');draw=ImageDraw.Draw(sheet)
draw.text((30,24),'All 24 photographed handbook branding variants',font=ImageFont.truetype(bold,37),fill='#163c36')
draw.text((30,77),'Source-derived normalized panels • 23 titles / two photographed no.20 copies • illustration fields intentionally open',font=ImageFont.truetype(font,22),fill='#52675e')
for i,r in enumerate(records):
 x=margin+(i%cols)*cellw;y=130+(i//cols)*cellh;pic=Image.open(OUT/r['png']).convert('RGB').resize((305,427),Image.Resampling.LANCZOS);sheet.paste(pic,(x,y))
 draw.text((x,y+437),f'{r["index"]:02d}  Handbook {r["handbook_number"]}',font=ImageFont.truetype(bold,20),fill='#163c36')
 label=T[i][0].replace('_',' ')
 if len(label)>33:label=label[:30]+'…'
 draw.text((x,y+466),label,font=ImageFont.truetype(font,17),fill='#52675e')
sheet.save(OUT/'All_24_Handbook_Branding_Templates.png')
# Six source-versus-template comparison sheets, four records per sheet.
for start in range(0,24,4):
 sh=Image.new('RGB',(2060,1700),'#f4f1e8');d=ImageDraw.Draw(sh)
 d.text((30,20),f'Handbook branding review — records {start+1}–{start+4}',font=ImageFont.truetype(bold,35),fill='#163c36')
 d.text((30,72),'Photographs beside normalized vector panels; all illustration fields intentionally open.',font=ImageFont.truetype(font,23),fill='#52675e')
 for k,r in enumerate(records[start:start+4]):
  x=30+(k%2)*1025;y=120+(k//2)*780
  d.text((x,y),f'{r["index"]:02d} / Handbook {r["handbook_number"]}',font=ImageFont.truetype(bold,24),fill='#163c36')
  for side,(p,label) in enumerate([(Path(inventory[start+k]['image_path']),'Source photograph'),(OUT/r['png'],'Normalized branding template')]):
   xx=x+side*480;d.text((xx,y+36),label,font=ImageFont.truetype(font,21),fill='#52675e');im=Image.open(p).convert('RGB');im.thumbnail((455,637),Image.Resampling.LANCZOS);sh.paste(im,(xx+(455-im.width)//2,y+73+(637-im.height)//2))
  d.text((x,y+726),'Approximate colour / comparison type / authors and illustration omitted',font=ImageFont.truetype(font,18),fill='#52675e')
 sh.save(OUT/f'Source_Comparison_{start//4+1:02d}.jpg',quality=93)
# Structural assertions resolve the specific deliverable requirement: font-free pure vectors.
for r in records:
 root=ET.parse(OUT/r['svg']).getroot();assert not root.findall(f'.//{{{NS}}}text');assert not root.findall(f'.//{{{NS}}}image')
 assert bool(root.findall('.//*[@id="bcpm-monogram"]'))==r['bcpm']
 assert bool(root.findall('.//*[@id="category-emblem"]'))==bool(r['category_emblem'])
(OUT/'README.md').write_text('''# All photographed handbook branding-panel variants\n\nThis folder contains 24 editable vector panel templates, corresponding one-to-one with the photographed source inventory (23 distinct handbook numbers; two separately photographed no.20 copies). The production SVGs have no text elements, embedded images, fonts or placeholder labels. Each also has a PNG preview.\n\nThese preserve the visible title line breaks, handbook numbers, subject-emblem presence and museum footer treatment. They use normalized panel geometry and approximate photographic colours. The open central field is intentional: natural-history illustrations and authors are outside this branding-panel reconstruction. They are not exact complete-cover facsimiles.\n\nNos.36 and37 have no BCPM monogram, following their photographs. No category symbol is added to covers where none is visible. Faint symbols are preserved as approximate pale ink. No.23 only shows “Some Common / Marine Fishes” in its actual photographed header. Bird-volume topic lines are included.\n\nFixed lettering is reconstructed from the closest inspected public modern Neue Helvetica Pro43ExtendedLight specimen, with straight and cubic paths. The exact historical handbook typeface is unconfirmed. These are limited fixed wordmarks, not a font distribution.\n\n`manifest.json` records the exact source URLs, source date status, heading text, observed mark status, panel positions and approximate palette for each template. Seller dates are not treated as verified publication dates. Source comparison sheets include full source photographs with the unillustrated templates beside them.\n''')
print(json.dumps({'templates':len(records),'distinct_numbers':len(set(r['handbook_number'] for r in records)),'pure_vectors':True,'output':str(OUT)}))
