#!/usr/bin/env python3
"""Actual-original image transcripts for the Rossland component layouts."""
import json
from gap_municipal_transcribe import AREA,entry

def rows(text):
 return [[None if t=='~' else t for t in line.split('|')] for line in text.strip().splitlines()]
def sections():
 out=[]
 a=entry('31dadfc3ccf6',2016,34,'elected-officials',rows('''Ms. K. Moore|Mayor|11798|0|3524|15322
Mr. A. Cosbey|Councillor|6016|0|3175|9191
Mr. J. Greene|Councillor|6016|0|3242|9258
Mr. M. Kruyse|Councillor|6016|~|0|6016
Mr. L. McLellan|Councillor|6016|0|0|6016
Mr. A. Morel|Councillor|6016|0|1086|7102
Mr. A. Zwicker|Councillor|6016|0|0|6016'''),{'remunerationComponent':'47894','taxableBenefits':'0','expenses':'11027','expenseInclusiveTotal':'58921'},components=True,notes=['M.Kruyse has a visibly blank Taxable Benefit cell, unlike the other explicit zero cells. Its value is unknown; no zero is inferred from the subtotal or row Total. Hold that row from composite-pay publication unless root explicitly adopts another source-defined pay representation.'])
 a['unresolvedCompositePayRows']=[4];out.append(a)
 out.append(entry('31dadfc3ccf6',2016,35,'employee-remuneration',rows('''Albo, D|Manager of Operations|111434|12130|70|123634
Hinchcliffe, M|Journeyman Mechanic|77815|1267|~|79082
Issel, S|Journeyman Mechanic|75185|3098|~|78283
Jenkin, T|Journeyman Electrician|72796|2907|70|75773
LaFond, P|Building Inspector|77379|3115|3475|83969
Lightbourne, S|Planner|87391|3196|2702|93289
Mercer, K|Accounting Clerk II|72448|2870|1561|76879
Pols, J|Journeyman Carpenter|72318|3067|117|75502
Skrudland, M|Plumber/Pipe Fitter|74445|2893|2075|79413
Teasdale, B|Chief Administrative Officer|77538|2149|3579|83266
Williams, D|Public Works Tradesman III|74294|2134|~|76428
Zanussi, R|Public Works Foreman|85218|3096|2658|90972'''),{'remunerationComponent':'958261','taxableBenefits':'41922','expenses':'16307','expenseInclusiveTotal':'1016490'},components=True))
 a=entry('11dd025d45a1',2018,36,'elected-officials',rows('''Ms. K. Moore|Mayor|12828|0|5234|18063
Mr. A. Cosbey|Councillor|5531|0|0|5531
Mr. J. Greene|Councillor|5531|0|3339|8870
Mr. M. Kruyse|Councillor|5531|~|0|5531
Mr. L. McLellan|Councillor|5531|0|0|5531
Mr. A. Morel|Councillor|6542|0|1408|7950
Mr. A. Zwicker|Councillor|5531|0|0|5531
Mr. C. Bowman|Councillor|1011|0|387|1398
Mr. S. Forsyth|Councillor|1011|0|387|1398
Mr. D. Lewis|Councillor|1011|0|387|1398
Mrs. J. Nightingale|Councillor|1011|0|387|1398
Mr. S. Spooner|Councillor|1011|0|0|1011'''),{'remunerationComponent':'52080','taxableBenefits':'0','expenses':'11530','expenseInclusiveTotal':'63610'},components=True,notes=['M.Kruyse has a visibly blank Taxable Benefit cell; no zero is inferred. That row is held from composite-pay publication unless root adopts another explicitly source-defined representation. The12 observations include outgoing and incoming council members.'])
 a['unresolvedCompositePayRows']=[4];out.append(a)
 out.append(entry('11dd025d45a1',2018,37,'employee-remuneration',rows('''Adamson, L|Public Works Clerk|75572|1695|44|77311
Albo, D|Manager of Operations|111430|11758|3481|126669
Fike, J|Public Works Tradesman III|74107|1245|172|75524
Hamming, E|Chief Financial Officer|104640|1850|3342|109832
Hinchcliffe, M|Journeyman Mechanic|82594|1225|~|83819
Issel, S|Journeyman Mechanic|77487|2404|44|79935
Jenkin, T|Journeyman Electrician|78518|1849|44|80411
LaFond, P|Building Inspector|79196|2269|5338|86803
Lightbourne, S|Planner|89539|2195|4964|96698
Powchuk, A|Journeyman Electrician|82185|2315|2325|86825
Skrudland, M|Plumber/Pipe Fitter|75507|2081|397|77985
Stefiuk, D|Accounting Clerk II|71137|2065|2918|76119
Teasdale, B|Chief Administrative Officer|132535|2458|2127|137119
Williams, D|Public Works Tradesman III|74897|2013|2266|79175
Zanussi, R|Public Works Foreman|87324|2379|1411|91114'''),{'remunerationComponent':'1296667','taxableBenefits':'39799','expenses':'28874','expenseInclusiveTotal':'1365341'},components=True))
 out.append(entry('698458fdc4ba',2019,36,'elected-officials',rows('''Ms. K. Moore|Mayor|17624|0|4426|22050
Mr. A. Morel|Councillor|8988|0|1043|10031
Mr. C. Bowman|Councillor|8988|0|2990|11978
Mr. S. Forsyth|Councillor|8988|0|0|8988
Mr. D. Lewis|Councillor|8988|18|2527|11533
Mrs. J. Nightingale|Councillor|8988|0|3069|12057
Mr. S. Spooner|Councillor|8988|0|915|9903'''),{'remunerationComponent':'71551','taxableBenefits':'18','expenses':'14970','expenseInclusiveTotal':'86539'},components=True))
 out.append(entry('698458fdc4ba',2019,37,'employee-remuneration',rows('''Adamson, L|Public Works Clerk|77951|2014|2014.32|81980
Albo, D|Manager of Operations|111441|11754|911.97|124107
Anonuevo, C|Deputy CAO|74358|2491|3175.46|80024
Fike, J|Public Works Tradesman III|73750|1564|1564.32|76879
Hamming, E|Chief Financial Officer|107718|2278|9278.19|119275
Hinchcliffe, M|Journeyman Mechanic|80925|1593|1592.80|84111
Hopkins, J|Public Works Tradesman II|77768|2515|2515.48|82799
Issel, S|Journeyman Mechanic|78427|2521|~|80948
LaFond, P|Building Inspector|94370|2603|2602.84|99576
Lightbourne, S|Planner|99539|2852|3306.58|105697
Powchuk, A|Journeyman Electrician|78035|2493|3855.62|84384
Skrudland, M|Plumber/Pipe Fitter|77252|2494|2493.96|82240
Stefiuk, D|Accounting Clerk II|73127|2783|~|75911
Teasdale, B|Chief Administrative Officer|136430|2850|6480.00|145760
Williams, D|Public Works Tradesman III|76743|2460|182.57|79386
Zanussi, R|Public Works Foreman|87141|2537|903.50|90581'''),{'remunerationComponent':'1404976','taxableBenefits':'47803','expenses':'40878','expenseInclusiveTotal':'1493656'},components=True))
 out.append(entry('7e75b2164251',2020,38,'elected-officials',rows('''Ms. K. Moore|Mayor|18691|0|806|19497
Mr. A. Morel|Councillor|9532|0|362|9894
Mr. C. Bowman|Councillor|9532|0|806|10337
Mr. D. Lewis|Councillor|9532|39|443|10014
Mr. T. Miller|Councillor|353|0|0|353
Mrs. J. Nightingale|Councillor|9532|0|897|10429
Mr. S. Spooner|Councillor|9532|0|362|9894
Mr. S. Forsyth|Councillor|623|0|0|623'''),{'remunerationComponent':'67326','taxableBenefits':'39','expenses':'3677','expenseInclusiveTotal':'71042'},components=True,notes=['Source states27biweekly pay periods in2020 rather than the usual26. Payments are not annualized or shifted into another period.']))
 out.append(entry('7e75b2164251',2020,39,'employee-remuneration',rows('''Adamson, L|Public Works Clerk|80163|1096|380|81639
Albo, D|Manager of Special Projects|116179|10382|629|127190
Anonuevo, C|Deputy Corporate Officer|80550|1130|4590|86270
Calder, K|Manager of Recreation & Events|77219|1132|3185|81536
Fike, J|Public Works Tradesman III|80108|1143|495|81746
Hamming, E|Chief Financial Officer|120998|1418|3899|126315
Hinchcliffe, M|Journeyman Mechanic|86323|1128|736|88186
Hopkins, J|Public Works Tradesman III|87043|1096|1031|89170
Issel, S|Journeyman Mechanic|83584|1157|736|85476
LaFond, P|Building Inspector|95811|1456|1162|98429
Lamont, S|Infrastructure|76148|646|645|77440
Lightbourne, S|Manager of Planning & Development|108533|1360|4440|114332
Powchuk, A|Journeyman Electrician|84499|1128|2367|87995
Teasdale, B|Chief Administrative Officer|150605|1479|3862|155946
Williams, D|Public Works Tradesman III|82200|1096|736|84032
Zanussi, B|Public Works Tradesman III|81588|1072|-|82660
Zanussi, R|Public Works Foreman|110598|1231|736|112565'''),{'remunerationComponent':'1602151','taxableBenefits':'29150','expenses':'29626','expenseInclusiveTotal':'1660927'},components=True,notes=['Source states27biweekly pay periods in2020. Literal remuneration and taxable benefits are added as known pay components; the expense-inclusive Total remains supporting evidence.']))
 return out
if __name__=='__main__':
 p=AREA/'transcripts-middle.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
