import fitz, subprocess, concurrent.futures
from pathlib import Path
base=Path(__file__).parent/'raw'
def f(i):
    p=fitz.open(str(base/'R4B-006.pdf')); q=base/f'R4B-006-ocr-p{i:03}.txt'
    if q.exists():return
    im=Path(f'/tmp/infra-{i}.png'); p[i-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(im)
    r=subprocess.run(['tesseract',str(im),'stdout'],capture_output=True,text=True);q.write_text(r.stdout);im.unlink()
    if any(w in r.stdout.lower() for w in ['division','organizational chart','amalgamat','policy and partnerships','community capital development']):print(i,r.stdout[:650],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(f,list(range(8,26))+list(range(119,143))))
