#!/usr/bin/env python3
"""Rebuild the BCR herald from manually authored geometric SVG components.

No raster contour extraction and no font software is used.  Only the 14 capital
letters required by the supplied wordmark are reconstructed.  All coordinates
in GLYPHS use a 100-unit cap height; contour overshoots are intentional.
Run with Python 3, from the same directory as flower.svg.
"""
from pathlib import Path
import copy
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'output' / 'British_Columbia_Railway_Vector'
if ROOT.name == 'source':
    OUT = ROOT.parent
OUT.mkdir(parents=True, exist_ok=True)

NS = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', NS)
ET.register_namespace('inkscape', INK)
def tag(t): return '{'+NS+'}'+t

# Hand-drawn Microgramma-family constructions, not a distributed typeface.
# The wide, flat counters, optical stroke contrast and curved R leg follow the
# supplied railway-car photograph.  Closed counters use the even-odd fill rule.
GLYPHS = {
    'B': (122, 'M0 0H85C112 0 120 5 120 27C120 40 117 45 107 48C119 50 122 57 122 74C122 95 116 100 88 100H0Z M29 23V39H79C88 39 92 37 92 31C92 25 89 23 79 23Z M29 59V77H82C92 77 95 74 95 68C95 61 92 59 82 59Z'),
    'R': (121, 'M0 0H85C113 0 121 6 121 31V38C121 52 117 58 105 61C117 63 121 69 121 82V100H92V86C92 76 88 74 78 74H29V100H0Z M29 24V49H78C90 49 93 46 93 37C93 26 90 24 78 24Z'),
    'I': (30, 'M0 0H30V100H0Z'),
    'T': (113.5, 'M0 0H113.5V24H72V100H41.5V24H0Z'),
    'S': (119, 'M117 31H89V28C89 23 86 21 77 21H43C32 21 29 23 29 30C29 36 33 37 45 38L84 40C111 41 119 47 119 68V75C119 96 110 101 79 101H40C10 101 0 95 0 74V67H28V72C28 78 32 80 42 80H78C89 80 91 78 91 71C91 65 88 63 78 63L37 61C10 60 1 54 1 34V25C1 5 12 -1 42 -1H77C108 -1 117 6 117 26Z'),
    'H': (128, 'M0 0H30V36.5H98V0H128V100H98V63H30V100H0Z'),
    'C': (124, 'M124 35H94V33C94 26 90 24 78 24H46C32 24 29 28 29 41V60C29 74 32 77 46 77H79C91 77 95 75 95 66V63H124V70C124 96 116 101 81 101H43C9 101 0 94 0 65V36C0 7 10 -1 43 -1H82C115 -1 124 6 124 31Z'),
    'O': (132, 'M47 -1H85C120 -1 132 6 132 35V65C132 94 122 101 86 101H47C11 101 0 93 0 65V35C0 7 11 -1 47 -1Z M46 24C33 24 30 28 30 41V60C30 74 33 77 46 77H84C98 77 102 74 102 60V41C102 28 98 24 84 24Z'),
    'L': (100, 'M0 0H30V75H100V100H0Z'),
    'U': (128, 'M0 0H30V63C30 75 33 77 48 77H78C94 77 98 74 98 62V0H128V65C128 95 116 101 82 101H45C11 101 0 94 0 64Z'),
    'M': (166, 'M0 0H52L83 66L114 0H166V100H136V25H131L95 100H71L35 25H29V100H0Z'),
    'A': (150, 'M0 100L51.5 0H98.5L150 100H116L107 82H43L34 100Z M52.5 61.5H97.5L79 23H71Z'),
    'W': (208, 'M0 0H31L56 76H61L85 0H122L146 76H151L176 0H208L171 100H126L104 26L82 100H38Z'),
    'Y': (143, 'M0 0H38L71.5 41L105 0H143L87 65V100H57V65Z'),
}

# Optically kerned individual positions. The final line-width adjustment keeps
# the photographed BRITISH:COLUMBIA:RAILWAY ratio of 636:898:759.  This is a
# normalized reconstruction, not a claim of measured historical specifications.
LINES = [
    ('BRITISH', 4, [0,131,261,300,419,458,586], 636/89*100),
    ('COLUMBIA', 127.6, [0,132,272,376,513,688,819,854], 898/89*100),
    ('RAILWAY', 251.2, [0,120.2,273.0,315.7,402.8,591.0,713.0], 759/89*100),
]
DISC = 356
WORD_X = 404.5
WIDTH = WORD_X+LINES[1][3]
HEIGHT = DISC
GREEN = '#005631'
GOLD = '#F8BF00'
WHITE = '#FFFFFF'
INK_COLOR = '#15251D'

def root_svg(w, h, title, desc):
    root = ET.Element(tag('svg'), {'version':'1.1','width':f'{w:g}', 'height':f'{h:g}',
        'viewBox':f'0 0 {w:g} {h:g}', 'role':'img', 'aria-labelledby':'title description'})
    ET.SubElement(root, tag('title'), {'id':'title'}).text=title
    ET.SubElement(root, tag('desc'), {'id':'description'}).text=desc
    return root

DESCRIPTION = ('Independent vector reconstruction of the five-petal British Columbia Railway dogwood herald. '
    'Manual cubic Bezier contours, true circles and custom wordmark glyph outlines. '
    'Main geometry reference: supplied railcar photograph IMG_7919.jpeg; secondary: IMG_7923.png. '
    'Microgramma Bold Extended family documented in The Cariboo issue 31, January 1998. '
    'Colours and precise curves are interpretive reconstruction choices, not authenticated corporate specifications. '
    'No embedded raster images, live fonts or external dependencies.')

def add_flower(parent, x, y, diameter=DISC):
    g = ET.SubElement(parent, tag('g'), {'id':'dogwood-emblem',
        'transform':f'translate({x:g} {y:g}) scale({diameter/1000:g})',
        '{'+INK+'}label':'Dogwood - five-petal reference'})
    flower=ET.parse(ROOT/'flower.svg').getroot()
    for child in flower:
        if child.tag not in (tag('title'),tag('desc')):
            g.append(copy.deepcopy(child))
    return g

def add_wordmark(parent, x, y, color):
    group=ET.SubElement(parent, tag('g'), {'id':'wordmark','fill':color,
        'fill-rule':'evenodd','transform':f'translate({x:g} {y:g})',
        '{'+INK+'}label':'BRITISH COLUMBIA RAILWAY - custom outlines'})
    for word, top, positions, target_width in LINES:
        natural_width=positions[-1]+GLYPHS[word[-1]][0]
        sx=target_width/natural_width
        line=ET.SubElement(group,tag('g'),{'id':'line-'+word.lower(),
            'transform':f'translate(0 {top:g}) scale({sx:.9f} 1)'})
        for i,(letter,left) in enumerate(zip(word,positions)):
            ET.SubElement(line,tag('path'), {'id':f'{word.lower()}-{i+1}-{letter}',
                'transform':f'translate({left:g} 0)','d':GLYPHS[letter][1]})
    return group

def write(root, name):
    seen = {}
    for el in root.iter():
        ident = el.get('id')
        if ident:
            seen[ident] = seen.get(ident, 0) + 1
            if seen[ident] > 1:
                el.set('id', f'{ident}-{seen[ident]}')
    ET.indent(root,space='  ')
    path=OUT/name
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    return path

def horizontal(name, color=WHITE, background=None, margin=12):
    root=root_svg(WIDTH+2*margin,HEIGHT+2*margin,
        'British Columbia Railway - reconstructed five-petal logo',DESCRIPTION)
    if background:
        ET.SubElement(root,tag('rect'), {'id':'background','width':'100%','height':'100%','fill':background})
    add_flower(root,margin,margin)
    add_wordmark(root,margin+WORD_X,margin,color)
    write(root,name)

def emblem():
    root=root_svg(1000,1000,'British Columbia Railway - reconstructed dogwood emblem',DESCRIPTION)
    add_flower(root,0,0,1000)
    write(root,'BCR_Dogwood_Emblem.svg')

def wordmark():
    root=root_svg(LINES[1][3]+24,HEIGHT+24,'British Columbia Railway - outlined wordmark',DESCRIPTION)
    add_wordmark(root,12,12,INK_COLOR)
    write(root,'BCR_Wordmark.svg')

def board():
    # Self-contained vector presentation; labels are the only live text, and are
    # outlined in a separate Inkscape export before delivery.
    root=root_svg(1600,1110,'British Columbia Railway - reconstruction preview',DESCRIPTION)
    ET.SubElement(root,tag('rect'),{'width':'1600','height':'1110','fill':'#F5F3EC'})
    def label(x,y,text,size=18,fill=INK_COLOR,weight='normal',tracking=None):
        attrs={'x':str(x),'y':str(y),'font-family':'DejaVu Sans','font-size':str(size),'fill':fill,'font-weight':weight}
        if tracking: attrs['letter-spacing']=str(tracking)
        ET.SubElement(root,tag('text'),attrs).text=text
    label(58,55,'BRITISH COLUMBIA RAILWAY',28,weight='bold')
    label(58,86,'Five-petal herald / independent vector reconstruction',18)
    ET.SubElement(root,tag('rect'),{'x':'32','y':'118','width':'1536','height':'460','fill':GREEN})
    lock=ET.SubElement(root,tag('g'),{'transform':'translate(87 170) scale(1.01)'})
    add_flower(lock,0,0)
    add_wordmark(lock,WORD_X,0,WHITE)
    label(58,620,'EMBLEM DETAIL',15,weight='bold',tracking='2')
    add_flower(root,80,652,380)
    label(550,620,'LIGHT-BACKGROUND VERSION',15,weight='bold',tracking='2')
    light=ET.SubElement(root,tag('g'),{'transform':'translate(550 674) scale(0.665)'})
    add_flower(light,0,0)
    add_wordmark(light,WORD_X,0,INK_COLOR)
    label(550,984,'Hand-built curves and outlined lettering',21,weight='bold')
    label(550,1014,'Primary proportions checked against the supplied railcar photograph.',17)
    label(550,1041,'Reconstruction colours; no authenticated brand colour specification.',17)
    label(58,1084,'SVG / VECTOR PDF / NO EMBEDDED RASTER ARTWORK',13,tracking='1.5')
    write(root,'BCR_Reconstruction_Preview.svg')

if __name__=='__main__':
    horizontal('BCR_Logo_White_Lettering.svg',WHITE)
    horizontal('BCR_Logo_Dark_Lettering.svg',INK_COLOR)
    horizontal('BCR_Logo_On_Green.svg',WHITE,GREEN,margin=64)
    emblem()
    wordmark()
    board()
    metrics={
        'construction':'Manually authored glyphs and cubic Bezier flower contours; no autotrace.',
        'palette':{'green':GREEN,'gold':GOLD,'white':WHITE,'outline':INK_COLOR},
        'word_widths':[round(line[3],5) for line in LINES],
        'word_width_ratios':[round(line[3]/LINES[1][3],6) for line in LINES],
        'cap_height':100,'disc_diameter':DISC,'emblem_to_wordmark_gap':WORD_X-DISC,
        'wordmark_height':351.2,'artwork_width':WIDTH,'artwork_height':HEIGHT,
        'distinct_glyphs':sorted(GLYPHS),
        'primary_geometry_reference':'IMG_7919.jpeg (user supplied)',
        'secondary_geometry_reference':'IMG_7923.png (user supplied)',
        'font_evidence':'https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%2031.pdf',
        'flower_components':{'petals':5,'leaves':5,'gold_stamens':15},
        'status':'Reference-based reconstruction; not authenticated original artwork.'}
    (OUT/'Construction_Notes.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print('Created',OUT)
