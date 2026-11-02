#!/usr/bin/env python3
"""Source-specific expense glyph evidence; blanks and OCR misses are not dashes."""
import argparse,gzip,hashlib,json,math
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE

ROI={35:(1840,2070,18),38:(1930,2270,20),69:(2010,2300,20),70:(2190,2450,23),78:(2000,2430,24),79:(2020,2450,20)}

def sha(b):return hashlib.sha256(b).hexdigest()
def components(points):
    points=set(points);count=0
    while points:
        stack=[points.pop()];count+=1
        while stack:
            x,y=stack.pop()
            for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if p in points:points.remove(p);stack.append(p)
    return count

def describe_mask(mask):
    """Pure-Python binary-matrix description used by offline semantic tests."""
    points={(x,y) for y,row in enumerate(mask) for x,v in enumerate(row) if v};result={'blank':not points,'blackPixels':len(points)}
    if not points:return result
    left=min(x for x,y in points);right=max(x for x,y in points)+1;top=min(y for x,y in points);bottom=max(y for x,y in points)+1
    width=right-left;height=bottom-top
    result.update(tightBox=[left,top,right,bottom],glyphWidth=width,glyphHeight=height,aspectRatio=width/height,inkFill=len(points)/(width*height))
    if width<=45 and height<=15:
        ordered=[int((x,y) in points) for y in range(top,bottom) for x in range(left,right)];packed=''.join(map(str,ordered));result.update(connectedInkComponents=components(points),packedMaskBits=packed,maskSha256=sha(json.dumps([width,height,packed],separators=(',',':')).encode()))
    return result

def plausible_horizontal(g):
    return not g['blank'] and 2<=g['glyphWidth']<=40 and 1<=g['glyphHeight']<=10 and g.get('connectedInkComponents')==1 and g['aspectRatio']>=2 and g['inkFill']>=.60

def is_source_dash(g,calibration):
    return (not g['blank'] and g.get('connectedInkComponents')==1 and calibration['widthRange'][0]<=g['glyphWidth']<=calibration['widthRange'][1] and calibration['heightRange'][0]<=g['glyphHeight']<=calibration['heightRange'][1] and g['aspectRatio']>=calibration['minimumAspectRatio'] and g['inkFill']>=calibration['minimumInkFill'])

def run(n):
    import fitz
    from PIL import Image
    path=AREA/f'sd{n}-scan-parsed-v5.json.gzip';b=path.read_bytes();parsed=json.loads(gzip.decompress(b));a=parsed['tesseractRows'];c=parsed['paddleRows'];assert len(a)==len(c),'Resolve row alignment before source-glyph comparison'
    assert [x['pdfPage'] for x in a]==[x['pdfPage'] for x in c]
    source=json.loads((AREA/f'sd{n}-sofi-2025-retrieval.json').read_text());pdfpath=Path(source['cachePath']);assert sha(pdfpath.read_bytes())==source['sha256'];doc=fitz.open(pdfpath)
    images={};features=[]
    for i,(one,two) in enumerate(zip(a,c),1):
        if one['category']!='employee-remuneration':continue
        number=one['pdfPage']
        if number not in images:
            pix=doc[number-1].get_pixmap(dpi=300);images[number]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples).convert('L')
        image=images[number];x0,x1,half=ROI[n];center=(one['sourceY300dpi']+two['sourceY300dpi'])/2;y0=math.floor(center-half);y1=math.ceil(center+half)
        crop=image.crop((x0,y0,x1,y1));pixels=list(crop.getdata());w,h=crop.size;mask=[[pixels[y*w+x]<128 for x in range(w)] for y in range(h)]
        g=describe_mask(mask);g.update(sequence=i,physicalPage=number,sourceExpenseCellBox300Dpi=[x0,y0,x1,y1],sourceRowYCenters=[one['sourceY300dpi'],two['sourceY300dpi']],sourceRowLocator={'tesseractName':one['name'],'paddleName':two['name'],'tesseractPay':one['remuneration'],'paddlePay':two['remuneration']})
        features.append(g)
    result={'district':n,'sourceSha256':source['sha256'],'parsedCandidate':{'path':str(path),'sha256':sha(b)},'method':'Independent sequential whole original PDF300dpi render; explicit expense-region ink geometry. No zero/dash inference from OCR absence; all cell ink must fit one calibrated short horizontal glyph.','features':features,'acceptedRows':0}
    dest=AREA/f'sd{n}-source-expense-glyphs.json.gzip';dest.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({'district':n,'expenseCells':len(features),'plausibleDashShapes':sum(plausible_horizontal(x) for x in features),'fullyBlankCells':sum(x['blank'] for x in features)}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--district',type=int,action='append');args=ap.parse_args()
    for n in args.district or [35,38,69,70,78,79]:run(n)
