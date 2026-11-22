"""Automatic outline tracing (potracer, a pure-Python port of potrace) used ONLY for the
complex drawn parts of the historic marks (interlaced monogram letters, script letters,
caribou heads). Geometric parts (diamonds, rings, ovals) and type are not traced.

The greyscale source crop is upsampled (bicubic) before thresholding so the trace follows
the printed edge rather than the 300-dpi pixel staircase; output coordinates are divided
back to source pixels.
"""
import numpy as np, cv2
import potrace


def upsampled_mask(gray, region_mask=None, up=4, thr=128, blur=0.0):
    g = cv2.resize(gray.astype(np.float32), None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC)
    if blur:
        g = cv2.GaussianBlur(g, (0, 0), blur * up)
    m = g < thr
    if region_mask is not None:
        rm = cv2.resize(region_mask.astype(np.uint8), None, fx=up, fy=up, interpolation=cv2.INTER_NEAREST).astype(bool)
        m &= rm
    return m


def trace_to_path(mask, up=4, turdsize=40, alphamax=1.0, opttolerance=0.2, offset=(0.0, 0.0), prec=2):
    bm = potrace.Bitmap(~mask.astype(bool))  # potracer inverts: True = background
    plist = bm.trace(turdsize=turdsize, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                     alphamax=alphamax, opticurve=True, opttolerance=opttolerance)
    ox, oy = offset
    f = lambda p: '%s %s' % (('%.*f' % (prec, p.x / up + ox)).rstrip('0').rstrip('.'),
                             ('%.*f' % (prec, p.y / up + oy)).rstrip('0').rstrip('.'))
    out = []
    for curve in plist:
        out.append('M' + f(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner:
                out.append('L' + f(seg.c) + 'L' + f(seg.end_point))
            else:
                out.append('C' + f(seg.c1) + ' ' + f(seg.c2) + ' ' + f(seg.end_point))
        out.append('Z')
    return ''.join(out), len(plist)
