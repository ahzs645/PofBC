"""Authored charred-ground apertures, with revision-5 branch protection.

The ground bands are connected dark printing masses. Their openings represent
visible gaps between timber, exposed fragments, and a few short wood cuts.
They are constructed as individual editable contours from visual study of the
reference, not extracted from a binary mask. No source image is read here.

The separate root columns and the restored arched rear-branch corridor belong
to foreground_v2.py and are protected by the clip. Irregular patch margins
avoid a new ruled ground edge. Fine print wear and small uncertain pale
speckles are deliberately left uninterpreted. The foreground's rear arch now
owns its opening; an authored vector clip protects that entire connected object.
"""

INK = '#242332'
ORANGE = '#F77913'
# Exposed wood is a pale gold in the supplied photograph, distinct from sky.
WOOD = '#ECD878'
YELLOW = WOOD


# Interstitial charred beds. Each patch joins the existing dark printing field;
# the modest zigzags at the side boundaries keep the replacement from creating
# a straight visible seam where adjacent root work remains separately editable.
DARK_BEDS = [
 ('left-bed', '''M0 1075 L9 1075 17 1077 25 1075 37 1076 49 1075
  L65 1076 79 1075 91 1077 103 1075 119 1075
  L118 1084 120 1092 117 1103 119 1112 118 1123 120 1133 119 1145
  L0 1145 Z'''),
 ('between-left-and-centre', '''M330 1075 L343 1076 355 1075 369 1076
  L381 1075 397 1076 408 1075 429 1075
  L430 1084 428 1095 430 1104 428 1116 430 1127 429 1145
  L331 1145 330 1137 332 1127 330 1118 332 1107 330 1097 331 1086 Z'''),
 ('between-centre-and-right', '''M550 1075 L566 1075 577 1076 587 1075 600 1075
  L599 1084 600 1092 598 1100 600 1110 599 1121 600 1132 599 1145
  L551 1145 550 1136 552 1128 550 1118 551 1105 550 1096 551 1085 Z'''),
 ('right-bed', '''M740 1075 L753 1076 767 1075 781 1076 797 1075
  L811 1076 824 1075 841 1075 860 1076 877 1075 892 1076
  L908 1075 927 1076 941 1075 957 1076 978 1075 1000 1075
  L1000 1145 742 1145 740 1139 742 1129 740 1118 741 1108 740 1098 742 1087 Z'''),
]

# Open gaps have a distinct physical scale and direction. The broad middle
# ones sit beneath crossing branches; the smaller low ones are broken chips
# and short cuts in the charred bed, rather than a random scatter of flecks.
ORANGE_OPENINGS = [
 ('left-edge-scorch', '''M0 1075 L3 1075 4 1078 3 1081
  L5 1084 3 1087 1 1086 0 1088 Z'''),
 ('left-upright-groove', '''M12 1075 L14 1075 13 1080 14 1082
  L12 1086 10 1087 10 1083 11 1080 Z'''),
 ('left-bent-gap', '''M13 1096 C17 1094 21 1092 25 1090
  L29 1090 27 1094 24 1095 C22 1100 19 1102 15 1102
  L12 1100 13 1098 Z'''),
 ('left-upper-right-split', '''M76 1075 L80 1075 80 1079 78 1082 76 1080 Z'''),
 ('left-small-upward-chip', '''M56 1103
  C58 1099 61 1096 64 1094 L66 1094 64 1098 60 1101 58 1104 Z'''),
 ('left-large-branch-gap', '''M54 1115
  C58 1113 61 1110 64 1108 C68 1105 74 1103 79 1102
  L81 1103 77 1108 C74 1111 73 1113 74 1116
  L78 1117 76 1120 72 1118 70 1123 68 1119
  C64 1120 59 1118 54 1115 Z'''),
 # A small bundle of carved wood faces: three shallow cross-grain slashes,
 # an upturned right end, and a separate diagonal cut below. Their direction
 # follows the exposed fragment instead of treating it as two orange blobs.
 ('left-far-edge-gap', '''M94 1095
  C98 1092 102 1093 106 1094 C109 1094 112 1095 114 1096
  L112 1097 C107 1096 102 1095 98 1095 L95 1097 Z'''),
 ('left-bundle-upturned-end', '''M115 1097
  C117 1095 118 1093 120 1092 L120 1095 118 1098 116 1099 Z'''),
 ('left-bundle-middle-cut', '''M94 1100
  C98 1098 103 1099 108 1100 L109 1102
  C103 1101 99 1101 95 1102 Z'''),
 ('left-bundle-low-face', '''M96 1104
  C99 1102 102 1103 105 1104 L106 1106
  C102 1105 99 1105 96 1106 Z'''),
 ('left-far-edge-underpiece', '''M99 1114
  C102 1111 105 1109 108 1107 L109 1108
  C106 1111 103 1113 100 1116 Z'''),
 ('left-low-fragment', '''M9 1135 L12 1133 14 1135 14 1140
  L12 1144 10 1141 Z'''),
 ('left-low-small-fragment', '''M36 1137 L40 1134 43 1135
  L42 1138 38 1140 Z'''),
 ('left-broken-sliver', '''M71 1134 L75 1131 79 1130 77 1133 Z'''),
 ('left-tiny-cut', '''M47 1120 L50 1118 52 1119 50 1121 Z'''),

 ('midleft-large-aperture', '''M338 1082
  C344 1080 350 1077 356 1077 C362 1078 368 1080 373 1083
  L374 1084 C369 1087 363 1090 356 1090
  C349 1089 342 1087 338 1084 Z'''),
 ('midleft-edge-notch', '''M330 1091 L335 1093 335 1097 330 1099 Z'''),
 ('midleft-under-branch', '''M389 1090
  C395 1089 402 1091 408 1094 C416 1097 423 1098 430 1095
  L430 1099 C422 1101 415 1100 408 1098
  C402 1096 395 1095 389 1093 Z'''),
 ('midleft-low-crossing-gap', '''M377 1107
  C384 1104 391 1104 396 1100 L401 1099
  C405 1101 410 1101 414 1103 L416 1105
  C410 1104 404 1104 399 1106 C392 1108 385 1109 378 1109 Z'''),
 ('midleft-low-chip', '''M338 1112
  C342 1110 346 1110 350 1111 L351 1113 348 1116
  L342 1117 338 1115 Z'''),
 ('midleft-low-edge-chip', '''M331 1124 L334 1122 336 1125 335 1129
  L333 1130 Z'''),
 ('midleft-small-low-chip', '''M391 1131 L396 1129 400 1129
  L401 1131 397 1133 392 1133 Z'''),
 ('midleft-diagonal-cut', '''M337 1145 L345 1142 352 1139
  L357 1138 354 1141 347 1145 Z'''),

 ('midright-under-timber-gap', '''M550 1075 L580 1075 588 1079
  L593 1081 600 1083 600 1086 592 1085 584 1084 573 1083
  L562 1083 558 1080 553 1078 550 1080 Z'''),
 ('midright-left-fork-gap', '''M550 1090 L555 1092 556 1096 553 1100
  L550 1102 Z'''),
 ('midright-long-low-gap', '''M554 1106 L562 1104 572 1104 581 1103
  L590 1101 600 1101 600 1108 592 1108 586 1107 575 1108
  L564 1109 557 1108 Z'''),
 ('midright-tiny-low-chip', '''M572 1135 L579 1134 585 1135
  L582 1137 575 1138 572 1137 Z'''),

 ('right-upper-gap-left', '''M802 1075 L825 1075 820 1078
  L813 1080 807 1078 Z'''),
 ('right-upper-root-gap', '''M842 1075 L852 1075
  C863 1076.5 874 1079 885 1081.5 L889 1081
  C896 1079 901 1077 905 1075 L914 1075 912 1078
  C907 1081 901 1085 895 1085 L889 1084
  C876 1084 861 1081 847 1079 L843 1078 Z'''),
 ('right-main-forked-aperture', '''M834 1079
  C840 1080 846 1082 852 1084 C859 1085 866 1088 872 1092
  L870 1093 C866 1091 861 1093 858 1093 L852 1092 848 1092
  C844 1096 842 1100 837 1103 L834 1104 836 1100
  C831 1103 823 1105 815 1104 L818 1101
  C823 1099 825 1096 828 1093 L829 1090 833 1089
  C835 1087 834 1083 832 1082 Z'''),
 ('right-left-small-chip', '''M741 1108 L745 1108 748 1105
  L749 1108 754 1109 751 1112 746 1113 742 1111 Z'''),
 ('right-small-chip-above', '''M791 1099 L796 1097 799 1098
  L797 1101 793 1102 790 1100 Z'''),
 ('right-small-chip-centre', '''M809 1112 L814 1110 817 1110
  L817 1113 813 1114 810 1114 Z'''),
 ('right-bent-chip', '''M805 1117 L809 1114 812 1115 810 1118
  L813 1121 811 1125 807 1123 803 1125 801 1121 802 1118 Z'''),
 ('right-small-teardrop', '''M907 1110 L910 1106 914 1104
  L914 1108 912 1112 909 1113 906 1112 Z'''),
 ('right-long-chip', '''M929 1107 L933 1104 939 1104 945 1105
  L952 1107 946 1108 939 1108 934 1111 929 1110 Z'''),
 ('right-upper-tiny-chip', '''M958 1096 L962 1096 966 1098
  L965 1100 961 1099 Z'''),
 ('right-paired-cut-upper', '''M862 1129 L866 1127 871 1124
  L877 1122 878 1123 873 1126 868 1129 Z'''),
 ('right-paired-cut-lower', '''M871 1130 L876 1127 883 1125
  L887 1124 883 1127 875 1131 Z'''),
 ('right-long-low-sliver', '''M887 1145 C897 1142 907 1138 916 1134
  L919 1134 915 1137 907 1141 896 1145 Z'''),
]

# These small dark cuts divide the wide orange aperture into the observed
# forked spaces around wood, rather than leaving a single orange blob.
APERTURE_DIVIDERS = [
 ('right-fork-divider', '''M833 1087 C835 1088 839 1089 841 1091
  L839 1093 836 1091 833 1090 Z'''),
 ('right-fork-lower-divider', '''M823 1099
  C826 1097 829 1096 832 1095 L831 1097
  C828 1098 826 1099 823 1100 Z'''),
 ('right-fork-splinter-cut', '''M866 1090 L868 1093
  L865 1092 Z'''),
 ('midleft-chip-notch', 'M346 1114 L348 1111 350 1112 348 1115 Z'),
]

YELLOW_CHIPS = [
 ('right-left-wood-face', '''M740 1075 L750 1075 756 1076 766 1078
  L775 1079 787 1079 800 1080 806 1078 804 1080
  L800 1082 789 1081 776 1081 766 1080 755 1077 747 1076 740 1076 Z'''),
 ('right-fork-wood-edge', '''M831 1080
  C833 1077 836 1076 839 1075 L841 1076 838 1077 834 1080 Z'''),
 ('right-upper-crossing-bevel', '''M882 1083
  C885 1081 889 1078 892 1075 L894 1075
  C890 1079 887 1082 883 1084 Z'''),
 ('midright-thin-wood-edge', '''M564 1085 L577 1085 590 1086 600 1087
  L600 1088 589 1088 577 1087 566 1087 Z'''),
]


# The crossing timber and its charred support form one local junction. This
# authored patch spans the old x600 scope edge instead of extending that
# rectangular strip into the root column. Its margins join existing dark wood;
# the two orange spaces and the short pale end-face remain separate objects.
# All contours stay within x550–635/y1075–1120, below the diagonal's main face.
CENTRAL_JUNCTION = [
 ('central-junction-bed', '''M550 1075 L555 1075 558 1080
  C570 1085 588 1084 601 1085 L607 1082 620 1075 635 1075
  L635 1085 634 1094 633 1099 632 1108 627 1112 618 1110
  L610 1112 601 1114 588 1112 574 1113 561 1111 553 1109 550 1107
  L555 1102 558 1097 558 1092 552 1089 550 1084 Z''', INK),
 ('central-junction-upper-gap', '''M550 1075 L580 1075
  C586 1079 595 1083 602 1085 C590 1084 575 1084 562 1083
  L558 1080 553 1078 550 1080 Z''', ORANGE),
 ('central-junction-horizontal-face', '''M566 1086
  C578 1084 594 1086 603 1087 L607 1089
  C594 1088 579 1088 568 1088 Z''', ORANGE),
 ('central-junction-face-tip', '''M596 1087 L602 1087 607 1089
  L601 1089 598 1088 Z''', YELLOW),
 ('central-junction-lower-aperture', '''M554 1107
  C565 1103 580 1104 592 1102 C600 1101 606 1099 610 1099
  C606 1103 599 1107 592 1109 C580 1110 568 1110 558 1109
  L554 1108 Z''', ORANGE),
 ('central-junction-short-end-face', '''M613 1085
  C618 1081 623 1078 627 1076 L628 1076 626 1079
  C622 1082 618 1085 615 1086 Z''', YELLOW),
 ('central-junction-end-face-grain', '''M616 1085 L620 1082
  L622 1082 619 1084 Z''', INK),
 ('central-junction-low-chip', '''M612 1110
  C610 1114 607 1118 604 1120 L600 1120
  C604 1116 607 1112 612 1110 Z''', ORANGE),
]


# Revision 6: the bowed under-branch opening continues across the old x430
# ground-band edge. The small upper closure removes an unsupported triangular
# orange tip. This object stops above the adjacent central root and its chip.
MIDLEFT_BRANCH_JOIN = [
 ('midleft-join-charred-support', '''M425 1085 L440 1085 449 1085
  L448 1089 445 1094 445 1105 434 1105 425 1104 Z''', INK),
 ('midleft-join-curved-opening', '''M425 1096
  C431 1093 437 1091 442 1088 L445 1087 443 1090
  C438 1094 433 1097 428 1099 L425 1100 Z''', ORANGE),
]


# The left end of the central crossing was another old foreground aperture,
# shaped like a broad horizontal club. The source shows a short diagonal
# exposed face instead. Its light contour stays right of the central stump's
# physical edge; the separate stump chip at x523–530 is untouched.
CENTRAL_BRANCH_END_JOIN = [
 ('central-left-end-charred-support', '''M532 1085 L538 1085 543 1087
  L549 1088 555 1090 557 1094 557 1103 549 1104 539 1104 532 1101 Z''', INK),
 ('central-left-end-exposed-face', '''M543 1087
  C546 1088 550 1091 554 1094 L553 1096 551 1098
  C548 1094 545 1090 543 1087 Z''', ORANGE),
]


def _path(name, contour, fill):
    return f'<path id="ground-v4-{name}" d="{contour}" fill="{fill}"/>'


def build_ground_details():
    out = ['<g id="ground-v4-refinements" aria-label="Charred interstitial ground, branch gaps and exposed wood fragments">']
    out.append('<defs><clipPath id="ground-v5-outside-rear-arch">')
    # This envelope follows the constructed branch and its enclosed opening.
    # Intersecting this clip with the older ground scope keeps both the dark
    # beds and their orange/yellow cuts out of the connected foreground object.
    # An even-odd clip is vector geometry; it does not require a raster mask.
    out.append('<path clip-rule="evenodd" d="M0 0 L1000 0 1000 1440 0 1440 Z '
               'M706 1077 C725 1065 743 1062 754 1064 '
               'L780 1072 813 1073 820 1080 812 1089 793 1091 774 1091 '
               'L751 1102 730 1112 714 1111 707 1105 Z"/>')
    out.append('</clipPath><clipPath id="ground-v4-interstitial-scope">')
    # The high-left part of the right band is reserved for the connected rear
    # arch now reconstructed with the physical branch geometry. Its return
    # occupies x740–815/y1075–1095 and must remain above these ground patches.
    scopes = [(0,1075,120,70),(330,1075,100,70),(550,1075,50,70),
              (815,1075,185,20),(740,1095,260,50)]
    for x,y,width,height in scopes:
        out.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}"/>')
    out.append('</clipPath></defs><g clip-path="url(#ground-v4-interstitial-scope)">'
               '<g clip-path="url(#ground-v5-outside-rear-arch)">')
    out.extend(_path(name, d, INK) for name, d in DARK_BEDS)
    out.extend(_path(name, d, ORANGE) for name, d in ORANGE_OPENINGS)
    out.extend(_path(name, d, INK) for name, d in APERTURE_DIVIDERS)
    out.extend(_path(name, d, YELLOW) for name, d in YELLOW_CHIPS)
    out.append('</g></g>')
    # The local junction has authored object boundaries, not a rectangular
    # scope edge. The rear arch clip is preserved exactly and still applies.
    out.append('<g id="ground-v5-central-junction" clip-path="url(#ground-v5-outside-rear-arch)">')
    out.extend(_path(name, d, fill) for name, d, fill in CENTRAL_JUNCTION)
    out.append('</g>')
    out.append('<g id="ground-v6-midleft-branch-join" clip-path="url(#ground-v5-outside-rear-arch)">')
    out.extend(_path(name, d, fill) for name, d, fill in MIDLEFT_BRANCH_JOIN)
    out.append('</g>')
    out.append('<g id="ground-v6-central-branch-end" clip-path="url(#ground-v5-outside-rear-arch)">')
    out.extend(_path(name, d, fill) for name, d, fill in CENTRAL_BRANCH_END_JOIN)
    out.append('</g>')
    out.append('</g>')
    return '\n'.join(out)

