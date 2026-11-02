import json,hashlib,pathlib,sys
root=pathlib.Path('/workspace/PofBC'); area=root/'research/salaries/gap-fill-2026-11-02/health_employees/peer-municipal'; packet=root/'research/salaries/gap-fill-2026-11-02/municipal/independent-review-packet-remaining-16.json'
x=json.load(open(packet)); n=int(sys.argv[1]); r=x['reports'][n-1]
assert hashlib.sha256(pathlib.Path(r['cachedPdf']).read_bytes()).hexdigest()==r['sourceSha256']
data=json.load(sys.stdin)
data.update({'reportNumber':n,'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'sourceSha256':r['sourceSha256'],'sourceUrl':r['sourceUrl'],'candidateValuesSeen':False,'method':'Read actual original source-page images personally before any candidate payload; literal fields and blank/dash/zero distinctions transcribed without subtotal inference.','sourceCohortIds':[c['sourceId'] for c in r['sourceCohorts']]})
for c in r['sourceCohorts']:
 if c.get('render300DpiImage'):
  assert hashlib.sha256(pathlib.Path(c['render300DpiImage']).read_bytes()).hexdigest()==c['renderSha256']
p=area/f'first-report-{n:02d}.json'
with p.open('x') as f: json.dump(data,f,indent=2); f.write('\n')
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
