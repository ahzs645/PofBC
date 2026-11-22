"""Reusable branding-panel templates, not complete illustrated cover replicas."""
from pathlib import Path
import sys,json,copy,io
import numpy as np,cv2,cairosvg
from PIL import Image,ImageDraw,ImageFont
from xml.etree import ElementTree as ET
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OUT=P/'templates';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(P));from label_engine import label_group
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)

CASES=[
 dict(slug='Edible_Plants_20',title='Guide to Common Edible Plants / no.20',file='page2_image2.jpeg',corners=[(55,33),(837,35),(832,1102),(81,1095)],
      source_url='https://www.etsy.com/listing/1642856129/guide-to-common-edible-plants-of-bc-af',
      header=(29,42,919,316),art=(33,401,914,787),footer=(45,1224,895,138),radius=34,
      headings=[('Guide to Common',54,84,610,51),('Edible Plants',54,146,598,70),('of British Columbia',55,226,550,45)],
      number=('20',817,84,96,99,77,49),emblem=('Flower',817,214,96),
      museum=(67,1246,728,37),victoria=(70,1310,132,33),canada=(660,1310,136,33),bcpm=(817,1242,95),
      palette_boxes={'ground':[200,370,800,390],'panel':[600,425,850,460],'ink':[55,1240,805,1289],'accent':[812,211,919,315]}),
 dict(slug='Marine_Fishes_23',title='Some Common Marine Fishes / no.23',file='abe_32246733201.jpg',corners=[(46,35),(846,36),(838,1128),(41,1134)],
      source_url='https://www.abebooks.com/Common-Marine-Fishes-British-Columbia-Handbook/32246733201/bd',
      header=(64,80,853,286),art=(64,405,853,740),footer=(64,1179,853,132),radius=34,
      headings=[('Some Common',105,108,487,52),('Marine Fishes',105,164,603,70)],
      number=('23',782,117,90,88,71,45),emblem=('Crab',782,238,91),
      museum=(89,1201,686,35),victoria=(90,1260,125,32),canada=(656,1260,126,32),bcpm=(796,1193,86),
      palette_boxes={'ground':[180,1320,830,1360],'panel':[300,420,650,448],'ink':[100,100,710,240],'accent':[779,235,879,334]}),
 dict(slug='Birds_29',title='The Birds / no.29',file='abe_32246743715.jpg',corners=[(39,62),(815,64),(817,1144),(36,1145)],
      source_url='https://www.abebooks.com/Birds-British-Columbia-Diving-Tube-nosed-Swimmers/32246743715/bd',
      header=(39,37,917,301),art=(34,380,923,794),footer=(30,1208,927,145),radius=35,
      headings=[('The Birds',69,79,448,73),('of British Columbia',94,157,535,43),('9) Diving Birds and Tube-nosed Swimmers',94,210,705,33)],
      number=('29',823,87,96,98,78,48),emblem=('Ram_Head',823,214,96),
      museum=(54,1233,758,37),victoria=(55,1298,132,34),canada=(669,1298,139,34),bcpm=(825,1233,98),
      palette_boxes={'ground':[200,1365,800,1385],'panel':[500,280,800,315],'ink':[65,70,650,210],'accent':[820,208,925,317]}),
 dict(slug='Dragonflies_35',title='The Dragonflies / no.35',file='abe_30890355070.jpg',corners=[(41,11),(359,71),(352,531),(31,582)],
      source_url='https://www.abebooks.com/first-edition/Dragonflies-British-Columbia-Handbook-No-35/30890355070/bd',
      header=(80,70,859,291),art=(76,405,861,716),footer=(76,1153,854,120),radius=38,
      headings=[('The Dragonflies',113,91,656,84),('of British Columbia',123,181,482,45)],
      number=('35',812,106,94,94,61,39),emblem=None,
      museum=(110,1172,681,37),victoria=(118,1236,122,28),canada=(659,1227,134,31),bcpm=(820,1166,80),
      palette_boxes={'ground':[200,1300,850,1350],'panel':[250,225,750,245],'ink':[105,80,780,225],'accent':[816,1165,904,1250]})
]

def rgbhex(v):return '#'+''.join(f'{int(np.clip(round(x),0,255)):02x}' for x in v)
def colour(arr,box,ink=False):
 x0,y0,x1,y1=box;a=arr[y0:y1,x0:x1].reshape(-1,3)
 if ink:
  l=a@np.array([.2126,.7152,.0722]);a=a[l<=np.percentile(l,8)]
 return rgbhex(np.median(a,axis=0))
def component(path,x,y,size,color,ident):
 root=ET.parse(path).getroot();parts=[]
 for child in list(root):
  if child.tag in [f'{{{NS}}}title',f'{{{NS}}}desc']:continue
  el=copy.deepcopy(child)
  for node in el.iter():
   for k in ['fill','stroke','color']:
    if node.attrib.get(k) in ['#000000','#163c36','black']:node.set(k,color)
   if 'id' in node.attrib:node.set('id',ident+'-'+node.attrib['id'])
  parts.append(ET.tostring(el,encoding='unicode'))
 return f'<g id="{ident}" transform="translate({x} {y}) scale({size/1000})">'+''.join(parts)+'</g>'
def rect(box,fill,stroke,radius,ident):
 x,y,w,h=box;return f'<rect id="{ident}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="3.6"/>'

records=[]
for c in CASES:
 source=ROOT/'variant_research/handbooks'/c['file'];im=np.array(Image.open(source).convert('RGB'));m=cv2.getPerspectiveTransform(np.float32(c['corners']),np.float32([(0,0),(1000,0),(1000,1400),(0,1400)]));ref=cv2.warpPerspective(im,m,(1000,1400),flags=cv2.INTER_CUBIC,borderValue=(255,255,255));Image.fromarray(ref).save(OUT/(c['slug']+'_source_rectified.png'))
 palette={k:colour(ref,box,k in ['ink','accent']) for k,box in c['palette_boxes'].items()}
 # Preserve observed pale emblem tint, independently of the main text colour.
 bg,panel,ink,accent=[palette[k] for k in ['ground','panel','ink','accent']]
 body=[f'<rect id="cover-ground" width="1000" height="1400" fill="{bg}"/>',rect(c['header'],panel,ink,c['radius'],'header-panel'),rect(c['art'],panel,ink,c['radius'],'illustration-panel'),rect(c['footer'],panel,ink,c['radius'],'footer-panel')]
 for i,(text,x,y,w,h) in enumerate(c['headings']):body.append(f'<g id="heading-line-{i+1}">'+label_group(text,x,y,w,h,ink)+'</g>')
 number,x,y,w,h,tw,th=c['number'];body.append(rect((x,y,w,h),panel,accent,17,'handbook-number-panel'));body.append(label_group(number,x+(w-tw)/2,y+(h-th)/2,tw,th,accent))
 if c['emblem']:
  em,x,y,size=c['emblem'];body.append(component(P/'svg'/f'{em}.svg',x,y,size,accent,'category-emblem'))
 for text,key in [('British Columbia Provincial Museum','museum'),('Victoria','victoria'),('Canada','canada')]:
  x,y,w,h=c[key];body.append(label_group(text,x,y,w,h,ink))
 x,y,size=c['bcpm'];body.append(component(ROOT/'output/package/svg/04_BC_Provincial_Museum.svg',x,y,size,accent,'bcpm-monogram'))
 svg=f'<svg xmlns="{NS}" width="1000" height="1400" viewBox="0 0 1000 1400"><title>{c["title"]} — reusable branding-panel template</title><desc>Historical branding-panel reconstruction preserving cover hierarchy. Illustration field intentionally open. Fixed title and museum lettering are outlined from the closest inspected modern Helvetica43ExtendedLight specimen; exact historical typeface and calibrated colours are unconfirmed. No raster images or fonts embedded.</desc>'+''.join(body)+'</svg>'
 (OUT/f'{c["slug"]}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/f'{c["slug"]}.png'))
 # Keep crops that show the actual original header/footer branding separately.
 for name,box in [('header',c['header']),('footer',c['footer'])]:
  x,y,w,h=box;Image.fromarray(ref).crop((max(0,x-8),max(0,y-8),min(1000,x+w+8),min(1400,y+h+8))).save(OUT/f'{c["slug"]}_source_{name}.png')
 rec={'slug':c['slug'],'title':c['title'],'svg':f'{c["slug"]}.svg','png':f'{c["slug"]}.png','canvas':[1000,1400],'source_file':c['file'],'source_url':c['source_url'],'source_front_plane_corners':c['corners'],'source_registration':'Four-corner perspective rectification to a standardized1000×1400front plane. Physical cover dimensions are not established.','panel_rectangles':{k:c[k] for k in ['header','art','footer']},'palette':palette,'palette_status':'Approximate colour medians/dark-ink samples from uncalibrated photographs; not official ink specifications.','category_emblem':c['emblem'][0] if c['emblem'] else None,'bcpm_in_source':True,'type_status':'Closest inspected modern Neue Helvetica Pro43ExtendedLight comparison; exact historical typeface unconfirmed.','status':'Reusable branding-panel template, not a complete cover facsimile. Illustration panel intentionally open; author lines omitted; visible bird-volume description included.','notes':'Dragonflies source retains the BCPM monogram but does not show a category emblem.' if c['slug']=='Dragonflies_35' else 'Panel hierarchy and emblem placement follow the photographed cover.'}
 records.append(rec)

(OUT/'manifest.json').write_text(json.dumps({'title':'Four handbook branding-panel templates','templates':records},indent=2))

# Sources and vector templates side by side, with editorial labels outside art.
W,H=2000,1710;sheet=Image.new('RGB',(W,H),'#f4f1e8');d=ImageDraw.Draw(sheet);ff='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
d.text((35,24),'Museum handbook branding-panel templates',font=ImageFont.truetype(fb,40),fill='#163c36')
d.text((35,81),'Photographed cover at left; reusable vector branding at right. Illustration fields are intentionally open.',font=ImageFont.truetype(ff,23),fill='#52675e')
for i,r in enumerate(records):
 gx=35+(i%2)*990;gy=135+(i//2)*785;d.text((gx,gy),r['title'],font=ImageFont.truetype(fb,25),fill='#163c36')
 for j,(label,name) in enumerate([('Source photograph',r['slug']+'_source_rectified.png'),('Branding-panel template',r['slug']+'.png')]):
  x=gx+j*470;d.text((x,gy+42),label,font=ImageFont.truetype(ff,21),fill='#52675e');pic=Image.open(OUT/name).convert('RGB').resize((440,616),Image.Resampling.LANCZOS);sheet.paste(pic,(x,gy+76))
 d.text((gx,gy+710),'Approximate colour / outlined comparison type / no reproduced illustration',font=ImageFont.truetype(ff,17),fill='#52675e')
sheet.save(OUT/'Handbook_Branding_Templates_Review.png')

# A clean four-template overview.
ov=Image.new('RGB',(2160,905),'#f4f1e8');dd=ImageDraw.Draw(ov);dd.text((30,20),'Reusable handbook branding panels',font=ImageFont.truetype(fb,36),fill='#163c36')
for i,r in enumerate(records):
 x=30+i*535;pic=Image.open(OUT/r['png']).resize((505,707),Image.Resampling.LANCZOS);ov.paste(pic,(x,85));dd.text((x,811),r['title'].split('/')[0].strip(),font=ImageFont.truetype(ff,20),fill='#163c36');dd.text((x,846),'Illustration field intentionally open',font=ImageFont.truetype(ff,17),fill='#52675e')
ov.save(OUT/'Handbook_Branding_Templates_Overview.png')
for r in records:
 tree=ET.parse(OUT/r['svg']);assert not tree.findall(f'.//{{{NS}}}text');assert not tree.findall(f'.//{{{NS}}}image')
print(json.dumps({'templates':len(records),'palettes':[{'slug':r['slug'],'palette':r['palette']} for r in records]},indent=2))
