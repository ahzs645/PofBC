from pathlib import Path
import hashlib,json,fitz
from PIL import Image,ImageDraw
ROOT=Path('/workspace/PofBC')
AREA=Path(__file__).resolve().parent
PACKET=ROOT/'research/salaries/gap-fill-2026-11-02/health_other_history/source-review-packets/employee-exceptions-001/packet.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(PACKET.read_bytes())=='05bbb208d3837de3797ec2456de3e5adc1338909a8d3ba237c17237732ab3dd0'
targets=json.loads(PACKET.read_text())['targets'];assert len(targets)==247
replays=[];pdf=None;source=None;page_number=None;pix=None
for t in targets:
    path=Path(t['sourceCachePath'])
    if source!=path:
        if pdf:pdf.close()
        assert sha(path.read_bytes())==t['sourceSha256'];pdf=fitz.open(path);source=path;page_number=None
    if page_number!=t['physicalPage']:
        pix=pdf[t['physicalPage']-1].get_pixmap(dpi=288,alpha=False);page_number=t['physicalPage']
    assert sha(pix.samples)==t['image']['wholePageRawPixelSha256']
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    crop=im.crop(t['image']['integerCropPixelBox'])
    supplied=Image.open(ROOT/t['image']['path']).convert('RGB')
    assert sha((ROOT/t['image']['path']).read_bytes())==t['image']['sha256']
    assert supplied.size==crop.size and supplied.tobytes()==crop.tobytes()
    replays.append({'id':t['id'],'sourceSha256':t['sourceSha256'],'physicalPage':t['physicalPage'],'cropPngSha256':t['image']['sha256'],'exactOriginalPixelsReplayed':True})
if pdf:pdf.close()
for start in range(0,len(targets),12):
    subset=targets[start:start+12];heights=[];images=[]
    for t in subset:
        im=Image.open(ROOT/t['image']['path']).convert('RGB');a,b=t['image']['targetRowVerticalPixelRange']
        central=im.crop((0,max(0,a-2),im.width,min(im.height,b+2)));images.append(central);heights.append(central.height+32)
    sheet=Image.new('RGB',(2448,sum(heights)),'white');draw=ImageDraw.Draw(sheet);y=0
    for t,im,h in zip(subset,images,heights):
        draw.rectangle((0,y,2448,y+30),fill='#ddd');draw.text((8,y+5),f"{t['id']} / {t['sourceKey']} / physical page {t['physicalPage']} / target row",fill='black');sheet.paste(im,(0,y+31));y+=h
    sheet.save(AREA/f'source-first-sheet-{start//12+1:02}.png')
(AREA/'source-pixel-replay.json').write_text(json.dumps({'packetSha256':sha(PACKET.read_bytes()),'targets':replays,'sourceOnly':True,'noCandidateValuesRead':True,'noOutreach':True},indent=2)+'\n')
print('Exact original pixels replayed',len(replays),'source-first sheets',(len(targets)+11)//12)
