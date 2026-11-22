"""Measured projective registration; no tracing or contour extraction.
The single photo has curved paper and no scale; this is an approximate comparison frame.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]/'review'
SRC=ROOT.parent/'references'/'supplied-poster.webp'
W,H=1000,1450
SRC_QUAD=np.array([[112,96],[1074,96],[1100,1521],[75,1521]],dtype=float)
DST_QUAD=np.array([[0,0],[W,0],[W,H],[0,H]],dtype=float)

def homography(src,dst):
    A=[];b=[]
    for (x,y),(u,v) in zip(src,dst):
        A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        b.extend([u,v])
    hh=np.linalg.solve(np.asarray(A),np.asarray(b))
    return np.r_[hh,1].reshape(3,3)

M=homography(SRC_QUAD,DST_QUAD)
MINV=np.linalg.inv(M);MINV/=MINV[2,2]
def rect_points(pts):
    pp=np.c_[np.asarray(pts),np.ones(len(pts))] @ M.T
    return (pp[:,:2]/pp[:,2,None]).round(3).tolist()

im=Image.open(SRC).convert('RGB')
rect=im.transform((W,H),Image.Transform.PERSPECTIVE,MINV.ravel()[:8],resample=Image.Resampling.BICUBIC,fillcolor='white')
rect.save(ROOT/'reference_rectified.png')

# Manually selected design vertices at the centre of the white separator stroke.
yellow_boundary=[
 [589,610], [531,742], [513,746], [405,650], [404,790], [387,800],
 [250,744], [303,882], [295,900], [145,900], [242,1009], [237,1034],
 [121,1089], [118,1266], [1070,1267], [1067,1084], [948,1033],
 [941,1006], [1041,899], [896,898], [880,881], [933,744], [795,798],
 [777,788], [776,648], [669,746], [649,742]
]
left_blue=[[117,99],[398,96],[403,788],[387,799],[249,743],[270,795],[115,651]]
right_blue=[[780,96],[1066,100],[1070,649],[915,798],[934,743],[795,798],[778,788]]
left_upper_red=[[114,662],[272,817],[301,882],[293,896],[219,897],[112,795]]
right_upper_red=[[1071,660],[1074,795],[968,894],[893,893],[884,878],[910,818]]
# These side/bottom red polygons join behind the white stroke and yellow panel.
left_bottom_red=[[109,958],[190,957],[240,1010],[235,1032],[117,1087],[113,1272],[590,1272],[590,1282],[105,1283]]
right_bottom_red=[[995,955],[1078,957],[1084,1285],[590,1282],[590,1272],[1074,1273],[1071,1080],[949,1030],[945,1009]]
central_red=[[517,95],[658,95],[659,741],[648,739],[589,609],[531,740],[519,743]]
landmarks={
'yellow_boundary_white_stroke_centre':yellow_boundary,
'blue_left':left_blue,'blue_right':right_blue,
'red_upper_left':left_upper_red,'red_upper_right':right_upper_red,
'red_lower_left':left_bottom_red,'red_lower_right':right_bottom_red,
'red_centre':central_red,
'credit_block_envelope':[[159,1289],[1026,1289],[1030,1514],[155,1514]],
'our_lettering_envelope':[[472,820],[736,820],[736,935],[472,935]],
'british_lettering_envelope':[[299,923],[875,923],[875,1105],[299,1105]],
'columbia_lettering_envelope':[[192,1052],[989,1052],[989,1224],[192,1224]],
'pavilion_logo_envelope':[[1008,1396],[1084,1404],[1089,1510],[1008,1505]],
'bob_rogers_logo_envelope':[[119,1451],[187,1451],[187,1500],[119,1500]],
'inuse_mark_envelope':[[125,1375],[206,1375],[206,1435],[125,1435]]
}

# Exclude physical holders and largely illegible reflected areas from numeric colour matching.
artifact_polygons={
 'top_square_magnet':[[253,147],[317,147],[320,217],[251,218]],
 'top_round_magnet':[[388,143],[475,143],[482,233],[390,235]],
 'top_patterned_magnet':[[565,159],[634,156],[642,224],[567,233]],
 'top_right_magnet':[[913,127],[995,124],[1003,207],[915,208]],
 'left_bottom_holder':[[145,1378],[211,1377],[220,1454],[157,1460]],
 'centre_bottom_holder':[[592,1422],[664,1417],[673,1505],[612,1506]],
 'right_bottom_holder':[[903,1411],[982,1412],[999,1505],[933,1508]],
 'strong_yellow_glare':[[570,1133],[693,1102],[1014,1137],[1071,1210],[1071,1268],[553,1269]],
 'credit_glare':[[643,1283],[1067,1283],[1082,1477],[658,1478]]
}
mask=Image.new('L',(W,H),255);md=ImageDraw.Draw(mask)
for poly in artifact_polygons.values():
 md.polygon([tuple(p) for p in rect_points(poly)],fill=0)
# Avoid cropped/bent paper boundary for quantitative comparisons.
md.rectangle((0,0,W-1,H-1),outline=0,width=12)
mask.save(ROOT/'comparison_validity_mask.png')

viz=rect.copy();d=ImageDraw.Draw(viz)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
except: f=ImageFont.load_default()
poly=rect_points(yellow_boundary)
d.line([tuple(p) for p in poly+[poly[0]]],fill='#00e0d0',width=2)
for i,(x,y) in enumerate(poly):
 d.ellipse((x-3,y-3,x+3,y+3),fill='#e000cd');d.text((x+5,y-12),str(i),font=f,fill='#000000',stroke_width=2,stroke_fill='#ffffff')
for x in [398,517,658,780]:
 p=rect_points([[x,100],[x,600]])
 d.line([tuple(t) for t in p],fill='#00e0d0',width=1)
viz.save(ROOT/'measured_landmarks.png')

payload={
 'method':'Manually selected quadrilateral projective registration; manually measured design vertices; no auto-tracing.',
 'source':str(SRC),'source_size_px':list(im.size),
 'working_artboard_px':[W,H],
 'physical_dimensions':'unknown; the 1000:1450 frame is a working estimate, not a documented original paper size',
 'source_paper_quad_px':SRC_QUAD.tolist(),'destination_quad_px':DST_QUAD.tolist(),
 'source_to_rectified_homography':M.tolist(),'rectified_to_source_homography':MINV.tolist(),
 'source_landmarks':landmarks,
 'rectified_landmarks':{k:rect_points(v) for k,v in landmarks.items()},
 'artifact_masks_source':artifact_polygons,
 'white_separator_stroke_source_px':{'typical':7,'range':[5,9]},
 'unrecoverable_from_photo':['exact original physical dimensions','calibrated ink colours','art hidden by magnets and holders','nonlinear paper curl'],
 'cautions':['Do not build a permanent asymmetry from small photo deviations. The main sunburst/ray motif is strongly bilateral.',
             'The red strip along the bottom is visibly curved in the photo; draw the original baseline straight.',
             'Horizontal title/credit baselines need local optical correction; one homography cannot flatten curved paper.',
             'RGB difference scoring is dominated by paper ageing, lighting, and glare. Use geometry and glyph-edge checks separately.']
}
(ROOT/'registration.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps({'files':[p.name for p in ROOT.iterdir()],'M':M.tolist(),'yellow_landmarks_rectified':payload['rectified_landmarks']['yellow_boundary_white_stroke_centre']},indent=2))
