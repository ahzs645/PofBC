"""Small native Potrace binding and SVG writer; no bitmap data is put in the SVG."""
from __future__ import annotations
import ctypes as C
import ctypes.util
import numpy as np

class Progress(C.Structure):
    _fields_=[('callback',C.c_void_p),('data',C.c_void_p),('min',C.c_double),('max',C.c_double),('epsilon',C.c_double)]
class Params(C.Structure):
    _fields_=[('turdsize',C.c_int),('turnpolicy',C.c_int),('alphamax',C.c_double),('opticurve',C.c_int),('opttolerance',C.c_double),('progress',Progress)]
class Bitmap(C.Structure):
    _fields_=[('w',C.c_int),('h',C.c_int),('dy',C.c_int),('map',C.POINTER(C.c_ulong))]
class Point(C.Structure):
    _fields_=[('x',C.c_double),('y',C.c_double)]
class Curve(C.Structure):
    _fields_=[('n',C.c_int),('tag',C.POINTER(C.c_int)),('c',C.POINTER(Point*3))]
class Path(C.Structure):
    pass
Path._fields_=[('area',C.c_int),('sign',C.c_int),('curve',Curve),('next',C.POINTER(Path)),('childlist',C.POINTER(Path)),('sibling',C.POINTER(Path)),('priv',C.c_void_p)]
class State(C.Structure):
    _fields_=[('status',C.c_int),('plist',C.POINTER(Path)),('priv',C.c_void_p)]

lib=C.CDLL(ctypes.util.find_library('potrace'))
lib.potrace_param_default.restype=C.POINTER(Params)
lib.potrace_param_free.argtypes=[C.POINTER(Params)]
lib.potrace_trace.argtypes=[C.POINTER(Params),C.POINTER(Bitmap)]
lib.potrace_trace.restype=C.POINTER(State)
lib.potrace_state_free.argtypes=[C.POINTER(State)]
lib.potrace_version.restype=C.c_char_p

def trace(mask, scale=1, alpha=1.0, tolerance=.2, speck=0):
    """Return positive closed outlines, each including its negative child holes.

    Input rows are deliberately top-to-bottom, keeping native image coordinates.
    The nonzero fill rule is used, so curve winding rather than draw order cuts holes.
    """
    h,w=mask.shape
    word_bits=C.sizeof(C.c_ulong)*8
    dy=(w+word_bits-1)//word_bits
    pad=np.zeros((h,dy*word_bits),dtype=np.uint8)
    pad[:,:w]=mask
    packed=np.packbits(pad,axis=1,bitorder='big')
    words=packed.view('>u'+str(C.sizeof(C.c_ulong))).astype('uint'+str(word_bits))
    bm=Bitmap(w,h,dy,words.ctypes.data_as(C.POINTER(C.c_ulong)))
    params=lib.potrace_param_default()
    params.contents.turdsize=int(speck*scale*scale)
    params.contents.alphamax=alpha
    params.contents.opttolerance=tolerance*scale
    state=lib.potrace_trace(params,C.byref(bm))
    if not state or state.contents.status:
        raise RuntimeError('Vector fitting failed')
    def outline(p):
        cv=p.curve
        last=cv.c[cv.n-1][2]
        points=[]
        def xy(pt):
            x,y=pt.x/scale,pt.y/scale
            points.append((x,y))
            return f'{x:.3f},{y:.3f}'
        commands=['M'+xy(last)]
        for i in range(cv.n):
            if cv.tag[i]==2:
                commands.extend(['L'+xy(cv.c[i][1]),'L'+xy(cv.c[i][2])])
            else:
                commands.append('C'+xy(cv.c[i][0])+' '+xy(cv.c[i][1])+' '+xy(cv.c[i][2]))
        commands.append('Z')
        xs,ys=zip(*points)
        return ''.join(commands),(min(xs),min(ys),max(xs),max(ys)),cv.n
    outputs=[]
    ptr=state.contents.plist
    while ptr:
        p=ptr.contents
        if p.sign==ord('+'):
            d,bbox,n=outline(p)
            holes=[]
            child=p.childlist
            while child:
                q=child.contents
                hd,_,hn=outline(q)
                holes.append(hd)
                n+=hn
                child=q.sibling
            outputs.append({'d':d+''.join(holes),'bbox':bbox,'area':p.area/(scale*scale),'segments':n,'holes':len(holes)})
        ptr=p.next
    lib.potrace_state_free(state)
    lib.potrace_param_free(params)
    return outputs

if __name__=='__main__':
    test=np.zeros((10,20),dtype=bool)
    test[1:4,2:6]=1
    print(lib.potrace_version().decode(),trace(test))
