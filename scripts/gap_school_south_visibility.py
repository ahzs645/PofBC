#!/usr/bin/env python3
"""Actual whole-page raster corroboration for native word bounding rectangles.

A nonblank rectangle does NOT certify its text. Completely blank rectangles and
column crossings are mandatory image-review targets, independently of agreement.
"""
import gzip,hashlib,json,math
from pathlib import Path
import fitz
from PIL import Image
from gap_school_south_fetch import AREA
from gap_school_south_native import SPECS

def run(n):
    path=AREA/f'sd{n}-native-candidate-v4.json.gzip';raw=path.read_bytes();r=json.loads(gzip.decompress(raw));spec=SPECS[n]
    pdf=fitz.open(r['source']['cachePath']);by_page={};output=[];flags=[]
    for i,row in enumerate(r['mupdfRows'],1):by_page.setdefault(row['pdfPage'],[]).append((i,row))
    for number,rows in sorted(by_page.items()):
        pix=pdf[number-1].get_pixmap(dpi=300)
        image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples).convert('L')
        image_hash=hashlib.sha256(pix.samples).hexdigest();word_checks=[]
        chars=[c for b in pdf[number-1].get_text('rawdict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] for c in s['chars'] if c['c'].strip()]
        for sequence,row in rows:
            words=row['sourceWordBoxes']+row.get('positionContinuationWords',[])
            for word in words:
                x0,y0,x1,y1,text=word[:5];box=[math.floor(x0*300/72),math.floor(y0*300/72),math.ceil(x1*300/72),math.ceil(y1*300/72)]
                pixels=image.crop(box).histogram();dark=sum(pixels[:128]);cross=any(x0<b<x1 for b in spec['bounds'])
                check={'sequence':sequence,'word':text,'sourceWordBoxPoints':word[:4],'integerRasterBox300Dpi':box,'darkPixelCountBelow128':dark,'rasterPixelCount':sum(pixels),'crossesColumnStart':cross}
                glyph_checks=[]
                for c in chars:
                    a,b,cx,dy=c['bbox'];cy=(b+dy)/2;mx=(a+cx)/2
                    if x0-.1<=mx<=x1+.1 and y0-.1<=cy<=y1+.1:
                        gb=[math.floor(a*300/72),math.floor(b*300/72),math.ceil(cx*300/72),math.ceil(dy*300/72)]
                        gp=image.crop(gb).histogram();gd=sum(gp[:128])
                        gc={'character':c['c'],'sourceGlyphBoxPoints':list(c['bbox']),'integerRasterBox300Dpi':gb,'darkPixelCountBelow128':gd}
                        glyph_checks.append(gc)
                        if gd==0:flags.append({'physicalPage':number,'sequence':sequence,'word':text,'reason':'native glyph rectangle contains no dark source pixels',**gc})
                check['nativeGlyphRectangles']=glyph_checks
                word_checks.append(check)
                if dark==0 or cross:flags.append({'physicalPage':number,**check})
        output.append({'physicalPage':number,'originalFullPageRgbPixelsSha256':image_hash,'width':pix.width,'height':pix.height,'wordChecks':word_checks})
    result={'district':n,'candidateSha256':hashlib.sha256(raw).hexdigest(),'sourceSha256':r['source']['sha256'],'method':'Sequential full original page.get_pixmap(dpi=300), integer bbox pixel counts; no glyph truth inferred from nonblank pixels','pages':output,'mandatoryImageReviewFlags':flags,'acceptedRows':0}
    dest=AREA/f'sd{n}-native-original-raster-visibility-v2.json.gzip';dest.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({'district':n,'pages':len(output),'wordRectangles':sum(len(p['wordChecks']) for p in output),'fullyBlankRectangles':sum(x['darkPixelCountBelow128']==0 for x in flags),'columnCrossings':sum(x.get('crossesColumnStart',False) for x in flags),'flags':flags[:20]},ensure_ascii=False),flush=True)

if __name__=='__main__':
    for n in [37,39,45,75]:run(n)
