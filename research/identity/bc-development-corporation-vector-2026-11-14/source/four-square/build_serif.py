"""Construct the serif Development Corporation wordmark from intentional paths.

No raster outlines or tracing are used. The source raster supplies measured
letter boxes only. Glyphs use a 61-unit capital height, with independently
designed contours, shared structures and optically adjusted occurrence widths.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent

# (design width, path). All closed paths, with explicitly open P bowl contours.
GLYPHS={
'D':(58,"M0 0H36C49 4 57 15 58 29C58 42 52 53 40 59L36 61H0V59.4L5.4 54.7V8C5.4 4.3 3.7 2.3 0 1.6Z M13.4 3V54.8C13.4 57.2 14.7 58 17.4 58H35C47 51 54 39 51 24C48 12 39 4 27 3Z"),
'E':(46,"M0 0H41.8L42.3 9.1H39.9C39 5.2 36.2 3 32.8 3H16C14 3 13 4 13 6V27H31C34 27 35 26 36.1 23H38V37H36C34.8 33.5 33.5 32 30 32H13V54.3C13 56.9 14.6 58 17.5 58H30C35.4 58 39.2 55 43.3 51.3L46 52.5L43.8 58.5L40.2 61H0V59.2C4.7 58.4 6.2 56.9 6.2 53.3V7.6C6.2 4.6 4.2 2.7 0 1.8Z"),
'V':(60,"M0 0H17V1.5C12.5 2.2 12.3 4.9 14 9.4L35 51.6L49.7 12.7C52.3 5.7 51.1 2.7 46.9 1.5V0H60V1.6C56.8 2.4 55.6 5.1 53.8 10.1L34.6 61H29.8L7.4 12C4.9 6.6 3.2 3.1 0 1.6Z"),
'L':(45,"M0 0H17V1.6C13.2 2.4 13 3.9 13 8V57.4H29C34.3 57.4 38.3 54.8 42.5 51.2H45V55C41 59.7 38 61 34 61H0V59.5C4.7 58.5 5.2 57 5.2 53V8C5.2 4.2 3.9 2.3 0 1.6Z"),
'O':(68,"M24 0H43C56 1 66 10 67.5 23.5C68 27 68 31 68 35C68 44 62 54 51 61H18L8 54C3 46 0 39 0 32C0 20 8 10 17 4Z M25 3H36C48 4 58 15 61 26L62 35C62 44 57 52 50 57H22C13 51 9 42 9 31C8 19 13 10 25 3Z"),
'P':(44,"M0 0H23C36 0 44 6.4 44 17.4C44 28.4 35.4 35.6 22 35.6H17.2L16.8 33C29.8 33 37.8 27.6 37.8 17.2C37.8 8 30.2 3 20 3H14C13 3 13 4 13 5.8V53C13 57 14.5 58.5 20 59.4V61H0V59.2C4.5 58.3 5 56.7 5 53V8C5 4.1 4.1 2.2 0 1.5Z"),
'M':(73,"M0 0H10.7L36.2 48.3L61.8 0H71.5V1.6C67.6 2.4 66.3 4.5 66.7 8.5L68.9 52.7C69.1 57 70.7 58.4 73 59.2V61H55.8V59.3C60.8 58.3 61.6 56.6 61.5 52.5L59.9 17.6L36.6 58.8L34.6 61L30.7 55.5L11 17.9L9.5 50.3C9.1 56.4 10.3 58.3 16.7 59.3V61H0V59.3C4.2 58.7 5.6 56.5 5.8 50.5L7.6 12.1C7.7 7.8 5.3 4.2 0 1.8Z"),
'N':(62,"M0 0C4.7 0 7.6 1.6 12.7 6.6L54.6 47.7V9C54.6 4.7 53.1 2.6 47.4 1.6V0H62V1.6C58.9 2.3 57.4 4.7 57.4 9V61H55.2L13.5 18.5V52.5C13.5 57 14.6 58.4 19 59.4V61H3.1V59.3C7.1 58.6 7.4 56.5 7.4 52.5V13.6C7.4 8 4.9 4 0 1.6Z"),
'T':(60,"M1.6 0H58.6L60 1.6V8.5H57.8C56.3 4.5 54.6 3 49 3H34.9V55.2L41 59.5V61H20.5V59.3L25.9 55V3H12C5.9 3 3.8 4.4 2.7 9H.8L0 7.8V3.3Z"),
'H':(60,"M0 0H16V1.7C12.4 2.7 12.3 3.9 12.3 7.8V27H47.8V8.3C47.8 4 47 2.5 43.3 1.6V0H60V1.6C57.6 2.5 57.3 4 57.3 8V53C57.3 57 57.7 58.5 60 59.4V61H43.5V59.3C47.2 58.5 47.8 57 47.8 52.9V31.5H12.3V53C12.3 57 12.9 58.6 16.7 59.3V61H0V59.3C3.2 58.3 4.1 56.8 4.1 53V7.8C4.1 4.1 3.6 2.5 0 1.6Z"),
'C':(57,"M27.8 0H40.8C47 1 52.7 3.5 56 7.4L57 12.9L54.4 17.2C50.7 10.4 45.5 5.4 38.1 4.5H26C14.8 10.5 9.1 20.2 7.6 31C7.2 43.4 12.7 52.6 22.2 57.3H38.3C45.4 55.8 50.3 51.8 54.8 46.5L56.4 48.5L55.5 53C50.6 58.3 45 60.3 40 61H20.6C8.5 57 0 46 0 34C0 19 9.9 6.4 22.1 1.8Z"),
'R':(52,"M0 1.3L4 0H24C39 0 43 6 43 15C43 23 37 27 31 29C32.4 31.4 37.2 38.7 41.2 45.5L49 56.2L52 58.6V61H48C43 58.8 39.6 55.4 35 49L24 33C21.6 30.8 19 30.5 13 31V53L19 59.2V61H0V59.2L6 54.3V8C6 4.9 4.3 3 0 2.4Z M13 4V27H23C31 27 35 21.7 35 15.5C35 8.3 31 4 23 4Z"),
'A':(61,"M30.5 0H33L54.8 52C57 57 58 58.3 61 59.5V61H44V59.5C48 59 48.2 57.3 47.2 54L41 38H17L10.5 53.5C9.4 57 10.4 58.9 14.3 59.5V61H0V59.4C3.5 58.5 5.5 56.5 7.6 51.4Z M19 33H39L29.9 10.9Z"),
'I':(16,"M1 0H15L16 1.6C13.1 2.5 12 4 12 8V53C12 57 13 58.5 16 59.5V61H0V59.5C3 58.5 4 57 4 53V8C4 4.2 2.5 2.5 0 1.6Z"),
}

# Optically distinct shapes visible in the smaller third line. These intentional
# alternate masters preserve its heavier P/R/N stems and the left-set T stem.
GLYPHS.update({
'P_c':(44,"M0 0H23C36 0 44 6.4 44 17.4C44 28.4 35.4 35.6 22 35.6H18.8L18.2 33C30.4 33 37.8 27.6 37.8 17.2C37.8 8 30.2 3 20 3H15C14 3 13.8 4 13.8 5.8V53C13.8 57 15 58.5 21 59.4V61H0V59.2C2.7 58.3 2.8 56.7 2.8 53V8C2.8 4.1 2.4 2.2 0 1.5Z"),
'R_c':(52,"M0 1.3L4 0H39.8L43 3.2V17.6C43 23 37 27 31 29C34 31 38 38 42 45C46 51 49 56 52 58V61H46C40 59 37 54 33 47L24 33C22 31 19 30.5 13.4 31V53C13.4 57 15.2 58.3 19 59.2V61H0V59.2C2.4 58.3 2.6 56.5 2.6 53V8C2.6 4.9 1.8 3 0 2.4Z M13.4 5.5V27H25C30 27 35 21.7 35 15.5V10.6C35 6.8 33.1 5.5 28.6 5.5Z"),
'N_c':(62,"M0 1C5.5 0 9.3 2 15 8L51.4 44.7V7.2C51.4 3.8 50.6 2.6 47.6 1.7V0H62V1.7C61 2.5 60.7 4.6 60.7 7.8V61H56.4L11.8 16.8V51.6C11.8 56.7 13.3 58.5 18 59.3V61H2.4V59.3C6.8 58.3 7.6 56.4 7.6 51.4L8.2 14.5C8.2 8.6 5.1 4.6 0 2.6Z"),
'T_c':(60,"M1.6 0H58.6L60 1.6V8.5H57.8C56.3 4.5 54.6 3 49 3H32.73V53.1C32.73 57.6 34.5 58.5 38 59.5V61H18.5V59.3C21.1 58.5 21.82 57.1 21.82 53V3H12C5.9 3 3.8 4.4 2.7 9H.8L0 7.8V3.3Z"),
'I_c':(16,"M1 0H15L16 1.6C13.5 2.5 13.3 4 13.3 8V53C13.3 57 14 58.5 16 59.5V61H0V59.5C3 58.5 4 57 4 53V8C4 4.2 2.5 2.5 0 1.6Z"),
})

# Source-aligned boxes, not extracted contours. Bottom-line baseline varied in
# the supplied raster; these retain each glyph's bounding box and overall line.
LINES=[
('THE',[(302,29,347,74),(357,29,401,74),(414,29,449,74)]),
('DEVELOPMENT',[(18,98,76,159),(87,98,131,159),(139,98,199,159),(210,98,257,159),(272,98,317,159),(322,98,390,159),(402,98,446,159),(458,98,531,159),(544,98,590,159),(602,98,664,159),(678,98,738,159)]),
('CORPORATION',[(93,180,140,230),(147,181,198,230),(207,182,248,230),(258,183,290,230),(299,182,351,230),(361,182,400,230),(408,184,455,230),(457,183,501,230),(513,184,525,230),(535,183,588,230),(595,182,642,230)])
]

def build():
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width='751',height='639',viewBox='0 0 751 639')
    ET.SubElement(svg,'title').text='The Development Corporation — reconstructed serif lettering'
    ET.SubElement(svg,'desc').text='Custom, manually constructed vector glyphs. No embedded raster, live font or automatic trace. Source aligned to the supplied 751 by 639 reference.'
    root=ET.SubElement(svg,'g',id='serif-lettering',fill='#000000',attrib={'fill-rule':'evenodd'})
    for row,(word,boxes) in enumerate(LINES):
        line=ET.SubElement(root,'g',id=f'line-{row+1}-{word.lower()}',attrib={'aria-label':word})
        for index,(letter,(x0,y0,x1,y1)) in enumerate(zip(word,boxes)):
            variant=letter
            if row==2 and letter in 'PNTI':variant=letter+'_c'
            if row==2 and index==5:variant='R_c'
            width,path=GLYPHS[variant]
            ET.SubElement(line,'path',id=f'letter-{row+1}-{index+1}-{letter}',d=path,transform=f'translate({x0} {y0}) scale({(x1-x0)/width:.7f} {(y1-y0)/61:.7f})')
    ET.indent(svg,space='  ')
    (OUT/'serif-lettering.svg').write_text(ET.tostring(svg,encoding='unicode')+'\n')
    (OUT/'serif-glyphs.json').write_text(json.dumps({'cap_height':61,'glyphs':GLYPHS,'lines':LINES},indent=2)+'\n')

if __name__=='__main__':build()
