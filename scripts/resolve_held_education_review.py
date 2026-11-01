#!/usr/bin/env python3
"""Read-only verification of frozen NIC recovery/search/structure receipts."""
import argparse,base64,gzip,json,re,subprocess
from pathlib import Path
import fitz
import resolve_held_education as m

def verify(originals=False):
 f=json.loads((m.AUDIT/'final-manifest-hashes.json').read_text())
 for name,expected in f['files'].items():assert m.sha((m.ROOT/name).read_bytes())==expected,name
 rs=json.loads((m.AUDIT/'retrievals.json').read_text());web=json.loads(gzip.decompress((m.AUDIT/'web-evidence.json.gzip').read_bytes()))
 for h,r in web.items():assert r['encoding']=='base64' and m.sha(base64.b64decode(r['data']))==h
 assert len(rs['requests'])==rs['requestCount'] and len({r['url'] for r in rs['requests']})==rs['distinctRequestedUrls']
 for r in rs['requests']:
  if r.get('detectedFormat') not in [None,'pdf']:assert r['sha256'] in web
 st=json.loads(gzip.decompress((m.AUDIT/'signed-scan-structure.json.gzip').read_bytes()));assert st['physicalPages']==9 and len(st['objects'])==42 and len(st['pdfminerPages'])==9 and len(st['allImageXrefs'])==len(st['allPageXrefs'])==9 and not st['unreferencedImageXrefs'] and st['embeddedFiles']==0
 for p in st['pages']:
  assert p['mediabox']==p['cropbox'] and p['rotation']==0 and p['imageHeight']==3300 and len(p['contentStreams'])==1
  assert len(re.findall(r'/Img\d+ Do',p['contentStreams'][0]['decoded']))==1
 assert st['missingEmployeePrintedPages']==[1,3,5]
 ap=json.loads((m.AUDIT/'approval-evidence.json').read_text());assert ap['physicalPages']==5 and 'YEAR ENDED MARCH 31, 2020' in ap['mupdfText'] and 'Motion carried' in ap['mupdfText']
 if originals:
  for p,h in [(m.PDF,m.SHA),(m.SIGNED,m.SIGNEDSHA),(Path(ap['original']['cacheFile']),ap['original']['sha256'])]:assert m.sha(p.read_bytes())==h,p
  d=fitz.open(m.SIGNED);assert len(d)==9 and d.xref_length()==43
  for x in st['objects']:
   assert d.xref_object(x['xref'])==x['object']
   if x['isStream']:assert m.sha(d.xref_stream(x['xref']))==x['decodedStreamSha256']
  a=fitz.open(ap['original']['cacheFile']);assert len(a)==5 and not a.is_repaired and a[3].get_text()==ap['mupdfText']
 print('Verified frozen NIC files, bounded request receipts, nine-page structure, and exact official approval evidence'+(' with originals' if originals else ' offline'))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originals',action='store_true');a=p.parse_args();verify(a.originals)
