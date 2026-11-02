#!/usr/bin/env python3
"""Public originals recovered beyond stale direct-link coverage."""
import json
from gap_municipal_transcribe import AREA,entry
from gap_municipal_transcribe_middle import rows

def sections():
 out=[]
 out.append(entry('5c8e8ff1f8c0',2014,57,'employee-remuneration',rows('''Mr. D Albo|Manager of Public Works|134352|13001|147353
Ms. T Butler|Deputy CAO/CO|134364|3272|137636
Miss L Hunter|Acting CFO|89412|7460|96873
Mrs. S Lightbourne|Planner|82517|3852|86369
Mr. P LaFond|Building Inspector|81591|6983|88574
Ryan Zanussi|Tradesman 3|76779|1242|78021'''),{'allEmployees':{'remunerationComponent':'2686448','expenses':'35811','expenseInclusiveTotal':'2722259'},'unnamedEmployees':{'remunerationComponent':'2087433','expenses':None,'expenseInclusiveTotal':'2087433'}},notes=['Recovered from the officialJune22,2015 council agenda, physicalpage57; the direct archive link labelled2014 retrieves the2013report instead. This distinct original explicitly says For the year2014 and its memorandum is datedJune16,2015.','The consolidated other-payment group is labelled including elected officials. No named council observations are supplied by this aggregate. The six named employee observations remain distinct from that aggregate.','The six known employee expense cells sum35810CAD; the sourceTOTALexpensecolumn prints35811CAD. The unnamed aggregate expense cell is blank, so no zero or exact named expense control is inferred. Miss L Hunter prints89412remuneration plus7460expenses while its separateTotal is96873, onehigher than those components. Published amounts are unchanged; no cause is inferred.']))
 out.append(entry('a8459d119235',2024,4,'elected-officials',rows('''Jones, Joan|Councillor|15681|2285|~
Lerner, Jonathan|Councillor|15681|7915|~
Mundell, Rachelle|Councillor|15681|710|~
Savage, Ian|Councillor.|15681|1548|~
Swain, Mark|Mayor|28291|7740|~'''),{'remunerationComponent':'91015','expenses':'20198'},notes=['The recovered2024original is distinct from the supplied2025report alreadyaccepted. Both reporting-year header and the signed approval page9identify2024; signatures are datedJune25,2025.']))
 out.append(entry('a8459d119235',2024,4,'employee-remuneration',rows('''Coates, Trudy|Director of Corporate Administration|80632|161|~
Gosling, Jason|Park Technician III|76495|1406|~
Masse, Amanda|Planner|83140|3021|~
Morphy, Glenn|Director of Public Works|151269|1458|~
Robinson, George|Director of Planning and Community Services|86077|2247|~
Rukus, Neil|Fire Chief|100619|3261|~
Thurlin, Eric|Maintenance Technician III|85230|1261|~
Wells, Delcy|Director of Corporate Administration|109385|3133|~
Woods, Matthew|Foreman|75211|4335|~'''),{'allEmployees':{'remunerationComponent':'1640104','expenses':'80933'},'unnamedEmployees':{'remunerationComponent':'792046','expenses':'60650'}},notes=['The2024report describes one18monthnonunionseverance agreement with payments in2024and2025, but provides no named allocation here. No amount or agreement is attributed to a person by inference and no payment is annualized. The signed approval on physicalpage9is datedJune25,2025.']))
 return out
if __name__=='__main__':
 p=AREA/'transcripts-recovered-originals.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
