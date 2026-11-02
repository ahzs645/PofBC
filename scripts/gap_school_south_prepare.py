#!/usr/bin/env python3
"""Apply image-calibrated dash evidence and stage true disagreement source crops."""
import gzip,json,hashlib,math,sys
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE
from gap_school_south_scan import FIELDS,comparison
from gap_school_south_dash import is_source_dash

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def dump(p,d):p.write_bytes(gzip.compress((json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def run(n):
    p=AREA/f'sd{n}-scan-parsed-v5.json.gzip';d=load(p);a=d['tesseractRows'];b=d['paddleRows'];assert len(a)==len(b);cal=json.loads((AREA/'expense-dash-primary-calibration.json').read_text())['calibrations'].get(str(n));glyphs=load(AREA/f'sd{n}-source-expense-glyphs.json.gzip');gs={x['sequence']:x for x in glyphs['features']};am=[];flags=[];chosen=[]
    for seq,(one,two) in enumerate(zip(a,b),1):
        row=dict(one);reasons=[]
        g=gs.get(seq)
        if g and cal and all(isinstance(r['expenses'],str) and r['expenses'].startswith('UNRESOLVED:') for r in [one,two]) and is_source_dash(g,cal):
            row['expenses']=None;am.append({'sequence':seq,'field':'expenses','value':None,'reason':'Actual original complete-cell ink is a calibrated source dash; not inferred from a blank/OCR absence.','glyphProofSequence':seq})
        for f in FIELDS:
            if f=='expenses' and row[f] is None and g and any(x['sequence']==seq for x in am):continue
            if comparison(one[f],f,n)!=comparison(two[f],f,n) or any(isinstance(r[f],str) and r[f].startswith('UNRESOLVED:') for r in [one,two]):reasons.append(f)
        if reasons:flags.append({'sequence':seq,'fields':reasons,'tesseract':[one[f] for f in FIELDS],'paddle':[two[f] for f in FIELDS]})
        chosen.append(row)
    d.update(chosenRows=chosen,imageCalibratedDashAmendments=am,remainingTrueFieldDifferences=flags,acceptedRows=0,dashEvidenceRef={'path':str(AREA/f'sd{n}-source-expense-glyphs.json.gzip'),'sha256':sha((AREA/f'sd{n}-source-expense-glyphs.json.gzip').read_bytes())},calibrationRef={'path':str(AREA/'expense-dash-primary-calibration.json'),'sha256':sha((AREA/'expense-dash-primary-calibration.json').read_bytes())})
    dump(AREA/f'sd{n}-scan-candidate-v6.json.gzip',d)
    print(json.dumps({'district':n,'rows':len(chosen),'dashResolutions':len(am),'remainingFlags':len(flags)}),flush=True)
    return d

def images(n,d):
    import fitz
    from PIL import Image,ImageDraw
    doc=fitz.open(CACHE/f'sd{n}-sofi-2025.pdf');cached={};targets=[];flags=d['remainingTrueFieldDifferences'];rows=d['chosenRows'];root=AREA/'scan-review-images';root.mkdir(exist_ok=True)
    for seq in [x['sequence'] for x in flags]:
        r=rows[seq-1];p=r['pdfPage'];cy=(d['tesseractRows'][seq-1]['sourceY300dpi']+d['paddleRows'][seq-1]['sourceY300dpi'])/2
        if p not in cached:
            pix=doc[p-1].get_pixmap(dpi=300);cached[p]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        box=[20,max(0,math.floor(cy-25)),min(2460,cached[p].width),math.ceil(cy+25)];crop=cached[p].crop(box);out=root/f'sd{n}-seq{seq}-original300.png';crop.save(out);targets.append({'district':n,'sequence':seq,'physicalPage':p,'integerBox300Dpi':box,'path':str(out),'sha256':sha(out.read_bytes()),'originalSha256':d['rawProofs'][0].get('sourceSha256')})
    for start in range(0,len(targets),15):
        batch=targets[start:start+15];canvas=Image.new('RGB',(2440,len(batch)*80),'white');dr=ImageDraw.Draw(canvas)
        for j,t in enumerate(batch):
            dr.text((10,j*80),f'SD{n} seq{t["sequence"]} p{t["physicalPage"]} SOURCE',fill='black');canvas.paste(Image.open(t['path']),(0,j*80+22))
        canvas.save(root/f'sd{n}-flags-sheet-{start//15+1}.png')
    (AREA/f'sd{n}-source-only-flag-packet.json').write_text(json.dumps({'district':n,'targets':targets,'noChosenValuesIncluded':True},indent=2)+'\n')

if __name__=='__main__':
    ns=list(map(int,sys.argv[1:])) or [35,38,69,70,78,79]
    for n in ns:images(n,run(n))
