from append_first import add
cols=['Remuneration','Expenses','Total']
add('vancouver-coastal-health-2019-20','2020-03-31','''Ballem,Penny J|Chair|43000|4605|47605
Au, Wendy|Director|17000|310|17310
Baydala, Allan|Director|24250|94|24344
Duvall, Bill|Director|12250||12250
Fregin, Cliff|Director|3625|32|3657
Harowitz, Howard|Director|25500|328|25828
Liang, Rowena|Director|2000||2000
McGregor, Margaret|Director|22000||22000
Nguyen, Vi|Director|13250|96|13346
Nocente, Daniel|Director|15125|264|15389
Slett,Marilyn|Director|12125||12125''',['190125','5729','195854'],cols=cols,notes=["1. C Fregin's term ended July3,2019", "2. R Liang's term ended April4,2019", "3. V. Nguyen's term ended January20,2020", "4. D. Nocente's term ended December19,2019",'Blank expense cells remain literal blanks.'])
add('vancouver-coastal-health-2018-19','2019-03-31','''Ballem,Penny J|Chair|-|194|194
Woodward, Kip|Chair|16750|2123|18873
Au, Wendy|Director|11750|199|11949
Baydala, Allan|Director|16500|27|16527
Duvall, Bill|Director|13125|105|13230
Fregin, Cliff|Director|9250|101|9351
Fung, Kenneth|Director|-|-|-
Harowitz, Howard|Director|16250|189|16439
Liang, Rowena|Director|12250|3163|15413
MacDiarmid, Margaret|Director|-|-|-
McGregor, Margaret|Director|12500|-|12500
Nguyen, Vi|Director|11000|-|11000
Nocente, Daniel|Director|15500|134|15634
Slett,Marilyn|Director|-|-|-
Yeung, Sze-Mei|Director|-|-|-''',['134875','6234','141110'],cols=cols,notes=['1. P Ballem was appointed December31,2018',"2. K Woodward's term ended December21,2018",'3. W. Au was appointed September22,2017. In FY18 retainer payment for September22 to December31,2017 returned as she was unable to attend any meetings in this time period.','4. B. Duvall was appointed December31,2017. Retainer for January31 to March31,2018 was paid in FY2018/19.',"5. K. Fung's term ended September22,2017", "6. M. MacDiarmid's term ended September22,2017",'7. M. McGregor was appointed September22,2017','8. V. Nguyen was appointed September22,2017','9. M Slett was appointed December31,2018',"10. S. Yeung's term ended December31,2017",'Source prints all five dash-only or remuneration-dash board members; preserve full table without inventing zeros.'])
add('vancouver-coastal-health-2017-18','2018-03-31','''Woodward, Kip|Chair|20750|6753|27503
Au, Wendy|Director|1875|47|1922
Baydala, Allan|Director|14726|16|14742
Duvall, Bill|Director|-|18|18
Fregin, Cliff|Director|9750|136|9886
Fung, Kenneth|Director|7754|-|7754
Harowitz, Howard|Director|16625|107|16732
Liang, Rowena|Director|12750|2454|15204
MacDiarmid, Margaret|Director|8750|-|8750
McGregor, Margaret|Director|5683|-|5683
Nguyen, Vi|Director|4433|-|4433
Nocente, Daniel|Director|16250|161|16411
Yeung, Sze-Mei|Director|8875|117|8992''',['128221','9809','138030'],cols=cols,notes=['1. W. Au was appointed September22,2017','2. B. Duvall was appointed December31,2017','3. K. Fung term ended September22,2017','4. M. MacDiarmid term ended September22,2017','5. M. McGregor was appointed September22,2017','6. V. Nguyen was appointed September22,2017','7. S. Yeung term ended December31,2017','Duvall remuneration is source dash, although expense18 is numeric.'])
