from pathlib import Path
import urllib.request,urllib.parse,concurrent.futures,json
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;(P/'specimens').mkdir(exist_ok=True)
PHRASES=['General Administration','Department of Recreation and Conservation','Fish and Wildlife Branch','Provincial Parks Branch','British Columbia Provincial Museum','Commercial Fisheries Branch','marine Resources Branch','Marine Resources Branch','[Commercial Fisheries]','Annual Report 1971','Annual Report 1972','Annual Report 1973','Province of British Columbia','Department of','Recreation and Conservation']
chars=sorted(set(''.join(PHRASES)) - {' '})
jobs=[('HH','HH')]+[(f'u{ord(c):04x}','H'+c+'H') for c in chars]
def one(item):
 name,txt=item;dest=P/'specimens'/f'{name}.png';url='https://sig.monotype.com/render/105/font/21b7f07b12a3c83e74b7f1db1c1faf19?'+urllib.parse.urlencode({'rt':txt,'rs':256,'w':2000,'fg':'000000','bg':'FFFFFF'})
 err=None
 try:
  if not dest.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.myfonts.com/'})
   with urllib.request.urlopen(req,timeout=40) as r:dest.write_bytes(r.read())
  im=Image.open(dest).convert('L');a=np.array(im);mask=a<128
  v=np.pad(mask.any(0).astype(int),(1,1));runs=[list(map(int,p)) for p in zip(np.where(np.diff(v)==1)[0],np.where(np.diff(v)==-1)[0])]
  return {'name':name,'text':txt,'char':txt[1] if len(txt)==3 else None,'path':str(dest.relative_to(P)),'url':url,'size':list(im.size),'column_runs':runs}
 except Exception as e:return {'name':name,'text':txt,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 results=[]
 for r in ex.map(one,jobs):
  results.append(r);print(r['name'],r.get('column_runs'),r.get('error',''),flush=True)
(P/'specimen_manifest.json').write_text(json.dumps({'phrases':PHRASES,'nominal_em_px':256*4/3,'items':results},indent=2))
