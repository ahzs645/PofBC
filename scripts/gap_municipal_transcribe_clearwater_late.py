#!/usr/bin/env python3
"""Remaining Clearwater schedule scopes from the actual PDF-painted pages."""
import json
from gap_municipal_transcribe import AREA,entry
from gap_municipal_transcribe_clearwater import add,rows

def sections():
 out=[]
 add(out,'0403cd1b4359',2011,3,'''Harwood, John|Mayor|17026.67|3675.65
Buck, David*|Councillor|8538.54|0.00
Dobi, Christine*|Councillor|8538.54|0.00
Graffunder, Candus*|Councillor|8538.54|737.69
Kjenstad, Ken|Councillor|8881.62|5673.46
Teare, Stephanie*|Councillor|8538.54|3631.87
Walker, Albert*|Councillor|8538.54|4480.17
Banford, Barry*|Councillor|343.08|516.92
Blackwell, Merlin*|Councillor|343.08|392.50
Heisterman, Gord*|Councillor|343.08|517.50
Kreke, Jon*|Councillor|343.08|517.50
Sim, Shelley*|Councillor|343.08|517.50''','''Isabell Hadford|Chief Administrative Officer|108095.31|2330.00
Leslie Groulx**|Corporate Administrator/CAO|96453.92|7860.44
Robert Griffiths|Public Works Foreman|78681.59|2102.01''',['70316.39','20660.76'],['993957.38','55942.46'],['710726.56','43650.01'],['Single asterisk denotes part of year. Leslie Groulx double asterisk includes EOC wages donated to Cancer Foundation and Municipal Election earnings; the disclosed payment is retained without charity deductions or annualization.'])
 out.append(entry('db8642b32d6f',2017,12,'elected-officials',rows('''Harwood, John|Mayor|17890.28|2022.30
Banford, Barry|Councillor|9309.42|2170.92
Blackwell, Merlin|Councillor|9310.05|1052.41
Greffard, Dennis|Councillor|9309.42|5037.96
Heisterman, Gord|Councillor|9309.42|4744.23
Kjenstad, Ken|Councillor|9309.42|4243.06
Sim, Shelley|Councillor|9309.42|4346.93'''),{'remunerationComponent':'73747.43','expenses':'23617.81'}))
 a=entry('db8642b32d6f',2017,12,'employee-remuneration',rows('''Groulx, Leslie|Chief Administrative Officer|122049.05|5356.66
Lipp, Bryan**|Public Works Leadhand|87321.80|69.99
Griffiths, Robert**|Public Works Maintenance|86621.39|3475.47
Mayer, Roger|Recreation Facilities Supervisor|95646.50|4739.45
Smith, Mike|Fleet & Road Manager/Fire Chief|79769.57|5666.22'''),{'allEmployees':{'remunerationComponent':'1074455.72','expenses':'19307.79'},'unnamedEmployees':{'remunerationComponent':'603047.41','expenses':None}},notes=['Printed Total Remuneration includes both operational and emergency-response remuneration. These original components remain in provenance; the Total is remuneration-only, not expense-inclusive. Double asterisk indicates employer RRSP contributions are included for Lipp and Griffiths. No amount is deducted or reclassified as base salary. Unnamed aggregate expense cells remain unknown.'])
 for row,op,er in zip(a['rows'],['114574.33','87142.76','86442.35','95646.50','77338.31'],['7474.72','179.04','179.04','0.00','2431.26']):row.update(operationalRemuneration=op,emergencyResponseRemuneration=er)
 a['additionalPrintedControls']={'allOperationalRemuneration':'1064191.66','allEmergencyResponseRemuneration':'10264.06'};out.append(a)
 out.append(entry('7c2f7c934eb9',2018,10,'elected-officials',rows('''Harwood, John|Mayor*|16447.43|1409.79
Banford, Barry|Councillor|10085.87|3141.02
Blackwell, Merlin|Mayor/Councillor|11272.59|1960.21
Frizzle, Lynne|Councillor*|1287.44|205.59
Greffard, Dennis|Councillor*|8798.44|4027.90
Haring, William|Councillor*|1287.44|277.02
Heisterman, Gord|Councillor*|8798.44|3995.52
Kjenstad, Ken|Councillor*|8798.44|4262.63
Mackenzie, Lyle|Councillor*|1287.44|273.60
Sim, Shelley|Councillor|10085.87|3477.61
Taylor, Nichola|Councillor*|1287.44|217.50'''),{'remunerationComponent':'79436.84','expenses':'23248.39'},notes=['An asterisk explicitly denotes partial year. Original combined Mayor/Councillor position is preserved as printed; no individual role or period is split or inferred.']))
 out.append(entry('7c2f7c934eb9',2018,10,'employee-remuneration',rows('''Groulx, Leslie|Chief Administrative Officer|117944.56|7905.74
Griffiths, Robert**|Public Works Maintenance|87524.06|185.57
Mayer, Roger|Recreation & Facilities Manager|93497.66|6804.18
Shepherd, Roxanne|Director of Finance|98764.47|1901.81
Smith, Mike|Fire Chief/ Bylaw/Safety|76900.70|10428.71'''),{'remunerationComponent':'474631.45','expenses':'27226.01'},notes=['Double asterisk on Griffiths means employer RRSP contribution included. Published total remuneration is retained without subtracting an unquantified contribution. Unnamed payroll715414.08 and all-employee1190045.53 remain aggregate evidence, not individual observations.']))
 out.append(entry('5795f93d9513',2019,6,'elected-officials',rows('''Banford, Barry|Councillor|11413.12|5163.53
Blackwell, Merlin|Mayor|21241.38|5054.51
Frizzle, Lynne|Councillor|11413.12|4710.78
Haring, William|Councillor|11413.12|5255.96
Mackenzie, Lyle|Councillor|11413.12|6557.14
Sim, Shelley|Councillor|11413.12|3676.23
Taylor, Nichola|Councillor|11413.12|2614.34'''),{'remunerationComponent':'89720.10','expenses':'33032.49'}))
 out.append(entry('5795f93d9513',2019,6,'employee-remuneration',rows('''Bezema, Ernst|Public Works Manager|84070.36|533.54
Groulx, Leslie|Chief Administrative Officer|118513.32|4417.52
Griffiths, Robert**|Public Works Maintenance|79727.05|604.00
Mayer, Roger|Recreation & Facilities Manager|92746.88|4715.17
Shepherd, Roxanne|Director of Finance|100227.56|3736.59
Smith, Mike|Fire Chief/Bylaw/Safety|78668.62|3258.91'''),{'remunerationComponent':'553953.79','expenses':'17265.73'},notes=['Double asterisk on Griffiths means employer RRSP contribution included. Aggregate payroll612966.05 under threshold and1166919.84 all employees do not become individual salary observations.']))
 out.append(entry('92a491e9872e',2020,36,'elected-officials',rows('''Banford, Barry|Councillor|11658.31|-
Blackwell, Merlin|Mayor|21712.75|537.21
Frizzle, Lynne|Councillor|11658.31|2038.05
Haring, William|Councillor|11658.31|-
Mackenzie, Lyle|Councillor|11658.31|-
Sim, Shelley|Councillor|11658.31|2168.50
Taylor, Nichola|Councillor|10908.31|-'''),{'remunerationComponent':'90912.61','expenses':'4743.76'}))
 out.append(entry('92a491e9872e',2020,36,'employee-remuneration',rows('''Bezema, Ernst|Public Works Manager|84977.96|50.00
Green, Ken|Utilities Worker 3|83016.31|1145.85
Groulx, Leslie|Chief Administrative Officer|135456.12|2752.22
Mayer, Roger|Recreation Facilities Supervisor|93836.20|2500.12
Shepherd, Roxanne|Director of Finance|102096.04|2523.41
Smith, Mike|Fleet & Road Manager/Fire Chief|80382.38|3885.19'''),{'remunerationComponent':'579765.01','expenses':'12856.79'},notes=['Unnamed payroll623101.11 and all-employee1202866.12 are supporting aggregate amounts only.']))
 return out
if __name__=='__main__':
 p=AREA/'transcripts-clearwater-2011-and-2017-2020.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
