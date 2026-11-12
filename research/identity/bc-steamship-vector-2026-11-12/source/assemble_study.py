#!/usr/bin/env python3
"""Assemble the explicitly provisional token inscription study."""
from pathlib import Path
import xml.etree.ElementTree as ET
import rebuild_emblem as m

OUT=Path(__file__).resolve().parent.parent
root=ET.parse(OUT/'studies'/'token-inscription-provisional.svg').getroot()
ns='{http://www.w3.org/2000/svg}'
lettering=root.find(ns+'g')
art=[ET.tostring(lettering,encoding='unicode'),
     f'<g transform="translate(750 750) scale({500/145.5:.10f})">{m.body()}</g>',
     '<path id="token-outer-rule" fill="#000000" fill-rule="evenodd" d="M 750 62 A 688 688 0 1 1 750 1438 A 688 688 0 1 1 750 62 Z M 750 70 A 680 680 0 1 1 750 1430 A 680 680 0 1 1 750 70 Z"/>',
     '<path id="token-bottom-dot" fill="#000000" d="M 750 1341 A 13 13 0 1 1 750 1367 A 13 13 0 1 1 750 1341 Z"/>']
(OUT/'studies'/'bc-steamship-token-study-provisional.svg').write_text(m.document('\n'.join(art),
    viewbox='0 0 1500 1500',width='1500',height='1500',
    title='PROVISIONAL STUDY - British Columbia Steamship Company token layout',
    desc='Optional study only. Reconstructed emblem with an outlined Euler Fraktur approximation of the perimeter inscription. Ornamental capitals, numerals and some lowercase letters differ from the token. The original typeface is unconfirmed; this is not an exact token reproduction.'))
print('Assembled provisional token study.')
