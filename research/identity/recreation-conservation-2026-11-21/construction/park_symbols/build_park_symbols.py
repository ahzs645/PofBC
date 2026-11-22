"""Geometric reconstruction of the22 proposed park signs,1971 report PDF68.

All artwork is deliberately authored from primitives and cubic paths. The scan
is used as a visual dimension reference, not passed to a contour tracer.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cairosvg,cv2

P=Path(__file__).resolve().parent
for folder in ['svg','png','overlays']:(P/folder).mkdir(exist_ok=True)
INK='#000000'
def path(d,fill=INK,stroke=None,sw=1,extra=''):
 return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+f' {extra}/>'
def line(d,w=4):return path(d,'none',INK,w)
def circle(x,y,r,fill=INK,stroke=None,sw=1):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def rect(x,y,w,h,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{INK}"/>'
def poly(points):return path('M'+' L'.join(f'{x} {y}' for x,y in points)+'Z')
def group(s,t):return f'<g transform="{t}">{s}</g>'
def ellipsepath(cx,cy,rx,ry):return f'M {cx-rx} {cy} a {rx} {ry} 0 1 0 {2*rx} 0 a {rx} {ry} 0 1 0 {-2*rx} 0 Z'
def ring():return circle(100,100,95,'none',INK,10)
EVEN='fill-rule="evenodd"'

def trailer(x=0,y=0,scale=1):
 body=path('M58 107 V82 Q58 58 83 58 H123 Q148 58 148 82 V109 H157 V115 H56 V107Z M112 78 H137 V91 H112Z',extra=EVEN)
 body+=circle(94,116,11)+line('M156 114 H177',4)
 return group(body,f'translate({x} {y}) scale({scale})')
def boat(x=0,y=0,scale=1,tilt=0):
 body=path('M28 73 L157 73 L154 94 H62 Q43 91 28 73Z')+line('M58 72 L62 61',3)
 body+=line('M29 101 H158',4)+circle(100,103,7,'none',INK,4)
 return group(body,f'translate({x} {y}) rotate({tilt} 100 90) scale({scale})')
def pletter():
 return path('M54 49 H111 C144 49 153 64 153 81 C153 101 140 112 111 112 H93 V145 H108 V157 H54 V145 H65 V61 H54Z M93 63 V99 H109 C126 99 129 89 129 81 C129 70 123 63 109 63Z',extra=EVEN)

art={}
art['fire_wood']=line('M89 79 L153 43',11)+path('M90 51 L54 72 C73 78 78 87 82 104 L79 111 L103 112 L116 102 L99 92 L91 78 Z')+path('M58 108 Q88 105 119 109 V165 H58Z')
art['water']=line('M78 53 L82 147 Q103 150 123 147 L130 53',6)+line('M81 73 Q85 65 90 73 Q94 65 99 73 Q104 65 109 73 Q114 65 119 73 Q124 65 128 73',5)
art['change_house']=line('M78 58 C79 39 106 37 113 52 C119 68 111 77 100 77 V95',4.5)+path('M23 124 Q96 59 170 123 Q179 129 175 135 Q102 87 28 132 Q20 135 23 124Z')
art['picnicking']=rect(51,64,87,11)+poly([(74,74),(91,74),(61,140),(44,140)])+poly([(104,74),(120,74),(149,141),(133,141)])+line('M34 100 L153 104',5)
art['amphitheatre']=line('M28 77 Q100 30 173 78',8)+line('M44 94 Q100 62 151 94',6)+line('M56 110 Q99 91 141 114',5)+rect(80,137,44,25,3)
art['tenting']=path('M45 137 L98 41 L149 137 Z M74 137 L98 99 L121 137Z',extra=EVEN)+line('M90 27 L104 56 M108 27 L94 56',3)+line('M34 139 H164',3)
camping_tent=path('M25 100 L71 25 L117 104 H90 L74 81 L65 102Z')+line('M64 18 L77 40 M78 19 L66 40',3)
art['camping']=group(camping_tent,'translate(0 15) scale(1 .85)')+group(trailer(), 'translate(25 45) scale(.80)')
art['boat_launch']=boat(0,7,1,7)+poly([(29,112),(173,132),(173,136),(29,136)])
art['sani_station']=path('M9 129 H191 C179 169 145 195 100 195 C54 195 21 169 9 129Z M56 135 H86 V171 H56Z',extra=EVEN)+trailer()+line('M72 115 V153',4)+poly([(64,153),(80,153),(72,173)])
female='M63 78 H77 L84 109 H78 L80 124 H73 V145 H67 V124 H61 L63 109 H57Z'
male='M127 78 H146 V113 H141 V145 H136 V112 H133 V145 H128 V89 H125 V111 H121 V81Z'
art['toilets']=path('M42 48 L92 37 V156 H42Z '+ellipsepath(68,64,6,6)+' '+female,extra=EVEN)+path('M111 38 L161 51 V158 H111Z '+ellipsepath(135,64,6,6)+' '+male,extra=EVEN)
art['parking']=pletter()
art['boat_trailer_parking']=group(pletter(),'translate(36 -9.3) scale(.66 .72)')+boat(0,49,1,0)
art['fishing']=path('M43 111 C78 82 115 83 145 110 C115 139 79 141 43 119 L27 131 L29 117 L26 102Z')+line('M159 45 V91 C159 107 147 111 142 101 L140 89 L147 98',3)
nature_dashes=line('M87 25 L107 26 M56 37 Q64 32 73 29 M121 33 L135 45 M45 49 L39 63 M144 54 L159 65 M171 76 L177 93 M37 80 L44 96 M176 108 L172 125 M43 109 L45 126 M43 144 L50 159 M64 169 L82 170 M95 169 L110 162 M118 157 L144 151 Q157 149 162 140',6)+poly([(152,139),(164,138),(164,150)])
art['nature_trail']=nature_dashes+circle(88,59,8)+path('M80 71 H92 L92 95 L109 102 Q114 106 109 110 L90 104 L83 119 L65 145 Q60 154 56 149 L58 139 L72 112Z')+poly([(83,112),(91,114),(103,146),(94,147),(79,128)])+poly([(119,103),(148,103),(142,115),(114,115)])+line('M129 115 V142 M125 142 H133',4)
horse=path('M54 94 C68 84 83 87 96 89 C109 90 119 85 129 74 L144 54 L153 50 L151 62 L163 70 Q168 79 155 84 L144 84 L137 98 L131 114 C119 128 94 126 77 122 L67 117 L58 128 L46 132 L49 119 L43 112 Q46 101 54 94Z')
horse+=line('M66 117 L61 150 M79 121 L76 150 M117 119 L108 150 M125 115 L134 150',6)+line('M48 104 L42 124',4)
rider=circle(94,37,8)+path('M89 49 Q95 44 101 50 L105 72 L112 81 L119 84 L116 88 L103 82 L98 67 L97 91 L111 101 L108 117 L102 117 L101 103 L88 96Z')
art['horse_trail']=horse+rider
art['hiking_trail']=circle(87,44,7)+path('M88 58 Q98 54 105 65 L113 87 L112 102 L123 129 L130 150 L124 155 L115 137 L104 120 L95 133 L89 154 L79 153 L84 127 L94 104 L91 83 L79 94 L67 101 Q60 102 61 97 L76 87 L84 67Z')+path('M106 57 L116 53 L123 76 Q125 85 115 88 L109 85Z')+line('M62 98 L98 155',2.5)
art['skiing']=circle(65,72,9)+path('M81 58 Q92 57 105 63 V69 L95 71 V78 C106 81 113 87 113 99 L118 116 L126 122 L140 132 L132 137 L119 131 L108 125 L103 116 L91 86 L85 81 L79 84 L78 75Z')+path('M54 86 L61 85 L63 96 L68 118 L64 124 L61 127 L56 100 L51 89Z')+poly([(57,86),(70,83),(79,80),(85,84),(88,97),(77,97),(72,93),(63,94)])+path('M89 85 L100 105 L106 123 L100 124 L92 111 L87 98Z')+line('M65 122 L130 105 M126 101 L129 110',2)+line('M48 140 Q52 145 57 146 L170 127',2.5)
art['sledding']=circle(154,119,8)+path('M127 105 C138 103 144 110 143 122 L141 134 L128 132 L111 121 L99 114 L78 105 L64 91 L49 60 H40 Q34 57 39 53 H51 Q58 54 61 62 L78 89 L101 92 L107 105Z')+line('M31 104 L123 152 Q131 158 144 151 L150 146 M46 95 L148 142',5)
art['swimming']=circle(151,84,12)+path('M36 108 L100 84 L115 93 L130 105 L163 109 Q166 114 156 117 Q150 113 144 117 Q138 113 132 117 Q126 113 120 117 Q114 113 108 117 Q102 113 96 117 Q90 113 84 117 Q78 113 72 117 Q66 113 60 117 Q54 113 48 117 Q42 112 36 108Z')+poly([(58,77),(57,71),(97,59),(111,71),(138,105),(129,108),(99,74),(93,69)])
art['water_skiing']=circle(64,38,8)+path('M58 51 Q66 47 73 53 L79 78 L63 83 L58 70Z')+line('M70 56 L114 65',8)+line('M114 65 L170 74',2)+path('M72 89 Q80 86 84 94 L92 116 L93 147 H85 L83 119 L69 102 Q66 94 72 89Z')+line('M83 151 Q119 151 139 144 L145 139',4)+line('M44 153 Q49 159 54 153 Q59 159 64 153 Q69 159 74 153 Q79 159 84 153 Q89 159 94 153 Q99 159 104 153 Q109 159 114 153 Q119 159 124 153 Q129 159 134 153 Q139 159 144 153 Q149 159 154 153 Q159 159 164 153',4)
snow_arm=rect(94,27,12,41)+path(ellipsepath(100,28,24,9)+ellipsepath(100,47,19,9)+ellipsepath(100,67,17,8))
art['winter_recreation_area']=''.join(group(snow_arm,f'rotate({a} 100 100)') for a in range(0,360,60))
center=ellipsepath(100,100,35,35)
for a in range(30,390,60):
 rad=math.radians(a);x=100+21*math.sin(rad);y=100-21*math.cos(rad);dx=5.5*math.cos(rad);dy=5.5*math.sin(rad)
 center+=f'M{x-dx} {y-dy} a5.5 11 {a} 1 0 {2*dx} {2*dy} a5.5 11 {a} 1 0 {-2*dx} {-2*dy}Z'
art['winter_recreation_area']+=path(center,extra=EVEN)
art['cross_country_skiing']=circle(117,45,9)+path('M101 55 L113 59 C115 65 112 72 109 77 L106 85 L102 94 L116 104 Q122 108 119 118 L116 135 H106 V117 L97 108 L88 124 L81 142 H70 L74 129 L79 112 L83 98 L88 79 L77 79 L66 88 L57 95 L55 90 L61 78 L72 70 L80 64 L91 59Z')+path('M110 63 Q123 70 145 81 V87 L139 89 L126 83 L112 74Z')+line('M57 94 L30 134 M141 87 L142 152 M27 132 L37 137 M135 147 H150',3)+line('M56 135 L147 137 Q158 135 164 128 M28 143 L116 147 Q123 146 126 141',3.5)

def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)

items=json.loads((P/'sources.json').read_text());metrics=[]
placement_path=P/'placement_refinement.json'
placement=json.loads(placement_path.read_text()) if placement_path.exists() else {}
sheet=Image.new('RGB',(1600,2380),'#f4f1e8');dr=ImageDraw.Draw(sheet)
dr.text((42,30),'PROPOSED PARK SYMBOLS / 1971',font=font(33,True),fill='#163c36')
dr.text((42,78),'Geometric reconstructions of all22 signs on report pageDD67 / PDF68',font=font(22),fill='#52675e')
overlay_sheet=Image.new('RGB',(1600,2470),'white');od=ImageDraw.Draw(overlay_sheet)
od.text((32,22),'Source / reconstruction / overlay',font=font(30,True),fill='black')
od.text((32,66),'Cyan = printed source; pink = vector; dark = overlap. Circles registered by their outer bounds.',font=font(20),fill='#444444')
for i,item in enumerate(items):
 key=item['id'][3:];body=art[key]
 if key in placement:
  v=placement[key]['svg_matrix'];body=group(body,'matrix('+' '.join(f'{x:.7f}' for x in v)+')')
 clip_id='circle_clip_'+item['id']
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 200 200"><title>{escape(item["name"])} — proposed 1971 park sign</title><desc>Geometric reconstruction from BC Department of Recreation and Conservation 1971 annual report, printed DD67, PDF68. No embedded image or live font. Original proposal status retained.</desc><defs><clipPath id="{clip_id}"><circle cx="100" cy="100" r="95"/></clipPath></defs>{ring()}<g clip-path="url(#{clip_id})">{body}</g></svg>'
 (P/'svg'/f'{item["id"]}.svg').write_text(svg)
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(P/'png'/f'{item["id"]}.png'),output_width=600,output_height=600)
 render=Image.open(P/'png'/f'{item["id"]}.png').convert('RGBA');white=Image.new('RGBA',render.size,'white');white.alpha_composite(render);gray=white.convert('L')
 ref=Image.open(P/'sources'/f'{item["id"]}.png').convert('L');a=np.asarray(ref.resize((400,400),Image.Resampling.NEAREST))<128;b=np.asarray(gray.resize((400,400),Image.Resampling.LANCZOS))<128
 yy,xx=np.mgrid[:400,:400];interior=(xx-199.5)**2+(yy-199.5)**2<(176)**2
 def iou(a,b,mask):return float(np.sum(a&b&mask)/max(1,np.sum((a|b)&mask)))
 m={'id':item['id'],'name':item['name'],'whole_ink_iou':iou(a,b,np.ones_like(a)),'interior_ink_iou':iou(a,b,interior),'source_bbox_native_px':item['source_bbox'],'source':'1971 annual report, printedDD67, PDF68','source_native_px':[ref.width,ref.height],'registration':'Independent outer-circle bounding boxes mapped to400square; no localwarp.','construction_refinement':placement.get(key),'note':'Pixel overlap, not a percentage of historical accuracy. Small printed source, scan speckle and regularizedgeometry affect score.'}
 metrics.append(m)
 rgb=np.stack([1-a*.8,1-b*.8,1-np.maximum(a,b)*.25],axis=-1);ov=Image.fromarray(np.uint8(rgb*255));ov.save(P/'overlays'/f'{item["id"]}.png')
 x=(i%4)*400+50;y=(i//4)*370+135;display=white.resize((300,300),Image.Resampling.LANCZOS).convert('RGB');sheet.paste(display,(x,y));dr.text((x,y+310),f'{i+1:02d}  {item["name"]}',font=font(18,True),fill='#163c36')
 ox=(i%4)*400+10;oy=(i//4)*385+115
 od.text((ox,oy),f'{i+1:02d} {item["name"]}',font=font(18,True),fill='black')
 for j,pic in enumerate([ref,gray,ov]):overlay_sheet.paste(pic.resize((120,120),Image.Resampling.NEAREST).convert('RGB'),(ox+j*128,oy+32))
 overlay_sheet.paste(ov.resize((225,225),Image.Resampling.NEAREST),(ox+70,oy+155))
sheet.save(P/'Park_Symbols_1971_Reconstructed.png');overlay_sheet.save(P/'Park_Symbols_1971_Overlay_Review.png')
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps([{'id':m['id'],'whole':round(m['whole_ink_iou'],3),'interior':round(m['interior_ink_iou'],3)} for m in metrics],indent=2))
