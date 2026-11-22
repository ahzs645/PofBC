from pathlib import Path
import sys,json,copy,re,math,html
from lxml import etree
import cairosvg
from PIL import Image,ImageDraw,ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'branding_rebuild';OUT=WORK/'collection';HERE=Path(__file__).parent
sys.path.insert(0,str(WORK/'type'))
from type_engine import text_group,measure_text
NS='http://www.w3.org/2000/svg';XL='http://www.w3.org/1999/xlink'
INK='#3d4539';PAPER='#eeece2';PALE='#999f90';DARK='#0c1c1b';CREAM='#e3e0cb'
FAMILY={
 'department':('01_Department_Recreation_Conservation','Department of Recreation and Conservation'),
 'fishwildlife':('02_Fish_and_Wildlife','Fish and Wildlife Branch'),
 'parks':('03_Provincial_Parks','Provincial Parks Branch'),
 'museum':('04_BC_Provincial_Museum','British Columbia Provincial Museum'),
 'fisheries':('05_Commercial_Fisheries_Marine_Resources','Commercial Fisheries / Marine Resources')}
PAGES={1971:{'general':10,'fishwildlife':16,'parks':64,'museum':98,'fisheries':126},1973:{'general':12,'fishwildlife':22,'parks':78,'museum':112,'fisheries':144}}
SOURCE={1971:'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf',1972:'https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1972.pdf',1973:'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf'}
manifest=[]

def relpath(p):return str(p.relative_to(OUT))
def embed(path,x,y,w,h=None,color=INK,paper=PAPER,prefix='mark'):
 root=etree.fromstring(Path(path).read_bytes());view=[float(a)for a in root.get('viewBox').split()];vx,vy,vw,vh=view
 if h is None:h=w*vh/vw
 ids={e.get('id'):prefix+'-'+e.get('id') for e in root.iter() if e.get('id')}
 for e in root.iter():
  for key,val in list(e.attrib.items()):
   if key=='id':e.set(key,ids[val]);continue
   for old,new in ids.items():
    if val=='#'+old:val='#'+new
    val=val.replace('url(#'+old+')','url(#'+new+')')
   if key in ['fill','stroke'] and val not in ['none','transparent','inherit','currentColor']:
    val=paper if val.lower() in ['#fff','#ffffff','white','#fffdf7'] else color
   e.set(key,val)
 content=''.join(etree.tostring(e,encoding='unicode') for e in root if etree.QName(e).localname not in ['title','desc','metadata'])
 return f'<g transform="translate({x} {y}) scale({w/vw} {h/vh}) translate({-vx} {-vy})">{content}</g>'

def core(key,x,y,size=211,color=INK,paper=PAPER,prefix=None):
 return embed(ROOT/'output/package/svg'/f'{FAMILY[key][0]}.svg',x,y,size,size,color,paper,prefix or key)

def svg(content,w,h,title,metadata=None,bg=None):
 desc=(metadata or {}).get('status','Geometric reconstruction from historical report artwork; not a recovered original vector master.')
 return f'<svg xmlns="{NS}" xmlns:xlink="{XL}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc><metadata>{html.escape(json.dumps(metadata or {},ensure_ascii=False))}</metadata>'+ (f'<rect id="paper" width="{w}" height="{h}" fill="{bg}"/>' if bg else '')+content+'</svg>'

def save(folder,name,content,w,h,title,meta,bg=None):
 p=OUT/folder/f'{name}.svg';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg(content,w,h,title,meta,bg))
 png=OUT/'previews'/folder/f'{name}.png';png.parent.mkdir(parents=True,exist_ok=True)
 cairosvg.svg2png(url=str(p),write_to=str(png),output_width=min(1500,round(w)),output_height=min(1500,round(w))*h/w)
 rec={'id':name,'title':title,'group':folder,'svg':relpath(p),'preview':relpath(png),'width':w,'height':h,**meta};manifest.append(rec);return rec

def type_line(text,x,y,font_size=33.2,tracking=-50,word_space=-220,width=None,color=INK,hscale=1):
 if width:
  b=measure_text(text,font_size,tracking,word_space,hscale)['ink_bbox'];natural=b[2]-b[0]
  # Retain the nominal glyph ratio. Solve tracking to match line width.
  gaps=len(text)-1
  if gaps:tracking+=(width-natural)/(font_size*hscale*gaps)*1000
 return text_group(text,font_size,tracking,word_space,color,hscale,x,y),{'text':text,'x':x,'baseline':y,'font_size':font_size,'tracking_per_1000':tracking,'word_space_extra_per_1000':word_space,'horizontal_scale':hscale,'target_ink_width':width}

def source_meta(year,page,**kwargs):
 return {'source_report':year,'source_pdf_page':page,'source_url':SOURCE[year]+f'#page={page}','status':'Historical reconstruction with outlined type; clean geometry, source scan colour approximation.',**kwargs}

def build_symbols():
 for key,(file,title) in FAMILY.items():
  for variant,c,bg in [('black','#000000',None),('report_green',INK,None),('report_pale',PALE,None),('reverse',CREAM,DARK)]:
   save('symbols',f'{file}_{variant}',core(key,0,0,1000,c,bg or PAPER),1000,1000,title+' / '+variant,source_meta(1971,PAGES[1971][key] if key!='department' else 10,component=key,treatment=variant),bg)

def related_path():
 # The 1973 report uses the completed two-panel lockup, not its narrow icon.
 # Never fall back to a construction SVG with unresolved knockout masks.
 paired=WORK/'related_emblems/07_Fish_Wildlife_Paired_Lockup_1973.svg'
 if paired.exists():return paired
 for p in sorted((WORK/'related_emblems').glob('*.svg')):
  if 'construction' not in p.stem.lower() and 'paired' in p.stem.lower() and 'fish' in p.stem.lower():return p
 return None

def divider(year,key):
 page=PAGES[year][key];parts=[];texts=[];placements=[]
 geometry=json.loads((HERE/'layout_geometry.json').read_text())
 source=next(r for r in geometry if r['year']==year and r['page']==page)
 x0,y0,x1,y1=source['frame_bbox_native'];sx=1000/(x1-x0);sy=1000/(y1-y0)
 def normalized(b):return [(b[0]-x0)*sx,(b[1]-y0)*sy,(b[2]-b[0])*sx,(b[3]-b[1])*sy]
 # Clean rounded rectangles use the median source edge centres. They do not
 # reproduce the scan's tilted sides or the paper's slight trapezoid warp.
 frames={(1971, 10): [7.0, 7.5, 981.5, 983.5],
 (1971, 16): [8.0, 8.0, 980.5, 983.0],
 (1971, 64): [10.0, 10.0, 977.0, 978.0],
 (1971, 98): [9.0, 9.5, 979.0, 978.5],
 (1971, 126): [8.0, 7.5, 980.5, 983.5],
 (1973, 12): [8.5, 8.0, 981.0, 981.5],
 (1973, 22): [7.0, 7.0, 982.5, 983.0],
 (1973, 78): [10.0, 8.0, 977.0, 981.5],
 (1973, 112): [7.0, 7.0, 982.5, 984.0],
 (1973, 144): [9.0, 8.0, 978.0, 982.0]}
 fx,fy,fw,fh=frames[(year,page)]
 parts.append(f'<rect id="outer-frame" x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="43" fill="none" stroke="{INK}" stroke-width="15"/>')
 for i,k in enumerate(['fishwildlife','parks','museum','fisheries','department']):
  nx,ny,nw,nh=normalized(source['marks_native'][i]);color=INK if k in [key,'department'] else PALE
  if year==1973 and k=='fishwildlife':
   new=related_path()
   if new:
    # Production master has a small transparent margin; register its ink,
    # rather than its viewBox, to the measured printed two-panel bounds.
    bx,by,bw,bh=11.282052,11.282052,1149.230765,978.974357
    wx,hy=nw/bw,nh/bh
    parts.append(embed(new,nx-bx*wx,ny-by*hy,1169.230769*wx,1000*hy,color,PAPER,'later-fw'))
   else:raise FileNotFoundError('Final 1973 paired F&W master is required for the divider')
  else:
   mark=ROOT/'output/package/svg'/f'{FAMILY[k][0]}.svg'
   parts.append(embed(mark,nx,ny,nw,nh,color,PAPER,k))
  placements.append({'component':k,'source_bounds_native':source['marks_native'][i],'frame_normalized_bounds':[round(v,4) for v in [nx,ny,nw,nh]]})
 # Each line is fitted to this page's measured position and printed width.
 # Font size scales glyphs uniformly; tracking solves width. No line has
 # been squeezed horizontally to force a match with the scanned lettering.
 line_specs={(1971, 10): [('General Administration', 46, 66.841, 35.0, 443, False, [46, 45, 489, 68]),
              ('Department of Recreation and Conservation', 68, 1027.906, 34.0, 866, False, [68, 1006, 934, 1031])],
 (1971, 16): [('Fish and', 514, 67.841, 35.0, 168, False, [514, 46, 682, 69]),
              ('Wildlife', 514, 96.906, 34.0, 131, False, [514, 75, 645, 100]),
              ('Branch', 514, 125.593, 33.0, 137, False, [514, 105, 651, 127]),
              ('Department of Recreation and Conservation', 69, 1027.906, 34.0, 865, False, [69, 1005, 934, 1031])],
 (1971, 64): [('Provincial', 514, 301.905, 33.5, 185, False, [514, 280, 699, 303]),
              ('Parks', 513, 329.905, 33.5, 111, False, [513, 308, 624, 330]),
              ('Branch', 513, 358.217, 34.0, 136, False, [513, 337, 649, 359]),
              ('Department of Recreation and Conservation', 68, 1024.906, 34.0, 862, False, [68, 1002, 930, 1028])],
 (1971, 98): [('British', 511, 536.841, 35.0, 124, False, [511, 515, 635, 537]),
              ('Columbia', 511, 564.841, 35.0, 174, False, [511, 543, 685, 566]),
              ('Provincial', 511, 593.529, 34.5, 186, False, [511, 572, 697, 594]),
              ('Museum', 511, 622.905, 33.5, 167, False, [511, 601, 678, 624]),
              ('Department of Recreation and Conservation', 69, 1025.906, 34.0, 863, False, [69, 1003, 932, 1029])],
 (1971, 126): [('Commercial', 508, 767.657, 31.5, 216, False, [508, 747, 724, 769]),
               ('Fisheries', 509, 797.153, 35.5, 173, False, [509, 775, 682, 797]),
               ('Branch', 509, 826.841, 35.0, 138, False, [509, 805, 647, 828]),
               ('Department of Recreation and Conservation', 69, 1028.555, 33.5, 865, False, [69, 1006, 934, 1032])],
 (1973, 12): [('General Administration', 46, 68.841, 35.0, 443, False, [46, 47, 489, 70]),
              ('Department of Recreation and Conservation', 70, 1026.906, 34.0, 867, False, [70, 1005, 937, 1032])],
 (1973, 22): [('Department of Recreation and Conservation', 68, 1027.906, 34.0, 867, False, [68, 1006, 935, 1032])],
 (1973, 78): [('Provincial', 512, 304.529, 34.5, 185, False, [512, 282, 697, 305]),
              ('Parks', 512, 332.841, 35.0, 109, False, [512, 311, 621, 333]),
              ('Branch', 511, 360.841, 35.0, 137, False, [511, 339, 648, 361]),
              ('Department of Recreation and Conservation', 68, 1026.555, 33.5, 862, False, [68, 1003, 930, 1029])],
 (1973, 112): [('British', 514, 537.841, 35.0, 123, False, [514, 516, 637, 538]),
               ('Columbia', 514, 566.841, 35.0, 173, False, [514, 545, 687, 567]),
               ('Provincial', 514, 595.529, 34.5, 185, False, [514, 574, 699, 596]),
               ('Museum', 514, 624.593, 33.0, 166, False, [514, 604, 680, 625]),
               ('Department of Recreation and Conservation', 69, 1027.906, 34.0, 866, False, [69, 1006, 935, 1032])],
 (1973, 144): [('marine', 505, 768.875, 32.0, 131, False, [505, 747, 636, 770]),
               ('Resources', 504, 797.593, 33.0, 208, True, [504, 778, 712, 798]),
               ('Branch', 504, 824.593, 33.0, 135, True, [504, 804, 639, 828]),
               ('[Commercial Fisheries]', 295, 855.258, 34.5, 421, False, [295, 829, 716, 863]),
               ('Department of Recreation and Conservation', 68, 1027.906, 34.0, 863, False, [68, 1005, 931, 1030])]}
 for text,x,baseline,fs,width,smallcap,bbox in line_specs[(year,page)]:
  delta=0;initial_scale=1
  if smallcap:
   # The marine heading has R/B forms at approximately the x-height.
   # This is a visible-letter reconstruction, not a claim about original case.
   from type_engine import data as glyph_data
   initial_scale=544.921875/624.023438
   delta=glyph_data()['glyphs'][text[0]]['advance']*fs/1000*(1-initial_scale)
  g,m=type_line(text,x,baseline,font_size=fs,tracking=-50,word_space=-250,width=width+delta)
  if smallcap:
   group=etree.fromstring(g.encode())
   for i,path in enumerate(group):
    offset=float(path.get('transform').split('(')[1].split()[0])
    path.set('transform',f'translate({offset} 0) scale({initial_scale} {initial_scale})' if i==0 else f'translate({offset-delta*1000/fs} 0)')
   g=etree.tostring(group,encoding='unicode')
   m.update({'initial_capital_scale':initial_scale,'letter_case_note':'Reduced initial capital reconstructed from the source shape; original typesetting case is not established.'})
  if text=='[Commercial Fisheries]':
   # The printed brackets are taller than the adjacent lettering, and their
   # top edges are staggered. Fit those visible shapes independently.
   group=etree.fromstring(g.encode());bracket_fits=[]
   for path in group:
    ch=path.get('data-character')
    if ch not in ['[',']']:continue
    top,bottom=(825,861) if ch=='[' else (829,863)
    unit_top,unit_bottom=-703.125,79.101562
    scale_y=(bottom-top)/((unit_bottom-unit_top)*fs/1000)
    shift_y=(top-baseline)/(fs/1000)-unit_top*scale_y
    path.set('transform',path.get('transform')+f' translate(0 {shift_y}) scale(1 {scale_y})')
    bracket_fits.append({'character':ch,'top':top,'bottom':bottom,'vertical_scale':scale_y})
   g=etree.tostring(group,encoding='unicode');m['bracket_shape_fits']=bracket_fits
  m.update({'target_ink_width':width,'source_ink_bbox_frame_normalized':bbox,'fit_method':'Uniform glyph size and page-specific baseline; tracking fitted to measured printed width. Marine brackets have their own source-height fit.' if text=='[Commercial Fisheries]' else 'Uniform glyph size and page-specific baseline; tracking fitted to measured printed width.'})
  parts.append(g);texts.append(m)
 branch_title=('General Administration' if key=='general' else 'Commercial Fisheries Branch' if key=='fisheries' and year==1971 else 'Marine Resources Branch' if key=='fisheries' else FAMILY[key][1])
 title=f'{year} / '+branch_title+' divider'
 note=('1971 design also appears in the 1972 report. Selected branch is dark; others are pale.' if year==1971 else 'Later paired F&W symbol on interior divider; old square retained on back cover.')
 if year==1973 and key=='fisheries':note+=' Marine heading letter case and reduced R/B forms are source-based approximations.'
 return save('report_dividers',f'{year}_{key}_divider',''.join(parts),1000,1045,title,
  source_meta(year,page,typography=texts,placements=placements,layout_note=note,
   registration_note='Measured native emblem bounds normalized against the full source frame. Clean frame uses median straight-edge positions; scan skew and local paper distortion are omitted.'),PAPER)

def branch_lockups():
 # Extract the historically positioned department / branch relationship as
 # a reusable lower-band combination, including both fisheries name forms.
 for key in ['fishwildlife','parks','museum','fisheries','marine']:
  parts=[core('department',20,20,235)];texts=[]
  mark='fisheries' if key=='marine' else key
  parts.append(core(mark,745,20,235))
  lines={
   'fishwildlife':['Fish and','Wildlife','Branch'],
   'parks':['Provincial','Parks','Branch'],
   'museum':['British','Columbia','Provincial','Museum'],
   'fisheries':['Commercial','Fisheries','Branch'],
   'marine':['marine','Resources','Branch','[Commercial Fisheries]']}[key]
  fs=33.2;lineh=29;y=58
  for i,s in enumerate(lines):
   x=505 if s=='[Commercial Fisheries]' else 510
   parts.append(text_group(s,fs,-50,-220,INK,1,x,y+i*lineh,anchor='middle' if s=='[Commercial Fisheries]' else 'start'))
  parts.append(f'<path id="lower-frame" d="M7.5 0V250Q7.5 292.5 50 292.5H950Q992.5 292.5 992.5 250V0" fill="none" stroke="{INK}" stroke-width="15"/>')
  g,m=type_line('Department of Recreation and Conservation',68,328,32.6,-22,-300,width=865,hscale=.97);parts.append(g)
  year=1973 if key=='marine' else 1971;pg=PAGES[year]['fisheries' if key=='marine' else key]
  save('branch_lockups',f'{key}_department_lockup',''.join(parts),1000,345,('Marine Resources Branch' if key=='marine' else 'Commercial Fisheries Branch' if key=='fisheries' else FAMILY[key][1])+' / departmental band',source_meta(year,pg,layout_note='Reusable reconstruction of the paired department/branch arrangement; condensed from the full divider, not an additional historical specimen.'),PAPER)

def stacks():
 for version,ink,bg,year in [('reverse',CREAM,DARK,1971),('positive',INK,PAPER,1973)]:
  parts=[]
  for i,k in enumerate(['fishwildlife','parks','museum','fisheries']):parts.append(core(k,20,20+i*237,210,ink,bg))
  parts.append(core('department',20,968,362,ink,bg))
  save('cover_stacks',f'family_vertical_stack_{version}',''.join(parts),420,1400,'Vertical family stack / '+version,source_meta(year,139 if year==1971 else 162,layout_note='Original deer/fish square is retained even on the1973 back cover.'),bg)

def covers():
 arms=WORK/'reused_arms/BC_Arms_1960_Museum_Refined.svg'
 for year in [1971,1972,1973]:
  ink,bg=(CREAM,DARK) if year<1973 else (INK,PAPER)
  parts=[text_group('Province of British Columbia',42,-45,-220,ink,1,30,50)]
  parts.append(embed(arms,20,70,130,116,ink,bg,'period-arms'))
  parts.append(core('department',30,200,105,ink,bg))
  specs=[('Department of',30,350,45,-45,-250,355),('Recreation and Conservation',30,386,45,-45,-250,742),(f'Annual Report {year}',30,448,64,-40,-220,743 if year==1971 else 775)]
  for s,x,y,fs,tr,ws,w in specs:
   g,m=type_line(s,x,y,fs,tr,ws,w,ink);parts.append(g)
  save('cover_headers',f'{year}_annual_report_header',''.join(parts),820,480,f'Annual Report {year} cover branding',source_meta(year,1,arms_note='Period coat of arms reuses the refined1960 Museum engraving reconstruction; it is not claimed to be the exact engraving master on this cover.',layout_note='Recreated branding block only. Cover photograph and library markings are outside this vector artwork.'),bg)

def build():
 OUT.mkdir(exist_ok=True)
 build_symbols()
 for year in [1971,1973]:
  for key in PAGES[year]:divider(year,key)
 branch_lockups();stacks();covers()
 (OUT/'manifest.json').write_text(json.dumps({'title':'BC Recreation and Conservation branding reconstruction','status':'Documented historical applications reconstructed as editable vectors','assets':manifest},indent=2))
 print(json.dumps({'assets':len(manifest),'later_fw_ready':bool(related_path()),'manifest':str(OUT/'manifest.json')},indent=2))
if __name__=='__main__':build()
