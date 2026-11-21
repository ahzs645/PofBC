#!/usr/bin/env python3
"""Assemble independently drawn edge components without changing their geometry."""
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess, sys, json

HERE=Path(__file__).resolve().parent
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
files=['upper_reserves.svg','upright_reserve.svg','child_reserves.svg']
fragments=[]
for name in files:
    root=ET.parse(HERE/name).getroot()
    assert root.get('viewBox')=='0 0 1000 1400',(name,root.get('viewBox'))
    for e in root:
        if e.tag.rsplit('}',1)[-1] not in ['title','desc','metadata']:
            fragments.append(ET.tostring(e,encoding='unicode'))
inner='\n'.join(fragments).replace('#e6f1ed','#e7f3f2')
code='''#!/usr/bin/env python3
"""Revision 3 white reserve. Geometry was manually specified from visual landmarks.

The component paths retain deliberate source-specific lobes and recesses.
The photograph and diagnostic mask are not inputs to this construction script.
"""
from pathlib import Path
PAPER='#e7f3f2'
GEOMETRY=GEOMETRY_LITERAL

def reserve_group(paper=PAPER):
    return '<g id="white-reserves-v3" fill="'+paper+'">'+GEOMETRY.replace(PAPER,paper)+'</g>'

def svg(paper=PAPER):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1400" viewBox="0 0 1000 1400"><title>White illustration reserve, revision 3</title><desc>Manually constructed curved edges and brush details. Diagnostic photo masks are evaluated separately and do not generate the output paths.</desc>'+reserve_group(paper)+'</svg>'

if __name__=='__main__':
    Path(__file__).with_suffix('.svg').write_text(svg())
'''.replace('GEOMETRY_LITERAL',repr(inner))
(HERE/'reserves_v3.py').write_text(code)
subprocess.run([sys.executable,str(HERE/'reserves_v3.py')],check=True)
root=ET.parse(HERE/'reserves_v3.svg').getroot()
counts={}
for e in root.iter():
    k=e.tag.rsplit('}',1)[-1];counts[k]=counts.get(k,0)+1
assert all(counts.get(k,0)==0 for k in ['image','text','filter'])
print(json.dumps({'components':files,'svg_counts':counts}))
