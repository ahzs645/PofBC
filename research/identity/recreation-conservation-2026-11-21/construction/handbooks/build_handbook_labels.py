"""Fixed museum-bar wording using the closest inspected Helvetica43 specimen.

The exact historical handbook typeface is not established. This reconstructs
fixed title and identity labels from an official public modern comparison specimen.
"""
from pathlib import Path
import ast,json,urllib.request,urllib.parse,concurrent.futures,io
from PIL import Image
import numpy as np
from skimage.measure import find_contours
import cairosvg
P=Path(__file__).resolve().parent;(P/'label_specimens').mkdir(exist_ok=True);(P/'labels').mkdir(exist_ok=True)
source=P.parent/'type/reconstruct_outlines.py';tree=ast.parse(source.read_text());nodes=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in node.targets):break
 nodes.append(node)
ns={'__file__':str(source)};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns);ns['UNIT']=1.
jobs=[('Museum_Name','British Columbia Provincial Museum',128),('Victoria','Victoria',256),('Canada','Canada',256),
 ('Guide_to_Common','Guide to Common',256),('Edible_Plants','Edible Plants',256),('of_British_Columbia','of British Columbia',256),
 ('Some_Common','Some Common',256),('Marine_Fishes','Marine Fishes',256),('The_Birds','The Birds',256),('The_Dragonflies','The Dragonflies',256),
 ('Number_20','20',256),('Number_23','23',256),('Number_29','29',256),('Number_35','35',256),
 ('The_Fresh_water','The Fresh-water',256),('Fishes','Fishes',256),
 ('Birds_1','1) The Woodpeckers',128),('Birds_2','2) The Crows and Their Allies',96),
 ('The_Barnacles','The Barnacles',256),('Birds_3','3) The Shorebirds',128),('Birds_4','4) Upland Game Birds',128),
 ('The_Ferns','The Ferns',256),('and_Fern_allies','and Fern-allies',256),
 ('Birds_5','5) Gulls, Terns, Jaegers and Skua',96),('Birds_6','6) Waterfowl',256),
 ('The_Orchids','The Orchids',256),('The_Intertidal','The Intertidal',256),('Bivalves','Bivalves',256),
 ('Guide_to','Guide to',256),('Marine_Life','Marine Life',256),
 ('Birds_8a','8) Chickadees, Thrushes, Kinglets,',96),('Birds_8b','Pipits, Waxwings and Shrikes',96),
 ('Mushrooms','Mushrooms',256),('Univalves','Univalves',256),('Some_Mosses','Some Mosses',256),
 ('Birds_9','9) Diving Birds and Tube-nosed Swimmers',96),
 ('The_Pea_Family','The Pea Family',256),('The_Figwort','The Figwort',256),('Family','Family',256),
 ('Food_Plants_of','Food Plants of',256),('British_Columbia_Indians','British Columbia Indians',128),
 ('Part_2_Interior_Peoples','Part 2/Interior Peoples',128),
 ('Birds_10','(10) Goatsuckers, Swifts, Hummingbirds and Swallows',64),
] + [(f'Number_{n}',str(n),256) for n in [5,6,7,8,10,12,13,15,16,17,21,22,24,26,28,32,33,36,37]]
def fetch(j):
 slug,text,size=j;url='https://sig.monotype.com/render/105/font/712562891968727505019b3ba8d08e3a?'+urllib.parse.urlencode({'rt':text,'rs':size,'w':4000,'fg':'000000','bg':'FFFFFF'});dest=P/'label_specimens'/f'{slug}.png'
 if not dest.exists():
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.myfonts.com/'})
  with urllib.request.urlopen(req,timeout=30) as r:dest.write_bytes(r.read())
 return {'slug':slug,'text':text,'size':size,'url':url,'path':str(dest)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:items=list(ex.map(fetch,jobs))
for item in items:
 a=np.array(Image.open(item['path']).convert('L'));mask=a<128;yy,xx=np.where(mask);x0,y0,x1,y1=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
 # Preserve a 3-pixel exterior margin for closed outer contours.
 crop=a[max(0,y0-3):y1+3,max(0,x0-3):x1+3];paths=[];nl=nc=0
 for c in find_contours(1-crop/255.,.5,fully_connected='high',positive_orientation='high'):
  if len(c)<4:continue
  pts=np.column_stack([c[:,1]+.5,c[:,0]+.5]);p,l,b=ns['build_path'](pts);paths.append(p);nl+=l;nc+=b
 h,w=crop.shape
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{item["text"]}</title><desc>Fixed-wording outline reconstruction from public Neue Helvetica Pro43ExtendedLight specimen. Closest inspected comparison; exact historical handbook typeface unconfirmed.</desc><path fill="#163c36" fill-rule="evenodd" d="{" ".join(paths)}"/></svg>'
 (P/'labels'/f'{item["slug"]}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(P/'labels'/f'{item["slug"]}.png'))
 item.update({'ink_bbox':[x0,y0,x1,y1],'svg':f'labels/{item["slug"]}.svg','line_segments':nl,'cubic_segments':nc,'status':'Closest inspected modern comparison; exact historical handbook typeface unconfirmed.'})
(P/'label_sources.json').write_text(json.dumps(items,indent=2));print(json.dumps({'fixed_labels':len(items),'status':'All outlined labels built.'}))
