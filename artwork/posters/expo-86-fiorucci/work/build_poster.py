"""Rebuild Vittorio's Expo 86 poster with authored Bezier geometry.

The coordinates are deliberately authored in a 1100 x 1600 normalized
registration space. No raster-to-path extraction is used. Export scales this
space to the dealer's listed 635 x 920 mm page proportion.
"""
from pathlib import Path
from copy import deepcopy
import json, subprocess
from lxml import etree as ET

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'output'/'expo-86-vector'
OUT.mkdir(parents=True,exist_ok=True)
SVG='http://www.w3.org/2000/svg'
# Standard Inkscape namespace, used for ordinary named editable layers.
INK='http://www.inkscape.org/namespaces/inkscape'
NS={'svg':SVG,'inkscape':INK}
HEIGHT=1100*920/635
YSCALE=HEIGHT/1600

COLORS={
 'paper':'#F7F5EF', 'red':'#B70F18', 'blue':'#24558F',
 'yellow':'#FFDA0A','green':'#0C602E','lemon':'#F6E579',
 'mint':'#62C5AF','orange':'#EC5006','pink':'#EC477D','ink':'#171716'
}

# Each silhouette is independently constructed. Sharp fin roots and tips are
# explicit nodes; longer body/tail contours use a small set of cubic curves.
SHAPES={
'red':'''M 0,228.5
C 75,186 130,102 213,68
C 260,48 313,45 350,29
C 370,20 393,12 411,2
C 388,24 377,39 358,57
C 328,79 297,100 271,126
C 348,108 415,99 485,99
C 567,96 637,100 700,104
C 741,106 777,116 794,110
C 816,88 839,62 868,53
C 905,40 931,49 969,58
C 1003,67 1039,76 1073,67
C 1054,91 1038,106 1019,119
C 975,145 930,164 886,198
C 928,208 963,232 1001,263
C 1032,293 1062,328 1100,354
C 1066,354 1037,350 1010,345
C 944,331 905,307 848,299
C 798,289 740,297 682,301
C 614,306 552,313 477,311
C 412,305 359,292 303,296
C 327,314 359,338 383,360
C 401,376 417,389 433,401
C 349,391 280,371 227,340
C 159,301 103,256 36,240
Z''',
'blue':'''M 7,339
C 102,350 164,372 258,430
C 317,422 389,410 444,414
C 516,412 564,428 622,442
C 677,454 728,458 774,455
C 756,410 717,363 679,323
C 752,334 800,362 846,398
C 924,444 1009,505 1092,535
C 1017,566 963,604 906,646
C 871,671 843,698 808,714
C 744,745 664,761 602,798
C 626,759 655,726 685,703
C 707,686 732,674 749,659
C 689,658 643,665 591,677
C 538,686 488,695 446,693
C 398,693 344,681 300,683
C 286,704 263,718 238,725
C 203,735 170,734 143,733
C 87,731 46,726 5,751
C 29,705 67,663 104,633
C 141,606 183,589 217,567
C 171,543 146,514 115,478
C 81,433 46,375 7,339
Z''',
'yellow':'''M 0,967
C 70,924 134,871 197,830
C 238,803 276,786 319,780
C 362,774 415,782 461,793
C 414,801 385,836 351,864
C 432,855 484,839 545,827
C 594,816 633,816 678,821
C 710,824 738,830 759,829
C 784,804 800,783 829,774
C 877,758 917,769 958,780
C 1012,790 1063,803 1100,795
C 1074,830 1040,852 998,872
C 963,884 930,893 898,910
C 941,933 979,965 1009,1005
C 1046,1054 1077,1116 1100,1167
C 1052,1139 1017,1129 978,1114
C 924,1098 885,1076 848,1050
C 795,1062 748,1067 700,1070
C 631,1073 579,1070 528,1063
C 462,1052 414,1038 357,1039
C 379,1063 405,1091 430,1116
C 356,1114 289,1098 234,1078
C 154,1047 87,1006 32,980
C 20,974 10,970 0,967
Z''',
'green':'''M 15,1088
C 112,1104 164,1131 229,1183
C 310,1173 392,1156 463,1154
C 534,1152 595,1166 660,1180
C 741,1194 826,1217 891,1216
C 868,1184 844,1138 818,1098
C 907,1129 965,1165 1023,1218
C 1055,1243 1076,1258 1100,1274
C 1058,1300 1032,1322 1007,1346
C 964,1378 930,1401 892,1416
C 843,1430 789,1432 743,1459
C 799,1421 851,1377 896,1332
C 816,1335 726,1371 645,1384
C 621,1408 585,1424 546,1435
C 476,1451 400,1457 339,1481
C 383,1442 436,1409 474,1377
C 420,1370 375,1355 326,1344
C 298,1335 270,1329 245,1334
C 212,1361 185,1379 149,1386
C 107,1389 44,1385 0,1388
C 22,1369 38,1334 69,1312
C 95,1289 135,1272 172,1259
C 134,1241 106,1205 82,1170
C 58,1136 41,1109 15,1088
Z'''
}

# Deliberately irregular quadrilaterals and rounded windows, independent
# objects rather than identical repeated stamps.
WINDOWS={
'lemon':[
 'M 404,167 C 425,166 440,181 439,201 C 439,220 425,233 405,233 C 385,233 369,220 369,200 C 369,183 384,168 404,167 Z',
 'M 506,168 C 526,168 541,181 541,200 C 541,220 525,234 507,234 C 487,234 471,221 471,201 C 471,183 486,168 506,168 Z',
 'M 607,168 C 626,168 641,183 641,202 C 641,221 627,235 608,235 C 589,235 574,222 574,202 C 574,183 588,169 607,168 Z',
 'M 707,168 C 728,168 743,182 742,202 C 742,220 728,233 709,234 C 690,234 674,219 674,201 C 674,183 688,169 707,168 Z'],
'mint':[
 'M 362,522 L 411,521 L 411,575 L 363,575 Z',
 'M 427,522 L 478,521 L 480,575 L 430,575 Z',
 'M 495,520 L 544,521 L 544,574 L 495,574 Z',
 'M 556,519 L 606,520 L 607,575 L 555,574 Z',
 'M 627,520 L 676,520 L 676,574 L 628,574 Z',
 'M 690,520 L 743,519 L 743,574 L 690,574 Z'],
'orange':[
 'M 357,909 L 405,909 L 405,969 L 358,967 Z',
 'M 422,910 L 459,910 L 459,969 L 422,970 Z',
 'M 475,910 L 520,910 L 518,973 L 473,972 Z',
 'M 535,910 L 582,910 L 582,973 L 534,973 Z',
 'M 595,910 L 640,911 L 640,972 L 593,972 Z',
 'M 652,911 L 695,911 L 695,974 L 651,973 Z',
 'M 709,911 L 750,912 L 750,975 L 708,974 Z'],
'pink':[
 'M 400,1245 C 421,1244 436,1259 436,1276 C 436,1296 421,1308 401,1308 C 381,1308 365,1295 365,1277 C 365,1259 379,1246 400,1245 Z',
 'M 502,1241 C 522,1241 534,1256 534,1275 C 534,1294 521,1307 502,1308 C 484,1308 470,1294 470,1276 C 470,1258 483,1242 502,1241 Z',
 'M 606,1242 C 624,1242 637,1258 637,1277 C 637,1297 623,1311 605,1311 C 586,1310 573,1297 573,1278 C 573,1258 586,1243 606,1242 Z',
 'M 700,1244 C 719,1244 733,1260 733,1277 C 733,1298 720,1310 701,1310 C 682,1309 667,1297 667,1279 C 667,1259 681,1244 700,1244 Z']
}

def node(tag, parent=None, **attrs):
 e=ET.Element('{%s}%s'%(SVG,tag))
 for k,v in attrs.items():e.set(k.replace('_','-'),str(v))
 if parent is not None:parent.append(e)
 return e

def layer(parent, ident, name, **attrs):
 g=node('g',parent,id=ident,**attrs)
 g.set('{%s}groupmode'%INK,'layer');g.set('{%s}label'%INK,name)
 return g

def text_layer(parent, source, live_text=False):
 g=layer(parent,'footer','06 — Bilingual footer: '+('editable Nimbus Sans text' if live_text else 'reused outlined Nimbus Sans'))
 targets={'english-copy':(639.5,1501.0,185.0,81.0),
          'french-copy':(846.0,1498.5,222.5,80.0)}
 bounds={'english-copy':(701.03139,1495.0238,200.606,88.8742),
         'french-copy':(937.716,1491.4637,241.884,85.4034)}
 for ident,target in targets.items():
  el=deepcopy(source.xpath('//*[@id="'+ident+'"]')[0])
  x,y,w,h=bounds[ident];tx,ty,tw,th=target
  wrap=node('g',g,id=ident+'-placement',transform=f'translate({tx} {ty}) scale({tw/w} {th/h}) translate({-x} {-y})')
  el.set('fill',COLORS['ink'])
  is_en=ident=='english-copy'
  anchor=700 if is_en else 937
  widths=[.943,.962,1,1,.956] if is_en else [.974,.932,1,1,.936]
  baseline=1508 if is_en else 1504.4399
  # Retain the site's paths. Horizontal placement transforms match the
  # photographed printing's slightly narrower bold lines independently.
  for i,child in enumerate(list(el)):
   child.set('transform',f'translate({anchor} 0) scale({widths[i]} 1) translate({-anchor} 0)')
   if live_text:
    replacement=node('text',x=anchor,y=baseline+18*i,id=child.get('id'),
                     font_family='Nimbus Sans, Helvetica, Arial, sans-serif',font_size='17.8',
                     font_weight='700' if i in [0,1,4] else '400',
                     transform=child.get('transform'),style='font-kerning:none')
    replacement.text=child.get('aria-label')
    el.replace(child,replacement)
  wrap.append(el)

def build(include_signature=True, live_text=False):
 root=ET.Element('{%s}svg'%SVG,nsmap={None:SVG,'inkscape':INK})
 root.set('version','1.1');root.set('width','635mm');root.set('height','920mm')
 root.set('viewBox',f'0 0 1100 {HEIGHT:.9f}')
 node('title',root).text='Expo 86 — Vittorio Fiorucci — reconstructed vector edition'
 node('desc',root).text=('Modern reconstruction from the user-supplied framed photograph. Four independently authored cubic Bezier silhouettes, 21 individual windows, and reused PofBC Expo logo and outlined bilingual footer. Signature is a removable approximate facsimile. Colours are estimated, not measured ink specifications. Catalogue page size 635 x 920 mm; image under frame may be cropped. No embedded raster images.')
 node('metadata',root).text=json.dumps({'artist':'Vittorio Fiorucci','historical_event':'Expo 86','reconstruction_date':'2026-11-21','source':'2_1573519323323_master.jpeg','source_site':'https://projects.ahmadjalil.com/PofBC/?view=posters&poster=expo-86-davidson','catalogue':'https://librairieseksik.fr/livre/1538','method':'Individually authored cubic Bezier geometry; no automatic bitmap tracing','signature':'Approximate editable facsimile; optional','font':'PofBC outlined Nimbus Sans substitute, not authenticated original printing font','logo':'PofBC modern gallery reconstruction, not original printer master','nominal_size_mm':[635,920],'normalization_scale_y':YSCALE,'colors':COLORS},ensure_ascii=False)
 content=node('g',root,id='design',transform=f'scale(1 {YSCALE:.12f})')
 paper=layer(content,'paper','01 — Paper')
 node('rect',paper,x=0,y=0,width=1100,height=1600,fill=COLORS['paper'])
 for i,(key,window) in enumerate(zip(SHAPES,['lemon','mint','orange','pink']),2):
  g=layer(content,key+'-motif',f'{i:02d} — {key.title()} silhouette and {len(WINDOWS[window])} windows')
  node('path',g,id=key+'-silhouette',d=SHAPES[key],fill=COLORS[key])
  windows=node('g',g,id=key+'-windows',fill=COLORS[window])
  for j,d in enumerate(WINDOWS[window],1):node('path',windows,id=f'{key}-window-{j}',d=d)
 source=ET.parse(str(BASE/'research-assets'/'expo86-davidson-full.svg'))
 text_layer(content,source,live_text)
 logo=layer(content,'expo-mark','07 — Expo logo: reused PofBC vector')
 wrap=node('g',logo,id='expo-logo-placement',transform=f'translate(28.0 1415.0) scale({124/133.2} {160/173.904358}) translate(-72 -1404.095642)')
 el=deepcopy(source.xpath('//*[@id="poster-expo-logo"]')[0]);wrap.append(el)
 # PofBC source geometry is preserved; only placement and colour change.
 for e in el.iter():
  if isinstance(e.tag,str):
   for attr in ['fill','stroke']:
    if e.get(attr) and e.get(attr) not in ['none','transparent']:e.set(attr,COLORS['ink'])
 if include_signature and (BASE/'work/signature-group.svg').exists():
  sig=layer(content,'signature','08 — Signature facsimile: approximate and removable')
  root_sig=ET.parse(str(BASE/'work/signature-group.svg')).getroot()
  if root_sig.tag.split('}')[-1]=='g':sig.append(deepcopy(root_sig))
  else:
   for e in root_sig:
    if isinstance(e.tag,str) and e.tag.split('}')[-1] not in ['metadata','title','desc']:sig.append(deepcopy(e))
 return root

def main():
 for suffix,withsig,livetext in [('',True,False),('-unsigned',False,False),('-editable-text',True,True)]:
  root=build(withsig,livetext)
  path=OUT/f'Expo86_Vittorio_Reconstructed{suffix}.svg'
  ET.ElementTree(root).write(str(path),encoding='UTF-8',xml_declaration=True,pretty_print=True)
 (OUT/'palette.json').write_text(json.dumps(COLORS,indent=2))
 print(json.dumps({'svg':str(OUT/'Expo86_Vittorio_Reconstructed.svg'),'page_mm':[635,920],'shape_segments':{k:v.count('C') for k,v in SHAPES.items()},'windows':sum(map(len,WINDOWS.values()))},indent=2))

if __name__=='__main__':main()
