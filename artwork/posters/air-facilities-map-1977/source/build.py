#!/usr/bin/env python3
"""Build a layered reconstruction of the 1977/78 Air Facilities Map cover.
Usage: python source/build.py (from any directory); requires fontTools and Pillow.
The photograph is a supplied modern recreation, not the original photograph.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image
from base64 import b64encode
from io import BytesIO
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent.parent
FONTS=Path('/usr/share/fonts/opentype/urw-base35')
PAPER='#f1e8d2'; INK='#262522'; CREAM='#f4ead3'
# Manually authored cubic letter shapes in coordinates of a 2x crop of the rectified cover.
# Main letters and punctuation are independent. Counters use even-odd fill.
S='M420 48 C381 33 342 27 315 30 C269 31 238 56 239 94 C239 139 277 151 323 160 C357 167 382 174 382 194 C382 219 353 234 322 233 C284 232 255 211 247 191 Q240 176 234 192 L225 221 Q222 233 234 238 C260 251 288 259 320 259 C381 259 424 232 424 193 C424 153 392 136 341 126 C303 118 278 110 279 87 C280 66 305 53 333 54 C362 54 381 65 393 90 Q398 102 405 93 L420 57 Q423 50 420 48Z'
U='M2 17 Q2 8 14 6 L42 0 Q53 -2 53 9 L53 116 C53 144 63 158 88 158 C116 158 133 136 133 107 L133 38 Q133 26 123 24 Q114 21 118 13 Q120 8 132 5 L164 0 Q177 -3 177 9 L177 152 Q177 166 185 171 Q195 180 186 187 L154 187 Q144 187 142 176 L140 164 C123 181 101 190 77 190 C31 190 10 160 10 119 L10 39 Q10 28 2 25 Q-4 22 2 17Z'
P='M610 94 Q610 86 621 83 L649 75 Q660 72 661 85 L661 94 C682 76 700 69 722 69 C771 69 805 112 805 165 C805 221 768 259 722 260 Q685 260 662 235 L662 281 Q662 294 673 301 Q685 309 673 315 L615 315 Q602 314 609 304 Q621 294 621 279 L621 117 Q621 104 612 102 Q606 100 610 94Z M663 165 C663 207 680 234 711 234 C741 234 763 205 763 165 C763 122 743 94 712 94 C681 94 663 122 663 165Z'
E='M990 159 Q991 165 978 165 L855 165 C856 206 876 231 911 232 C936 232 953 221 966 201 Q976 187 984 198 Q987 204 979 219 C962 247 936 260 902 260 C847 260 812 222 812 166 C812 111 848 69 903 69 C951 69 989 104 990 159Z M857 141 L948 141 C946 112 927 95 903 95 C877 95 862 113 857 141Z'
R='M0 20 Q-2 13 10 9 L39 0 Q51 -3 51 10 L51 25 Q68 0 89 0 Q115 -2 111 14 L103 42 Q100 55 90 44 Q80 35 70 38 Q51 43 51 81 L51 145 Q51 159 65 165 Q76 174 65 181 L7 181 Q-6 181 0 171 Q12 164 12 150 L12 42 Q12 29 2 27 Q-4 25 0 20Z'
COMMA='M1091 213 C1108 210 1121 222 1122 239 C1122 258 1109 280 1090 291 Q1077 297 1075 287 Q1075 282 1081 275 Q1091 264 1091 254 C1078 254 1071 245 1072 232 C1073 219 1081 214 1091 213Z'
N='M154 282 L204 282 Q213 282 220 291 L332 416 L332 320 Q332 306 319 300 Q303 289 314 282 L369 282 Q383 282 378 292 Q375 298 367 301 Q353 308 353 325 L353 490 Q353 512 340 501 L186 328 L186 458 Q186 475 204 484 Q222 497 207 499 L147 499 Q135 498 143 488 Q148 481 155 479 Q168 472 168 457 L168 324 Q168 310 157 303 Q140 291 154 282Z'
A='M9 17 Q39 0 77 0 C122 0 152 24 152 70 L152 146 Q152 160 164 168 Q174 179 161 184 L125 184 Q114 183 112 168 C95 181 76 187 54 187 C22 187 0 167 0 133 C0 97 28 78 70 73 L112 69 Q111 28 78 28 Q52 28 36 48 Q27 65 19 59 Q15 56 12 45 L9 27 Q7 19 9 17Z M112 93 L77 98 C52 101 41 113 41 133 C41 152 56 162 74 162 C96 162 112 146 112 125Z'
T='M585 282 Q595 277 595 290 L595 323 L624 323 Q635 323 632 335 Q630 350 619 351 L596 351 L596 448 Q596 474 613 478 Q629 480 620 492 Q613 501 593 502 C569 502 555 489 555 462 L555 351 L541 351 Q531 350 534 338 Q536 330 550 324 Q568 307 579 288 Q582 284 585 282Z'
L='M1134 267 L1169 256 Q1184 251 1184 266 L1184 461 Q1184 475 1197 483 Q1212 493 1201 500 L1136 500 Q1122 499 1129 489 Q1143 482 1143 462 L1143 298 Q1143 286 1133 283 Q1125 277 1134 267Z'
shapes=[('super-S',S,''),('super-u',U,'translate(424 75)'),('super-p',P,''),('super-e',E,''),('super-r',R,'translate(986 74)'),('super-comma',COMMA,''),('natural-N',N,''),('natural-a1',A,'translate(367 317) scale(1.03 1)'),('natural-t',T,''),('natural-u',U,'translate(632 321) scale(1.01 .96)'),('natural-r',R,'translate(833 320) scale(1.01 .99)'),('natural-a2',A,'translate(939 317) scale(1.04 1)'),('natural-l',L,'')]
def lettering(text,font_name,box,tracking=0):
    font=TTFont(FONTS/font_name); gs=font.getGlyphSet(); cmap=font.getBestCmap(); x=0; items=[]
    for ch in text:
        g=cmap[ord(ch)]; glyph=gs[g]; bp=BoundsPen(gs);glyph.draw(bp)
        if bp.bounds:
            p=SVGPathPen(gs);glyph.draw(p);items.append((ch,x,p.getCommands(),bp.bounds))
        x+=glyph.width+tracking
    x0=min(x+b[0] for _,x,_,b in items); x1=max(x+b[2] for _,x,_,b in items); y0=min(b[1] for *_,b in items);y1=max(b[3] for *_,b in items)
    X,Y,W,H=box;sx=W/(x1-x0);sy=H/(y1-y0)
    return f'<g transform="translate({X} {Y}) scale({sx:.8f} {-sy:.8f}) translate({-x0} {-y1})">'+''.join(f'<path data-letter="{escape(c)}" transform="translate({x} 0)" d="{d}"/>' for c,x,d,b in items)+'</g>'
def make(web=False):
    title=lettering('Air Facilities Map','URWBookman-Demi.otf',(44,139,906,106),tracking=-32)
    date=lettering('1977/78','NimbusSans-Bold.otf',(896,39,60,15),tracking=-5)
    tagline=lettering('British Columbia, Canada.','URWBookman-Light.otf',(188,1265,649,47),tracking=-37)
    logo=''.join(f'<path id="{id}"'+(f' transform="{t}"' if t else '')+f' d="{d}"/>' for id,d,t in shapes)
    buf=BytesIO(); scene=Image.open(ROOT/'source/scene.jpg').convert('RGB')
    if web: scene.thumbnail((1300,1730))
    scene.save(buf,'JPEG',quality=83 if web else 92,optimize=True)
    uri='data:image/jpeg;base64,'+b64encode(buf.getvalue()).decode()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 1500" width="10in" height="15in" role="img" aria-labelledby="cover-title cover-description">
<title id="cover-title">Air Facilities Map — 1977/78</title>
<desc id="cover-description">Modern mixed-media reconstruction of a photographed historical map cover. The scene is a supplied Gemini-generated image; the title and tagline use approximate outlined substitute glyphs; the large Super, Natural lettering is individually authored cubic vector geometry. The page dimensions and colours are estimated; no original printer master is claimed.</desc>
<defs><clipPath id="air-photo-clip"><rect x="40" y="334" width="914" height="1010"/></clipPath></defs>
<rect id="air-paper" width="1000" height="1500" fill="{PAPER}"/>
<g id="air-date" fill="{INK}">{date}</g>
<g id="air-title" fill="{INK}" stroke-linejoin="round" stroke-linecap="round"><g stroke="{INK}" stroke-width="90">{title}</g><g stroke="{PAPER}" stroke-width="54">{title}</g><g stroke="{INK}" stroke-width="8">{title}</g></g>
<g id="air-photo" clip-path="url(#air-photo-clip)"><image x="40" y="334" width="914" height="1010" preserveAspectRatio="none" xlink:href="{uri}"/></g>
<g id="air-wordmark" fill="{CREAM}" fill-rule="evenodd"><g id="air-stacked" transform="translate(170 1000) scale(.5)">{logo}</g><g id="air-tagline" stroke="{CREAM}" stroke-width="23" stroke-linejoin="round">{tagline}</g></g>
</svg>'''
if __name__=='__main__':
    (ROOT/'poster.svg').write_text(make(),encoding='utf-8')
    (ROOT/'poster-web.svg').write_text(make(web=True),encoding='utf-8')
