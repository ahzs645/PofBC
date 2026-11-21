#!/usr/bin/env python3
"""A restrained visual reconstruction of the faint photographed signature.
Reading and attribution remain unconfirmed. This is manually drawn lettering,
not a tracing of the autograph or a claim of authentication.
"""
from pathlib import Path

OUT=Path(__file__).resolve().parent
COLOUR='#ef6c32'
STROKES=[
 ('initial-1','M896 1378.5 C895.1 1381.5 893.5 1385.8 891.5 1387.6 Q890.8 1388 890.3 1387.6'),
 ('point-1','M899.1 1387.6 L899.5 1387.1'),
 ('initial-2','M906.2 1378.6 L903.7 1386 Q902.6 1388.2 900.8 1387.5'),
 ('point-2','M908.6 1387.3 L909.1 1387.3'),
 ('A','M911.6 1387.4 L917.5 1378.3 L921.1 1387.3 M914.1 1384.5 L919.7 1384.1'),
 ('N','M924 1387.5 L926.1 1380.8 L932.1 1387.4 L935 1380.3'),
 ('D','M936.5 1387.5 L938.2 1380.3 C948.2 1379.8 949.5 1388 936.5 1387.5'),
 ('R','M949.5 1387.6 L952 1380.6 C961.2 1380 961.3 1384.1 950.9 1384.4 M954.4 1384.3 L959.2 1388.1'),
 ('E','M964 1381 L974.1 1381 M963.9 1381.1 L962.3 1387.8 L973.5 1387.8 M963 1384.6 L972.3 1384.6'),
]

def signature_group():
 return '<g id="signature-v2-unconfirmed-reading" aria-label="Signature appears to read J.J. ANDRE; reading and attribution unconfirmed" fill="none" stroke="'+COLOUR+'" stroke-width=".9" stroke-linecap="round" stroke-linejoin="round" opacity=".68">'+''.join('<path id="signature-v2-'+label+'" d="'+d+'"/>' for label,d in STROKES)+'</g>'

if __name__=='__main__':
 body=signature_group()
 (OUT/'signature_v2.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1400" viewBox="0 0 1000 1400"><title>Photographed signature reading - visual reconstruction</title><desc>Manually composed faint lettering. The apparent J.J. ANDRE reading and artist attribution are unconfirmed.</desc>'+body+'</svg>')
 (OUT/'signature_v2_detail.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="252" viewBox="885 1372 100 23.333"><rect x="885" y="1372" width="100" height="23.333" fill="#da2809"/>'+body+'</svg>')
