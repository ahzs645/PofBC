"""Export native SVG masters into vector PDF/EPS and transparent PNG previews."""
from pathlib import Path
import concurrent.futures, subprocess, json, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
for d in ['pdf','eps','png']:(ROOT/d).mkdir(exist_ok=True)
def one(path):
    root=ET.parse(path).getroot();vb=[float(v) for v in root.attrib['viewBox'].split()]
    width=min(2400,round(3200*vb[2]/vb[3]))
    for ext in ['pdf','eps','png']:
        out=ROOT/ext/(path.stem+'.'+ext)
        args=['inkscape',str(path),'--export-area-page','--export-type='+ext,'--export-filename='+str(out)]
        if ext=='png':args+=['--export-width='+str(width)]
        p=subprocess.run(args,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(path.name+' '+ext+' '+p.stderr)
    return path.stem
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for name in pool.map(one,sorted((ROOT/'svg').glob('*.svg'))):print(name)
