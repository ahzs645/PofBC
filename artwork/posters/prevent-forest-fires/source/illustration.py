"""Constructed illustration for the BC forest-fire poster.

Geometry is authored from visual landmarks, branch structure, and brush-cut
shapes. No source pixels, bitmap contours, or image tracing are used here.
The source photograph is only used outside this module for comparison.
"""
from random import Random
from math import hypot, sin, cos, pi
import re

INK = '#242332'
YELLOW = '#F5E928'
ORANGE = '#F77913'
PAPER = '#F5F0D7'


def path(d, fill=INK, **attrs):
    a = ' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
    return f'<path d="{d}" fill="{fill}" {a}/>'


def woodcut_edge(d, seed, amplitude=.65, spacing=4.5):
    """Give a designed polygon a restrained, hand-cut edge.

    This operates on authored vector lines, never on a bitmap. Cubic contours
    are kept untouched; only straight-edged wood facets are treated here.
    The endpoints are retained, preserving the designed structural landmarks.
    """
    if re.search(r'[CcQqAaHhVvSsTt]',d): return d
    tokens=re.findall(r'[MLZmlz]|-?\d*\.?\d+(?:[eE][+-]?\d+)?',d)
    rng=Random(seed);out=[];i=0;first=None;prev=None
    while i<len(tokens):
        command=tokens[i];i+=1
        if command.upper()=='Z':
            target=first
        else:
            target=(float(tokens[i]),float(tokens[i+1]));i+=2
        if command.upper()=='M':
            first=target;prev=target;out.append(f'M{target[0]:.2f} {target[1]:.2f}');continue
        if prev is None or target is None: continue
        dx,dy=target[0]-prev[0],target[1]-prev[1];length=hypot(dx,dy)
        steps=max(1,int(length/spacing))
        if length:
            nx,ny=-dy/length,dx/length
            for k in range(1,steps):
                t=k/steps
                jitter=rng.uniform(-amplitude,amplitude)
                x=prev[0]+dx*t+nx*jitter;y=prev[1]+dy*t+ny*jitter
                out.append(f'L{x:.2f} {y:.2f}')
        if command.upper()=='Z':out.append('Z')
        else:out.append(f'L{target[0]:.2f} {target[1]:.2f}')
        prev=target
    return ' '.join(out)


def narrow_facet(d, start, end, factor=.62):
    """Narrow a designed highlight across its grain without shrinking length."""
    dx,dy=end[0]-start[0],end[1]-start[1];ll=hypot(dx,dy)
    ux,uy=dx/ll,dy/ll;nx,ny=-uy,ux
    def point(m):
        x,y=float(m.group(1)),float(m.group(2))
        u=(x-start[0])*ux+(y-start[1])*uy
        v=((x-start[0])*nx+(y-start[1])*ny)*factor
        return f'{start[0]+u*ux+v*nx:.2f} {start[1]+u*uy+v*ny:.2f}'
    return re.sub(r'(-?\d*\.?\d+)\s+(-?\d*\.?\d+)',point,d)


def build_flames():
    # Each tongue has a different reach, bend, and gap. The open central orange
    # field is designed to support the title rather than filled with decoration.
    d = '''M0 313
    C13 345 17 363 25 386 L17 328 C29 355 35 374 42 392
    L33 302 C52 350 76 380 105 421 L67 351 L97 387 L89 351
    L126 396 L143 422 C139 391 150 365 144 337
    L171 371 L167 319 L186 348 L169 252
    C187 295 205 317 215 345 L211 304 L219 331 L220 178
    C237 215 258 242 275 274 L286 226 L288 262 L299 279
    L309 244 L316 266 L316 217 C328 231 335 247 349 263
    L363 206 L380 163 L382 204 L390 184 C393 206 396 223 405 236
    L414 139 C435 164 447 186 456 209 L462 255 L462 219
    L478 255 L481 232 L489 273 L499 246 L503 280
    C516 259 520 238 524 219 L526 258 L536 300 L544 277
    C550 236 556 204 574 162 C581 206 600 244 609 279
    L610 306 L619 277 L616 300 L629 266 L637 279
    L652 237 L649 265 L676 204 L681 197 L673 234
    L701 191 L689 237 C708 213 724 190 731 162 L721 289
    C734 263 753 246 764 216 L758 278 L774 255 L777 270
    L787 254 L790 302 L810 272 L821 262 L827 229
    L837 297 L835 391 L848 352 L850 318 L860 376
    L874 340 L872 370 L899 328 L921 287 C912 342 904 367 893 406
    L916 374 L914 424 L932 392 L932 356 L946 393 L943 366
    C962 391 966 418 965 449 L973 420 L979 468
    L986 450 L986 496 L1000 446 L1000 1440 L0 1440 Z'''
    tongues = [
        'M0 349 C20 401 22 453 67 519 C41 490 31 454 27 423 Z',
        'M0 485 C12 528 33 565 60 592 C22 565 8 537 0 516 Z',
        'M0 649 C8 700 14 724 31 757 C8 736 2 715 0 699 Z',
        'M999 473 C982 537 981 606 940 666 C966 606 966 552 978 511 Z',
        'M903 632 C869 669 839 701 821 756 C838 693 867 658 903 632 Z',
        'M1000 757 C993 784 982 810 969 826 C990 809 998 791 1000 777 Z',
    ]
    return '<g id="flames">' + path(d, ORANGE) + ''.join(path(t,YELLOW) for t in tongues) + '</g>'


def build_script():
    # Brush construction: broad downstrokes, lighter turns, two shared e bowls,
    # and a separately shaped capital P. Outlined contours remain editable.
    p_loop = '''M240 331 C257 308 294 287 328 279
    C352 273 378 272 385 289 C396 313 373 334 345 349
    C325 359 305 365 289 369 L282 357
    C307 350 341 336 359 321 C374 309 377 298 368 293
    C351 286 321 294 296 306 C273 317 257 331 247 344
    C242 351 234 345 237 337 Z'''
    p_stem = '''M314 314 C318 309 327 307 333 309
    C315 345 290 386 273 420 C271 426 260 425 257 421
    C255 417 263 402 271 386 L299 337 Z'''
    # A single brush outline gives the bowl/descender one continuous join.
    # The sweep and counter remain deliberately open, as in the painted P.
    p_brush = '''M239 331 C256 309 293 286 326 278
    C345 274 369 273 379 285 C389 301 383 321 365 336
    C346 352 318 362 298 368 C289 386 280 405 274 418
    C272 422 262 420 258 417 C255 416 257 410 260 404
    C267 388 274 371 281 354 C278 354 277 351 280 348
    C283 346 287 344 292 342 C297 329 302 317 307 309
    C312 305 321 304 327 306 C318 325 310 341 305 348
    C322 342 343 328 355 316 C369 306 375 296 367 291
    C350 286 321 293 296 306 C273 317 258 331 249 345
    C245 351 239 348 237 343 C235 339 236 336 239 331 Z'''
    r = '''M316 378 C334 372 350 357 357 346 C360 341 369 340 370 346
    L368 353 C369 359 377 362 382 361 C386 361 388 366 383 372
    C375 382 367 395 363 402 C359 409 363 412 371 410
    C381 408 390 402 398 394 L403 400 C389 416 374 424 359 419
    C340 414 345 401 355 386 L365 370 C360 369 356 366 356 363
    C344 375 332 383 321 386 C316 387 311 383 316 378 Z'''
    # Both lowercase e's derive from a shared bowl and counter. The second
    # occurrence is slightly wider, as on the printed reference.
    e = '''M0 47 C3 29 21 8 39 4 C52 1 61 7 57 18
    C53 31 32 43 12 42 C9 52 12 59 23 59
    C36 59 52 47 65 32 L69 38 C54 56 37 69 20 70
    C2 71 -5 61 0 47 Z
    M16 34 C30 32 44 22 46 16 C47 12 43 12 39 14
    C29 19 21 27 16 34 Z'''
    v = '''M471 355 C476 353 484 354 487 357
    C474 373 465 387 461 399 C458 408 463 411 472 407
    C484 401 497 387 506 373 C504 369 501 365 504 358
    C507 349 514 346 519 352 C524 358 520 365 517 371
    C523 377 531 379 540 376 L541 385 C528 389 516 384 511 381
    C499 399 483 414 469 418 C454 423 444 417 445 406
    C447 392 457 373 471 355 Z'''
    n = '''M612 357 C618 354 625 355 628 357 L621 368
    C632 358 643 352 651 354 C664 355 665 365 659 375
    L642 403 C638 410 640 413 648 409 C665 400 680 387 691 374
    L697 380 C684 398 666 414 650 419 C635 424 624 417 628 405
    C632 392 642 378 646 369 C648 365 646 364 642 366
    C629 372 612 389 603 405 L595 420 C590 423 582 420 578 418
    C586 399 599 374 612 357 Z'''
    t_stem = '''M730 306 C733 300 744 296 750 302
    C751 306 747 313 743 319 C727 344 708 371 701 393
    C697 405 696 413 702 419 C700 424 686 422 684 417
    C678 405 685 385 695 367 C707 345 720 324 730 306 Z'''
    t_cross = '''M686 319 C720 315 765 313 810 312
    C817 310 819 314 816 320 L812 328
    C773 331 732 328 694 333 C682 334 675 332 680 325 Z'''
    # Revision 6: bounded construction-parameter calibration of the drawn
    # glyphs. Photo registration is unchanged; no pixel contour is traced.
    pieces = [
        ('P', [('prevent-p-brush',p_brush)], 1,1,0),
        ('r', [('prevent-r',r)], -1,-3,4/3),
        ('e1', [], 0,-1,2),
        ('v', [('prevent-v',v)], 1,-1,2),
        ('e2', [], 3,-2,2),
        ('n', [('prevent-n',n)], -3,-1,4/3),
        ('t', [('prevent-t-stem',t_stem),('prevent-t-cross',t_cross)], -1,0,2),
    ]
    out=['<g id="prevent-script" aria-label="Prevent" fill="'+PAPER+'">']
    for name,shapes,dx,dy,weight in pieces:
        out.append(f'<g id="prevent-brush-{name}" transform="translate({dx} {dy})" stroke="{PAPER}" stroke-width="{weight:.5f}" stroke-linejoin="round">')
        if name=='e1':
            out.append(f'<path id="prevent-e-first" d="{e}" fill="{PAPER}" fill-rule="evenodd" transform="translate(390 350)"/>')
        elif name=='e2':
            out.append(f'<path id="prevent-e-second" d="{e}" fill="{PAPER}" fill-rule="evenodd" transform="translate(523 349) scale(1.03 1)"/>')
        else:
            out.extend(path(d,PAPER,id=ident) for ident,d in shapes)
        out.append('</g>')
    out.append('</g>')
    return ''.join(out)


def line_cut(x1,y1,x2,y2,width,fill=YELLOW, tip=.7):
    """A tapered gouge, not a stroked line; editable woodcut geometry."""
    dx,dy=x2-x1,y2-y1
    length=hypot(dx,dy)
    if length<.01:return ''
    nx,ny=-dy/length*width,dx/length*width
    return path(f'M{x1:.2f} {y1:.2f} L{x1+dx*.18+nx:.2f} {y1+dy*.18+ny:.2f} '
                f'L{x2:.2f} {y2:.2f} L{x1+dx*.30-nx*tip:.2f} {y1+dy*.30-ny*tip:.2f} Z',fill)


def build_foreground():
    parts=['<g id="burnt-forest">']
    # Background cross-grain, fallen branches, and root structures.
    branches=[
        'M0 1065 L48 1052 L96 1060 L139 1051 L194 1065 L250 1061 L280 1069 L312 1062 L338 1073 L374 1066 L409 1078 L450 1072 L490 1080 L525 1067 L557 1082 L590 1075 L628 1086 L661 1078 L697 1090 L730 1076 L764 1081 L800 1068 L841 1074 L873 1061 L913 1064 L951 1048 L1000 1041 L1000 1440 L0 1440 Z',
        'M64 1041 L148 1035 L185 1046 L211 1038 L252 1039 L285 1053 L326 1045 L353 1058 L380 1050 L402 1058 L432 1052 L463 1064 L499 1057 L501 1065 L454 1070 L414 1060 L385 1068 L355 1069 L327 1056 L299 1064 L277 1061 L250 1050 L211 1048 L186 1053 L143 1043 L91 1049 Z',
        'M307 1096 L367 1087 L421 1063 L470 1036 L503 1025 L513 1012 L522 1016 L533 1010 L540 1014 L589 1016 L619 1012 L648 1014 L665 1009 L664 1017 L614 1020 L574 1027 L550 1022 L511 1041 L466 1050 L409 1079 L366 1097 Z',
        'M697 1092 L746 1080 L778 1062 L811 1049 L819 1035 L825 1034 L823 1045 L847 1062 L875 1055 L910 1059 L939 1046 L965 1045 L999 1016 L1000 1029 L969 1054 L941 1057 L914 1070 L879 1066 L846 1072 L810 1062 L777 1075 L748 1090 Z',
        'M690 1031 L727 1027 L750 1036 L795 1036 L839 1061 L861 1060 L881 1054 L885 1060 L862 1066 L841 1071 L797 1044 L751 1043 L727 1036 L700 1040 Z',
        'M357 1114 L381 1102 L389 1081 L384 1070 L382 1053 L388 1045 L390 1040 L393 1048 L387 1060 L391 1077 L403 1089 L427 1099 L452 1098 L462 1103 L446 1107 L422 1106 L399 1099 L388 1103 L366 1120 Z',
        'M534 1096 L551 1069 L567 1053 L571 1042 L577 1038 L578 1044 L573 1055 L564 1065 L557 1075 L574 1078 L587 1088 L618 1093 L612 1098 L584 1095 L568 1087 L554 1086 L545 1101 Z',
        'M919 1022 L947 1005 L961 982 L956 974 L950 972 L960 969 L968 973 L993 958 L995 964 L976 979 L968 990 L966 1006 L982 1010 L998 1024 L1000 1034 L982 1020 L962 1017 L943 1025 Z',
    ]
    parts.extend(path(woodcut_edge(d,101+i,.6)) for i,d in enumerate(branches))
    # Small left stumps and the branched snag at the far right.
    stumps=[
        'M0 1077 L7 1025 L2 1017 L6 996 L11 957 L19 974 L23 974 L24 963 L34 982 L29 1010 L40 1019 L58 1003 L66 974 L74 990 L80 997 L82 1022 L98 1068 L122 1098 L98 1107 L69 1084 L66 1053 L53 1061 L43 1081 L24 1088 Z',
        'M851 1083 C867 1056 863 1027 863 1000 L859 939 L854 839 L861 842 L860 830 L866 833 L868 817 L878 836 L885 779 L897 786 L903 805 L903 861 L909 936 L918 981 C923 1005 927 1024 941 1045 L957 1059 L946 1071 L925 1066 L904 1073 L886 1062 L873 1086 Z',
        'M743 1006 L760 1000 L758 958 L749 939 L746 931 L750 932 L763 949 L773 935 L783 924 L785 927 L776 939 L767 957 L769 990 L774 1000 L805 1005 L832 1019 L864 1038 L863 1048 L835 1032 L806 1015 L772 1009 Z',
        'M197 1072 L205 1047 L214 1027 L212 1015 L215 1008 L219 1017 L233 1015 L243 1018 L250 1016 L256 1020 L247 1023 L234 1021 L220 1028 L214 1048 L211 1068 Z',
        'M45 979 L56 968 L56 945 L23 950 L21 944 L53 936 L78 928 L88 915 L95 918 L86 932 L63 943 L61 966 L65 973 L61 978 L56 974 L51 981 Z',
        'M557 940 L569 961 L580 978 L591 982 L599 981 L605 986 L600 990 L606 1003 L602 1008 L598 995 L590 986 L580 983 L573 969 L565 953 L552 943 Z',
    ]
    parts.extend(path(woodcut_edge(d,201+i,.9)) for i,d in enumerate(stumps))
    # Long diagonal fallen timber: distinct facets and a splintered top edge.
    logs=[
        'M168 982 L194 977 L206 964 L235 963 L264 960 L305 956 L319 961 L356 960 L369 967 L335 973 L309 969 L283 976 L241 977 L213 981 L208 991 L202 996 L204 982 L177 986 Z',
        'M346 970 L381 972 L412 982 L458 991 L501 1006 L544 1020 L573 1044 L601 1065 L633 1080 L652 1099 L642 1105 L617 1090 L591 1079 L567 1061 L539 1035 L501 1023 L453 1008 L412 995 L377 984 L347 980 Z',
        'M276 979 L312 964 L358 954 L407 943 L464 929 L526 919 L570 912 L617 908 L630 900 L638 887 L639 899 L634 907 L654 910 L696 904 L742 905 L764 902 L779 911 L787 900 L791 914 L820 925 L852 940 L885 958 L907 977 L919 998 L905 1007 L886 985 L864 967 L835 950 L806 938 L778 925 L748 925 L709 929 L669 931 L629 938 L587 942 L553 952 L507 960 L464 970 L420 982 L375 993 L331 1008 L292 1023 L274 1014 L287 998 L281 992 L292 987 Z',
    ]
    parts.extend(path(woodcut_edge(d,301+i,.85)) for i,d in enumerate(logs))
    # Three principal stumps and the leaning left trunk/root fan.
    cores=[
        'M39 824 L48 817 L47 801 L54 795 L62 800 L74 784 L77 773 L77 751 L85 747 L110 748 L105 751 L84 754 L83 774 L73 797 L66 807 C86 854 111 910 138 961 C156 997 172 1025 192 1048 L211 1064 L239 1072 L255 1080 L266 1094 L250 1105 L216 1091 L204 1091 L222 1113 L237 1116 L222 1122 L201 1111 L184 1111 L170 1127 L145 1135 L122 1130 L147 1118 L156 1101 L151 1084 C144 1061 133 1036 116 1006 C88 953 60 898 44 852 Z',
        'M207 1129 L230 1105 L244 1083 L254 1040 L262 1006 L268 977 L275 990 L281 985 L289 1005 L302 1009 L301 1047 L307 1083 L316 1104 L332 1116 L339 1136 L320 1139 L307 1128 L301 1143 L283 1150 L278 1129 L267 1142 L250 1149 L233 1142 Z',
        'M439 1116 L454 1090 L467 1069 L480 1046 L487 1005 L488 962 L496 956 L501 976 L509 966 L518 977 L519 1024 L527 1065 L533 1087 L550 1116 L533 1121 L519 1111 L509 1128 L485 1126 L476 1119 L458 1130 Z',
        'M600 1139 L621 1117 L633 1090 L642 1059 L649 1011 L658 977 L664 986 L669 1000 L680 1006 L679 1014 L697 1020 L712 1017 L713 1044 L708 1080 L713 1111 L723 1136 L739 1144 L723 1150 L711 1143 L705 1152 L686 1145 L674 1135 L661 1147 L649 1141 L638 1147 L621 1141 L608 1148 Z',
    ]
    parts.extend(path(woodcut_edge(d,401+i,.7)) for i,d in enumerate(cores))
    # Deliberate light-facing facets, carved from each structural silhouette.
    facets=[
        'M54 802 L61 808 L81 859 L112 926 L142 986 L165 1028 L194 1065 L187 1077 L172 1063 L148 1024 L124 976 L99 924 L72 864 Z',
        'M158 1095 L172 1080 L178 1085 L177 1099 L168 1110 L153 1118 L132 1127 L151 1116 Z',
        'M191 1072 L200 1077 L212 1077 L224 1081 L217 1087 L203 1083 L197 1088 L191 1083 Z',
        'M219 1114 L235 1098 L248 1076 L257 1044 L268 1009 L266 1044 L257 1082 L245 1104 L232 1119 Z',
        'M264 1050 L277 1019 L280 1036 L278 1065 L270 1086 L259 1098 L266 1080 Z',
        'M294 1014 L295 1060 L298 1093 L307 1110 L303 1119 L294 1103 L289 1069 Z',
        'M290 979 L332 967 L377 955 L426 943 L474 933 L524 923 L569 918 L612 913 L634 912 L618 920 L575 923 L526 930 L480 942 L431 952 L383 966 L337 978 L303 990 L291 988 L304 984 Z',
        'M330 986 L379 974 L420 962 L460 953 L507 941 L540 938 L532 943 L490 950 L449 963 L410 972 L370 982 L337 994 Z',
        'M628 913 L654 913 L683 909 L710 908 L745 909 L765 906 L776 915 L751 914 L719 915 L690 914 L654 919 Z',
        'M787 916 L814 930 L844 945 L870 959 L894 979 L896 987 L869 965 L840 950 L811 935 Z',
        'M209 969 L247 966 L272 964 L306 959 L311 963 L279 970 L249 971 L224 974 L204 975 Z',
        'M398 980 L422 988 L461 999 L500 1013 L536 1027 L560 1045 L583 1062 L609 1076 L611 1081 L581 1066 L553 1047 L534 1034 L496 1021 L454 1007 L416 993 Z',
        'M490 1048 L496 1025 L501 1030 L504 1060 L498 1078 L494 1069 Z',
        'M516 1074 L521 1084 L524 1100 L521 1108 L516 1092 Z',
        'M655 988 L661 994 L666 1009 L675 1015 L672 1026 L666 1019 L658 1015 L656 1007 Z',
        'M677 1021 L697 1026 L707 1023 L703 1029 L691 1031 L680 1026 Z',
        'M699 1033 L703 1032 L701 1069 L701 1097 L705 1128 L712 1141 L707 1142 L697 1121 L695 1089 Z',
        'M675 1089 L671 1110 L664 1124 L653 1133 L656 1121 L667 1102 Z',
        'M860 844 L866 846 L870 898 L868 922 L870 959 L865 950 Z',
        'M887 789 L892 800 L894 835 L893 864 L890 861 Z',
        'M899 920 L901 947 L907 974 L915 991 L910 990 L903 969 L899 942 Z',
        'M879 1006 L884 1036 L889 1050 L900 1066 L893 1067 L881 1054 L876 1028 Z',
        'M895 1077 L914 1076 L932 1066 L956 1062 L969 1053 L973 1056 L958 1068 L938 1073 L917 1084 L900 1084 Z',
        'M713 1054 L745 1047 L773 1046 L793 1046 L801 1050 L776 1051 L749 1052 L723 1060 Z',
        'M713 1075 L744 1064 L762 1070 L778 1069 L788 1074 L774 1077 L757 1075 L746 1072 L721 1082 Z',
        'M5 1034 L21 1029 L24 1022 L20 1022 L15 1029 L7 1030 Z',
        'M46 1005 L57 990 L62 987 L67 982 L70 987 L63 991 L57 1007 L49 1019 L39 1026 Z',
    ]
    for i,axis in {0:((60,811),(186,1071)),6:((300,981),(634,913)),
                   7:((333,990),(535,940)),8:((634,916),(773,912)),
                   9:((790,920),(893,983)),10:((207,971),(306,964)),
                   11:((400,985),(608,1078))}.items():
        facets[i]=narrow_facet(facets[i],*axis,.60)
    parts.append('<defs><clipPath id="wood-grain-boundary">'+''.join(path(d) for d in branches+stumps+logs+cores)+'</clipPath></defs>')
    parts.append('<g id="carved-highlight-facets" clip-path="url(#wood-grain-boundary)">')
    parts.extend(path(woodcut_edge(d,501+i,.65,3.0),YELLOW) for i,d in enumerate(facets))
    parts.append('</g>')
    # Orange split grain and burnt ground openings. These describe wood and
    # roots, rather than recreating photographic dirt and compression noise.
    orange_cuts=[
        'M0 1041 L16 1039 L29 1045 L34 1052 L19 1049 L5 1047 Z',
        'M2 1055 L19 1056 L30 1068 L21 1074 L8 1072 L4 1064 Z',
        'M19 1079 L34 1065 L41 1060 L39 1078 L31 1086 Z',
        'M62 1090 L80 1077 L90 1078 L82 1086 L83 1093 L73 1094 Z',
        'M99 1106 L116 1095 L131 1095 L127 1102 L112 1105 L108 1111 Z',
        'M307 1071 L322 1067 L337 1077 L329 1085 L311 1081 Z',
        'M341 1080 L358 1076 L377 1084 L362 1092 L350 1088 Z',
        'M314 1095 L331 1090 L341 1099 L329 1105 L313 1104 Z',
        'M365 1109 L378 1103 L390 1107 L404 1104 L413 1109 L393 1115 L376 1114 Z',
        'M418 1089 L437 1083 L449 1085 L441 1094 L428 1094 Z',
        'M438 1108 L452 1098 L459 1098 L455 1106 L449 1110 Z',
        'M548 1107 L563 1097 L580 1101 L577 1106 L563 1110 Z',
        'M576 1121 L596 1111 L616 1111 L611 1116 L594 1122 Z',
        'M637 1117 L642 1096 L647 1080 L648 1102 Z',
        'M643 1130 L648 1116 L654 1106 L654 1119 Z',
        'M660 1135 L674 1120 L680 1108 L679 1126 L668 1137 Z',
        'M682 1133 L686 1105 L690 1086 L688 1127 Z',
        'M714 1100 L739 1088 L754 1089 L748 1095 L725 1105 Z',
        'M750 1113 L766 1103 L785 1100 L795 1104 L778 1111 L762 1114 Z',
        'M801 1091 L818 1081 L840 1085 L834 1092 L817 1093 Z',
        'M856 1104 L872 1094 L887 1094 L877 1101 L866 1107 Z',
        'M911 1113 L923 1104 L929 1106 L924 1112 Z',
        'M934 1110 L940 1104 L955 1107 L946 1114 Z',
        'M946 1091 L962 1087 L968 1090 L954 1096 Z',
    ]
    parts.extend(path(woodcut_edge(d,601+i,.65,2.7),ORANGE) for i,d in enumerate(orange_cuts))
    # Short, reproducible engraving strokes are positioned along the physical
    # grain of a log, never sampled from a raster mask.
    rng=Random(1946)
    parts.append('<g id="carved-grain" clip-path="url(#wood-grain-boundary)">')
    grain_axes=[(61,830,181,1070,11,180),(300,980,775,913,13,270),
                (863,850,882,1048,7,72),(671,1023,665,1126,13,62),
                (270,1025,248,1115,9,54),(493,1030,504,1103,10,44)]
    for x1,y1,x2,y2,band,count in grain_axes:
        dx,dy=x2-x1,y2-y1;l=hypot(dx,dy);ux,uy=dx/l,dy/l;nx,ny=-uy,ux
        for j in range(count):
            t=rng.random(); off=rng.uniform(-band,band)
            x=x1+t*dx+off*nx;y=y1+t*dy+off*ny
            length=rng.uniform(1.8,12)
            color=INK if j%3 else ORANGE
            parts.append(line_cut(x,y,x+ux*length,y+uy*length,rng.uniform(.3,1),color))
        # Fine parallel flecks on the shadow plane break up the broad flat ink.
        for j in range(count//3):
            t=rng.random();off=rng.uniform(-band,band)
            x=x1+t*dx+off*nx;y=y1+t*dy+off*ny
            length=rng.uniform(1.2,6.5)
            parts.append(line_cut(x,y,x+ux*length,y+uy*length,rng.uniform(.15,.45),YELLOW))
    parts.append('</g>')
    # Broken ground: low-density chips near roots, sparing the lettering field.
    for j in range(155):
        x=rng.uniform(0,1000); y=rng.uniform(1082,1152)
        if 320<x<620 and y<1125: continue
        length=rng.uniform(2,11)
        parts.append(line_cut(x,y,x+length,y-rng.uniform(1,5),rng.uniform(.35,1.1),ORANGE))
    parts.append('</g>')
    return ''.join(parts)


if __name__ == '__main__':
    from pathlib import Path
    p=Path(__file__).parent
    content=(f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1440" viewBox="0 0 1000 1440">'
             f'<rect width="1000" height="1440" fill="{YELLOW}"/>'
             +build_flames()+build_foreground()+build_script()+'</svg>')
    (p/'illustration-preview.svg').write_text(content)
