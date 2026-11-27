"""Small source-guided vector helpers used for the coat-of-arms reconstruction."""
from pathlib import Path
import ctypes as C
import ctypes.util
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'upload' / 'Ornate historical coat of arms.png'
W,H = 1261,1247
PALETTE = dict(ink='#171513', ivory='#fff5df', gold='#ffc928', red='#ee3429', blue='#168fc1', ribbon='#cd365a', warm='#e8be8d')

class Point(C.Structure):
    _fields_=[('x',C.c_double),('y',C.c_double)]
class Curve(C.Structure):
    _fields_=[('n',C.c_int),('tag',C.POINTER(C.c_int)),('c',C.POINTER(Point*3))]
class PathRec(C.Structure): pass
PathRec._fields_=[('area',C.c_int),('sign',C.c_int),('curve',Curve),('next',C.POINTER(PathRec)),('childlist',C.POINTER(PathRec)),('sibling',C.POINTER(PathRec)),('priv',C.c_void_p)]
class Bitmap(C.Structure):
    _fields_=[('w',C.c_int),('h',C.c_int),('dy',C.c_int),('map',C.POINTER(C.c_ulong))]
class Progress(C.Structure):
    _fields_=[('callback',C.c_void_p),('data',C.c_void_p),('min',C.c_double),('max',C.c_double),('epsilon',C.c_double)]
class Params(C.Structure):
    _fields_=[('turdsize',C.c_int),('turnpolicy',C.c_int),('alphamax',C.c_double),('opticurve',C.c_int),('opttolerance',C.c_double),('progress',Progress)]
class State(C.Structure):
    _fields_=[('status',C.c_int),('plist',C.POINTER(PathRec)),('priv',C.c_void_p)]

lib=C.CDLL(ctypes.util.find_library('potrace'))
lib.potrace_param_default.restype=C.POINTER(Params)
lib.potrace_param_free.argtypes=[C.POINTER(Params)]
lib.potrace_trace.argtypes=[C.POINTER(Params),C.POINTER(Bitmap)]
lib.potrace_trace.restype=C.POINTER(State)
lib.potrace_state_free.argtypes=[C.POINTER(State)]

def source_array():
    return np.asarray(Image.open(SOURCE).convert('RGBA'))

def polygon_mask(points,shape=(H,W)):
    im=Image.new('L',(shape[1],shape[0]),0)
    ImageDraw.Draw(im).polygon(points,fill=255)
    return np.asarray(im)>0

def remove_small(mask, min_size=8):
    labels,n=ndi.label(mask)
    sizes=np.bincount(labels.ravel())
    keep=sizes>=min_size
    keep[0]=False
    return keep[labels]

def clean_mask(mask,sigma=0.6,min_size=8,hole_size=0):
    mask=np.asarray(mask,dtype=bool)
    if sigma:
        mask=ndi.gaussian_filter(mask.astype(float),sigma)>=0.5
    if min_size:
        mask=remove_small(mask,min_size)
    if hole_size:
        holes=ndi.binary_fill_holes(mask)&~mask
        large_holes=remove_small(holes,hole_size)
        mask=mask|(holes&~large_holes)
    return mask

def trace_mask(mask,offset=(0,0),turdsize=8,alphamax=1.0,opttolerance=0.35):
    """Return a compound SVG path from a 2D bool mask, same top-down coordinates."""
    mask=np.asarray(mask,dtype=bool)
    h,w=mask.shape
    bits=C.sizeof(C.c_ulong)*8
    dy=(w+bits-1)//bits
    padded=np.pad(mask,((0,0),(0,dy*bits-w)))
    packed=np.packbits(padded,axis=1,bitorder='big')
    words=np.frombuffer(packed.tobytes(),dtype='>u8').astype(np.uint64)
    bmp=Bitmap(w,h,dy,words.ctypes.data_as(C.POINTER(C.c_ulong)))
    param=lib.potrace_param_default()
    param.contents.turdsize=turdsize
    param.contents.alphamax=alphamax
    param.contents.opticurve=1
    param.contents.opttolerance=opttolerance
    state=lib.potrace_trace(param,C.byref(bmp))
    if not state or state.contents.status!=0:
        raise RuntimeError('Vector curve fit failed')
    dx,dy=offset
    def pt(p):return f'{p.x+dx:.2f},{p.y+dy:.2f}'
    pieces=[]
    node=state.contents.plist
    while node:
        path=node.contents
        curve=path.curve
        if curve.n:
            d=['M'+pt(curve.c[curve.n-1][2])]
            for i in range(curve.n):
                c=curve.c[i]
                if curve.tag[i]==2:
                    d.append('L'+pt(c[1])+' '+pt(c[2]))
                else:
                    d.append('C'+pt(c[0])+' '+pt(c[1])+' '+pt(c[2]))
            d.append('Z')
            pieces.append(' '.join(d))
        node=path.next
    lib.potrace_state_free(state)
    lib.potrace_param_free(param)
    return ' '.join(pieces)

def mask_path(mask,fill,**kwargs):
    return '<path fill="'+fill+'" fill-rule="evenodd" d="'+trace_mask(mask,**kwargs)+'"/>'

def svg_document(body,width=W,height=H,title='Reconstructed coat of arms component'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><title>{title}</title>{body}</svg>'

def save_svg(path,body):
    Path(path).write_text(svg_document(body))
