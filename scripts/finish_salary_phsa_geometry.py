#!/usr/bin/env python3
"""Actual-painted name bands and source-calibrated explicit expense-dash proof."""
import hashlib
import json
import statistics
from pathlib import Path
import finish_salary_phsa_rows as readers


def sha(raw):return hashlib.sha256(raw).hexdigest()


def groups(values,gap=7):
    result=[]
    for y in values:
        if result and int(y)-result[-1][-1]<=gap:result[-1].append(int(y))
        else:result.append([int(y)])
    return result


def page_geometry(raw,profile):
    import numpy as np
    from PIL import Image
    image_path=Path(raw['sourceImagePath'])
    if sha(image_path.read_bytes())!=raw['sourceImageSha256']:raise ValueError('Actual source raster changed')
    ink=np.asarray(Image.open(image_path).convert('L'))<128
    words=readers.tess_words(raw['tesseractRawTsv']);h,w=ink.shape
    header=[x for x in words if x['text'].lower()=='name' and x['x']<profile['namePayBoundary'] and x['y']<h*.4]
    header_uncertain=len(header)!=1
    head=header[0] if not header_uncertain else profile['firstTableHeaders']['Name']
    top=head['box'][3]+1;bottom=min(int(h*profile['tableBodyBottomFraction']),profile['sourceLegalFooterTop']-5);left=max(0,head['box'][0]-8)
    rule_width=int(w*.95)-left
    long_rule_ys=np.flatnonzero(ink[top+int(profile['sourceFirstTableRowPitchPixels']):bottom,left:int(w*.95)].sum(axis=1)>rule_width*.8)
    if len(long_rule_ys):bottom=top+int(profile['sourceFirstTableRowPitchPixels'])+int(long_rule_ys[0])
    name_right=int(profile['namePayBoundary'])-12
    projection=ink[top:bottom,left:name_right].sum(axis=1)
    bands=[]
    for band in groups(np.flatnonzero(projection>=3)):
        mass=int(projection[band[0]:band[-1]+1].sum())
        if band[-1]-band[0]+1<5 or mass<50:continue
        bands.append({'top':top+band[0],'bottom':top+band[-1]+1,'center':top+(band[0]+band[-1])/2,
                      'inkPixels':mass,'sourceNameBandBox':[left,top+band[0],name_right,top+band[-1]+1]})
    centers=[b['center'] for b in bands]
    pitch=statistics.median(b-a for a,b in zip(centers,centers[1:])) if len(centers)>1 else profile['sourceFirstTableRowPitchPixels']
    return {'actualSourceImageSha256':raw['sourceImageSha256'],'imageDimensions':[w,h],
            'tableNameHeader':head,'tableHeaderNeedsReview':header_uncertain,
            'bodyTop':top,'bodyBottom':bottom,'firstHorizontalControlRuleY':bottom if len(long_rule_ys) else None,
            'nameBands':bands,'rowPitchPixels':pitch},ink


def components(mask):
    points={(int(y),int(x)) for y,x in zip(*mask.nonzero())};count=0
    while points:
        stack=[points.pop()];count+=1
        while stack:
            y,x=stack.pop()
            for point in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
                if point in points:points.remove(point);stack.append(point)
    return count


def expense_glyph(ink,geometry,profile,index):
    import numpy as np
    bands=geometry['nameBands'];band=bands[index];pitch=geometry['rowPitchPixels'];h,w=ink.shape
    centers=[b['center'] for b in bands]
    y0=round((centers[index-1]+band['center'])/2) if index else max(geometry['bodyTop'],round(band['center']-pitch/2))
    y1=round((centers[index+1]+band['center'])/2) if index+1<len(bands) else min(geometry['bodyBottom'],round(band['center']+pitch/2))
    x0=int(profile['payExpenseBoundary']);x1=int(w*.95)
    mask=ink[y0:y1,x0:x1];ys,xs=np.where(mask)
    result={'sourceExpenseCellBox':[x0,y0,x1,y1],'blackPixels':int(len(xs)),'blank':not len(xs)}
    if not len(xs):return result
    l,r,t,b=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
    tight=mask[t:b,l:r];height,width=tight.shape
    result.update({'glyphBox':[x0+l,y0+t,x0+r,y0+b],'glyphWidth':width,'glyphHeight':height,
                   'inkFill':len(xs)/(width*height),'aspectRatio':width/height})
    if width<=40 and height<=15:
        packed=np.packbits(tight.astype(np.uint8),axis=None).tobytes().hex()
        result.update({'connectedInkComponents':components(tight),'packedMask':packed,
                       'maskSha256':sha(json.dumps([width,height,packed],separators=(',',':')).encode())})
    return result


def dash_calibration(raw,profile,fixture):
    geometry,ink=page_geometry(raw,profile)
    if len(geometry['nameBands'])!=len(fixture):
        raise ValueError('Independent actual-name band count differs from the image-first fixture: '+raw['sourceId'])
    examples=[]
    for i,row in enumerate(fixture):
        if row['expensesLiteral'] not in ['-','–','—']:continue
        glyph=expense_glyph(ink,geometry,profile,i)
        if glyph['blank'] or 'packedMask' not in glyph or glyph['connectedInkComponents']!=1 or glyph['aspectRatio']<2:
            raise ValueError('Original null example is not an independently isolated short horizontal glyph')
        examples.append({'sourceRowOnPage':i+1,**glyph})
    if not examples:raise ValueError('Source needs actual-image dash examples')
    return {'sourceSha256':raw['sourceSha256'],'fixturePhysicalPage':raw['physicalPage'],
            'actualSourceImageSha256':raw['sourceImageSha256'],'allImageVerifiedNullExamples':examples,
            'knownMaskSha256':sorted({g['maskSha256'] for g in examples}),
            'widthRange':[max(2,min(g['glyphWidth'] for g in examples)-1),max(g['glyphWidth'] for g in examples)+1],
            'heightRange':[1,max(g['glyphHeight'] for g in examples)+1],
            'minimumAspectRatio':min(g['aspectRatio'] for g in examples)*.8,
            'minimumInkFill':max(.65,min(g['inkFill'] for g in examples)-.08),
            'connectedInkComponents':1,'requiresAllCellInkWithinTheSingleShortHorizontalGlyph':True,
            'neverDetectorAbsenceBlankDotOrMinusAttachedToNumbers':True,
            'geometryDerivation':'Per-source actual image examples establish a one-pixel raster tolerance and horizontal shape bounds. Every source expense cell is checked independently; explicit zeros/negative numbers and any other ink fail dash geometry.'}


def is_source_dash(glyph,calibration):
    if glyph['blank'] or 'connectedInkComponents' not in glyph:return False
    return (calibration['widthRange'][0]<=glyph['glyphWidth']<=calibration['widthRange'][1]
            and calibration['heightRange'][0]<=glyph['glyphHeight']<=calibration['heightRange'][1]
            and glyph['connectedInkComponents']==1
            and glyph['aspectRatio']>=calibration['minimumAspectRatio']
            and glyph['inkFill']>=calibration['minimumInkFill'])
