"""Assemble the reconstructed signs with outlined editorial labels."""
from pathlib import Path
import json
from lxml import etree
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import cairosvg
P=Path(__file__).resolve().parent
FONT=TTFont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
GL=FONT.getGlyphSet();CM=FONT.getBestCmap();UPM=FONT['head'].unitsPerEm
def outlined_text(s,x,y,size,color='#163c36'):
    parts=[];pos=0
    for c in s:
        g=CM.get(ord(c),'question');pen=SVGPathPen(GL);GL[g].draw(pen)
        parts.append(f'<path transform="translate({pos} 0)" d="{pen.getCommands()}"/>')
        pos+=FONT['hmtx'][g][0]
    return f'<g transform="translate({x} {y}) scale({size/UPM} {-size/UPM})" fill="{color}">'+''.join(parts)+'</g>'
items=json.loads((P/'sources.json').read_text());parts=[]
parts.append('<rect width="1600" height="2380" fill="#f4f1e8"/>')
parts.append(outlined_text('PROPOSED PARK SYMBOLS / 1971',42,64,35))
parts.append(outlined_text('Geometric reconstructions of all 22 signs on report page DD67 / PDF 68.',42,106,23,'#52675e'))
for i,item in enumerate(items):
    x=(i%4)*400+50;y=(i//4)*370+135
    svg=etree.fromstring((P/'svg'/f'{item["id"]}.svg').read_bytes())
    body=''.join(etree.tostring(el,encoding='unicode') for el in svg if etree.QName(el).localname not in ['title','desc'])
    parts.append(f'<g id="{item["id"]}" transform="translate({x} {y}) scale(1.5)">{body}</g>')
    parts.append(outlined_text(f'{i+1:02d}  {item["name"]}',x,y+333,19))
parts.append(outlined_text('Icons: reconstructed historical proposals. Labels: modern editorial type, converted to paths.',42,2362,19,'#52675e'))
sheet='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2380" viewBox="0 0 1600 2380"><title>All 22 proposed park symbols, 1971</title>'+''.join(parts)+'</svg>'
(P/'Park_Symbols_1971_Reconstructed.svg').write_text(sheet)
cairosvg.svg2pdf(bytestring=sheet.encode(),write_to=str(P/'Park_Symbols_1971_Reconstructed.pdf'))
print('Wrote outlined SVG and vector PDF contact sheets.')
