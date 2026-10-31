import fitz, subprocess, concurrent.futures
from pathlib import Path
base=Path(__file__).parent/'raw'
jobs=[('R4B-039',i) for i in list(range(1,20))+list(range(149,155))]+[('R4B-038',i) for i in range(1,16)]
def f(t):
    s,i=t; q=base/f'{s}-ocr-p{i:03}.txt'
    if q.exists():return
    p=fitz.open(str(base/f'{s}.pdf')); im=Path(f'/tmp/{s}-{i}.png'); p[i-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(im)
    r=subprocess.run(['tesseract',str(im),'stdout'],capture_output=True,text=True);q.write_text(r.stdout);im.unlink()
    if any(w in r.stdout.lower() for w in ['community safety', 'organization', 'organizational', 'contents']):print(s,i,r.stdout[:1800],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(f,jobs))
