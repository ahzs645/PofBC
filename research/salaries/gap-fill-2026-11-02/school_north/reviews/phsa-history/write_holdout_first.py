from pathlib import Path
import json,hashlib
b=Path(__file__).parent;p=b/'own-independent20-personal-first-transcript.json'
rows='''Armstrong,Lana Marie|86253|6045
Basso,Melanie|105475|454
Butterfield,Yaron|77461|7255
Callaghan,Stephanie A|75691|-
Chu,Ron|78444|1138
Edgson,Karlene|85533|19
Fogarty,Kimberly M.|83442|-
Jagodzinska,Katarzyna|76098|-
Juszko,Paul|110832|-
Kwan,Alice|81139|-
Livingston,James|78629|11092
Mckenna,Kevin P|75385|-
Munday,Melanie|82393|50
Nishi,Liana N|81534|5356
Pang-Wong,Esther|79076|350
Soo Chan,Geoffrey|89758|-
Soroka,Amanda Leigh|97946|90
Strilaiff,Donald|83543|820
Young,Sean|135139|2654
Zitouni,Abderrachid|111997|1364'''
packet=json.loads((b/'own-independent20-source-only-packet.json').read_text());source=next(s for s in packet['sources'] if s['sourceKey']=='phsa-2011-12');out=[]
for r,loc in zip(rows.splitlines(),source['records']):out.append(dict(id=loc['id'],physicalPage=loc['physicalPage'],pageRow=loc['pageRow'],literalName=r.split('|')[0],literalRemuneration=r.split('|')[1],literalExpenses=r.split('|')[2],position=None,sourceCropSha256=loc['sha256']))
j=dict(candidateValuesOpened=False,method='Personal source-first read of all20 deterministically selected original400dpi full-row crops; no producer OCR/candidate accessed. Literal comma spacing and source dashes preserved.',sources=[dict(sourceKey='phsa-2011-12',rows=out)],noOutreach=True);assert not p.exists();p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest())
