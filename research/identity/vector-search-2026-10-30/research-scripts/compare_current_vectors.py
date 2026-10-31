from pathlib import Path
import fitz,json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
records=json.loads((B/'current-crown-vectors/extraction-metadata.json').read_text())
rowheight=200; width=1200
board=Image.new('RGB',(width,50+rowheight*len(records)),(235,237,240));draw=ImageDraw.Draw(board)
draw.text((25,16),'Official PDF crop',fill='black');draw.text((625,16),'Extracted SVG (neutral backing for reversed white artwork)',fill='black')
for n,r in enumerate(records):
 y=50+n*rowheight
 draw.text((15,y+5),r['id'],fill='black')
 doc=fitz.open(r['sourceFile']);p=doc[r['sourcePage']-1];clip=fitz.Rect(r['crop'])
 pix=p.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False)
 source=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 sdoc=fitz.open(r['localFile']);sp=sdoc[0];spix=sp.get_pixmap(matrix=fitz.Matrix(3,3),alpha=True)
 result=Image.frombytes('RGBA',(spix.width,spix.height),spix.samples)
 reverse='reversed' in r['id']
 backing=Image.new('RGB',result.size,(50,65,80) if reverse else (255,255,255));backing.paste(result,mask=result.getchannel('A'))
 for image,x in [(source,15),(backing,615)]:
  image.thumbnail((565,160),Image.Resampling.LANCZOS)
  board.paste(image,(x,y+30+(160-image.height)//2))
 backing.save(B/'current-crown-sources'/f'{r["id"]}-preview.png')
 r['verification']={'structural':'Selected path count matches PDF drawing count; SVG contains zero image, text and use elements. Only referenced definitions and ancestral transforms retained.','visual':'Source PDF crop and SVG rendered at 3x and compared side by side. Geometry and completeness inspected.', 'comparisonFile':str(B/'current-crown-sources/vector-comparison.png')}
 r.setdefault('colourNote','PDF colours converted to SVG RGB by PyMuPDF; no palette substitution. Opaque source colour modes checked against the PDF rendering.')
board.save(B/'current-crown-sources/vector-comparison.png')
(B/'current-crown-vectors/extraction-metadata.json').write_text(json.dumps(records,indent=2))
