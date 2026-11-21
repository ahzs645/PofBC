"""Build explicitly labelled visual review sheets, outside vector artwork."""
from pathlib import Path
import argparse,json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work' if (ROOT/'work/reference-rectified.png').exists() else ROOT/'analysis'
DATA=WORK/'overlap_v6' if (WORK/'overlap_v6/before_metrics.json').exists() else WORK
OUT=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'review'
ART=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'artwork'
PAPER='#F5F0E4'
INK='#242332'
FP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size):
    for candidate in [FP,'DejaVuSans.ttf','/System/Library/Fonts/Helvetica.ttc','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(candidate,size)
        except OSError:pass
    try:return ImageFont.load_default(size=size)
    except TypeError:return ImageFont.load_default()
def put_crop(board,im,box,xy,size):
    board.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),xy)

def main(trees_only=False):
    OUT.mkdir(exist_ok=True,parents=True)
    src=Image.open(WORK/'reference-rectified.png').convert('RGB')
    new=Image.open(ART/'BC_Forest_Service_Preview.png').convert('RGB').resize((1000,1440),Image.Resampling.LANCZOS)
    # Main comparison: consistent scale and registration.
    can=Image.new('RGB',(1480,1170),PAPER);d=ImageDraw.Draw(can)
    d.text((30,21),'Supplied photograph',font=font(28),fill=INK)
    d.text((775,21),'Revised vector',font=font(28),fill=INK)
    d.text((30,61),'Perspective corrected for comparison',font=font(21),fill=INK)
    d.text((775,61),'Remaining tree and timber shapes reworked',font=font(21),fill=INK)
    for im,xy in [(src,(30,102)),(new,(775,102))]:
        can.paste(im.resize((675,972),Image.Resampling.LANCZOS),xy)
    d.text((30,1094),'Revision 6: repeated refinement of boughs, timber, ground, flame folds and lettering.',font=font(21),fill=INK)
    d.text((30,1126),'Fine illustration details remain reconstructed from the supplied photograph.',font=font(21),fill=INK)
    can.save(OUT/'BC_Forest_Service_Comparison.png')
    # Full-width woodland crops: original and revision are exactly aligned.
    can=Image.new('RGB',(2080,1180),PAPER);d=ImageDraw.Draw(can)
    d.text((30,20),'TREE AND TIMBER DETAIL REVIEW',font=font(30),fill=INK)
    d.text((30,65),'Supplied photograph',font=font(24),fill=INK)
    d.text((1050,65),'Revised vector',font=font(24),fill=INK)
    for im,x in [(src,30),(new,1050)]:put_crop(can,im,(0,0,1000,425),(x,108),(1000,425))
    d.text((30,552),'Upper conifers: bough shape, drooping foliage, trunk grain and irregular gaps.',font=font(23),fill=INK)
    for im,x in [(src,30),(new,1050)]:put_crop(can,im,(0,735,1000,1160),(x,605),(1000,425))
    d.text((30,1052),'Lower woodland: split trunks, fallen logs, root shapes and burnt ground.',font=font(23),fill=INK)
    d.text((30,1102),'Each panel uses the same crop, scale and registration. No photograph is embedded in the SVG.',font=font(21),fill=INK)
    can.save(OUT/'BC_Forest_Service_Tree_Details.png')
    if trees_only:
        print('Comparison and tree review sheets written; prior flame review retained.')
        return
    # Flame line comparison, maintaining a consistent zoom within each row.
    before=json.loads((DATA/'before_metrics.json').read_text())
    old_path=Path(before['candidate'])
    if not old_path.exists():old_path=WORK/'before_preview.png'
    old=Image.open(old_path).convert('RGB').resize((1000,1440),Image.Resampling.LANCZOS)
    can=Image.new('RGB',(1370,785),PAPER);d=ImageDraw.Draw(can)
    d.text((25,20),'FLAME-LINE DETAIL REVIEW',font=font(30),fill=INK)
    cols=[(src,25,'Reference'),(old,475,'Revision 5'),(new,925,'Revision 6')]
    for im,x,label in cols:d.text((x,70),label,font=font(23),fill=INK)
    for im,x,_ in cols:
        pair=Image.new('RGB',(330,445),PAPER)
        pair.paste(im.crop((0,315,125,760)),(0,0))
        pair.paste(im.crop((810,315,1000,760)),(140,0))
        can.paste(pair.resize((420,566),Image.Resampling.LANCZOS),(x,110))
        d.text((x,686),'Left edge                 Right edge',font=font(18),fill=INK)
    d.text((25,724),'Revision 6: retained side ribbons checked alongside the revised flame crest.',font=font(22),fill=INK)
    d.text((25,755),'Each column shows the same two edge crops, at the same scale.',font=font(18),fill=INK)
    can.save(OUT/'BC_Forest_Service_Flame_Details.png')
    # The standalone edge crops above intentionally magnify their narrow shapes;
    # all three columns within each row have exactly the same display scaling.
    print('Comparison and detail review sheets written.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trees-only',action='store_true')
    main(parser.parse_args().trees_only)
