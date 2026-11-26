from pathlib import Path
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from html import escape
import math, json, re, os
BASE=Path(__file__).resolve().parents[1]; SVG=BASE/'svg'; COMPONENTS=BASE/'components'; SVG.mkdir(exist_ok=True); COMPONENTS.mkdir(exist_ok=True)
URW='/usr/share/fonts/opentype/urw-base35/'; NOTO='/usr/share/fonts/truetype/noto/'
F={'serif':URW+'NimbusRoman-Regular.otf','serif-bold':URW+'NimbusRoman-Bold.otf','serif-italic':URW+'NimbusRoman-Italic.otf','serif-bi':URW+'NimbusRoman-BoldItalic.otf','sign':NOTO+'NotoSerif-Regular.ttf','sans':URW+'NimbusSans-Regular.otf','sans-bold':URW+'NimbusSans-Bold.otf','sans-italic':URW+'NimbusSans-Italic.otf','sans-bi':URW+'NimbusSans-BoldItalic.otf','narrow':URW+'NimbusSansNarrow-Regular.otf','narrow-bold':URW+'NimbusSansNarrow-Bold.otf','narrow-italic':URW+'NimbusSansNarrow-Oblique.otf','script':'/usr/share/fonts/opentype/lobstertwo/LobsterTwo-BoldItalic.otf','heavy':NOTO+'NotoSansDisplay-ExtraCondensedBlack.ttf','mono':URW+'NimbusMonoPS-Regular.otf'}
# Font paths are external dependencies, never distributed. Override FONT_DIRS by editing F if needed.
@lru_cache(None)
def font(k):
 t=TTFont(F[k]);return t,t.getGlyphSet(),t.getBestCmap(),t['hmtx'].metrics,t['head'].unitsPerEm
@lru_cache(None)
def glyph(k,ch):
 t,gs,cm,hm,up=font(k); name=cm.get(ord(ch),cm.get(63)); p=SVGPathPen(gs); b=BoundsPen(gs); gs[name].draw(p);gs[name].draw(b);return p.getCommands(),b.bounds,hm[name][0]
@lru_cache(None)
def run(k,s):
 x=0; out=[]; bounds=[]
 for ch in s:
  d,b,a=glyph(k,ch)
  if d:out.append((x,d));bounds.append((x+b[0],b[1],x+b[2],b[3]))
  x+=a
 if not bounds:return out,(0,0,max(x,1),1),x
 return out,(min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)),x

def fmt(n):return f'{n:.4f}'.rstrip('0').rstrip('.') or '0'
def path(d,fill='#171717',stroke=None,sw=1):return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else '')+'/>'
def rect(x,y,w,h,fill='none',stroke=None,sw=1,rx=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def ell(cx,cy,rx,ry,fill='none',stroke=None,sw=1):return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def line(x1,y1,x2,y2,sw=1,color='#171717'):return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{sw}"/>'
def group(a,transform='',label=''):return f'<g'+(f' transform="{transform}"' if transform else '')+(f' aria-label="{escape(label,quote=True)}"' if label else '')+'>'+''.join(a)+'</g>'
def fit(s,k,x,y,w,h,fill='#171717',rotate=None):
 out,b,adv=run(k,s);sx=w/max(b[2]-b[0],1);sy=h/max(b[3]-b[1],1)
 ss=group([f'<path d="{d}" transform="translate({fmt(o)} 0)"/>' for o,d in out],f'translate({fmt(x-sx*b[0])} {fmt(y+sy*b[3])}) scale({fmt(sx)} {fmt(-sy)})',s)
 return f'<g fill="{fill}"'+(f' transform="{rotate}"' if rotate else '')+'>'+ss+'</g>'
def text(s,k,x,y,size,maxw=None,align='left',fill='#171717'):
 # y is top of actual glyph ink. Natural font proportions except maximum-width constraint.
 _,b,_=run(k,s); up=font(k)[4];sc=size/up; w=(b[2]-b[0])*sc;h=(b[3]-b[1])*sc
 if maxw and w>maxw:w=maxw
 if align=='center':x-=w/2
 elif align=='right':x-=w
 return fit(s,k,x,y,max(w,.01),max(h,.01),fill)
def width(s,k,size):return run(k,s)[2]*size/font(k)[4]
def wrap(s,k,size,maxw):
 result=[]
 for para in s.split('\n'):
  a=''
  for word in para.split():
   c=(a+' '+word).strip()
   if a and width(c,k,size)>maxw:result.append(a);a=word
   else:a=c
  result.append(a)
 return result

def multiline(lines,k,x,y,size,leading,maxw,align='left',fill='#171717'):
 if isinstance(lines,str):lines=wrap(lines,k,size,maxw)
 return ''.join(text(s,k,x,y+i*leading,size,maxw,align,fill) for i,s in enumerate(lines) if s)
def document(name,w,h,body,desc,folder=SVG):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(name)}</title><desc>{escape(desc)}</desc>'+''.join(body)+'</svg>'
 (folder/(name+'.svg')).write_text(s);return s
# All artwork is original manually authored primitive/Bezier construction. No raster embedding, contour tracing or auto-vectorizer.
INK='#202020'
def paw():
 return group([path('M 5 156 C 3 119 18 93 46 72 C 59 59 69 41 89 40 C 107 39 123 52 127 66 C 146 66 158 76 163 92 C 183 91 194 103 196 123 C 216 130 222 148 212 163 C 207 171 192 173 191 188 C 189 208 174 225 156 224 C 134 223 113 212 95 202 C 73 190 51 191 31 184 C 15 178 5 170 5 156 Z',INK),path('M104 24 Q127 3 155 0 Q132 14 121 32 Q114 26 104 24 Z',INK),path('M159 44 Q177 29 189 14 Q186 38 165 60 Q165 49 159 44 Z',INK),path('M183 77 Q202 61 214 46 Q208 73 190 89 Q190 82 183 77 Z',INK),path('M203 107 Q222 92 234 76 Q229 100 210 120 Q210 112 203 107 Z',INK),path('M219 137 Q235 125 248 109 Q244 133 226 148 Q226 141 219 137 Z',INK)],label='Bear paw and five claws')
def walking_bear():
 return group([path('M 7 60 C 3 45 7 29 17 18 C 27 7 42 5 56 8 C 69 0 80 4 85 11 C 90 7 94 8 97 12 C 101 16 100 21 99 25 C 103 31 101 38 98 43 L 104 58 Q 108 64 106 70 Q 99 74 94 68 L 87 58 Q 82 61 81 72 L 88 79 Q 91 83 83 84 L 69 83 Q 64 81 65 72 L 61 59 Q 52 64 41 62 L 32 70 L 35 78 Q 35 82 28 82 L 15 80 Q 11 78 13 72 L 15 62 Q 11 67 7 60 Z'),path('M82 18 Q89 13 93 19 Q89 20 88 24 Q83 24 82 18Z','#fff'),ell(92,29,2,2,'#fff'),path('M 98 42 Q 93 45 90 43 L 87 37 Q 93 39 98 42Z','#fff'),path('M 21 27 Q 28 21 33 23 L 27 29 Z','#fff')],label='Walking bear emblem')
def tree(x,y,w,h):
 return path(f'M{x} {y} l{-w*.17} {h*.23} l{w*.10} 0 l{-w*.22} {h*.24} l{w*.13} 0 l{-w*.31} {h*.25} l{w*.31} 0 l{-w*.34} {h*.19} l{w*.40} 0 v{h*.09} h{w*.20} v{-h*.09} h{w*.40} l{-w*.34} {-h*.19} h{w*.31} l{-w*.31} {-h*.25} h{w*.13} l{-w*.22} {-h*.24} h{w*.10} Z')
def crest():
 a=[ell(50,50,49,49,'#fff','#171717',1),ell(50,50,41,41,'none','#171717',.8)]
 # Top arc lettering: independently placed outlined glyphs, not sampled contours.
 label='FRIENDS OF MT. REVELSTOKE & GLACIER'; chars=list(label); ws=[width(c,'sans-bold',6.0) for c in chars]; total=sum(ws); ang=math.radians(158); spread=math.radians(316);cum=0
 # Arc runs from left-lower side through top to right-lower side, actual crest lettering occupies upper 230 degrees.
 span=math.radians(222); radius=44; start=-math.pi/2-span/2
 for ch,w in zip(chars,ws):
  theta=start+span*(cum+w/2)/total;cum+=w
  if ch==' ':continue
  x=50+radius*math.cos(theta);y=50+radius*math.sin(theta);deg=math.degrees(theta)+90
  a.append(text(ch,'sans-bold',x,y-2.7,6.1,align='center',fill='#171717').replace('<g fill="#171717">',f'<g fill="#171717" transform="rotate({deg} {x} {y})">',1))
 a += [path('M 11 33 L 26 24 L 36 18 L 44 21 L 52 14 L 63 20 L 75 28 L 89 31 L 88 36 L 77 33 L 63 28 L 56 23 L 48 28 L 37 25 L 23 34 Z','#fff','#171717',.7)]
 for x in range(24,83,3):a.append(line(x,27+(abs(x-51)*.13),x,31+(abs(x-51)*.10),.55))
 a += [path('M10 65 C20 57 28 62 36 61 C45 57 54 61 63 61 C74 58 82 65 90 66 C84 84 69 92 50 93 C30 92 15 81 10 65Z'),tree(20,32,19,35),tree(44,15,26,52),tree(58,34,17,32),tree(75,29,23,40),path('M 12 70 Q 30 62 43 66 Q 53 68 62 67 Q 74 69 87 72 L 86 75 Q 74 73 61 71 Q 46 68 40 69 Q 26 67 14 74 Z','#fff'),path('M47 44 Q51 41 53 46 Q56 51 54 54 Q60 60 56 66 L53 72 L52 81 Q49 85 48 81 L48 71 L45 66 Q42 60 46 55 Q43 50 47 44Z','#fff'),path('M30 77 L36 75 L34 80 Z','#fff'),path('M70 81 l5 1 l-2 2 Z','#fff')]
 return group(a,label='Friends of Mt. Revelstoke & Glacier crest')
def basin_mark():
 # Aspect ratio 100 x 158; ram head and fish cut out at the left edge.
 return group([path('M 22 0 H 100 V 158 L 64 122 L 49 137 L 45 133 L 22 155 Z'),path('M 22 36 C 29 35 32 41 33 43 C 42 47 45 50 46 54 C 46 57 40 59 34 59 Q 29 62 28 70 L 23 65 Q 15 62 14 56 Q 11 48 22 36 Z','#fff'),path('M22 36 C 4 33 0 49 8 57 C 13 63 26 62 28 55 C 30 50 24 46 20 48 C 26 52 21 55 17 54 C 10 50 16 43 22 43 Z'),path('M8 75 Q15 66 28 68 Q36 71 40 75 Q25 74 19 78 L16 83 L15 77 L7 78 L10 74 Z'),path('M3 170 H10 L46 139 L50 143 L65 128 L101 162','none','#171717',2.8)],label='Columbia Basin Fish & Wildlife Compensation Program symbol')
def basin_stacked():
 return group([group([basin_mark()],'translate(11 0) scale(.80)'),fit('Columbia Basin','sans-bold',10,143,80,8),fit('Fish & Wildlife','sans-bold',10,153,80,8),fit('Compensation Program','sans-bold',0,163,100,8)])
def basin_horizontal():
 a=[group([basin_mark()],'translate(0 0) scale(.40)')]
 for i,s in enumerate(['Columbia Basin','Fish & Wildlife','Compensation','Program']):a.append(text(s,'serif-bold',47,4+i*14,14,108))
 return group(a,label='Columbia Basin horizontal signature')
def basin_word():
 return group([fit('Columbia','serif-bold',0,0,80,17),fit('Basin','serif-bold',0,18,46,17),rect(0,42,80,3,'#171717'),fit('Fish & Wildlife','serif',0,50,74,10),fit('COMPENSATION PROGRAM','narrow-bold',0,62,80,7)],label='Columbia Basin wordmark')
def hydro():
 return group([fit('BChydro','heavy',0,0,108,20),rect(119,2,19,16,'#171717',rx=2),path('M128.5 3 V17 M120 10 H137','none','#fff',1),path('M121 13 L126 6 L131 14 L136 7','none','#fff',1.5)],label='BC Hydro historic wordmark')
def env():
 return group([fit('BC','sans-bi',0,0,27,20),path('M30 4 L47 1 L45 15 L28 19 Z'),path('M29 13 L33 9 L37 12 L41 7 L46 5','none','#fff',2.3),fit('Environment','narrow-italic',49,0,128,20)],label='BC Environment flag wordmark')
def pawlock():
 return group([group([paw()],'translate(18 0) scale(.35)'),fit('BE','serif-bold',14,72,23,9),fit('BEAR','serif-bold',16,81,38,10),fit('AWARE','serif-bold',19,91,47,10),path('M0 72 L10 70 L9 76 L0 78Z'),path('M2 74 L8 72','none','#fff',.7)],label='Be Bear Aware paw lockup')
# Standalone reusable components.
for nm,w,h,b in [('bear-paw',250,226,paw()),('walking-bear',110,86,walking_bear()),('friends-mt-revelstoke-glacier',100,100,crest()),('columbia-basin-symbol',104,173,basin_mark()),('columbia-basin-stacked',100,172,basin_stacked()),('columbia-basin-horizontal',160,70,basin_horizontal()),('columbia-basin-wordmark',80,70,basin_word()),('bc-hydro-historic',139,21,hydro()),('bc-environment-historic',178,21,env()),('be-bear-aware-paw-lockup',108,103,pawlock())]:document(nm,w,h,[b],'Manual vector reconstruction from the 1997 campaign scan; not an authenticated original logo.',COMPONENTS)
M=[]
def add(n,w,h,b,source,notes=''):
 document(n,w,h,b,'Historical recreation, '+source+'. '+notes);M.append(dict(file='svg/'+n+'.svg',width=w,height=h,source=source,notes=notes))
# Window sign: typographic reconstruction. A and W are original reusable letter masters
# (contrasting strokes, flared serifs, wedge crossbar and interlocking double-V),
# not a vectorized image contour. E/B/R use font outlines adjusted to the source proportions.
def sign_letter(ch,x,y,w,h):
    # master coordinate system 100 x 100, heavy diagonals balanced by thinner upstrokes
    if ch=='W':
        v='M0 0 H25 Q27 1 25 3 Q16 4 20 13 L37 84 L59 13 Q64 3 53 3 L50 3 L50 0 H75 L75 3 Q67 4 62 16 L35 100 H30 L8 14 Q4 5 0 4 Z'
        # Two interlocking V constructions; second V deliberately shares the first's central stroke.
        return group([path(v,INK),group([path(v,INK)],'translate(33 0)')],f'translate({x} {y}) scale({w/108} {h/100})','W custom letter master')
    if ch=='A':
        return group([f'<path fill="{INK}" fill-rule="evenodd" d="M0 97 Q8 96 15 82 L49 0 L58 0 L91 87 Q95 96 100 97 L100 100 H65 V97 Q79 96 76 87 L68 71 L30 60 L19 84 Q13 97 32 97 V100 H0 Z M32 58 L50 15 L65 58 Z"/>'],f'translate({x} {y}) scale({w/100} {h/100})','A custom letter master')
    if ch=='E':
        return group([path('M0 0 H97 Q94 9 94 23 H90 Q89 6 75 6 H32 Q29 6 29 13 V45 H68 Q81 45 82 32 H86 V64 H82 Q81 51 68 51 H29 V86 Q29 94 37 94 H72 Q89 94 96 76 L100 78 L95 100 H0 V97 Q13 96 13 86 V13 Q13 4 0 3 Z',INK)],f'translate({x} {y}) scale({w/100} {h/100})','E custom letter master')
    return fit(ch,'sign',x,y,w,h,INK)
a=[rect(0,0,764,1000,'#fff'),ell(396,430,344,368,'none',INK,16)]
for ch,x,y,w,h in [('W',231,130,183,93),('E',389,158,77,68),('A',210,240,131,94),('R',338,260,88,69),('E',433,259,77,69),('B',187,347,109,94),('E',291,373,75,68),('A',364,373,94,68),('R',455,373,94,68),('A',204,462,130,94),('W',291,463,128,70),('A',390,462,91,69),('R',471,463,91,69),('E',554,463,85,70)]:a.append(sign_letter(ch,x,y,w,h))
a += [group([paw()],'translate(322 548) scale(.89 .95)'),group([crest()],'translate(47 800) scale(1.55)'),group([basin_stacked()],'translate(624 716) scale(1.31 1.36)'),fit('Sponsored','script',322,844,165,35,INK,rotate='rotate(-9 404 861)'),fit('By','script',389,879,46,33,INK,rotate='rotate(-8 412 896)'),group([hydro()],'translate(402 966) scale(1.04)'),group([env()],'translate(566 966) scale(1.04)')]
add('01-we-are-bear-aware-window-sign',764,1000,a,'close-up p.1; full report p.27','Main oval and text independently rebuilt. Sponsor marks and script approximate.')
# Checklists: source layout cropped to printed artwork, clean page geometry, historical specimen IDs retained.
def checkbox(x,y,w,h):return rect(x,y,w,h,'#fff','#171717',max(2,w*.12))
EMPHASIS=['all garbage','each evening','Store','stay indoors','Call','persists','Informed','follow','Safety Information','aware','Removed','Pick','do not leave','Fenced','indoors','air-tight bags','Do not put','Burn','Feed']
def styled_checkline(s,x,y,size,maxw):
    pat='('+'|'.join(r'\b'+re.escape(p)+r'\b' for p in sorted(EMPHASIS,key=len,reverse=True))+')'
    parts=[p for p in re.split(pat,s) if p]; pos=0; content=[]
    for p in parts:
        k='narrow-italic' if p in EMPHASIS else 'narrow'; o,b,adv=run(k,p); sc=size/font(k)[4]
        content.append(group([f'<path d="{d}" transform="translate({fmt(off)} 0)"/>' for off,d in o],f'translate({fmt(pos)} {fmt(size*.78)}) scale({fmt(sc)} {fmt(-sc)})',p));pos+=adv*sc
    return group(content,f'translate({x} {y}) scale({min(1,maxw/max(pos,1))} 1)',s)
def checkrow(a,x,y,lines,size=20,lead=23,w=510,boxsize=23):
 a.append(checkbox(x,y+2,boxsize,boxsize*.85));a.extend(styled_checkline(s,x+boxsize+14,y+i*lead,size,w) for i,s in enumerate(lines))
def heading(a,x,y,s,size=20):
 a.append(text(s,'narrow-bold',x,y,size));ww=width(s,'narrow-bold',size);a.append(text('We','narrow-italic',x+ww+18,y,size));a.append(line(x+ww+18,y+size*.78,x+ww+18+width('We','narrow-italic',size),y+size*.78,2.2))
a=[rect(0,0,560,750,'#fff'),group([crest()],'translate(9 6) scale(.74)'),fit('Bear Aware','heavy',140,28,218,35),fit('Business','sans-bi',149,72,110,21),line(149,98,259,98,3),fit('Checklist','narrow-bold',269,72,93,20),group([pawlock()],'translate(415 9) scale(1.05)')]
heading(a,0,130,'Management:',27)
checkrow(a,2,170,['Keep all garbage in air-tight bags','and enclosed in a secured area or','locked dumpster each evening.'],26,27,485,33)
checkrow(a,2,264,['Store used cooking oil in a secured area.'],25,27,485,33)
checkrow(a,2,320,['Know to stay indoors until a bear leaves.'],25,27,485,33)
checkrow(a,2,377,['Call the Conservation Officer (837-5553)','or the RCMP (837-5255)','if a bear problem persists.'],25,27,485,33)
checkrow(a,2,461,['Informed our staff to follow','these guidelines.'],26,27,365,33)
heading(a,0,554,'Staff:',27)
checkrow(a,2,593,['Know and follow these Bear','Safety guidelines.'],25,27,365,33)
a += [rect(430,444,77,31,'#171717'),fit('B027','sans-italic',434,448,69,23,'#fff'),group([basin_stacked()],'translate(426 498) scale(1.05)'),group([hydro()],'translate(0 715) scale(1.0)'),group([env()],'translate(353 715) scale(1.12)')]
add('02-business-checklist',560,750,a,'close-up p.2; full report p.28','Printed checklist, clean art area. Serial B027 retained; type approximated.')
a=[rect(0,0,560,750,'#fff'),group([crest()],'translate(8 8) scale(.74)'),fit('Bear Aware','heavy',140,9,250,36),fit('Family','sans-bi',168,53,76,21),line(167,78,242,78,3),fit('Checklist','narrow-bold',250,53,106,22),group([pawlock()],'translate(425 6) scale(.98)')]
heading(a,0,106,'PROPERTY MANAGMENT:',19)
rows=[(135,['Received Bear Safety Information pamphlets or a presentation.']),(167,['Are aware berries, fruit trees, domestic animals, animal foods,','compost, garbage, unclean barbeques and bee hives attract bears.']),(205,['Removed unwanted fruit trees.']),(238,['Pick all ripe fruit and do not leave fruit on the ground.']),(271,['Fenced our orchards,beehives or livestock if they are a problem.'])]
for y,s in rows:checkrow(a,2,y,s,18,19,520,23)
heading(a,0,305,'GARBAGE AND COMPOST:',19)
for y,s in [(336,['Keep garbage indoors in air-tight bags until pick-up day.']),(368,['Do not put oil,grease,dairy products,meat, bones or fruit in our compost.']),(400,['Cover compost with soil, leaves, grass or lime to reduce odors.'])]:checkrow(a,2,y,s,18,19,520,23)
heading(a,0,431,'BARBECUES:',19)
for y,s in [(458,['Burn or clean off food residues after use.']),(490,['Store our barbecue inside or under plastic.'])]:checkrow(a,2,y,s,18,19,520,23)
heading(a,0,522,'PETS:',19)
for y,s in [(550,['Store pet food indoors.']),(582,['Feed our pets indoors.'])]:checkrow(a,2,y,s,18,19,380,23)
heading(a,0,614,'SAFETY:',19)
for y,s in [(643,['Know to stay indoors until a bear leaves.']),(675,['Call the Conservation Officer (837-5553) or','RCMP (837-5255) if a bear problem persists.'])]:checkrow(a,2,y,s,18,19,405,23)
a += [fit('0003','mono',452,454,55,18),group([basin_stacked()],'translate(430 516) scale(1.13)'),group([hydro()],'translate(9 722) scale(1.05)'),group([env()],'translate(326 722) scale(1.15)')]
add('03-family-checklist',560,750,a,'close-up p.3; full report p.29','Original misspelling PROPERTY MANAGMENT and specimen number 0003 retained.')
# Campaign editorial content transcribed from user-provided scans. Keep historical statements as historical, not current advice.
D={
'black-bear-range':('facts',[], 'Black bears continue to occupy 85% of their historic range in B.C. with the total population estimated between 120,000 and 160,000. Habitat preferences are forested areas with a dense shrub underlay and high food availability - typical of B.C. valley bottoms where the majority of our towns and cities are located.'),
'john-krebs':('mind',['John Krebs- Senior Wildlife Biologist,','Columbia Basin Fish & Wildlife Compensation Plan'],'“A bear’s existence is a continuous search for food - up to 20,000 calories a day! In the wild, bears pose no more risk to people than crossing the road! But when we make human food available, we are unwittingly encouraging bears to leave their environment and enter ours. That’s when the risks to both bears and people increase considerably. The only solution is for each of us to manage our garbage responsibly. That will force bears back into the wild - where they belong.”'),
'grizzly-population':('facts',[],'BC has an estimated 10,000 to 13,000 grizzly bears, which is about half of all the grizzlies in Canada, and one quarter of all the grizzlies in North America. Over 60% of the remaining grizzly bear habitat in Canada is designated as either vulnerable or threatened, and all is considered to be at risk.'),
'susan-hall':('mind',['Susan Hall- Ecosystem Management','Specialist Representative on','Revelstoke Bear Management Committee'],'“Our experience with national parks has shown that we need a very high compliance level to reduce the number of bears foraging in town. The greatest challenge is to have everybody clean up, not just almost everybody.”'),
'conservation-officer-budget':('facts',[],'In the province of B.C., between 11% and 15% of the Conservation Officer Service’s budget goes to dealing with bear/human conflict situations. Valuable time and dollars are lost that otherwise could be spent on other enforcement issues, such as poaching.'),
'john-woods':('mind',['Dr. John Woods','Faunal Specialist- Parks Canada','WEST SLOPES BEAR RESEARCH PROJECT'],'“Doing something positive environmentally sometimes seems like an elusive goal. When we offer our help far from home the results of our efforts are hard to see. But by paying attention to garbage and fruit trees the people of Revelstoke have an opportunity to do something both constructive and valuable for the local environment and local bears.”'),
'future-bear-populations':('facts',[],'It is expected that people will outnumber bears 60:1 in BC within 50 years. Bear populations will undoubtedly decline due to urban encroachment on bear habitat. Teaching this generation of bears to forage away from human settlements ensures that bear populations will not also decline due to avoidable bear/human conflict situations.'),
'bruce-mclellan':('mind',['Dr. Bruce McLellan','Wildlife Habitat Ecologist - Ministry of Forests','WEST SLOPES BEAR RESEARCH PROJECT'],'“We can’t go into the next millenium continuing to have this many bears wandering around town. It is only a matter of time before someone is seriously hurt. We don’t want to leave it until then to realize we should have cleaned up our problem.”'),
'grizzly-reproduction':('facts',[],'Female grizzlies produce their first litter at 5 to 7 years of age. Cubs are born every 2 - 5 years, averaging 1 - 2 cubs per litter. Under optimal conditions a female could produce a maximum of 12 cubs in her lifetime. With a high cub mortality rate, only 7 - 10 cubs would reach maturity. Threats to their survival such as “problem” bear management, hunting, poaching, vehicles, habitat loss, or food shortages would further reduce their population.'),
'cub-learning':('facts',[],'Grizzly and black bear cubs learn survival skills from their mother in the 2 to 4 years they spend with her. If the mother feeds on garbage, domestic fruit, or compost, and displays no fear of human presence, then this is the behavior that her cubs will learn.\nThroughout life, trial and error, and curiosity will continue to drive a bear’s learning process. This ability enables it to obtain the highest energy foods.')}
CONTACT='For more information contact Revelstoke’s Bear Awareness Program at 837-5507'
def adaptive(s,k,preferred,maxw,maxh,ratio=1.08):
 size=preferred
 while size>5:
  lines=wrap(s,k,size,maxw);lead=size*ratio
  if len(lines)*lead<=maxh:return lines,size,lead
  size-=.15
 return lines,size,lead

# Original newspaper line breaks reconstructed from the legible close-up specimens.
TIMES_LINES={
'black-bear-range':['Black bears continue to occupy 85% of','their historic range in B.C. with the total','population estimated between 120,000 and','160,000. Habitat preferences are forested','areas with a dense shrub underlay and high','food availability - typical of B.C. valley bot-','toms where the majority of our towns and','cities are located.'],
'grizzly-population':['BC has an estimated 10,000 to 13,000','grizzly bears, which is about half of all the','grizzlies in Canada, and one quarter of all the','grizzlies in North America. Over 60% of the','remaining grizzly bear habitat in Canada is','designated as either vulnerable or threatened,','and all is considered to be at risk.'],
'conservation-officer-budget':['In the province of B.C., between','11% and 15% of the Conservation','Officer Service’s budget goes to dealing','with bear/human conflict situations.','Valuable time and dollars are lost that','otherwise could be spent on other','enforcement issues, such as poaching.'],
'future-bear-populations':['It is expected that people will outnum-','ber bears 60:1 in BC within 50 years. Bear','populations will undoubtedly decline due to','urban encroachment on bear habitat.','Teaching this generation of bears to forage','away from human settlements ensures that','bear populations will not also decline due to','avoidable bear/human conflict situations.'],
'grizzly-reproduction':['Female grizzlies produce their first litter at','5 to 7 years of age. Cubs are born every 2 - 5','years, averaging 1 - 2 cubs per litter. Under opti-','mal conditions a female could produce a maxi-','mum of 12 cubs in her lifetime. With a high cub','mortality rate, only 7 - 10 cubs would reach','maturity. Threats to their survival such as “prob-','lem” bear management, hunting, poaching, vehi-','cles, habitat loss, or food shortages would further','reduce their population.'],
'cub-learning':['Grizzly and black bear cubs learn survival','skills from their mother in the 2 to 4 years they','spend with her. If the mother feeds on garbage,','domestic fruit, or compost, and displays no fear','of human presence, then this is the behavior that','her cubs will learn.','Throughout life, trial and error, and curiosity will','continue to drive a bear’s learning process. This','ability enables it to obtain the highest energy','foods.'],
'john-krebs':['“A bear’s existence is a continuous search for food - up','to 20,000 calories a day! In the wild, bears pose no','more risk to people than crossing the road! But when','we make human food available, we are unwittingly','encouraging bears to leave their environment and enter','ours. That’s when the risks to both bears and people','increase considerably. The only solution is for each of','us to manage our garbage responsibly. That will force','bears back into the wild - where they belong.”'],
'susan-hall':['“Our experience with national parks has','shown that we need a very high compli-','ance level to reduce the number of bears','foraging in town. The greatest challenge','is to have everybody clean up, not just','almost everybody.”'],
'john-woods':['“Doing something positive environmentally some-','times seems like an elusive goal. When we offer','our help far from home the results of our efforts','are hard to see. But by paying attention to','garbage and fruit trees the people of Revelstoke','have an opportunity to do something both con-','structive and valuable for the local environment','and local bears.”'],
'bruce-mclellan':['“We can’t go into the next millenium continuing','to have this many bears wandering around town.','It is only a matter of time before someone is seri-','ously hurt. We don’t want to leave it until then to','realize we should have cleaned up our problem.”']}
def times_ad(key):
 kind,by,body=D[key];a=[rect(0,0,300,375,'#d1d1d1','#171717',1.8,18),rect(10,10,86,64,'#fff','#171717',1.4,12),group([walking_bear()],'translate(17 16) scale(.66)')]
 if kind=='facts':a.extend([fit('Just the','serif-bold',111,26,142,33),fit('“BEAR” FACTS','serif-bold',30,84,241,28)])
 else:a.extend([fit('“BEAR”','serif-bold',105,10,180,39),fit('in mind','serif-bi',121,51,150,36)])
 top=123 if kind=='facts' else 94
 a.append(rect(12,top,276,296-top,'#fff','#171717',1.5,19));y=top+8
 for i,s in enumerate(by):
  k='serif-bold' if s.isupper() else 'serif-italic';a.append(text(s,k,150,y,11.8,266,'center'));y+=13
 if by:y+=3
 lines=TIMES_LINES[key]; lead=min(15.4,(271-y)/len(lines));size=min(lead*.94,258/max(width(t,'serif',1) for t in lines));
 for li,ls in enumerate(lines):
  xx=20+(8 if li==0 and kind=='facts' else 0);a.append(text(ls,'serif',xx,y+li*lead,size,288-xx-7))
 a.append(multiline(['For more information contact Revelstoke’s Bear','Awareness Program at 837-5507'],'serif-bold',150,273,11.1,12,260,'center'))
 a.extend([group([basin_horizontal()],'translate(12 299) scale(1.05)'),group([crest()],'translate(219 309) scale(.58)')]);return a

def unique_ad(key):
 kind,by,body=D[key];a=[rect(0,0,350,280,'#fff','#171717',2),rect(9,6,77,64,'#fff','#171717',1.5,10),group([walking_bear()],'translate(15 12) scale(.60)')]
 if kind=='facts':a.extend([fit('Just the','serif-bi',128,16,58,16),fit('“BEAR” FACTS','serif-bold',128,40,174,20)])
 else:a.append(fit('“BEAR” IN MIND','serif-bold',118,31,217,24))
 top=74;bot=194;a.append(rect(8,top,334,bot-top,'#fff','#171717',1.3,8));y=top+5
 for s in by:
  s=s.replace('Compensation Plan','Compensation Program').replace('Senior Wildlife Biologist,','Senior Wildlife Biologist').replace('Faunal Specialist-','Faunal Specialist -');a.append(text(s,'sans-bold',13,y,12.0,323));y+=13
 lines,size,lead=adaptive(body,'sans',12.7,322,bot-24-y,1.1);a.append(multiline(lines,'sans',13,y,size,lead,322));a.append(multiline(['For more information contact Revelstoke’s Bear Awareness','Program at 837-5507.'],'sans-bold',13,bot-22,11,11,323))
 a.extend([group([basin_word()],'translate(28 199) scale(1.12)'),group([crest()],'translate(244 198) scale(.77)')]);return a
TIMES=[('black-bear-range','p.4 top left','1997-10-08'),('john-krebs','p.4 top right','1997-10-08'),('grizzly-population','p.4 bottom left','1997-10-22'),('susan-hall','p.4 bottom right','1997-10-22'),('conservation-officer-budget','p.5 top left','date uncertain'),('john-woods','p.5 top right','date uncertain'),('future-bear-populations','p.5 bottom left','1997-10-01 (faint annotation)'),('bruce-mclellan','p.5 bottom right','1997-10-01 (faint annotation)'),('grizzly-reproduction','p.6 left','1997-10-29'),('cub-learning','p.6 right','1997-10-29')]
for i,(key,p,date) in enumerate(TIMES,1):add(f'times-{i:02}-{key}',300,375,times_ad(key),'close-up '+p+'; Times Review; '+date,'Grey tone and recurring emblems normalized. Historical copy.')
UNIQUE=[('future-bear-populations','p.7 top left','1997-09-18?'),('john-woods','p.7 top right','1997-09-18?'),('conservation-officer-budget','p.7 middle left','1997-09-25'),('john-woods','p.7 middle right','1997-09-25'),('future-bear-populations','p.7 bottom left','1997-10-02'),('bruce-mclellan','p.7 bottom right','1997-10-02'),('john-krebs','p.8 top left','1997-10-09'),('black-bear-range','p.8 top right','1997-10-09'),('susan-hall','p.8 middle left','1997-10-16'),('grizzly-population','p.8 middle right','1997-10-16'),('grizzly-reproduction','p.8 bottom left','1997-10-23'),('cub-learning','p.8 bottom right','1997-10-23 or 30 (annotation)')]
for i,(key,p,date) in enumerate(UNIQUE,1):add(f'unique-{i:02}-{key}',350,280,unique_ad(key),'close-up '+p+'; Unique; '+date,'Right column clipped in scan; completed using corresponding intact Times copy. Repeated placements retained.')
# Larger campaign advertisement, both newspaper treatments. Icons redrawn as line illustrations.
def pictogram(i):
 if i==0:return group([path('M12 16 Q10 12 21 10 L24 3 L30 6 L32 2 L36 8 Q53 7 62 23 L71 47 Q52 53 41 45 Q25 57 8 49 Q1 40 12 16Z','#fff','#171717',1.7),path('M30 8 L22 19 M34 9 L43 19 M10 43 Q21 30 35 42 L41 45 M53 30 L60 38','none','#171717',1.5)])
 if i==1:return group([path('M12 7 H58 L53 25 H18 Z M8 6 H63 M16 25 L5 36 H66 L56 25 M19 36 V65 H51 V36 M12 39 L5 56 M60 39 L68 56 M27 65 H49 M23 16 H48','none','#171717',1.7),ell(16,64,4,3,'none','#171717',1),ell(54,64,4,3,'none','#171717',1)])
 if i==2:
  a=[path('M30 68 Q37 39 35 19 M35 43 L16 27 M35 35 L56 18 M34 53 L57 39 M35 50 L14 43','none','#171717',2)]
  for x,y,r in [(15,25,12),(25,16,12),(42,12,14),(55,23,13),(53,38,13),(25,39,14),(11,40,8),(37,27,13)]:
   a.append(path(f'M{x-r} {y} Q{x-r} {y-r} {x} {y-r} Q{x+r} {y-r} {x+r} {y} Q{x+r} {y+r} {x} {y+r} Q{x-r} {y+r} {x-r} {y}Z','none','#171717',1.2));a.append(ell(x+2,y+1,2,2,'#171717'))
  return group(a)
 if i==3:return group([path('M8 15 L64 15 L59 60 L15 60Z M6 14 H66 M16 26 H61 M15 36 H60 M14 46 H60 M23 17 L26 60 M46 17 L43 60','none','#171717',1.5),path('M12 14 Q17 5 26 10 Q30 1 40 9 Q49 2 61 14','none','#171717',1.4),path('M17 31 l8 6 l-4 8 l9 7 l10 -14 l12 8','none','#171717',1.3)])
 return group([path('M6 25 H67 L61 31 H10 Z M16 31 V68 M57 31 V68 M16 35 L57 64 M57 35 L16 64 M13 68 H22 M51 68 H62 M16 12 H32 V25 H16 Z M39 6 H55 V25 H39 Z M13 10 H35 M36 4 H58','none','#171717',1.6)])
INTRO='The bears are back. They’re hungry and looking for an easy meal. Will they show up unannounced at your home for dinner? Midnight snack? They will if you leave the food out. If they like the menu and great service they’ll come back. And you’ll get them killed. Last year in B.C., we were so nice to bears that nearly 900 are no longer with us. Over five years we wiped out 4,500 “problem” bears this way. Sad… and avoidable.'
INTRO2='How many bears will be killed in 1997? That depends on how inhospitable we can be. Follow this Do’s and Don’ts Checklist and be downright inhospitable. Yes, some of these may seem an inconvenience. But we’re trying to get bears to change their habits too. The least we can do is change ours. After all, aren’t humans supposed to be the smarter and more adaptable species? The bears lose their lives. What do we have to lose?'
ROWS=[(['HOUSEHOLD','GARBAGE'],['Leave containers inside until pickup.','Ensure lids are properly sealed.','Wash cans regularly.'],['Put garbage outside - bags','Throw oil/grease outside.','Stockpile garbage.','Leave fish/animal bones, by-products/parts outside.']),(['YARDS &','PROPERTY'],['Keep yards/property clean','Wash BBQ grills after use','Store BBQ’s inside','Secure pet/livestock feed','Thin trees on property'],['Keep BBQ’s on decks.','Leave supplies/garbage in back of pickups - canopy or not.','Let refuse/garbage accumulate on property.']),(['FRUIT','TREES'],['Pick fruit daily as it ripens','Pick fruit before it ripens if you won’t use immediately','Enclose trees with chain link or electric fencing'],['Allow windfalls to accumulate.','Permit fruit to rot on the ground.']),(['COMPOST'],['Use a proper, sealed compost unit.','Enclose compost with bear-proof fencing.','Lime compost regularly.'],['Put fish, meat or fruit into compost.','Locate compost bins near forests or thickets.']),(['BEEHIVES'],['Place beehives on platforms over 2 metres high.','Wire beehives together with metal strapping.'],['Allow beehives & area to become dirty.','Set up beehives in early spring when other natural bear food is unavailable.'])]
def full_ad(times=False):
 a=[rect(0,0,900,680,'#fff'),rect(3,3,894,674,'none','#171717',1.5)]
 k='serif' if times else 'sans';bold='serif-bold' if times else 'sans-bold';headline='We’re so nice to bears it kills them' if times else 'We’re So Nice to Bears It Kills Them!'
 a.append(fit(headline,'heavy' if times else 'sans-bold',19,15,862 if times else 600,48 if times else 31))
 if not times:a[-1]=fit(headline,'sans-bold',150,15,600,28)
 if times:
  a.extend([rect(15,73,157,145,'#f3f3f3','#171717',.9),multiline(['Photograph','not reproduced','in vector edition'],'sans',93,120,12,15,145,'center')]);a.append(multiline(INTRO,k,183,73,14,16,360));a.append(multiline(INTRO2,k,550,73,13.4,15.5,333));start=235;rh=87
 else:
  a.append(multiline(INTRO,k,10,52,15,18,875));a.append(multiline(INTRO2,k,10,138,15,18,650));start=237;rh=86
 tablew=655
 for i,(title,dos,donts) in enumerate(ROWS):
  y=start+i*rh;a.append(line(5,y,tablew,y,1.2));a.append(group([pictogram(i)],f'translate(17 {y+15}) scale(.85)'));a.append(multiline(title,'heavy' if times else 'sans-bold',89,y+20,21,24,136));a.append(text('DO','heavy' if times else 'sans-bold',244,y+7,19));a.append(text('DON’T','heavy' if times else 'sans-bold',438,y+7,19))
  for xx,items,col in [(282,dos,150),(505,donts,143)]:
   yy=y+8
   for item in items:
    lines=wrap(item,k,10.6,col-14);a.append(checkbox(xx,yy+1,7,7));a.append(multiline(lines,k,xx+12,yy,10.6,11.2,col-14));yy+=len(lines)*11.2+2.1
 a.append(line(5,start+rh*5,tablew,start+rh*5,1.2));a.append(line(tablew,start,tablew,start+rh*5,1.1))
 yy=238 if times else 140;a.append(text('Your Inhospitality Score',bold,673,yy,18.4,215));a.append(text('OUT OF 29 CHECKLIST POINTS:',k,673,yy+21,11.5,215))
 for i,(n,s) in enumerate([('25 - 29','Downright Inhospitable'),('20 - 24','Somewhat Inhospitable'),('15 - 19','Open for Dinner'),('10 - 14','Smorgasbord - Bears Welcome Anytime'),('0 - 9','Feast - We’re Nice to Bears')]):
  a.append(text(n,k,673,yy+40+i*24,12.7,50));a.append(multiline(s,k,725,yy+40+i*24,12.2,12.5,161))
 yy+=169;a.append(line(669,yy-6,889,yy-6,.9));a.append(multiline(['“Excuse me, but I have','a bear in my yard…”'],bold,673,yy,17,18,213));yy+=43
 for s in ['Stay calm.','Remain indoors until well after the bear leaves.','If the bear stays, is persistent or aggressive, call the Conservation Officer at 837-5553.']:
  ls=wrap(s,k,12.3,199);a.append(ell(676,yy+4,1.7,1.7,'#171717'));a.append(multiline(ls,k,685,yy,12.3,13.5,199));yy+=len(ls)*13.5+4
 a.append(multiline('If you would like more information on Revelstoke’s Bear Awareness Program or advice on avoiding bear conflicts call 837-5507.',k,673,yy+6,12.4,13.6,212));
 if times:a.extend([group([crest()],'translate(674 607) scale(.35)'),group([basin_horizontal()],'translate(736 604) scale(.53)'),group([hydro()],'translate(670 650) scale(.68)'),group([env()],'translate(768 650) scale(.67)')])
 else:a.extend([group([crest()],'translate(673 514) scale(.60)'),group([basin_word()],'translate(673 589) scale(1.10)'),group([basin_mark()],'translate(792 510) scale(.68)'),multiline(['A B.C. HYDRO','B.C. ENVIRONMENT','PARTNERSHIP'],'narrow-italic',833,632,12,13,107,'center')])
 return a
add('campaign-large-unique-1997-06-19',900,680,full_ad(False),'full report p.46 (rotated upright)','Manually rebuilt checklist and pictograms. Text reflowed; sponsor marks approximate.')
add('campaign-large-times-1997-06-18',900,680,full_ad(True),'full report p.33','Original photograph omitted, labeled placeholder. Cropped text recovered using Unique edition; layout approximate.')
# Source metadata and text for reproducible editing.
(BASE/'manifest.json').write_text(json.dumps(M,indent=2,ensure_ascii=False));(BASE/'source'/'advertisement-copy.json').write_text(json.dumps(D,indent=2,ensure_ascii=False))
print(f'{len(M)} composition SVGs and {len(list(COMPONENTS.glob("*.svg")))} component SVGs')
