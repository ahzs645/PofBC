#!/usr/bin/env python3
"""Remaining bounded Rossland source-image transcripts, preserving source defects."""
import json
from gap_municipal_transcribe import AREA,entry
from gap_municipal_transcribe_middle import rows

def sections():
 out=[]
 out.append(entry('2c30435db6cd',2012,40,'elected-officials',rows('''Mr. Greg Granstrom|Mayor|11797.23|4278.10|~
Ms. Jill Spearn|Councillor|6016.14|2929.96|~
Ms. Kathy Moore|Councillor|6016.14|1389.30|~
Ms. Kathy Wallace|Councillor|6016.14|387.70|~
Mr. Tim Thatcher|Councillor|6016.14|37.70|~
Ms. Jody Blomme|Councillor|6016.14|3141.37|~
Mr. Cary Fisher|Councillor|6016.14|37.70|~'''),{'remunerationComponent':'47894.07','expenses':'12201.83'}))
 out.append(entry('2c30435db6cd',2012,41,'employee-remuneration',rows('''Victor Kumar|~|180441.01|8546.05|188987.06
Darrin Albo|~|124353.60|3470.52|127824.12
Mike Maturo|~|99294.32|2693.52|101987.84
Tracey Butler|~|112174.17|6135.96|118310.13
Parry Lafond|~|75169.88|4663.84|79833.72
Kathy Smith|~|79790.77|-|79790.77
Ryan Zanussi|~|70072.82|2672.14|72744.96'''),{'allEmployees':{'remunerationComponent':'2023692.88','expenses':'40645.68','expenseInclusiveTotal':'2064338.56'},'unnamedEmployees':{'remunerationComponent':'1282396.31','expenses':'12463.65','expenseInclusiveTotal':'1294859.96'}},notes=['A source footnote on Victor Kumar states14038.75 benefit participation reimbursement included in remuneration. The reported payment is retained without subtraction or adjustment. The source names Ryan Zanussi below75000; the named row is retained.']))
 a=entry('fd093bc75659',2017,35,'elected-officials',rows('''Ms. K. Moore|Mayor|12010|0|6131|18141
Mr. A. Cosbey|Councillor|6125|0|450|6575
Mr. J. Greene|Councillor|6125|0|450|6575
Mr. M. Kruyse|Councillor|6125|~|450|6575
Mr. L. McLellan|Councillor|6125|0|2875|9000
Mr. A. Morel|Councillor|6125|0|450|6575
Mr. A. Zwicker|Councillor|6125|0|450|6575'''),{'remunerationComponent':'48760','taxableBenefits':'0','expenses':'11256','expenseInclusiveTotal':'60016'},components=True,notes=['The separate Taxable Benefit cell for M.Kruyse is visibly blank and remains unknown. App pay uses the literal Remuneration column uniformly for this entire council cohort, excluding separately displayed taxable benefits; no missing benefit is imputed zero and the expense-inclusiveTotal is not used as pay.'])
 a['payRepresentation']='remuneration-column-excluding-separately-published-taxable-benefits';out.append(a)
 out.append(entry('fd093bc75659',2017,36,'employee-remuneration',rows('''Albo, D|Manager of Operations|111436|12302|1328|125066
Hamming, E|Chief Financial Officer|96374|2302|6112|104788
Hinchcliffe, M|Journeyman Mechanic|82719|1254|550|84523
Issel, S|Journeyman Mechanic|75423|3086|150|78659
Jenkin, T|Journeyman Electrician|73072|3062|~|76134
LaFond, P|Building Inspector|77660|3103|5101|85864
Lightbourne, S|Planner|88042|3183|2645|93870
Skrudland, M|Plumber/Pipe Fitter|77808|3054|489|81351
Teasdale, B|Chief Administrative Officer|122096|3341|8941|134378
Williams, D|Public Works Tradesman III|88661|1220|~|89881
Zanussi, R|Public Works Foreman|89464|3111|841|93416'''),{'remunerationComponent':'982755','taxableBenefits':'39018','expenses':'26157','expenseInclusiveTotal':'1047930'},components=True))
 a=entry('ffa3b5b7e017',2023,47,'elected-officials',rows('''Andy Morel|Mayor|30000|8493|~
Stewart Spooner|Councillor|15000|1069|~
Maya Provencal|Councillor|15000|1692|~
Lisa Kwiatkowski|Councillor|15000|6660|~
Jeff Weaver|Councillor|15000|6224|~
Eliza Boyce|Councillor|15000|936|~
Craig Humpherys|Councillor|15000|798|~'''),{'remunerationComponent':'120000','expenses':'25872','expenseInclusiveTotal':'145872'},notes=['Schedule heading explicitly says year ended December31,2023; its contracts boilerplate refers to2022, retained as a separate source inconsistency rather than changing the remuneration year. Prepared and signed May6,2024. Several separate expense-inclusiveTotal cells have visibly missing digit strokes; no total is reconstructed by adding remuneration and expenses and these cells are not used for pay.'])
 for row,literal in zip(a['rows'],['3 493','1 069','1 692','2 660','2 224','1 936','1 798']):row['expenseInclusiveTotalRawVisible']=literal;row['expenseInclusiveTotalStatus']='visibly-incomplete-original-number-not-used'
 out.append(a)
 out.append(entry('ffa3b5b7e017',2023,48,'employee-remuneration',rows('''Adamson, L|Public Works Clerk|93008|1005|94012
Anonuevo, C|Deputy Corporate Officer|102877|4383|107260
Borwick, H|Recreation Programmer|75519|590|76109
Brogan, J|Accounting Clerk II|83672|8226|91898
Calder, K|Manager of Recreation & Events|97590|6981|104571
Fike, J|Public Works Tradesman III|87807|110|87917
Grey, D|Public Works Tradesman II|80072|218|80290
Hinchcliffe, M|Journeyman Mechanic|94903|706|95609
Huska, B|Water Treatment Plant Operator|89810|1811|91621
Issel, S|Journeyman Mechanic|89082|218|89300
Keating, Z|Bylaw Officier|74930|3784|78714
Kennedy, M|Manager of Finance|123880|4995|128875
Lafond, P|Building Inspector|101786|5083|106870
Lamont, S|Manager of Operations|127662|1889|129551
Lightbourne, S|Manager of Planning & Development|124196|3178|127374
Newton, R|Executive Assistant|70612|5496|76108
Nowak, H|Recreation Attendant II|76436|1243|77679
Powchuk, A|Journeyman Electrician|94390|866|95256
Silva, C|Public Works Tradesman I|78422|218|78640
Spearman, K|Development Services Clerk|75005|225|75230
Stefiuk, D|Accounting Clerk I|74949|497|75446
Teasdale, B|Chief Administrative Officer|185600|8894|194494
Turner, E|Recreation Attendant II|81536|2645|84182
Williams, D|Public Works Tradesman III|87575|1005|88579
Zanussi, R|Public Works Foreman|110165|1806|111970'''),{'remunerationComponent':'2381483','expenses':'66072','expenseInclusiveTotal':'2447555'},notes=['The literal source job title By law/Bylaw Officier spelling is not repaired from a dictionary. All named below75000 remuneration rows are retained; the source does not imply a complete workforce census.']))
 return out
if __name__=='__main__':
 p=AREA/'transcripts-rossland-additional.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
