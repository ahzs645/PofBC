#!/usr/bin/env python3
"""Verify frozen education wave receipts; optionally recreate reviewed PDF images.

Default is read-only/offline, including exact embedded compiled multiset replay.
--originals also checks all six original PDF fingerprints.
--render-review recreates only the specified original-image review artifacts in /tmp.
Image recreation is not a new claim of visual inspection.
"""
import argparse,collections,gzip,json
from pathlib import Path
import fitz
import recover_wave_education as m

def verify():
 frozen=json.loads((m.AUDIT/'final-manifest-hashes.json').read_text())
 for name,expected in frozen['files'].items():
  assert m.sha((m.ROOT/name).read_bytes())==expected,name
 c=json.loads(gzip.decompress((m.AUDIT/'compiled-comparison.json.gzip').read_bytes()))
 a=collections.Counter((r[1],r[3],r[4]) for r in c['officialRows'])
 b=collections.Counter((r[0],r[2],r[3]) for r in c['compiledRows'])
 assert list((a-b).elements())==[tuple(x) for x in c['exactMultisetOnlyOfficial']]
 assert list((b-a).elements())==[tuple(x) for x in c['exactMultisetOnlyCompiled']]
 assert len(c['oneToOneComparison'])==124
 assert len({x['compiledRow'] for x in c['oneToOneComparison']})==124
 for x in c['oneToOneComparison']:
  r=c['officialRows'][x['officialRow']];s=c['compiledRows'][x['compiledRow']]
  assert r[1].replace('-','')==s[0].replace('-','') and r[3]==s[2] and (r[4] or 0)==s[3]
 assert c['documentedMissingToZeroDifferences']==12
 assert len(c['documentedLostHyphenDifferences'])==3
 n=json.loads((m.AUDIT/'nic-incomplete-original.json').read_text());assert n['missingEmployeePrintedPages']==[1,3,5] and n['acceptedRows']==0
 assert [(x['physicalPage'],x['printedPage']) for x in n['physicalToPrintedPageCrosswalk'] if x['schedule']=='employee remuneration']==[(5,2),(6,4)]
 print('Verified frozen file hashes, complete124-row compiled comparison, NIC missing-page receipt, and held-source receipts')

def originals():
 ss=json.loads((m.OUT/'sources.json').read_text())['sources']
 originals=[(Path(s['cacheFile']),s['sha256']) for s in ss]
 for name in ['nic-incomplete-original.json','cnc-clipped-name-hold.json']:
  h=json.loads((m.AUDIT/name).read_text())['original'];originals.append((Path(h['cacheFile']),h['sha256']))
 for p,expected in originals:assert m.sha(p.read_bytes())==expected,p
 print('Verified6 original PDF fingerprints')

def render():
 from PIL import Image,ImageDraw
 visual=json.loads((m.AUDIT/'visual-review.json').read_text());ss={s['id']:s for s in json.loads((m.OUT/'sources.json').read_text())['sources']}
 for v in visual:
  doc=fitz.open(ss[v['sourceId']]['cacheFile'])
  for r in v['renderReceipts']:
   p=Path(r['cacheFile']);p.parent.mkdir(parents=True,exist_ok=True);doc[r['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p);assert m.sha(p.read_bytes())==r['sha256']
 n=json.loads((m.AUDIT/'nic-incomplete-original.json').read_text());doc=fitz.open(n['original']['cacheFile']);imgs=[]
 for r in n['physicalToPrintedPageCrosswalk']:
  p=Path(r['render']['cacheFile']);doc[r['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(p);assert m.sha(p.read_bytes())==r['render']['sha256']
  im=Image.open(p);im.thumbnail((390,520));c=Image.new('RGB',(400,550),'white');c.paste(im,(0,25));ImageDraw.Draw(c).text((5,5),str(r['physicalPage']),fill='black');imgs.append(c)
 sheet=Image.new('RGB',(1200,1650),'#ddd')
 for i,im in enumerate(imgs):sheet.paste(im,(i%3*400,i//3*550))
 path=Path(n['visualReview']['contactSheet']['cacheFile']);sheet.save(path);assert m.sha(path.read_bytes())==n['visualReview']['contactSheet']['sha256']
 h=json.loads((m.AUDIT/'cnc-clipped-name-hold.json').read_text());path=Path(h['visualReview']['image']['cacheFile']);fitz.open(h['original']['cacheFile'])[3].get_pixmap(matrix=fitz.Matrix(2,2)).save(path);assert m.sha(path.read_bytes())==h['visualReview']['image']['sha256']
 s=next(s for s in ss.values() if s['employerSlug']=='university-of-bc');ev=json.loads(gzip.decompress((m.OUT/s['validation']['evidenceFile']).read_bytes()));d=fitz.open(s['cacheFile']);crops=[]
 for e in ev['pageEvidence']:
  for r in e['rowEvidence']:
   if r['expenseToken'].startswith('('):
    p=d[e['physicalPage']-1];x=50 if r['column']==1 else 316;y=r['baseline'];pix=p.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(x,max(y-14,0),x+252,y+18));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);c=Image.new('RGB',(620,90),'white');ImageDraw.Draw(c).text((3,3),f"physical {e['physicalPage']}: {r['name']}",fill='black');c.paste(im,(0,20));crops.append(c)
 out=Image.new('RGB',(620,len(crops)*90),'#ddd')
 for i,c in enumerate(crops):out.paste(c,(0,i*90))
 v=next(v for v in visual if v['sourceId']==s['id']);r=v['additionalOriginalImageEvidence'][0];path=Path(r['cacheFile']);out.save(path);assert m.sha(path.read_bytes())==r['sha256']
 print('Recreated pinned review images; visual inspection itself remains limited to the recorded receipt')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originals',action='store_true');p.add_argument('--render-review',action='store_true');a=p.parse_args();verify()
 if a.originals or a.render_review:originals()
 if a.render_review:render()
