"""Geometric reconstructions of three associated BC emblems.

Silhouettes are manually drawn from registered source observations. They are
not whole-image traces. Botanical hatching and substitute type are explicitly
approximate. All lettering is converted to paths from locally available faces.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import json,math,random
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cairosvg
from flatten_knockouts import flatten

P=Path(__file__).resolve().parent
INK='#000000'
BOOK='/usr/share/fonts/opentype/urw-base35/URWBookman-Demi.otf'
SERIF='/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf'
SANS='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'

def text_paths(text,fontfile=BOOK):
    font=TTFont(fontfile);gs=font.getGlyphSet();cmap=font.getBestCmap();parts=[];xx=0;bb=[]
    for char in text:
        name=cmap.get(ord(char),'.notdef');pen=SVGPathPen(gs);gs[name].draw(pen)
        bp=BoundsPen(gs);gs[name].draw(bp)
        if bp.bounds:
            a,b,c,d=bp.bounds;bb.append((xx+a,b,xx+c,d))
        parts.append((pen.getCommands(),xx,font['hmtx'].metrics[name][0]))
        xx+=font['hmtx'].metrics[name][0]
    bbox=(min(b[0] for b in bb),min(b[1] for b in bb),max(b[2] for b in bb),max(b[3] for b in bb))
    return parts,bbox,xx,font['head'].unitsPerEm

def text_fit(text,x,y,w,h,fontfile=BOOK,color='black'):
    parts,b,_,_=text_paths(text,fontfile);sx=w/(b[2]-b[0]);sy=h/(b[3]-b[1])
    inner=''.join(f'<path d="{d}" transform="translate({a:g} 0)"/>' for d,a,_ in parts)
    return f'<g fill="{color}" transform="matrix({sx:.8f} 0 0 {-sy:.8f} {x-b[0]*sx:.6f} {y+b[3]*sy:.6f})">{inner}</g>'

def arc_text(text,cx,cy,rx,ry,fontsize,span,fontfile=SANS,color='black'):
    parts,_,_,upem=text_paths(text,fontfile);scale=fontsize/upem
    widths=[adv*scale for _,_,adv in parts];total=sum(widths)
    angles=np.linspace(-math.pi/2-span/2,-math.pi/2+span/2,2000)
    pts=np.column_stack([cx+rx*np.cos(angles),cy+ry*np.sin(angles)])
    distances=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))]
    pos=0;out=[]
    for (d,_,adv),w in zip(parts,widths):
        frac=(pos+w/2)/total;ang=np.interp(frac*distances[-1],distances,angles)
        x=cx+rx*math.cos(ang);y=cy+ry*math.sin(ang)
        rot=math.degrees(math.atan2(ry*math.cos(ang),-rx*math.sin(ang)))
        out.append(f'<g transform="translate({x:.5f} {y:.5f}) rotate({rot:.5f}) scale({scale:.6f} {-scale:.6f}) translate({-adv/2:g} 0)"><path d="{d}"/></g>')
        pos+=w
    return f'<g fill="{color}">'+''.join(out)+'</g>'

def svg_doc(body,w,h,title,desc):
    scale=1000/h
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w*scale:.6f} 1000" width="{w*scale:.6f}" height="1000"><title>{title}</title><desc>{desc}</desc><g transform="scale({scale:.8f})">{body}</g></svg>'

def fw_body(paired=False):
    # Source coordinates are retained as construction units (115 x 195 px).
    outer='<rect x="2.2" y="2.2" width="110.7" height="190.1" rx="14.5"/>'
    oval='M49 8.7 C28 10.5 14.5 30 10.7 51 C5.7 79 13 110 26.7 129.1 C37 143 51 148.1 67 144.8 C87 140.5 99 119.6 102.9 97.2 C107.1 71.1 98.2 45.2 83.3 27.5 C73.6 16 60.7 9.3 49 8.7 Z'
    bear='M23.5 29.2 L28.4 27.8 L30.5 25.4 L35.6 24 L36.4 21.4 L42.7 18.7 L47 17.7 L49.8 14.4 L51.4 11.3 L54.4 14.3 C71.9 20.2 86.8 37.4 95.7 58.5 C99.3 67.5 100.3 74.8 101 80.2 C91.1 84.6 83.3 85.1 76.5 82.4 L67.6 78.8 L58.1 72.2 L55.3 68.3 C55.1 59.6 52 54 46 51 C40.1 48.1 34.6 46.1 29.7 43.6 L25.3 41 L23.5 37 Z'
    lower='M17.5 43 C26 46.7 32.3 49.9 37.8 55.8 C42.4 60.9 46.1 67.5 50 71.7 L55.4 76.8 C63 82.4 71.2 86.5 78.4 87.5 C87.5 89.2 95.5 87.3 100 84.4 C100 102 93.6 121.1 83.2 132 L79.4 134.8 L80.7 136.9 C71.5 140.4 60.5 140 53.7 137.5 L51.3 135.6 L50.4 133.4 L50.2 136.5 C42 133.9 35.9 129 30.6 122 L29.9 118.5 L28.2 116 C21.6 103.7 17.3 86.8 15.7 71.5 C14.3 59.5 14.4 49.3 17.5 43 Z'
    fish='M50.6 75.2 C55 80.3 61.3 85.6 66.1 91.1 C73.3 99 80.5 110.4 82.2 118.3 C83.6 124.9 80.8 129.7 75.7 130 C69.6 130.3 64.7 122.4 60.7 112.6 C56.2 101 54.5 88.3 50.6 80.8 L48.5 76.7 L50.2 77.4 L52 78.9 Z'
    letter_f='M17.7 153.4 L36.1 153.4 Q39 153.5 39.4 156.5 L39.8 160.4 Q39.8 162.8 37.6 162.2 L35.6 159.6 Q34.6 158.2 29.2 158.8 L29.2 165.2 L32 165.2 Q33.3 162.5 35.1 164.3 Q36 165.5 36 168.6 L36 172.5 Q36 175 34.2 174.2 L31.9 171.2 L29.2 171.2 L29.2 178.4 Q29.2 180.1 31.6 181.1 L31.6 184.8 L17.3 184.8 L17.3 181.8 Q20.1 180.7 20.1 178.6 L20.1 159.9 Q20.1 158 17.7 157.2 Z'
    letter_w='M54.3 153.4 L69.4 153.4 L69.4 157.3 L67.8 158.3 L71.6 170 L75.4 158.2 L73.4 157.1 L73.4 153.4 L86.5 153.4 L86.5 157 L84.2 158.2 L88.1 170.1 L92.1 158.4 L90 157.2 L90 153.4 L101.2 153.4 L101.2 157.2 L99.1 158.3 L89.7 183.5 Q88.9 185.6 86.7 185.5 L82.5 185.5 L77.8 173.1 L73.2 183.4 Q72.3 185.6 69.8 185.5 L66.5 185.5 L57.3 159.2 L54.3 157.4 Z'
    cuts=f'<rect x="6.8" y="6.9" width="101.4" height="180.8" rx="10.2" fill="none" stroke="black" stroke-width="1.5"/><path d="{oval}" fill="black"/><path d="{bear}" fill="white"/><path d="{lower}" fill="white"/><path d="{fish}" transform="translate(0 12) scale(1 .84)" fill="black"/><circle cx="39.1" cy="24.5" r="0.85" fill="black"/><path d="M7 147.3H108" stroke="black" stroke-width="1.65"/><path d="{letter_f}" transform="translate(-1 -1)" fill="black"/><path d="{letter_w}" transform="translate(0 -1)" fill="black"/>'+text_fit('&',40.2,166.1,16.4,18.1,BOOK,'black')
    out='<defs><mask id="fw-cutout" maskUnits="userSpaceOnUse" x="0" y="0" width="115" height="195"><rect width="115" height="195" fill="white"/>'+cuts+'</mask></defs><g fill="black" mask="url(#fw-cutout)">'+outer+'</g>'
    if paired:
        out+='<rect x="119.3" y="3.3" width="106.1" height="188.9" rx="14.3" fill="none" stroke="black" stroke-width="1.8"/>'
        for t,x,y,w,h in [('British',151.5,42.1,44.3,8.8),('Columbia',144.1,57.2,59.6,8.9),('Fish &',140,75.3,65.7,13.8),('Wildlife',127.8,97.1,88.9,14.2),('Branch',151.2,119,46.5,9.3)]:
            out+=text_fit(t,x,y,w,h,BOOK)
    return out

def parks_body():
    shield='M8.3 4.6H128.5V128.7L67.5 147L8.3 129.8Z'
    province='M18.5 32.5H91.5L93.1 56L96 63.8L98 81L119 110.3L78 112L65.3 112.2L59.1 107.5L56.3 108.3L50.5 105.7L48.8 99.5L47.4 92.1L47.8 83.9L45.6 77.2L44.5 68.2L41.8 65.4L41.6 60.8L38 57.7L31.9 46.6L27 39.9L24.1 39.8L21.9 42.5L20.2 40.2L16.9 40.3L14.6 38.4L18 36.4Z'
    petals=[
        'M55.8 57.4 C54.1 51.6 56.2 45.5 59.3 43.5 L66.8 42 L68.6 39.9 L70.1 42 L78.8 43 C82.6 44 81.8 49.4 80.8 53.7 L77.8 58.4 L72.9 61.2 L64 61.7Z',
        'M78.8 60.1 L84.2 54 C88 54.3 90.4 57.8 92.7 60.3 L94.4 65.9 L98.7 69.7 L94.9 72.8 L93.2 78.6 L87.8 81.3 L82.6 79.5 L76.9 75.3 L75.1 68.7Z',
        'M75 77.4 C80.3 80.1 85.3 81.5 90.7 80.5 L94.1 83.9 L91.6 88.4 L89.1 91.3 L83.2 92.5 L80.2 91.3 L77.9 93 L73.1 90.8 L70.9 85.8 L69.8 79.1Z',
        'M64.7 76.9 L67.5 81.4 L70.4 91.2 L69.2 94.4 L64.1 96 L59.5 94.8 L56.9 96 L51.3 93.4 L47.6 91.1 L47.8 85.3 L49.3 81 L48.8 77 L54.9 73.4 L60.1 73.8Z',
        'M56.1 58.7 L59.3 61.3 L63.2 63.7 L61.5 67.7 L61 71.3 L55 72.8 L51.9 73 L48.4 76.1 L43.3 75.8 L40.5 73.3 L40.7 68.4 L38.6 64.9 L42.6 62.4 L47.1 60.2 L49.6 56.4 L53 55.7Z'
    ]
    cut='<circle cx="68.2" cy="67.7" r="12" fill="black"/>'+''.join(f'<path d="{d}" fill="black"/>' for d in petals)
    cut+='<path d="M50 94L55 102L61.5 110" fill="none" stroke="black" stroke-width="2"/>'
    out=f'<path d="{shield}" fill="none" stroke="black" stroke-width="6.1" stroke-linejoin="miter"/>'
    out+='<defs><mask id="parks-flower" maskUnits="userSpaceOnUse" x="0" y="0" width="134" height="153"><rect width="134" height="153" fill="white"/>'+cut+'</mask></defs>'
    out+=f'<path d="{province}" fill="black" mask="url(#parks-flower)"/>'
    out+='<path d="M46 93L50.7 94.2L53.5 100.1L57.6 104L61.8 110L59.1 113.3L48.8 109.8L47.1 103.6Z" fill="black"/><path d="M28.6 59.2L31.6 58.8L34.2 61.1L34.5 64.9L31.1 67L27.1 64.8L26.5 62.5Z M33.7 66.2L36.4 67.3L37.6 72.2L35.8 74L33.3 71.9L32.3 68.5Z" fill="black"/><circle cx="68.2" cy="67.7" r="6.7" fill="black"/>'
    out+=text_fit('PARKS',24,11.8,89.3,15.7,SERIF)
    out+=text_fit('BRITISH COLUMBIA',13.7,117.2,111.5,8.5,'/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
    return out

def oval_body():
    # Source coordinate system 204 x 262. Five visible bracts and the surrounding
    # leaf clusters are reconstructed separately rather than tracing ink noise.
    out='<ellipse cx="102.1" cy="130.3" rx="99" ry="128.8" fill="black"/>'
    white='<ellipse cx="102.1" cy="130.3" rx="95.2" ry="124.6" fill="none" stroke="black" stroke-width="0.75"/>'
    white+=arc_text('BRITISH COLUMBIA',102,128,76,100,15.9,math.radians(112),SANS,'black')
    leaves=[
        'M68 71L48 68L51 77L50 88L67 83L76 79Z',
        'M140 78L149 76L168 78L156 84L153 92L143 90Z',
        'M62 119L47 124L31 151L49 144L61 135L74 130Z',
        'M74 135L56 144L38 164L59 157L80 145Z',
        'M142 125L160 127L168 143L177 155L160 149L145 147Z',
        'M132 140L146 146L153 165L152 148L145 136Z',
        'M95 51L104 42L109 38L115 51L118 66L107 67Z'
    ]
    petals=[
        'M101 92C88 90 78 85 69 75C61 65 63 55 72 45L80 34L83 41L94 46L103 43C107 52 109 62 108 73L106 88Z',
        'M108 90C111 75 113 60 118 50C129 51 137 53 149 55L146 61L150 71L146 81L136 87L119 94Z',
        'M120 101C132 94 142 89 152 89C160 96 159 105 163 113L163 124L154 130L147 138L137 137C129 131 123 119 116 111Z',
        'M105 117C116 122 125 136 130 148L122 153L114 157L99 158L86 156L80 151L79 144C84 132 91 122 99 115Z',
        'M91 107C79 118 68 131 60 133L54 130L48 129L45 122L43 112L44 99L47 91L54 86L67 85C78 87 89 94 96 100Z'
    ]
    white+=''.join(f'<path d="{d}" fill="black"/>' for d in leaves)
    white+='<circle cx="103" cy="104" r="23" fill="black"/>'
    white+=''.join(f'<path d="{d}" fill="black"/>' for d in petals)
    # Hatching is an interpreted engraving detail; these curves have semantic
    # radial layout and deliberate control points, not pixels copied to paths.
    hatch=[]
    for d in [
        'M97 86Q94 65 87 54','M93 88Q88 68 81 58','M89 89Q81 72 76 64','M84 89Q75 81 69 75',
        'M100 86Q101 68 97 58','M104 86Q108 67 107 61','M95 82Q92 69 90 64','M86 80L82 71',
        'M112 88Q123 66 140 60','M115 91Q128 73 134 71','M117 94Q134 84 140 78','M122 97Q137 92 145 85',
        'M120 104Q140 108 155 116','M120 109Q136 115 144 122','M116 112Q130 127 137 129','M123 108Q136 110 141 112',
        'M107 121Q115 137 118 146','M104 124Q108 140 108 149','M99 123Q95 140 96 150','M95 123Q88 136 87 145','M102 128L101 139',
        'M90 108Q70 106 55 114','M88 105Q68 100 55 102','M89 100Q72 92 65 92','M87 112Q75 116 67 123','M81 112L66 118',
        'M51 73L65 78L56 81','M52 71L60 74','M150 80L159 80L150 87','M143 84L151 83',
        'M35 148L59 131L67 128','M46 139L49 143','M52 132L56 137','M59 128L61 132',
        'M43 159L69 142','M53 151L57 153','M61 144L65 147','M147 132L168 150','M151 136L158 136','M157 142L166 143','M145 144L150 155'
    ]:hatch.append(f'<path d="{d}" fill="none" stroke="white" stroke-width="1.05" stroke-linecap="round"/>')
    white+=''.join(hatch)
    white+='<path d="M91 91Q99 87 109 89L115 94L117 104L112 112L103 116L94 112L89 105Z" fill="white"/>'
    # Discrete flower-centre florets: broad locations visible in the scan.
    dots=[(98,95,1.8),(103,92,1.6),(110,96,1.6),(105,100,2.1),(95,101,2.3),(98,108,2),(105,110,1.6),(112,105,1.5),(91,105,1.4),(109,113,1),(101,103,1.2),(93,96,1.3)]
    white+=''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="black"/>' for x,y,r in dots)
    white+=text_fit('DEPARTMENT OF',67,165.1,70.6,6.7,SANS,'black')
    white+=text_fit('RECREATION',63,174.8,79,9.1,SANS,'black')
    white+=text_fit('AND',93,188.1,20.7,5.6,SANS,'black')
    white+=text_fit('CONSERVATION',53.2,197,99,9.4,SANS,'black')
    return '<defs><mask id="oval-cutout" maskUnits="userSpaceOnUse" x="0" y="0" width="204" height="262"><rect width="204" height="262" fill="white"/>'+white+'</mask></defs><g mask="url(#oval-cutout)">'+out+'</g>'

ASSETS=[
 ('06_Fish_Wildlife_Oval_1973',fw_body(False),115,195,'fw_symbol_source.png','Fish and Wildlife oval emblem, 1973','Manually reconstructed bear/fish silhouette, framing and F/W letters; ampersand from a close outlined Bookman face. Source native cap height limits exact letter shape.',22,'sources/forgov_1973.pdf'),
 ('07_Fish_Wildlife_Paired_Lockup_1973',fw_body(True),228,195,'fw_pair_source.png','Fish and Wildlife paired lockup, 1973','Geometric emblem with separately outlined close substitute Bookman wording. Lettering is a reconstruction, not the recovered original face.',22,'sources/forgov_1973.pdf'),
 ('08_Parks_Dogwood_Shield_1973',parks_body(),134,153,'parks_shield_source.png','Parks dogwood and province shield, 1973','Manually rebuilt shield, simplified province silhouette, islands and five visible bracts; Nimbus Roman/Sans outline lettering approximates the small original captions.',80,'sources/forgov_1973.pdf'),
 ('09_Department_Dogwood_Oval_1970',oval_body(),204,262,'oval_department_source.png','Department dogwood oval, 1970 predecessor','Source-limited reconstruction of the earlier oval badge; compound botanical bracts/leaves and interpreted engraving hatching. Lettering uses outlined close Nimbus Sans forms. Not an exact recovered engraved master.',10,'research/forests_annual_report_1970.pdf')
]

def render(path,w,h):
    return Image.open(__import__('io').BytesIO(cairosvg.svg2png(url=str(path),output_width=w,output_height=h))).convert('RGBA')

def build():
    manifest=[]
    for key,body,w,h,source,title,desc,page,pdf in ASSETS:
        file=P/(key+'.svg');construction=svg_doc(body,w,h,title,desc)
        (P/(key+'_construction.svg')).write_text(construction)
        file.write_text(flatten(construction))
        pic=render(file,round(w/h*1000),1000);bg=Image.new('RGBA',pic.size,'white');bg.alpha_composite(pic);bg.convert('RGB').save(P/(key+'.png'))
        target=Image.open(P/source).convert('L');a=np.array(target)<128
        model=render(file,w,h);bg=Image.new('RGBA',model.size,'white');bg.alpha_composite(model);b=np.array(bg.convert('L'))<128
        union=(a|b).sum();inter=(a&b).sum();iou=inter/union
        # Layout matched in original source coordinates; not independently fit.
        color=np.ones((*a.shape,3),float);color[a]=[.05,.63,.60];color[b]=[.82,.16,.55];color[a&b]=[.10,.18,.18]
        overlay=Image.fromarray(np.uint8(color*255));overlay.resize((round(w/h*1000),1000),Image.Resampling.NEAREST).save(P/(key+'_overlay.png'))
        coords={'fw_symbol_source.png':[1193,247,1308,442],'fw_pair_source.png':[1193,247,1421,442],'parks_shield_source.png':[489,1614,642,1748],'oval_department_source.png':[1137,1443,1341,1705]}[source]
        metrics={'id':key,'title':title,'svg':file.name,'construction_svg':key+'_construction.svg','preview':key+'.png','overlay':key+'_overlay.png','source_crop':source,'source_pdf':pdf,'source_url':'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR'+('1970' if page==10 else '1973')+'.pdf','pdf_page':page,'source_render_dpi':200,'crop_rectangle_in_render_pixels':coords,'crop_rotation_degrees':-90 if page==80 else 0,'source_units':[w,h],'viewBox':[0,0,w/h*1000,1000],'whole_ink_IoU':round(float(iou),4),'registration':'Fixed source coordinate geometry; no local distortion fitted. Threshold128. Whole-ink score includes border and is not a percentage of historical accuracy.','method':desc,'font_dependency':False,'embedded_raster':False,'status':'reconstructed; see stated source/type limitations'}
        manifest.append(metrics)
    (P/'manifest.json').write_text(json.dumps(manifest,indent=2))
    build_review(manifest)
    print(json.dumps(manifest,indent=2))

def build_review(manifest):
    W=1800;rowh=600;H=180+rowh*len(manifest)
    page=Image.new('RGB',(W,H),'#f4f1e8');d=ImageDraw.Draw(page)
    f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    d.text((55,35),'ASSOCIATED EMBLEMS / GEOMETRIC RECONSTRUCTIONS',font=ImageFont.truetype(fb,30),fill='#163c36')
    d.text((55,84),'Source image · clean vector · overlay. Cyan source / magenta reconstruction / dark agreement.',font=ImageFont.truetype(f,23),fill='#52675e')
    for i,item in enumerate(manifest):
        y=150+i*rowh
        d.text((55,y),item['title'],font=ImageFont.truetype(fb,28),fill='#163c36')
        d.text((55,y+40),f"PDF page {item['pdf_page']} · whole-ink IoU {item['whole_ink_IoU']:.3f} · outlined type is approximate",font=ImageFont.truetype(f,20),fill='#52675e')
        for j,(label,filename) in enumerate([('SOURCE',item['source_crop']),('RECONSTRUCTION',item['preview']),('OVERLAY',item['overlay'])]):
            d.text((55+j*580,y+82),label,font=ImageFont.truetype(fb,18),fill='#52675e')
            pic=Image.open(P/filename).convert('RGB');factor=min(540/pic.width,440/pic.height);pic=pic.resize((round(pic.width*factor),round(pic.height*factor)),Image.Resampling.LANCZOS if j==1 else Image.Resampling.NEAREST)
            page.paste(pic,(55+j*580+(540-pic.width)//2,y+112+(440-pic.height)//2))
        d.line((55,y+580,W-55,y+580),fill='#cbd0c4',width=2)
    page.save(P/'Related_Emblems_Source_Vector_Overlay.png')

if __name__=='__main__':build()
