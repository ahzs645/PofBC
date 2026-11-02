import fitz,json
from PIL import Image
from pathlib import Path
sp=Path('/workspace/PofBC/research/salaries/queue-completion-2026-11-01/reviews/root-phsa-history-2019-20-batch-011-fiftyone-name-source-only-peer.json');s=json.loads(sp.read_text());doc=fitz.open('/tmp/queue-completion-phsa/originals/phsa-2019-20.pdf');bad=[]
for r in s['rows']:
 rect=fitz.Rect([x*72/300 for x in r['sourceNative300Field']['originalPdf300DpiPixelBox']]);pix=doc[r['physicalPage']-1].get_pixmap(dpi=1200,clip=rect,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).crop(r['whiteOnlyHorizontalCropBox']);got=Image.open(r['actualOriginal1200']['path']).convert('RGB');assert im.size==got.size and im.tobytes()==got.tobytes()
 context=fitz.Rect(rect);context.y0-=24;context.y1+=24;pix=doc[r['physicalPage']-1].get_pixmap(dpi=300,clip=context,alpha=False);got=Image.open(r['actualOriginal300Context']['path']).convert('RGB')
 if got.size!=(pix.width,pix.height) or got.tobytes()!=pix.samples:bad.append(r['sequence'])
print({'exact1200Names':51,'contextMismatches':bad})
