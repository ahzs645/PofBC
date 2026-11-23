"""Optional shared-branch update after dark-master edits.

Requires NumPy and svgpathtools. No bitmap is read. Run assemble_logo.py afterwards.
The explicit compiled pale paths remain sufficient for the ordinary portable build.
"""
from pathlib import Path
import json
import numpy as np
from svgpathtools import parse_path
from svgpathtools.path import transform
HERE=Path(__file__).resolve().parent
p=HERE/'tree-geometry.json'
m=json.loads(p.read_text());fit=json.loads((HERE/'alignment-fit.json').read_text())
def matrix(name):
    dx,dy,sx,sy=fit[name]['matrix_parameters_dx_dy_sx_sy']
    return np.array([[sx,0,dx],[0,sy,dy],[0,0,1.]])
source=np.array(m['pale_construction']['source_affine'])
A=np.linalg.inv(matrix('pale'))@source@matrix('dark')
excluded=set(m['pale_construction']['excluded_dark_voids'])
for dst,src in [('pale','dark'),('pale_voids','dark_voids')]:
    kept={name:d for name,d in m[dst].items() if not name.startswith('shared_')}
    shared={'shared_'+name:transform(parse_path(d),A).d() for name,d in m[src].items()
            if src!='dark_voids' or name not in excluded}
    m[dst]={**shared,**kept}
p.write_text(json.dumps(m,indent=2)+'\n')
print('Updated shared pale branches; independent pale completion retained.')
