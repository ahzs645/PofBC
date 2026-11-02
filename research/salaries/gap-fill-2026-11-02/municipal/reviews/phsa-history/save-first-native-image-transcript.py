from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent
readings={
'phsa-2006-07':[(1,'Abadi, Shirin',95628,'2,403'),(97,'Bjornson, Bruce',183501,'(0)'),(141,'Butts, Janet',77327,'-'),(282,'Dobson, Simon M',255452,'5,139'),(423,'Haderer, Franziska',85928,'-'),(563,'Kendrick, Jennifer',90304,'650'),(704,'MacKenzie, Jennifer',111997,'8,570'),(845,'Nichols, Ann Marie',78680,'-'),(985,'Rudolph, Susan M',100315,'-'),(1126,'Ternes, Joyce L',107885,'1,056'),(1267,'Zilberman, Lilia',78356,'8,856')],
'phsa-2007-08':[(1,'Abadi,Shirin',99450,'3,244'),(142,'Burchill,Nancy',84686,'-'),(283,'Dobson,Simon M',267983,'3,518'),(424,'Gwynn,Heather E.',77826,'-'),(441,'Hartley,Daria',96322,'(0)'),(565,'Kerray,Betty M',104979,'10,764'),(706,'MacKay,Florence Catharine',84116,'3,854'),(847,'Ng,Sylvia',83771,'6,120'),(988,'Rowe,Susan I.',80780,'2,084'),(1129,'Tejpar,Ismet',161542,'624'),(1271,'Zhu,Weigang',85814,'197')],
'phsa-2008-09':[(1,'Abadi,Shirin',103140,'2,195'),(172,'Butts,Janet',82626,'-'),(289,'Cranston,Lynda*',408452,'50,569'),(343,'Dharamsi,Azmina',125380,'664'),(515,'Graham,Darryl',113792,'3,808'),(686,'Kelly,Barbara J',85322,'772'),(858,'Maginley,Juanita',82286,'8,980'),(1029,'Norrish,Avery',75527,'-'),(1201,'Sam,Janette',79430,'12,378'),(1372,'Thomas,Eva E.',402078,'12,738'),(1544,'Zhu,Weigang',86173,'3,281')]
}
packet=json.loads((B/'native-source-image-peer-packet.json').read_text());targets={(r['sourceKey'],r['sequence']):r for r in packet['targets']}
rows=[]
for key,rs in readings.items():
 for seq,name,pay,expense in rs:
  t=targets[key,seq]
  rows.append({'sourceKey':key,'sequence':seq,'pdfPage':t['physicalPage'],'name':name,'position':None,'remuneration':pay,'sourceExpenses':expense,'expenses':None if expense=='-' else 0 if expense=='(0)' else int(expense.replace(',','')),'sourceNameFootnote':'*' if name.endswith('*') else None,'imagePath':t['path'],'imageSha256':t['sha256']})
out={'phase':'first personal source-image transcript before producer candidates','scope':'33 complete named rows /66 monetary cells:30 deterministic holdouts plus3 literal native-reader flags. Not an all4082-row personal transcription claim.','rows':rows,'all33RowsPersonallyViewed':True,'sourceParenthesesZeroNumericZero':True,'sourceDashExpensesRemainNull':True,'sourceCranstonAsteriskIsSuperscriptFootnote':True,'noOutreach':True}
p=B/'native-first-source-image-transcript.json';assert not p.exists();p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest())
