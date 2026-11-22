import sys,pymupdf
# crop.py pdf page x0 y0 x1 y1 out.png [dpi]
d=pymupdf.open(sys.argv[1]);p=d[int(sys.argv[2])-1]
r=pymupdf.Rect(*map(float,sys.argv[3:7]))
p.get_pixmap(dpi=int(sys.argv[8]) if len(sys.argv)>8 else 300,clip=r).save(sys.argv[7])
