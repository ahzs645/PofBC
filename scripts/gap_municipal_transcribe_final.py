#!/usr/bin/env python3
"""Final bounded small municipal scopes from actual original salary pages."""
import json
from gap_municipal_transcribe import AREA,entry
from gap_municipal_transcribe_clearwater import rows
from gap_municipal_transcribe_middle import rows as totalrows

def sections():
 out=[]
 out.append(entry('93428c2dc056',2021,36,'elected-officials',rows('''Banford, Barry|Councillor|11745.64|475.00
Blackwell, Merlin|Mayor|21880.46|1480.86
Frizzle, Lynne|Councillor|10995.64|721.42
Haring, William|Councillor|11745.64|484.92
Mackenzie, Lyle|Councillor|11745.64|29.79
Sim, Shelley|Councillor|11745.64|1375.70
Taylor, Nichola|Councillor|10995.64|30.08'''),{'remunerationComponent':'90854.30','expenses':'4597.77'}))
 out.append(entry('93428c2dc056',2021,36,'employee-remuneration',rows('''Green, Ken|Utility Operator II - Public Works|82959.25|2186.18
Groulx, Leslie|Chief Administrative Officer|136652.13|1957.12
Mayer, Roger|Manager of Facilities,Parks & Recreation|94167.45|3158.65
Shepherd, Roxanne|Director of Finance|104200.27|4122.06
Smith, Mike|Fire Chief/Community Safety Manager|81562.60|664.03
Woolliscroft, Shane|Public Works Foreman|82624.02|3410.00'''),{'remunerationComponent':'582165.72','expenses':'15498.04'},notes=['The printed name Woolliscroft is retained for this2021 source; spelling is not harmonized using later reports.']))
 out.append(entry('4433fd96ccd1',2022,37,'elected-officials',rows('''Banford, Barry|Councillor|10563.52|-
Blackwell, Merlin|Mayor|21699.44|7074.76
Braaten, Theresa|Councillor|1478.15|191.35
Frizzle, Lynne|Councillor|11291.67|638.10
Haring, William|Councillor|11291.67|162.04
Mackenzie, Lyle|Councillor|11291.67|9222.50
Matheson, Ken|Councillor|1478.15|170.60
Sim, Shelley|Councillor|11291.67|175.18
Taylor, Nichola|Councillor|9813.52|-'''),{'remunerationComponent':'90199.46','expenses':'17634.53'}))
 out.append(entry('4433fd96ccd1',2022,37,'employee-remuneration',rows('''Klassen, Linda|Director of Finance|90798.48|8697.93
Mayer, Roger|Manager of Facilities, Parks & Recreation|93318.42|5750.64
Smith, Mike|Fire Chief/Community Safety Manager|84416.27|4357.71
Thomas, John|Chief Administrative Officer|133874.35|7381.43
Vissher, Joshua|Utility Operator II - Public Works|75642.49|198.80
Wooliscroft, Shane|Public Works Foreman|92209.56|1291.75'''),{'remunerationComponent':'570259.57','expenses':'27678.26'},notes=['The printed name Wooliscroft is retained for2022, separately from the2021 spelling. No identity match or enrichment is inferred.']))
 out.append(entry('781bf4c10df9',2020,2,'elected-officials',totalrows('''ARMSTRONG, JUDY|~|8246.73|~|8246.73
KERSLAKE, ROBERT|~|8246.73|~|8246.73
KERSHAW, SCOTT|~|8246.73|~|8246.73
FORTIN: AL|~|8246.73|~|8246.73
KIBBLE: DONNA|~|8246.73|~|8246.73
SABYAN: AMANDA|~|8246.73|~|8246.73
STAMER: WARD|~|13112.94|75.00|13187.94'''),{'remunerationComponent':'62593.32','expenses':'75.00','expenseInclusiveTotal':'62668.32'},notes=['The source labels the complete group council remuneration but publishes no individual office/position labels; those positions stay null. Six visibly blank expense cells remain unknown, despite the row Totals equalling pay and the printed group expense subtotal being75.00. The staff section has no named observations and prints a dash under the over75000category; the separate767339.82 aggregate payroll is not individual salary data.']))
 out.append(entry('6433575e105c',2024,2,'elected-officials',totalrows('''ARMSTRONG, JUDY|~|9375.72|184.04|9559.76
KERSHAW, SCOTT|~|9375.72|508.08|9883.80
KERSLAKE, ROBERT|~|11122.40|196.40|11318.80
KIBBLE, DONNA|~|9375.72|~|9375.72
LODGE. LOUISE|~|9375.72|763.20|10138.92
MCINNIS, COLIN|~|9375.72|~|9375.72
STAMER, WARD|~|9743.84|381.06|10124.90'''),{'remunerationComponent':'67744.84','expenses':'2032.78','expenseInclusiveTotal':'69777.62'},notes=['No individual office labels are published in the council group, so positions remain null. Source punctuation is preserved, including LODGE. LOUISE. Blank expense cells are not inferred zero.']))
 out.append(entry('6433575e105c',2024,2,'employee-remuneration',totalrows('''P. AMOS|~|77608.85|380.00|77988.85
T. BUCHANAN|~|118749.23|1999.12|120748.35
C. MATTHEWS|~|89505.03|965.12|90470.15'''),{'allEmployees':{'remunerationComponent':'1069943.33','expenses':'39805.01','expenseInclusiveTotal':'1109748.34'},'unnamedEmployees':{'remunerationComponent':'784080.22','expenses':'36460.77','expenseInclusiveTotal':'820540.99'}},notes=['The source labels the named selection Employees with remuneration & expenses exceeding75000. The column Duties Remuneration is used as pay; the separate expense-inclusiveTotal is not pay. The source explains calendar cash-payment basis versus consolidated accrual financial statements.']))
 out.append(entry('04d85b324515',2023,6,'elected-officials',totalrows('''Maureen Pinkney|Mayor|22990.00|11639.14|34629.14
Donna Barnett|Councillor|9735.00|~|9735.00
Jenni Guimond|Councillor|11085.00|3664.35|14749.35
Ralph Fossum|Councillor|10782.00|4699.05|15481.05
Dave Mingo|Councillor|10935.00|4682.59|15617.59'''),{'remunerationComponent':'65527.00','expenses':'24685.13','expenseInclusiveTotal':'90212.13'},notes=['The supporting expense column is specifically Travel & Conferences, not a claim of all expense categories. Donna Barnett has a blank travel cell, which remains unknown rather than zero.']))
 out.append(entry('04d85b324515',2023,6,'employee-remuneration',totalrows('''Bissat, David|Fire Chief|83264.28|2035.93|85300.21
Boulanger, Tammy|Chief Administrative Officer|133446.37|10048.13|143494.50
Conway, Todd|Director of Community Services|147434.85|-|147434.85
Doddridge, Joanne|Director of Planning & Ec. Dec.|96276.84|2821.49|99098.33
Donnelly, Paul|Water & Sewer Operator|90337.24|2108.74|92445.98
Elias, Sheena|Director of Finance|89244.65|2111.47|91356.12
Hollander, Roger|Fire Chief|107921.58|2482.13|110403.71
Todd, Barry|Water & Sewer Operator|86027.30|3393.90|89421.20'''),{'remunerationComponent':'750688.83','expenses':'22965.86','expenseInclusiveTotal':'773654.69'},notes=['The source heading calls the remuneration column Base Salary, while its explanation says the schedule reflects actual in-year payments including vacation payouts, EOC overtime, overtime banks, personal-needs-time bonuses, retirement allowances and taxable benefits. Values remain the literal published column, not an annual base salary rate or a separately reconstructed compensation total. Travel & Conferences is the only separate expense column; it does not establish all other expenses. Conway has a printed expense dash retained as unknown. Two different Fire Chief observations are retained without an inferred identity or service-period split.']))
 return out
if __name__=='__main__':
 p=AREA/'transcripts-final.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
