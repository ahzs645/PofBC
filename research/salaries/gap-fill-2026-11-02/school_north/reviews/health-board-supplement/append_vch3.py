from append_first import add
cols=['Remuneration','Expenses','Total']
add('vancouver-coastal-health-2013-14','2014-03-31','''Woodward, Kip|Chair|19750|4949|24699
Gibson, Carol|Director|11750|449|12199
Heath, Sandra|Director|13750|436|14186
Hsieh, James|Director|12250|-|12250
MacDiarmid,Margaret|Director|5750|436|6186
Nocente Daniel|Director|15500|598|16098
Rehkatsch, Axel F|Director|13000|-|13000
Spitz, Grant|Director|11250|4794|16044
Withers, Victoria|Director|15250|34|15284''',['118250','11696','129946'],cols=cols,notes=['1. Appointed September2013','Nocente name is visibly printed without comma; no comma invented in literal source reading.'])
add('vancouver-coastal-health-2009-10','2010-03-31','''Thompson, David|Chair|-|1589.71|1589.71
Di Blasio, Alfredo|Director|11250.0|-|11250.00
Heath, Sandra|Director|16750.0|-|16750.00
Hsieh, James|Director|15500.00|376.25|15876.25
McLay, Catherine|Director|12750.00|72.00|12822.00
Rehkatsch, Axel F|Director|19750.00|-|19750.00
Spitz, Grant|Director|20000.0|5063.00|25063.00
Withers, Victoria|Director|4000.00|-|4000.00''',['100000.00','7100.96','107100.96'],cols=cols,page=4,notes=['1. Withers appointed November2009','Chair remuneration is source dash, expense1589.71 remains known separately.'])
add('vancouver-coastal-health-2008-09','2009-03-31','''Thompson, David|Chair|-|-|-
Di Blasio, Alfredo|Director|14000.00|-|14000.00
Heath, Sandra|Director|16250.00|-|16250.00
Hsieh, James|Director|10750.00|268.80|11018.80
McLay, Catherine|Director|12500.00|146.00|12646.00
Rehkatsch, Axel F|Director|15500.00|-|15500.00
Smith, Andrew|Director|4250.00|-|4250.00
Spitz, Grant|Director|16750.00|5695.85|22445.85
Yamamoto, Naomi|Director|15250.00|-|15250.00
Yung, Bennie|Director|2000.00|-|2000.00''',['107250.00','6110.65','113360.65'],cols=cols,page=2,notes=['1. Smith term ended April2008','2. Yung term ended March2008','Chair row has all three monetary source dashes; full named scope preserved separately, no invented zero.'])
