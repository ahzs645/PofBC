from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parent;R=Path('/workspace/PofBC');key=sys.argv[1];part=sys.argv[2];packet=R/f'research/salaries/gap-fill-2026-11-02/phsa_history/source-only-packets/{key}-v4/packet.json';p=json.loads(packet.read_text());ts={t['sequence']:t for t in p['targets']};rows=[]
for line in sys.stdin:
 if not line.strip():continue
 seq,name,pay,expense=line.rstrip('\n').split('|');seq=int(seq);t=ts[seq];rows.append({'sequence':seq,'pdfPage':t['physicalPage'],'name':name,'position':None,'remuneration':int(pay.replace(',','')),'sourceExpenses':expense,'expenses':None if expense=='-' else int(expense.replace(',','')),'sourceImagePath':t['sourceCropPath'],'sourceImageSha256':t['sourceCropSha256']})
d={'phase':'first personal source-image readings before any scan producer candidate','sourceKey':key,'part':part,'allRowsPersonallyImageRead':True,'rows':rows,'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'noOutreach':True};out=B/f'{key}-first-transcript-part-{part}.json';assert not out.exists();out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print(len(rows),hashlib.sha256(out.read_bytes()).hexdigest())
