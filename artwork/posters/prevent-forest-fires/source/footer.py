"""Constructed poster lettering: geometric masters, never pixel tracing.

The glyph skeletons are bespoke squared/chamfered display capitals.
Each word is optically fitted to the supplied rectified photograph.
All visible geometry is SVG paths; no fonts, images, or external resources.
"""
from pathlib import Path

IVORY = '#F5F0D7'
YELLOW = '#F5E928'
ORANGE = '#F77913'
INK = '#242332'


def poly(points):
    return 'M' + ' L'.join(f'{x:g},{y:g}' for x, y in points) + ' Z'


def glyphs(weight=16):
    """100-unit capitals; modest chamfers preserve the printed display idiom."""
    t = weight
    # The exact same shapes are used wherever a capital is repeated.
    g = {}
    g['A'] = (62, poly([(0,100),(22,0),(41,0),(63,100),(45,100),(40,77),(21,77),(17,100)])
                  + poly([(25,61),(37,61),(30.5,23)]))
    g['B'] = (57, 'M0,0 H46 Q55,0 55,10 V39 Q55,47 47,49 Q57,51 57,61 V89 Q57,100 45,100 H0 Z'
                  + f'M{t},16 H35 Q40,16 40,21 V38 Q40,43 35,43 H{t} Z'
                  + f'M{t},58 H36 Q42,58 42,64 V78 Q42,84 36,84 H{t} Z')
    g['C'] = (54, f'M12,0 H54 V16 H{t+5} Q{t},16 {t},22 V78 Q{t},84 {t+5},84 H54 V100 H12 Q0,100 0,88 V12 Q0,0 12,0 Z')
    g['D'] = (56, 'M0,0 H44 Q56,0 56,12 V88 Q56,100 44,100 H0 Z'
                  + f'M{t},16 H34 Q40,16 40,23 V77 Q40,84 34,84 H{t} Z')
    g['E'] = (50, f'M0,0 H50 V16 H{t} V41 H45 V57 H{t} V84 H50 V100 H0 Z')
    g['F'] = (50, f'M0,0 H50 V16 H{t} V43 H44 V59 H{t} V100 H0 Z')
    g['H'] = (58, f'M0,0 H{t} V42 H{58-t} V0 H58 V100 H{58-t} V58 H{t} V100 H0 Z')
    g['I'] = (20, 'M1.5,0 H18.5 V100 H1.5 Z')
    g['L'] = (48, f'M0,0 H{t} V84 H48 V100 H0 Z')
    g['M'] = (76, f'M0,100 V0 H17 L38,49 L59,0 H76 V100 H{76-t} V35 L43,72 H33 L{t},35 V100 Z')
    g['N'] = (60, f'M0,100 V0 H17 L{60-t},64 V0 H60 V100 H43 L{t},36 V100 Z')
    g['O'] = (58, 'M12,0 H46 Q58,0 58,12 V88 Q58,100 46,100 H12 Q0,100 0,88 V12 Q0,0 12,0 Z'
                  + f'M{t+5},16 H{53-t} Q{58-t},16 {58-t},22 V78 Q{58-t},84 {53-t},84 H{t+5} Q{t},84 {t},78 V22 Q{t},16 {t+5},16 Z')
    g['P'] = (57, 'M0,0 H45 Q57,0 57,12 V50 Q57,62 45,62 H16 V100 H0 Z'
                  + f'M{t},16 H35 Q41,16 41,22 V40 Q41,46 35,46 H{t} Z')
    g['R'] = (59, 'M0,0 H45 Q56,0 56,11 V49 Q56,58 45,61 L60,100 H42 L28,63 H16 V100 H0 Z'
                  + f'M{t},16 H34 Q40,16 40,22 V40 Q40,46 34,46 H{t} Z')
    g['S'] = (54, 'M12,0 H54 V16 H22 Q16,16 16,22 V36 Q16,42 22,42 H42 Q54,42 54,54 V88 Q54,100 42,100 H0 V84 H32 Q38,84 38,78 V64 Q38,58 32,58 H12 Q0,58 0,46 V12 Q0,0 12,0 Z')
    g['T'] = (60, f'M0,0 H60 V16 H{30+t/2:g} V100 H{30-t/2:g} V16 H0 Z')
    g['U'] = (58, f'M0,0 H{t} V77 Q{t},84 {t+6},84 H{52-t} Q{58-t},84 {58-t},77 V0 H58 V86 Q58,100 44,100 H14 Q0,100 0,86 Z')
    g['V'] = (61, 'M0,0 H17 L31,76 L45,0 H62 L40,100 H22 Z')
    g['Y'] = (62, 'M0,0 H18 L32,42 L46,0 H64 L40,61 V100 H24 V61 Z')
    return g


def heavy_glyphs():
    """Broad lower slogan: thick strokes and blunt angular joins."""
    g = {}
    g['A'] = (69, poly([(0,100),(27,0),(49,0),(71,100),(49,100),(44,78),(23,78),(17,100)])
                  + poly([(28,60),(41,60),(35,24)]))
    g['B'] = (69, 'M0,0 H55 Q69,0 69,13 V37 Q69,47 59,50 Q69,51 69,62 V86 Q69,100 55,100 H0 Z'
                  + 'M22,18 H43 Q48,18 48,23 V36 Q48,42 42,42 H22 Z'
                  + 'M22,58 H42 Q48,58 48,64 V77 Q48,83 42,83 H22 Z')
    g['E'] = (61, 'M0,0 H61 V18 H22 V40 H56 V58 H22 V82 H61 V100 H0 Z')
    g['I'] = (25, 'M1.5,0 H23.5 V100 H1.5 Z')
    g['L'] = (57, 'M0,0 H22 V82 H57 V100 H0 Z')
    g['M'] = (86, 'M0,100 V0 H21 L43,46 L65,0 H86 V100 H64 V39 L47,72 H38 L22,40 V100 Z')
    g['O'] = (68, 'M15,0 H53 Q68,0 68,15 V85 Q68,100 53,100 H15 Q0,100 0,85 V15 Q0,0 15,0 Z'
                  + 'M27,18 H41 Q46,18 46,24 V76 Q46,82 41,82 H27 Q22,82 22,76 V24 Q22,18 27,18 Z')
    g['P'] = (68, 'M0,0 H53 Q68,0 68,15 V50 Q68,64 53,64 H22 V100 H0 Z'
                  + 'M22,18 H41 Q46,18 46,24 V40 Q46,47 40,47 H22 Z')
    g['R'] = (71, 'M0,0 H54 Q69,0 69,15 V46 Q69,58 56,62 L72,100 H48 L34,64 H22 V100 H0 Z'
                  + 'M22,18 H43 Q48,18 48,24 V40 Q48,47 42,47 H22 Z')
    g['S'] = (64, 'M15,0 H64 V18 H29 Q22,18 22,25 V34 Q22,41 29,41 H49 Q64,41 64,56 V85 Q64,100 49,100 H0 V82 H35 Q42,82 42,75 V66 Q42,59 35,59 H15 Q0,59 0,44 V15 Q0,0 15,0 Z')
    g['T'] = (67, 'M0,0 H67 V18 H44.5 V100 H22.5 V18 H0 Z')
    g['Y'] = (70, 'M0,0 H22 L37,41 L52,0 H74 L47.5,62 V100 H25.5 V62 Z')
    return g


def word(text, box, glyphset, tracking=12, shear=0, fill=IVORY, ident='word', glyph_fits=None):
    x, y, width, height = box
    positions = []
    cursor = 0
    for c in text:
        if c == ' ':
            cursor += 45
            continue
        w, d = glyphset[c]
        positions.append((c, cursor, d))
        cursor += w + tracking
    cursor -= tracking
    sx = width / (cursor + shear * 100)
    sy = height / 100
    if glyph_fits is None:
        out = [f'<g id="{ident}" aria-label="{text}" fill="{fill}" fill-rule="evenodd" transform="matrix({sx:.7f} 0 {-shear*sx:.7f} {sy:.7f} {x+shear*100*sx:.5f} {y:g})">']
        for i, (c, x0, d) in enumerate(positions):
            out.append(f'<path id="{ident}-{c}-{i+1}" transform="translate({x0:g} 0)" d="{d}"/>')
    else:
        # Bounded optical fits of the existing masters. Each tuple is
        # (horizontal scale, vertical scale, x shift, y shift), in poster
        # space about that glyph's baseline-left anchor and the word's top.
        # These placements are authored from visible letter landmarks; no
        # raster outlines or new glyph contours are generated.
        out = [f'<g id="{ident}" aria-label="{text}" fill="{fill}" fill-rule="evenodd">']
        for i, (c, x0, d) in enumerate(positions):
            fx, fy, dx, dy = glyph_fits[i]
            anchor = x + x0 * sx
            tx = anchor + dx + fx * shear * 100 * sx
            out.append(f'<path id="{ident}-{c}-{i+1}" transform="matrix({fx*sx:.7f} 0 {-fx*shear*sx:.7f} {fy*sy:.7f} {tx:.5f} {y+dy:g})" d="{d}"/>')
    out.append('</g>')
    return '\n'.join(out)


def build_footer():
    g = glyphs()
    h = heavy_glyphs()
    out = ['<g id="lower-slogan" aria-label="Fire destroys timber and payrolls! British Columbia Forest Service">']
    # Source-placed brush scratches. Both edges are hand-designed curves:
    # unequal taper, small bends, and separated fragments preserve the printed
    # marks without treating them as generic triangular rays or bitmap traces.
    sparks = [
        ('upper-left-long', 'M15 1162 C24 1171 35 1180 42 1191 C31 1182 23 1175 15 1162 Z'),
        ('upper-left-fragment', 'M10 1159 Q13 1160 16 1165 Q12 1163 10 1159 Z'),
        ('left-diagonal', 'M0 1184 C12 1190 24 1197 31 1204 C18 1197 8 1192 0 1186 Z'),
        ('above-F-long', 'M56 1133 C65 1143 74 1153 81 1168 C74 1163 64 1147 56 1133 Z'),
        ('above-F-fragment', 'M50 1127 L54 1131 L55 1135 L52 1132 Z'),
        ('above-F-upright', 'M127 1115 C130 1124 133 1136 131 1145 C129 1141 129 1126 127 1115 Z'),
        ('above-I-long', 'M183 1154 C185 1142 188 1126 191 1115 L194 1115 C191 1128 188 1145 183 1154 Z'),
        ('above-R-short', 'M229 1153 C230 1146 233 1137 235 1132 C237 1140 232 1149 229 1153 Z'),
        ('above-E-long', 'M260 1140 C263 1131 267 1122 270 1115 L273 1115 C268 1125 265 1134 260 1140 Z'),
        ('above-E-right', 'M295 1139 C298 1131 302 1126 305 1122 C303 1129 299 1135 295 1139 Z'),
        ('upper-right-ray', 'M319 1162 C328 1156 340 1150 350 1146 L350 1149 C337 1154 326 1161 319 1164 Z'),
        ('above-R-fleck', 'M207 1135 Q211 1131 216 1130 Q213 1133 207 1135 Z'),
        ('left-horizontal', 'M0 1276 C12 1272 23 1269 31 1268 C25 1272 12 1274 0 1278 Z'),
        ('left-lower-ray', 'M0 1333 C8 1328 17 1322 23 1317 C19 1325 8 1331 0 1335 Z'),
        ('bottom-left-ray', 'M8 1388 C15 1380 22 1372 28 1366 Q30 1365 29 1368 C24 1375 17 1382 8 1388 Z'),
        ('bottom-left-fragment', 'M4 1390 L8 1386 L10 1384 L8 1388 Z'),
        ('below-F-upright', 'M106 1376 C104 1364 107 1350 109 1340 C109 1353 108 1363 108 1374 Z'),
        ('below-I-sliver', 'M144 1327 C147 1337 148 1348 152 1358 C147 1353 146 1345 145 1337 Z'),
        ('below-R-short', 'M184 1316 C189 1323 192 1335 194 1344 C189 1339 188 1327 184 1316 Z'),
        ('below-R-long', 'M217 1308 C224 1320 233 1336 240 1351 C231 1343 222 1324 217 1308 Z'),
        ('lower-right-ray', 'M251 1296 C261 1306 273 1320 280 1330 C268 1320 258 1308 251 1296 Z'),
        ('right-diagonal', 'M275 1277 C286 1282 296 1288 304 1295 C293 1290 283 1284 275 1277 Z'),
        ('right-horizontal', 'M312 1251 C321 1253 332 1255 340 1259 C329 1258 319 1255 312 1251 Z'),
    ]
    out.append('<g id="lettering-sparks" fill="'+ORANGE+'">')
    out.extend(f'<path id="fire-scratch-{name}" d="{d}"/>' for name, d in sparks)
    out.append('</g>')
    out.append('<g id="fire-brush-lettering" aria-label="Fire" fill="'+YELLOW+'" fill-rule="evenodd">')
    out.append('<path id="fire-F" d="M35,1219 Q85,1178 145,1154 L141,1192 Q97,1209 56,1233 L75,1226 L70,1262 L99,1249 L96,1278 L67,1292 L63,1348 L36,1360 L48,1242 L32,1250 Z"/>')
    out.append('<path id="fire-I" d="M117,1236 L143,1223 L134,1314 L109,1326 Z"/>')
    out.append('<path id="fire-R" d="M151,1220 Q186,1195 207,1187 Q224,1182 226,1197 Q229,1224 207,1248 L227,1275 L203,1285 L187,1261 L178,1266 L178,1295 L152,1306 L155,1237 L149,1241 Z M172,1228 Q190,1213 203,1215 Q199,1225 181,1237 L184,1228 Z"/>')
    out.append('<path id="fire-E" d="M237,1175 Q265,1161 299,1152 L296,1181 Q268,1188 248,1199 L269,1192 L267,1217 L260,1221 L257,1235 L295,1222 L292,1249 Q268,1266 249,1264 Q233,1262 235,1242 L241,1196 L233,1200 Z"/>')
    out.append('</g>')
    out.append(word('DESTROYS', (335,1187,294,47), g, tracking=15, ident='destroys'))
    out.append(word('TIMBER', (644,1176,339,61), h, tracking=13, shear=.40, ident='timber', glyph_fits=[
        (.88,.95082,.9,0), (.88,.95082,-4.8,0), (.93,.96721,1,0),
        (.90,.95082,6,1), (.90,.96721,10.1,1), (.87,.95082,13.1,2),
    ]))
    out.append(word('AND', (360,1274,108,47), g, tracking=10, ident='and'))
    out.append(word('PAYROLLS', (486,1264,440,60), h, tracking=13, shear=.40, ident='payrolls', glyph_fits=[
        (.88,.96667,1.1,-2), (.93,.96667,-9,-1), (1,.96667,-12,-1), (.93,.96667,-7,-1),
        (.88,.98333,-.6,-1), (.975,.96667,3,0), (1,.96667,1,0), (.945,.96667,2,0),
    ]))
    out.append('<g id="yellow-exclamation" fill="'+YELLOW+'"><path d="M935,1306 L927,1300 L988,1220 L998,1238 Z"/><path d="M937,1320 C937,1326 934,1330 928,1330 C922,1330 919,1326 920,1320 C921,1314 924,1311 930,1311 C935,1311 938,1315 937,1320 Z"/></g>')
    out.append(word('BRITISH COLUMBIA FOREST SERVICE', (37,1388,936,27), g, tracking=34, fill=YELLOW, ident='forest-service-credit'))
    out.append('</g>')
    return '\n'.join(out)


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="340" viewBox="0 1100 1000 340"><rect x="0" y="1100" width="1000" height="340" fill="'+INK+'"/>'+build_footer()+'</svg>'
    (root/'footer-preview.svg').write_text(svg)
