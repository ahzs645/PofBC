from pathlib import Path
import json,hashlib
B=Path(__file__).parent;j=json.loads((B/'own-all-expense-shape-source-only-audit.json').read_text());out=[]
raw={'phsa-2011-12':'''Barnetson,Duncan Stewart|78158|5
Moosa,Nazma K.|93837|4
Lencewicz,Andrzej Jan|87635|-
Riddell,Janice E.|85308|-
Gooding,Sherill J|116889|-
Strohmaier,John|110860|-
Campbell,Trevor|77992|-
Ho,Terry T.|75812|-
Casson,Gail|88249|-
Barron,Lorne|78082|-
Van Mulligen,Paula|76010|-
Hilder,David|124630|-''','phsa-2012-13':'''Cheung, Vivian Y.|77647|8
Gillies, Patricia|82416|6
Roka, Shkumbin|85169|9
Ryan, Cindy (Louise)|79766|5
Sachedina, Salina|89406|7
Zalter, Michael D.|87545|8
Harry, Teresa|82461|-
Bagri, Harpreet (Sunny) Singh|77780|-
Sugrue, Aaron|136296|-
Stevens, Jillian|79010|-
Leung, Nicole Faith|77242|-
Klar, Sandy|75876|-
Sorotla, Jean|85330|-
Cumming, Linda|86995|-
Brandon, Maaret|89480|-
Fair, Steve|77225|-'''}
for s in j['sources']:
 rows=[];lines=raw[s['sourceKey']].splitlines();assert len(lines)==len(s['sourceOnlyCalibrationRecords'])
 for r,loc in zip(lines,s['sourceOnlyCalibrationRecords']):
  n,p,e=r.split('|');rows.append(dict(id=loc['id'],physicalPage=loc['physicalPage'],pageRow=loc['pageRow'],literalName=n,literalRemuneration=p,literalExpenses=e,sourceCropSha256=loc['sha256']))
 out.append(dict(sourceKey=s['sourceKey'],sourceSha256=s['sourceSha256'],rows=rows))
p=B/'own-expense-calibration-personal-first-transcript.json';assert not p.exists();p.write_text(json.dumps(dict(candidateValuesOpened=False,method='Personally read all8 narrow/tall expense-cell source targets and20 original dash benchmarks in full-row400dpi originals before producer rawreader/candidate access. Eight actual numeric values4/5/5/6/7/8/8/9; no explicit numeric0 found in these targets. Shape classification is only a review diagnostic, not value proof. One initial cropped leadingZ independently rerendered with expanded original margin before this transcript.',sources=out,noOutreach=True),indent=2,ensure_ascii=False)+'\n');print('first28',hashlib.sha256(p.read_bytes()).hexdigest());files=['own-all-expense-shape-source-only-audit.json','own-expense-calibration-personal-first-transcript.json','own-expense-calibration/expanded-name-margin-addendum.json'];q=B/'expense-calibration-source-first-freeze.json';q.write_text(json.dumps(dict(candidateValuesOpened=False,personalSourceRows=28,files=[dict(path=str((B/f).relative_to(Path('/workspace/PofBC'))),sha256=hashlib.sha256((B/f).read_bytes()).hexdigest()) for f in files]),indent=2)+'\n');print('freeze',hashlib.sha256(q.read_bytes()).hexdigest())
