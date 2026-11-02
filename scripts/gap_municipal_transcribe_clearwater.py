#!/usr/bin/env python3
"""Literal Clearwater source-image observations; footnote marks remain in evidence."""
import json
from gap_municipal_transcribe import AREA,entry

def rows(t):return [[None if c=='~' else c for c in l.split('|')]+[None] for l in t.strip().splitlines()]
def add(out,sha,year,page,council,employees,ccontrol,allcontrol,under,notes=None):
 out.append(entry(sha,year,page,'elected-officials',rows(council),dict(zip(['remunerationComponent','expenses'],ccontrol)),notes=notes))
 out.append(entry(sha,year,page,'employee-remuneration',rows(employees),{'allEmployees':dict(zip(['remunerationComponent','expenses'],allcontrol)),'unnamedEmployees':dict(zip(['remunerationComponent','expenses'],under))},notes=notes))
def sections():
 out=[]
 add(out,'74b9c233c081',2012,2,'''Harwood, John|Mayor|17142.06|3189.83
Banford, Barry|Councillor|8920.08|3133.05
Blackwell, Merlin|Councillor|8920.08|2067.95
Heisterman, Gord|Councillor|8920.08|3955.04
Kjenstad, Ken|Councillor|8920.08|5477.07
Kreke, Jon|Councillor|8920.08|5224.53
Sim, Shelley|Councillor|8920.08|4125.66''','''Leslie Groulx|Chief Administrative Officer|100351.94|7376.10
Sheila Thiessen|Director of Finance|88936.45|6242.11
Robert Griffiths|Public Works Foreman|76994.43|558.68''',['70662.54','27173.13'],['903509.95','49110.95'],['637227.13','34934.06'])
 add(out,'98e145752fb7',2013,2,'''Harwood, John|Mayor|17210.70|5182.35
Banford, Barry|Councillor|8955.70|5197.62
Blackwell, Merlin|Councillor|8955.70|72.74
Heisterman, Gord|Councillor|8955.70|5190.31
Kjenstad, Ken|Councillor|8955.70|4583.42
Kreke, Jon|Councillor|8955.70|4244.91
Sim, Shelley|Councillor|8955.70|6418.11''','''Leslie Groulx|Chief Administrative Officer|104146.92|10777.72
Sheila Thiessen|Director of Finance|91287.14|8668.56
Jared Brounstein|Public Works Superintendent|83557.53|4979.21
Robert Griffiths|Public Works|81913.39|3318.41''',['70944.90','30889.46'],['1028727.17','54777.64'],['667822.19','27033.74'])
 add(out,'a47910232589',2014,2,'''Harwood, John|Mayor|17210.70|3841.02
Banford, Barry|Councillor|8955.70|3728.98
Blackwell, Merlin|Councillor|8955.70|2035.18
Greffard, Dennis*|Councillor|344.45|304.80
Heisterman, Gord|Councillor|8955.70|3202.91
Kjenstad, Ken|Councillor|8955.70|3129.63
Kreke, Jon*|Councillor|8611.26|4164.35
Sim, Shelley|Councillor|8955.70|3959.99''','''Leslie Groulx|Chief Administrative Officer|105584.83|6968.44
Sheila Thiessen|Director of Finance|92572.23|4358.60
Roger Mayer|Recreation Facilities Supervisor|76829.15|1093.31
Jared Brounstein*|Public Works Superintendent|47416.07|3452.96
Ryan Papp*|Public Works Superintendent|31420.93|1561.94''',['70944.91','24366.86'],['955972.47','50290.88'],['602149.26','32855.63'],['The printed asterisk means partial year. Named below-threshold partial-year observations stay included; no annualization is performed. The marker remains in source-name evidence and is removed only as an explicitly defined footnote marker from the displayed name.'])
 add(out,'7ef7d7b46337',2015,2,'''Harwood, John|Mayor|18042.53|7109.75
Banford, Barry|Councillor|9388.51|3192.65
Blackwell, Merlin|Councillor|9388.51|764.34
Greffard, Dennis|Councillor|9388.51|5388.88
Heisterman, Gord|Councillor|9388.51|4450.69
Kjenstad, Ken|Councillor|9388.51|5492.44
Sim, Shelley|Councillor|9388.51|4743.14''','''Bruce Forsyth*|Public Works Superintendent|71578.89|5553.94
Leslie Groulx|Chief Administrative Officer|114968.80|10294.62
Papp Ryan*|Public Works Superintendent|9409.44|235.00
Roger Mayer|Recreation Facilities Supervisor|89247.74|2325.22
Sheila Thiessen*|Director of Finance|46979.77|908.68
Wesley Renaud*|Director of Finance|56343.53|8963.42''',['74373.59','31141.89'],['1080548.37','41587.50'],['692020.20','13306.62'],['The printed asterisk means partial year. Papp Ryan is retained in the original printed name order, without correction using another year. Source states27pay periods for elected officials and employees in2015; no annualization is performed.'])
 add(out,'1040cf980005',2016,7,'''Harwood, John|Mayor|17573.94|1217.93
Banford, Barry|Councillor|9144.82|801.35
Blackwell, Merlin|Councillor|9144.82|1730.44
Greffard, Dennis|Councillor|9144.82|2747.49
Heisterman, Gord|Councillor|9144.82|5222.87
Kjenstad, Ken|Councillor|9144.82|5832.02
Sim, Shelley|Councillor|9144.82|5388.71''','''Forsyth, Bruce*|Public Works Superintendent|17865.28|42.96
Groulx, Leslie|Chief Administrative Officer|111268.78|6326.31
Lipp, Bryan|Public Works Leadhand|78655.12|164.96
Mayer, Roger|Recreation Facilities Supervisor|92760.11|2619.57
Renaud, Wesley|Director of Finance|92420.38|4145.99''',['72442.86','22940.81'],['1080204.78','13299.79'],['687235.11',None],['The source leaves the unnamed aggregate expense cell blank. Its expense amount remains unknown even though the known named expense sum equals the printed all-employee expense total; no zero is inferred. The printed asterisk means partial year.'])
 return out
if __name__=='__main__':
 p=AREA/'transcripts-clearwater-2012-2016.json';p.write_text(json.dumps({'status':'candidate-awaiting-independent-peer','sections':sections()},ensure_ascii=False,indent=2)+'\n');print(p)
