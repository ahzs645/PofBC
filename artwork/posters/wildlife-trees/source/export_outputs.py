"""Export the outlined SVG as a true vector PDF and render review previews."""
from pathlib import Path
import subprocess
import fitz
from reconstruct_illustrations import ROOT,TMP,render

def run():
    svg=ROOT/'Wildlife-Trees-outlined.svg';pdf=ROOT/'Wildlife-Trees-vector.pdf';fresh=TMP/'poster-vector-export.pdf'
    if fresh.exists():fresh.unlink()
    subprocess.run(['inkscape',str(svg),'--export-type=pdf','--export-filename='+str(fresh)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    d=fitz.open(fresh);assert len(d)==1;assert not d[0].get_images(full=True),'Unexpected bitmap in production PDF'
    expected=(823.68,2468.7);actual=(d[0].rect.width,d[0].rect.height)
    assert max(abs(a-b) for a,b in zip(actual,expected))<.05,(actual,expected)
    d.close();fresh.replace(pdf)
    render(svg,ROOT/'Wildlife-Trees-preview.png',1600)
    render(svg,TMP/'poster-proof-render.png',2000)
    print('Vector PDF verified:',actual,'pt; embedded images: 0.',flush=True)

if __name__=='__main__':run()
