#!/usr/bin/env python3
"""Fetch only nine explicitly catalogued PHSA ORIGINAL salary assets; inspect sequentially."""
import concurrent.futures,gzip,hashlib,json,re,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/phsa_history'
CACHE=Path('/workspace/gap-phsa-history-cache')
LOCATORS=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees/phsa-earlier-original-locators.json'

def sha(b):return hashlib.sha256(b).hexdigest()
def fetch_asset(item):
 serial=' '.join(item['item']['serialIssue']);match=re.search(r'(\d{4})/(\d{4})',serial);assert match;key='phsa-'+match[1]+'-'+match[2][-2:];path=CACHE/(key+'.pdf');request=urllib.request.Request(item['url'],headers={'User-Agent':'PofBC public salary source audit'})
 if path.exists():data=path.read_bytes();status=200;url=item['url'];headers={};cache=True
 else:
  with urllib.request.urlopen(request,timeout=120) as response:data=response.read();status=response.status;url=response.url;headers=dict(response.headers)
  assert data.startswith(b'%PDF-');path.write_bytes(data);cache=False
 stored=item.get('storedChecksum',{});delivered_md5=hashlib.md5(data).hexdigest();stored_match=stored.get('checkSumAlgorithm')=='MD5' and delivered_md5==stored.get('value')
 return {'key':key,'catalogueYear':match[1]+'/'+match[2][-2:],'cataloguePeriodIsNotAcceptanceEvidence':True,'sourceUrl':item['url'],'officialCatalogueHandle':'https://digitalcollections.llbc.leg.bc.ca/handle/'+item['item']['handle'],'bitstreamUuid':item['bitstreamUuid'],'originalFileName':item['name'],'sourceSha256':sha(data),'bytes':len(data),'officialStoredChecksum':stored,'officialStoredBytes':item['storedBytes'],'deliveredMd5':delivered_md5,'matchesStoredBytes':len(data)==item['storedBytes'],'matchesStoredMd5':stored_match,'deliveryObservation':'The official Library content endpoint prepends an explicit catalogue cover page and repacks the PDF. Delivered and stored-bitstream fingerprints are recorded separately; no byte identity is asserted.','cachePath':str(path),'httpStatus':status,'finalUrl':url,'httpHeaders':headers,'cached':cache,'bundleMetadataSha256':item['bundleMetadataSha256'],'noOutreach':True}
def run():
 import fitz
 AREA.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True);items=json.loads(LOCATORS.read_text());assert len(items)==9;(AREA/'original-locators.json').write_bytes(LOCATORS.read_bytes())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:retrievals=list(pool.map(fetch_asset,items))
 for entry in sorted(retrievals,key=lambda x:x['key']):
  doc=fitz.open(entry['cachePath']);pages=[]
  for i,page in enumerate(doc,1):
   text=page.get_text();pages.append({'physicalPage':i,'nativeCharacters':len(text),'text':text,'imageCount':len(page.get_images()),'pageWidth':page.rect.width,'pageHeight':page.rect.height})
  poppler=subprocess.check_output(['pdftotext','-layout',entry['cachePath'],'-']);out=AREA/(entry['key']+'-poppler.txt.gzip');out.write_bytes(gzip.compress(poppler,mtime=0));raw={'sourceSha256':entry['sourceSha256'],'pages':pages,'probeMethod':'Sequential original MuPDF text/image probes; independent Poppler physical-layout text retained separately.'};native=AREA/(entry['key']+'-native-probe.json.gzip');native.write_bytes(gzip.compress((json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));entry.update(pageCount=len(doc),nativeCharacters=sum(p['nativeCharacters'] for p in pages),imageOnlyPages=[p['physicalPage'] for p in pages if p['nativeCharacters']<30],originalPageInventory=[{k:p[k] for k in ['physicalPage','nativeCharacters','imageCount','pageWidth','pageHeight']} for p in pages],nativeProbe={'path':str(native.relative_to(ROOT)),'sha256':sha(native.read_bytes())},popplerProbe={'path':str(out.relative_to(ROOT)),'sha256':sha(out.read_bytes())});print(json.dumps({k:entry[k] for k in ['key','pageCount','nativeCharacters','imageOnlyPages','sourceSha256','bytes']}),flush=True)
 (AREA/'source-inventory.json').write_text(json.dumps({'catalogueLocatorInput':{'path':str(LOCATORS.relative_to(ROOT)),'sha256':sha(LOCATORS.read_bytes())},'sources':retrievals,'acceptedRows':0,'noOutreach':True},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':run()
