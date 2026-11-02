from append_first import add
cols=['Remuneration','Expenses','Total']
add('vancouver-coastal-health-2024-25','2025-03-31','''Ballem, Penny|Chair|69575|2732|72307
Baker, Deborah|Director|22300|157|22457
Duvall, William|Director|30430|275|30705
Greenberg, Kathy|Director|33310|1005|34315
McGregor, Margaret|Director|28420|2950|31370
McKenzie, Davis Paul|Director|20140|898|21038
McLaughlin, John Hedley|Director|42090|19|42109
Naizghi, Eyob|Director|29860|156|30016
Shroff, Farah|Director|24100|1838|25938
Slett, Marilyn|Director|16540||16540''',['316765','10030','326795'],cols=cols,notes=['Blank expense cell for Slett is literal blank; not inferred zero. All subordinate members appear under Directors heading.'])
add('vancouver-coastal-health-2023-24','2024-03-31','''Ballem, Penny|Chair|84825|3209|88034
Au, Wendy|Director|27160|966|28126
Baker, Deborah|Director|28675|471|29146
Baydala, Allan|Director|6625||6625
Duvall, William|Director|33405|89|33494
Greenberg, Kathy|Director|37975||37975
McGregor, Margaret|Director|33885|2222|36107
McKenzie, Davis Paul|Director|25711|2946|28657
McLaughlin, John Hedley|Director|41530|1618|43148
Naizghi, Eyob|Director|31725|1262|32987
Slett,Marilyn|Director|22855||22855''',['374371','12781','387152'],cols=cols,notes=['Blank expense cells remain literal blanks.'])
add('vancouver-coastal-health-2021-22','2022-03-31','''Ballem, Penny|Chair|43750|2702|46452
Au, Wendy|Director|13125|51|13176
Baker, Deborah|Director|16000||16000
Baydala, Allan|Director|16125||16125
Duvall, William|Director|19125||19125
Greenberg, Kathy|Director|16750||16750
McGregor, Margaret|Director|17625||17625
Naizghi, Eyob|Director|16250||16250
Slett,Marilyn|Director|8125||8125''',['166875','2753','169628'],cols=cols,notes=['Blank expense cells remain literal blanks.'])
