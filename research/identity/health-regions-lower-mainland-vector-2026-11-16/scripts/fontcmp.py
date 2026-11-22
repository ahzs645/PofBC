import sys,glob,os,numpy as np
from PIL import Image, ImageDraw, ImageFont
def crop_ink(m):
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]; return m[ys.min():ys.max()+1, xs.min():xs.max()+1]
def run(target_png, box, text, fontglob, out, thr=128):
    im=np.array(Image.open(target_png).convert('L'))
    x0,y0,x1,y1=box
    T=crop_ink(im[y0:y1,x0:x1]<thr)
    th,tw=T.shape
    res=[]
    for f in sorted(glob.glob(fontglob)):
        try:
            font=ImageFont.truetype(f,200)
        except Exception as e: continue
        img=Image.new('L',(len(text)*220,500),0)
        ImageDraw.Draw(img).text((50,100),text,font=font,fill=255)
        m=crop_ink(np.array(img)>128)
        R=np.array(Image.fromarray((m*255).astype('uint8')).resize((tw,th),Image.LANCZOS))>128
        iou=(R&T).sum()/(R|T).sum()
        aspect=(m.shape[1]/m.shape[0])/(tw/th)
        res.append((iou,os.path.basename(f),aspect,R))
    res.sort(key=lambda r:-r[0])
    rows=[Image.fromarray((~T*255).astype('uint8'))]
    for iou,n,asp,R in res[:12]:
        rows.append(Image.fromarray((~R*255).astype('uint8')))
        print(f'{iou:.3f} aspect{asp:.2f} {n}')
    sheet=Image.new('L',(tw,(th+10)*len(rows)),255)
    for i,r in enumerate(rows): sheet.paste(r,(0,i*(th+10)))
    sheet.save(out)
if __name__=='__main__':
    run(sys.argv[1],tuple(map(int,sys.argv[2].split(','))),sys.argv[3],sys.argv[4],sys.argv[5])
