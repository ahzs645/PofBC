"""Geometric reconstruction of the border, field, mountains and gull.

The landmark lists below are sparse, manually chosen construction measurements.
They fit eight smooth cubic arcs for each squircle-like perimeter; no bitmap
contour is converted into a vector path. All illustration paths are authored
explicitly. The source is only used separately for comparison.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
CREAM = '#fce6a3'
TEAL = '#1da4a9'
GREEN = '#047634'
NAVY = '#031e24'
INK = '#070a09'
GOLD = '#efb247'

def n(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.')

def fit_arc(p0, p3, tangent0, tangent3, landmarks):
    """Two tangent handles plus landmark parameters, for one cubic arc."""
    p0, p3 = np.array(p0, float), np.array(p3, float)
    u, v = np.array(tangent0, float), np.array(tangent3, float)
    u /= np.linalg.norm(u)
    v /= np.linalg.norm(v)
    xy = np.array(landmarks, float)
    chord = np.linalg.norm(p3-p0)
    ts = np.linalg.norm(xy-p0, axis=1) / chord
    ts = np.clip(ts, .01, .99)
    def residual(z):
        a,b = z[:2]
        t = z[2:,None]
        curve = (1-t)**3*p0 + 3*(1-t)**2*t*(p0+a*u) + 3*(1-t)*t*t*(p3-b*v) + t**3*p3
        return (curve-xy).ravel()
    x = np.r_[chord*.43,chord*.43,ts]
    result = least_squares(residual,x,bounds=(np.r_[0,0,np.zeros(len(ts))],np.r_[chord*1.6,chord*1.6,np.ones(len(ts))]),max_nfev=2000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
    a,b = result.x[:2]
    p1,p2 = p0+a*u,p3-b*v
    return 'C '+' '.join(n(k) for p in [p1,p2,p3] for k in p), {'max_landmark_error_px':round(float(np.linalg.norm(residual(result.x).reshape(-1,2),axis=1).max()),3),'handles':[p1.tolist(),p2.tolist()]}

OUTER = [
 ((677,24),(1208,150),(1,0),(1.27,1),[(818,30),(956,50),(1054,75),(1123,100),(1172,125)]),
 ((1208,150),(1334,589),(1.27,1),(0,1),[(1235,175),(1255,200),(1281,250),(1298,300),(1310,350),(1319,400),(1326,450),(1331,500),(1334,550)]),
 ((1334,589),(1215,1000),(0,1),(-1.16,1),[(1333,650),(1329,700),(1323,750),(1314,800),(1302,850),(1284,900),(1258,950)]),
 ((1215,1000),(677,1127),(-1.16,1),(-1,0),[(1139,1050),(981,1100),(853,1120),(753,1127)]),
 ((677,1127),(140,1000),(-1,0),(-1.16,-1),[(600,1127),(499,1120),(372,1100),(215,1050)]),
 ((140,1000),(20.5,589),(-1.16,-1),(0,-1),[(97,950),(71,900),(53,850),(41,800),(32,750),(26,700),(22,650)]),
 ((20.5,589),(145,150),(0,-1),(1.27,-1),[(20,550),(23,500),(28,450),(35,400),(45,350),(56,300),(73,250),(98,200),(119,175)]),
 ((145,150),(677,24),(1.27,-1),(1,0),[(183,125),(233,100),(300,75),(390,50),(513,30),(615,24)]),
]

INNER = [
 ((676,102),(1144,200),(1,0),(1.18,1),[(761,105),(818,110),(920,125),(1025,150),(1099,175)]),
 ((1144,200),(1247.5,587),(1.18,1),(0,1),[(1169,225),(1187,250),(1199,275),(1208,300),(1222,350),(1232,400),(1239,450),(1244,500),(1247,550)]),
 ((1247.5,587),(1127,950),(0,1),(-1.6,1),[(1247,600),(1245,650),(1240,700),(1233,750),(1223,800),(1208,850),(1183,900),(1161,925)]),
 ((1127,950),(677,1040),(-1.6,1),(-1,0),[(1075,975),(994,1000),(896,1020),(823,1030),(750,1036)]),
 ((677,1040),(228,950),(-1,0),(-1.6,-1),[(600,1036),(528,1030),(459,1020),(363,1000),(279,975)]),
 ((228,950),(103.5,587),(-1.6,-1),(0,-1),[(194,925),(173,900),(146,850),(130,800),(119,750),(112,700),(107,650),(104,600)]),
 ((103.5,587),(207,200),(0,-1),(1.18,-1),[(105,550),(109,500),(114,450),(122,400),(132,350),(145,300),(154,275),(166,250),(182,225)]),
 ((207,200),(676,102),(1.18,-1),(1,0),[(250,175),(322,150),(430,125),(531,110),(588,105),(640,102)]),
]

def perimeter(arcs):
    d='M '+' '.join(n(v) for v in arcs[0][0])
    reports=[]
    for args in arcs:
        curve,report=fit_arc(*args)
        d+=' '+curve
        reports.append(report)
    return d+' Z',reports

outer,outer_report=perimeter(OUTER)
inner,inner_report=perimeter(INNER)
base = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1354" height="1161" viewBox="0 0 1354 1161">
<g id="border-and-field">
<title>Reconstructed smooth eight-arc sticker perimeter and inner field</title>
<path id="outer-gold-edge" fill="{GOLD}" d="{outer}"/>
<path id="cream-border" fill="{CREAM}" d="{outer}" transform="translate(677 575.5) scale(.994 .9928) translate(-677 -575.5)"/>
<path id="teal-field" fill="{TEAL}" d="{inner}"/>
</g>
<g id="mountains">
<title>Manually constructed mountain ridge with three snow caps</title>
<path id="mountain-mass" fill="{GREEN}" d="M 125.6 652.2 C 171.4 521.8 223.3 403.7 287.2 314.8 L 410.1 173.2 L 486.8 237.9 L 547.2 198.5 L 599.4 242.9 L 744.1 382.9 L 834.4 312.8 L 923.9 386.1 L 1037.4 294.8 L 1126.2 376.4 C 1180.2 421.4 1212.7 522.7 1240.4 650.2 Z"/>
<path id="snow-cap-west" fill="{CREAM}" d="M 287.2 314.8 L 410.1 173.2 L 486.8 237.9 L 547.2 198.5 L 599.4 242.9 C 542.6 275.9 484.9 288.2 426.1 262.3 C 383.8 300.5 333.4 321.7 287.2 314.8 Z"/>
<path id="snow-cap-centre" fill="{CREAM}" d="M 782.1 353.4 L 834.4 312.8 L 894.4 362.1 C 859.8 368.8 825.0 364.6 782.1 353.4 Z"/>
<path id="snow-cap-east" fill="{CREAM}" d="M 946.9 367.6 L 1037.4 294.8 L 1126.2 376.4 C 1093.5 384.6 1061.1 372.2 1045.1 354.1 C 1023.4 376.9 990.9 377.7 946.9 367.6 Z"/>
</g>
</svg>'''

gull=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1354" height="1161" viewBox="0 0 1354 1161">
<g id="gull">
<title>Hand-drawn soaring gull, with separate feather tips and eye</title>
<path id="gull-cream-silhouette" fill="{CREAM}" d="M 376.9 345.5 C 373.2 371.8 383.6 401.5 409.7 404.8 C 433.2 407.7 450.1 393.5 472.7 377.5 C 669.0 224.4 765.1 196.983 837.5 185.4 C 876.4 174.4 921.5 170.4 961.8 174.7 C 966.5 175.1 967.1 177.9 963.4 181.2 C 927.9 213.2 886.7 239.2 842.0 251.9 C 790.9 266.5 735.4 277.4 684.8 293.6 C 640.7 308.0 601.7 341.9 585.2 366.9 C 575.2 382.3 578.4 392.7 591.3 398.4 C 608.8 406.1 629.2 402.1 646.3 413.2 C 656.5 419.1 669.2 420.2 679.4 419.1 C 684.4 418.5 686.8 423.1 681.8 425.3 C 660.7 431.9 642.4 438.8 623.4 448.4 C 568.7 475.0 515.2 479.5 466.3 464.7 C 447.1 457.7 432.3 467.3 418.9 484.5 C 402.3 505.9 390.2 535.0 379.0 565.5 C 361.5 603.9 347.8 634.1 338.0 649.5 Q 273.0 749.5 240.1 834.5 C 238.3 837.6 236.3 837.9 234.8 829.1 C 229.2 796.2 234.4 746.5 243.4 708.4 C 261.9 632.6 318.5 549.4 397.3 452.6 C 353.5 447.0 305.1 464.1 271.7 483.2 C 301.1 434.3 338.9 387.9 374.9 346.4 Q 376.7 344.3 376.9 345.5 Z"/>
<path id="gull-upper-dark-feathers" fill="{NAVY}" d="M 837.5 185.4 C 876.4 174.4 921.5 170.4 961.8 174.7 C 966.5 175.1 967.1 177.9 963.4 181.2 C 929.9 211.7 891.4 236.6 849.6 249.6 L 891.3 222.9 L 850.4 237.8 L 910.2 202.6 L 849.1 225.1 L 900.5 197.0 L 848.3 213.8 L 891.9 191.7 L 848.7 203.7 L 884.0 186.3 L 848.5 194.2 L 876.2 181.4 C 861.8 183.2 848.9 187.9 837.5 185.4 Z"/>
<path id="gull-lower-dark-feathers" fill="{NAVY}" d="M 243.4 708.4 L 259.8 691.9 L 250.0 718.0 L 262.7 698.4 L 249.5 742.0 L 273.2 699.2 L 252.2 762.8 L 285.7 701.3 L 261.5 765.0 L 306.952 699.5 Q 264.615 771.164 240.1 834.5 C 238.3 837.6 236.3 837.9 234.8 829.1 C 229.2 796.2 234.4 746.5 243.4 708.4 Z"/>
<circle id="gull-eye" fill="{INK}" cx="634.4" cy="423.2" r="4.3"/>
</g>
</svg>'''

(HERE/'base.svg').write_text(base)
(HERE/'gull.svg').write_text(gull)
(HERE/'base-landmark-fit.json').write_text(json.dumps({'method':'Sparse manually selected landmark fit; eight cubic arcs per perimeter, fixed endpoint tangents. Not bitmap contour tracing.','outer':outer_report,'inner':inner_report},indent=2))
print('Created base.svg and gull.svg; maximum landmark errors: outer',max(r['max_landmark_error_px'] for r in outer_report),'inner',max(r['max_landmark_error_px'] for r in inner_report))
