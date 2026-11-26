"""Register the final black-ink PDF to the lossless screenshot and measure ink overlap."""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / 'src/posters/carecard'
reference = np.asarray(Image.open(ART/'reference.webp').convert('L'))
with TemporaryDirectory() as tmp:
    for mode in ['grayscale','sepia']:
        prefix = Path(tmp)/mode
        subprocess.run(['pdftoppm','-png','-singlefile','-scale-to-x','891','-scale-to-y','1215',
                        str(HERE/f'carecard-{mode}.pdf'), str(prefix)],check=True)
        im = Image.open(prefix.with_suffix('.png'))
        if mode == 'grayscale':
            print_gray = np.asarray(im.convert('L'))
        else:
            im.thumbnail((360,500), Image.Resampling.LANCZOS)
            im.convert('RGB').save(ART/'thumbnail.jpg',quality=90)

# A level halfway between clean paper and the interior of a solid headline stroke.
def ink_mask(a):
    paper = np.median(a[24:60, 50:450])
    solid = np.median(a[283:337, 29:47])
    cut = (paper + solid)/2
    return a < cut, round(float(cut),1)


ref, ref_cut = ink_mask(reference)
out, print_cut = ink_mask(print_gray)
both = ref & out
colours = [(34,40,39),(196,72,49),(24,130,147)]
overlay = np.full((*ref.shape,3),255,dtype='uint8')
for mask, colour in zip([both,ref & ~out,out & ~ref],colours):
    overlay[mask] = colour
overlay = Image.fromarray(overlay)
plate = Image.new('RGB',(1490,1332),'#f7f5ee')
d = ImageDraw.Draw(plate)
FONTS = Path('/System/Library/Fonts/Supplemental')
def write(x,y,text,size=20,bold=False,colour='#232725'):
    font = ImageFont.truetype(str(FONTS/('Arial Bold.ttf' if bold else 'Arial.ttf')),size)
    d.text((x,y),text,font=font,fill=colour,spacing=6)

write(37,20,'BC’s New CareCard.  /  Print registration',36,True)
write(39,72,'1989 launch advertisement     ·     Supplied scan and final black-ink PDF at 891 × 1215 pixels',20)
plate.paste(overlay,(35,106))
x = 959
write(x,112,'Ink overlay',26,True)
for i,(label,colour) in enumerate(zip(['Shared ink','Scan only','Reconstruction only'],colours)):
    y = 167+i*39
    d.rectangle((x,y+3,x+20,y+23),fill=colour)
    write(x+34,y,label)
write(x,324,'Ink intersection / union',26,True)
areas = [('Headline',(17,147,868,387)),('Closing slogan',(35,1034,840,1108)),
         ('Minister’s body copy',(41,520,300,818)),('Centre body copy',(302,646,568,850)),
         ('Seniors’ body copy',(575,738,852,950)),('Standard card face',(310,403,581,573)),
         ('Gold card face',(580,511,849,679)),('Ministry signature',(573,969,759,1025))]
for i,(name,(l,t,r,b)) in enumerate(areas):
    a,c = ref[t:b,l:r],out[t:b,l:r]
    score = (a & c).sum()/(a | c).sum()
    write(x,380+i*35,name)
    write(x+383,380+i*35,f'{score:.1%}',20,True)
    print(name, f'{score:.1%}')
write(x,685,'How to read the differences',24,True)
write(x,735,'The two pages share the screenshot frame.\nEach mask uses the midpoint between paper\nand solid headline ink. Thresholds on the\n0–255 scale are %.1f (scan) and %.1f (PDF).'%(ref_cut,print_cut),20)
write(x,885,'The headline and slogan follow the scan’s ink\ncontours. Reset type, halftone dots and the\ncatalogue card artwork account for much of\nthe red and blue inside the columns.',20)
write(x,1040,'Card placement',24,True)
write(x,1091,'At the scan’s scale, the rectangular card\nframes intersect by about 5 × 67 pixels.\nThe reconstruction gives 4 × 65 pixels.\nThe Gold card sits in front. Rounded corners\nreduce the area that actually hides ink.',20)
plate.save(ART/'overlap.png',optimize=True)
