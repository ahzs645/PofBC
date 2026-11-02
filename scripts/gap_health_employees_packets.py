#!/usr/bin/env python3
"""Create candidate-value-withheld original-image packets for independent readers."""
import collections,gzip,json,pathlib,re,subprocess,xml.etree.ElementTree as ET
import fitz
from gap_health_employees_fetch import ROOT,AREA,sha
from gap_health_employees_native import amount,nameclean,load

NS={'x':'http://www.w3.org/1999/xhtml'}

def bbox_words(spec):
    cache=pathlib.Path('/workspace/gap-health-employees-cache/bbox');cache.mkdir(exist_ok=True);p=cache/(spec['sourceSha256']+'.xml')
    if not p.exists():p.write_bytes(subprocess.check_output(['pdftotext','-bbox-layout','-enc','UTF-8',spec['retrieval']['cachePath'],'-']))
    return [[{'text':w.text or '',**{k:float(w.attrib[k]) for k in ['xMin','yMin','xMax','yMax']}} for w in page.findall('.//x:word',NS)] for page in ET.fromstring(re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]',b'',p.read_bytes())).findall('.//x:page',NS)]

def locate(row,sourcewords):
    name,pay,pn=row[1],row[3],row[5];words=sourcewords[pn-1];anchors=[]
    for w in words:
        try:v=amount(w['text'])
        except ValueError:continue
        if v==pay and w['xMin']>150:
            near=[q for q in words if abs(q['yMin']-w['yMin'])<2.2 and q['xMax']<w['xMin']-2];text=nameclean(' '.join(q['text'] for q in sorted(near,key=lambda q:q['xMin'])))
            anchors.append((w,text))
    exact=[w for w,text in anchors if name==text]
    if len(exact)==1:return exact[0]
    same=[w for w,text in anchors if name.split(',')[0] in text]
    #Same-position overprinted tokens do not denote separate source rows.
    by={(round(w['xMin'],1),round(w['yMin'],1)):w for w in same}
    if len(by)==1:return next(iter(by.values()))
    #Overprinted rows can split a comma-bearing monetary token in BOTH bbox
    #extractors. Target coordinates may instead use exact visible surname and
    #given-name tokens; no inferred spelling/value is supplied to the reader.
    surname=name.split(',')[0];given=name.split(',',1)[1].split()[0] if ',' in name else None;ys=[]
    for w in words:
        if w['xMin']>250 or surname.split()[0] not in w['text']:continue
        near=' '.join(q['text'] for q in words if q['xMin']<280 and abs(q['yMin']-w['yMin'])<2.2)
        if given and given not in near:continue
        if not any(abs(w['yMin']-y)<2 for y in ys):ys.append(w['yMin'])
    if len(ys)==1:
        return {'xMin':40,'yMin':ys[0],'xMax':560,'yMax':ys[0]+11}
    raise ValueError(('Ambiguous independent target coordinate',row,anchors))

def main():
    specs=json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes());specs={s['sourceSha256']:s for s in specs};index=json.loads((AREA/'native-primary-candidate-index.json').read_bytes());targets=[]
    for s in index:
        primary=load(ROOT/s['file']);byrow={tuple(x['row']):x for x in primary['rows']};wanted={tuple(x) for x in s['onlyPrimary']}
        for f in primary['flags']:
            if f['kind'] in ('name-digits-require-original-review','named-pay-below-threshold-requires-review'):
                wanted.update(t for t in byrow if t[5]==f['physicalPage'] and t[1]==f.get('name'))
        for row in wanted:targets.append((s,row,byrow[row].get('sourceRowOnPage')))
        if s['key']=='island-health-2005-06':targets.append((s,('island-health','M.S.',None,88941,0,17),None))
        if s['key']=='island-health-2023-24':
            wanted2={'SAHOTA,NASHHATER KAUR N','ZETARUK,SAVANNAH'}
            targets.extend((s,t,byrow[t]['sourceRowOnPage']) for t in byrow if t[1] in wanted2)
    targets.sort(key=lambda x:(x[0]['key'],x[1][5],x[2] or 0))
    out=AREA/'source-review-packets/reader-disagreements-001';out.mkdir(parents=True,exist_ok=True);entries=[];docs={};boxes={};renders={}
    for n,(summary,row,ordinal) in enumerate(targets,1):
        spec=specs[summary['sourceSha256']];key=summary['key'];pn=row[5]
        if key not in boxes:boxes[key]=bbox_words(spec);docs[key]=fitz.open(spec['retrieval']['cachePath'])
        anchor=locate(row,boxes[key]);page=docs[key][pn-1];cy=(anchor['yMin']+anchor['yMax'])/2;scale=4
        renderkey=(key,pn)
        if renderkey not in renders:
            pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);renders[renderkey]=pix
        pix=renders[renderkey];bounds=fitz.IRect(40*scale,max(0,int((cy-18)*scale)),int((page.rect.width-20)*scale),min(pix.height,int((cy+18)*scale)))
        crop=fitz.Pixmap(pix.colorspace,bounds,False);crop.copy(pix,bounds);p=out/f'target-{n:03}.png';crop.save(p)
        entries.append({'id':f'health-reader-001-{n:03}','sourceKey':key,'sourceSha256':spec['sourceSha256'],'sourceUrl':spec['url'],'sourceCachePath':spec['retrieval']['cachePath'],'physicalPage':pn,'sourceRowOnPage':ordinal,'image':{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'wholePageRawPixelSha256':sha(pix.samples),'wholePageDpi':288,'integerCropPixelBox':list(bounds),'targetRowVerticalPixelRange':[round((anchor['yMin']*scale)-bounds.y0),round((anchor['yMax']*scale)-bounds.y0)]},'requestedFields':['name','remuneration','expenses'],'candidateValuesWithheld':True})
    packet={'status':'awaiting-independent-original-image-transcription','noOutreach':True,'sourceRendering':'Complete original page rendered at288dpi, then integer crop; no PDF clip or resampling. Target center row identified by vertical pixel range. Adjacent rows remain context.','candidateValuesWithheld':True,'targets':entries}
    p=out/'packet.json';p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'packet':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'targets':len(entries)}))

if __name__=='__main__':main()
