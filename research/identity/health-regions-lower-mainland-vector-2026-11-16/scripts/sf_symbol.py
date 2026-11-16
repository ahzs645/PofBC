"""Hand-built geometry for the Simon Fraser Health Region 'S' symbol, in pixels of the January 2001
Continuum 1-bit bitmap (1943 x 990). Straight edges are placed at the measured block edges; each of the four
curved edges is a cubic Bezier chain least-squares fitted (max error 1 px) to the edge positions sampled
row by row or column by column from the bitmap."""
import numpy as np
from PIL import Image
from scipy.ndimage import label
from contourfit import fit_cubic, unit
SRC='/home/user/PofBC/public/identity-collected/simon-fraser-health-region/simon-fraser-health-region-continuum-2001-monochrome.png'
def f(v): return f'{v:.2f}'.rstrip('0').rstrip('.')
def smooth(P,k=9):
    w=np.ones(k)/k; Q=P.copy()
    for j in (0,1): Q[:,j]=np.convolve(np.pad(P[:,j],k//2,mode='edge'),w,'valid')
    Q[0]=P[0]; Q[-1]=P[-1]; return Q
def chain(P,maxerr=1.25):
    k=min(6,len(P)-1)
    bs=fit_cubic(P,unit(P[k]-P[0]),unit(P[-1-k]-P[-1]),maxerr)
    return ' '.join('C '+' '.join(f'{f(p[0])} {f(p[1])}' for p in b[1:]) for b in bs)
K=25
def build():
    a=np.array(Image.open(SRC).convert('L'))<128
    lab,_=label(a)
    top=lab==lab[50,500]; ml=lab==lab[500,10]; mr=lab==lab[500,980]; bot=lab==lab[950,500]
    # measured straight edges (pixel-edge coordinates)
    L,R=245.0,747.0            # top and bottom blocks
    MT,MB,MR=243.0,746.0,991.0 # middle square
    BT=990.0
    out=[]
    # top block: lower edge, column by column (bottom-most ink pixel + 1)
    xs=np.arange(int(L)+1,int(R)-1); ys=np.array([np.where(top[:,x])[0].max()+1 for x in xs],float)
    P=smooth(np.c_[xs+0.5,ys],K); P[0,0]=L; P[-1,0]=R  # left -> right
    out.append(f'M {f(L)} 0 L {f(R)} 0 L {f(R)} {f(P[-1,1])} '+chain(P[::-1])+' Z')
    # middle-left: right edge, row by row (right-most ink pixel + 1)
    ys=np.arange(int(MT)+2,int(MB)-1); xs=np.array([np.where(ml[y])[0].max()+1 for y in ys],float)
    P=smooth(np.c_[xs,ys+0.5],K); P[0,1]=MT; P[-1,1]=MB
    out.append(f'M 0 {f(MT)} L {f(P[0,0])} {f(MT)} '+chain(P)+f' L 0 {f(MB)} Z')
    # middle-right: left edge, row by row (left-most ink pixel)
    ys=np.arange(int(MT)+2,int(MB)-1); xs=np.array([np.where(mr[y])[0].min() for y in ys],float)
    P=smooth(np.c_[xs,ys+0.5],K); P[0,1]=MT; P[-1,1]=MB
    out.append(f'M {f(MR)} {f(MT)} L {f(MR)} {f(MB)} L {f(P[-1,0])} {f(MB)} '+chain(P[::-1])+' Z')
    # bottom block: upper edge, column by column (top-most ink pixel)
    xs=np.arange(int(L)+1,int(R)-1); ys=np.array([np.where(bot[:,x])[0].min() for x in xs],float)
    P=smooth(np.c_[xs+0.5,ys],K); P[0,0]=L; P[-1,0]=R
    out.append(f'M {f(L)} {f(BT)} L {f(R)} {f(BT)} L {f(R)} {f(P[-1,1])} '+chain(P[::-1])+' Z')
    return out
if __name__=='__main__':
    for d in build(): print(d[:300]); print()
