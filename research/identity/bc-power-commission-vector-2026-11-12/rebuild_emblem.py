#!/usr/bin/env python3
"""Rebuild the supplied emblem from deliberately authored vector geometry.

This is a construction file, not an image-tracing script. It never reads the
reference pixels. Dimensions were chosen from visual study of the supplied
1448 x 1086 image and checked separately against a rendered comparison.
"""

from pathlib import Path
from xml.sax.saxutils import escape
from math import hypot

DEST = Path(__file__).resolve().parent
INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"
COLORS = {
    "yellow": "#FFD800",
    "red": "#E60010",
    "navy": "#011842",
    "white": "#FFFFFF",
    "black": "#000000",
}


def polygon(points):
    return "M" + " L".join(f"{x:g},{y:g}" for x, y in points) + " Z"


def angular_inner_joins(points, length=14.0):
    """Short mitered corner segments retain angular inward notches.

    The main outline keeps rounded exterior tips. A separate sparse path
    supplies the inward miter joins consistently in SVG and PDF renderers.
    """
    corners = []
    for i, (x, y) in enumerate(points):
        px, py = points[i-1]
        nx, ny = points[(i+1) % len(points)]
        cross = (x-px)*(ny-y) - (y-py)*(nx-x)
        if cross < 0:
            before = hypot(px-x, py-y)
            after = hypot(nx-x, ny-y)
            start = (x + (px-x)*length/before, y + (py-y)*length/before)
            end = (x + (nx-x)*length/after, y + (ny-y)*length/after)
            corners.append((start, (x, y), end))
    def xy(p):
        return f"{p[0]:.3f},{p[1]:.3f}"
    return " ".join("M" + xy(start) + " L" + xy(tip) + " L" + xy(end)
                    for start, tip, end in corners)


def path(id_, d, **attrs):
    attrs = {"id": id_, "d": d, **attrs}
    return "    <path " + " ".join(f'{k}="{escape(str(v))}"' for k, v in attrs.items()) + "/>"


def layer(id_, label, content, **attrs):
    extra = " ".join(f'{k}="{escape(str(v))}"' for k, v in attrs.items())
    return (f'  <g id="{id_}" inkscape:groupmode="layer" inkscape:label="{label}" {extra}>\n'
            + "\n".join(content) + "\n  </g>")


# A single carefully placed polygon creates the rays. Slight left/right
# differences in the supplied mark are retained; no noisy pixel contours.
sun = [
    (724, 36), (781.2, 331.7), (831, 261), (835.7, 362.9),
    (881, 325), (884.5, 386.2), (1067, 276), (967.6, 453.2),
    (1067, 429), (1017.6, 495.8), (1265, 430), (1095.1, 573.3),
    (1190, 574), (1129.3, 618.7), (1419, 593), (1242, 684),
    (202, 684), (28, 593), (305.8, 615), (253, 574),
    (345.5, 571.3), (182, 430), (428.4, 495.6), (382, 429),
    (477.4, 450.4), (382, 276), (560.9, 387.2), (568, 326),
    (613, 362.6), (619, 260), (663.4, 326.6),
]

# Two cubic segments reproduce the white arch. Its original left and right
# curvature differs subtly; its crest is not forced onto the frame's midpoint.
arch = "M395 684 C407 529 563 389 724 389 C894 389 1033 545 1041 684"
plaque = arch + " H1337 V1027 H103 V684 Z"

bc_b = (
    "M541.5 484 L670 438.5 L703.5 464 V528.5 L683 555.5 "
    "L704.5 575 V648 L675.5 678 H541.5 Z "
    "M592.5 506 L649.5 487 V537.5 L592.5 549 Z "
    "M592.5 592 L649.5 582 V635.5 H592.5 Z"
)
bc_c = (
    "M745 469 L780 440 L875.5 472 L908 505 V555 L853.5 537 "
    "V504 L801.5 490.5 V636 H853.5 V608.5 H908 V652.5 "
    "L885 678 H772.5 L745 649 Z"
)

power = [
    ("power-P", "M392.5 705.5 H482 L503 724 V777 L483 797 H434 V844 H392.5 Z M434 733.5 H460 V769 H434 Z"),
    ("power-O", "M539 705.5 H608 L628 724 V825 L609 844 H538 L519.5 825 V724 Z M562 733.5 H585 V815 H562 Z"),
    ("power-W", "M637 705.5 H677 L697 774 L715.5 705.5 H743 L761 774 L779 705.5 H819 L783 844 H744.5 L729 794 L714 844 H675 Z"),
    ("power-E", "M832 705.5 H929 V734 H872.5 V755 H918 V784 H872.5 V815 H931 V844 H832 Z"),
    ("power-R", "M944.5 705.5 H1030 L1051 724 V774 L1026 794 L1063 844 H1013 L985 795 V844 H944.5 Z M985 734 H1009 V765.5 H985 Z"),
]

commission = [
    ("commission-C", "M175 860.5 H252 L269 878 V906 H225.5 V889 H199 V974 H225.5 V953 H269 V984 L252 1002 H175 L155.5 984 V879 Z", {}),
    ("commission-O-1", "M302 860.5 H374 L394 879 V983 L375 1002 H302 L283 983 V879 Z M327 889 H350 V974 H327 Z", {}),
    ("commission-M-1", "M0 0 H42 L71 53.5 L99 0 H141 V141.5 H100.5 V84.5 L74 133.5 H67 L40 84.5 V141.5 H0 Z", {"transform": "translate(408 860.5)"}),
    ("commission-M-2", "M0 0 H42 L71 53.5 L99 0 H141 V141.5 H100.5 V84.5 L74 133.5 H67 L40 84.5 V141.5 H0 Z", {"transform": "translate(560.5 860.5) scale(0.989362 1)"}),
    ("commission-I-1", "M713.5 860.5 H757 V1002 H713.5 Z", {}),
    ("commission-S-1", "M791 860.5 H858 L874 877 V901 H836 V889 H813 V914 H855 L874 932 V983 L855 1002 H789 L772 984 V960 H809 V974 H830 V943.5 H792 L772 924 V879 Z", {}),
    ("commission-S-2", "M791 860.5 H858 L874 877 V901 H836 V889 H813 V914 H855 L874 932 V983 L855 1002 H789 L772 984 V960 H809 V974 H830 V943.5 H792 L772 924 V879 Z", {"transform": "translate(114 0)"}),
    ("commission-I-2", "M1000.5 860.5 H1043 V1002 H1000.5 Z", {}),
    ("commission-O-2", "M1074 860.5 H1144 L1163 879 V983 L1144 1002 H1074 L1055 983 V879 Z M1097 889 H1119 V974 H1097 Z", {}),
    ("commission-N", "M1175 860.5 H1213 L1247 919 V860.5 H1289 V1002 H1248 L1213 943 V1002 H1175 Z", {}),
]

layers = [
    layer("sunburst", "01 - Sunburst", [
        path("sunburst-outline", polygon(sun), **{"stroke-linejoin": "round"}),
        path("sunburst-angular-notches", angular_inner_joins(sun), fill="none",
             **{"stroke-linejoin": "miter", "stroke-miterlimit": 10}),
    ], fill=COLORS["yellow"], stroke=COLORS["black"], **{"stroke-width": 9}),
    layer("plaque", "02 - White plaque and border", [
        path("plaque-white", plaque, fill=COLORS["white"]),
        path("plaque-frame", "M399 684 H103 V1027 H1337 V684 H1037", fill="none", stroke=COLORS["black"],
             **{"stroke-width": 11, "stroke-linejoin": "miter", "stroke-linecap": "butt"}),
        path("plaque-arch", arch, fill="none", stroke=COLORS["black"],
             **{"stroke-width": 8, "stroke-linecap": "butt"}),
    ]),
    layer("bc-initials", "03 - BC initials", [path("initial-B", bc_b), path("initial-C", bc_c)],
          fill=COLORS["red"], stroke=COLORS["black"], **{"stroke-width": 8, "stroke-linejoin": "miter", "fill-rule": "evenodd"}),
    layer("power-word", "04 - POWER lettering", [path(id_, d) for id_, d in power],
          fill=COLORS["navy"], **{"fill-rule": "evenodd"}),
    layer("commission-word", "05 - COMMISSION lettering", [path(id_, d, **attrs) for id_, d, attrs in commission],
          fill=COLORS["navy"], **{"fill-rule": "evenodd"}),
]

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="{INKSCAPE}"
     width="1448" height="1086" viewBox="0 0 1448 1086"
     version="1.1" role="img" aria-labelledby="emblem-title emblem-description"
     shape-rendering="geometricPrecision">
  <title id="emblem-title">BC Power Commission emblem - geometric vector reconstruction</title>
  <desc id="emblem-description">Reconstructed from the supplied raster reference using a manually authored sunburst polygon, two cubic arch segments, a rectilinear frame, and seventeen custom letter outlines. Five named layers. No embedded image, automatic tracing, external font, or linked asset. Exterior transparent; plaque white. Colours are flat visual approximations of the supplied image.</desc>
''' + "\n".join(layers) + "\n</svg>\n"

out = DEST / "BC_Power_Commission_Rebuilt.svg"
out.write_text(svg, encoding="utf-8")
print(out)
