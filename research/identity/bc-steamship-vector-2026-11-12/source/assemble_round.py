#!/usr/bin/env python3
"""Assemble the corrected circular mark using two independent vector sources."""
from pathlib import Path
import xml.etree.ElementTree as ET
import rebuild_round_geometry as geometry
HERE=Path(__file__).resolve().parent;OUT=HERE.parent
NS='{http://www.w3.org/2000/svg}';ET.register_namespace('','http://www.w3.org/2000/svg')
def make(color):
    lettering=ET.parse(HERE/'round-inscription.svg').getroot().find(NS+'g')
    lettering.set('fill',color)
    return '\n'.join(['<?xml version="1.0" encoding="UTF-8"?>',
       '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500" role="img" aria-labelledby="title desc">',
       '<title id="title">British Columbia Steamship Company (1975) Ltd. - finalized round logo</title>',
       '<desc id="desc">Finalized vector reconstruction following the supplied circular reference. Corrected curved C and S terminals, lowercase curls, date numerals, optical letter size and spacing, concentric ring proportions, central emblem and separator dot. All lettering is outlined. No embedded raster or font dependency. Correct wording ends Ltd.</desc>',
       geometry.body(color),ET.tostring(lettering,encoding='unicode'),'</svg>',''])
for filename,color in [('bc-steamship-round-logo.svg','#000000'),('bc-steamship-round-logo-white.svg','#ffffff')]:
    (OUT/filename).write_text(make(color))
print('Finalized black and white round SVGs assembled.')
