"""Semantic masks measured from the original lower-tree illustration.

These paths organise source ink; they are not replacement tree artwork.
Axes used for thin-branch corridors were manually read from the native scan.
No v1 synthetic branches, random hatching, or image contour extraction are used.
"""
from pathlib import Path
from math import hypot
import json

OUT=Path(__file__).resolve().parent

def rect(x0,y0,x1,y1):
    return f'M{x0} {y0}H{x1}V{y1}H{x0}Z'

def corridor(axes,radius):
    # Nonzero union of rounded segment corridors. The source still supplies
    # every line within these masks; these paths are never rendered as branches.
    parts=[]
    for pts in axes:
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            ll=hypot(x1-x0,y1-y0)
            if not ll:continue
            nx=-(y1-y0)/ll*radius;ny=(x1-x0)/ll*radius
            parts.append(f'M{x0+nx:.2f} {y0+ny:.2f}L{x1+nx:.2f} {y1+ny:.2f}A{radius} {radius} 0 0 1 {x1-nx:.2f} {y1-ny:.2f}L{x0-nx:.2f} {y0-ny:.2f}A{radius} {radius} 0 0 1 {x0+nx:.2f} {y0+ny:.2f}Z')
    return ' '.join(parts)

regions=[]
bases=[]

def region(id,path,notes=None,**extra):
    item={'id':id,'path':path}
    if notes:item['notes']=notes
    item.update(extra);regions.append(item)

def base(id,path,notes):
    bases.append({'id':id,'path':path,'notes':notes})

# Small, specific features first. Preserve the original mark, rather than
# recreating a signature or treating the original author's mark as scan noise.
region('original-illustrator-mark',rect(762,1914,811,1935),
       'Original source mark reading approximately d.g.01. Preserve existing ink; no new signature or attribution is generated.')

conk_right='M682 1195 C690 1200 697 1212 704 1218 C711 1222 720 1227 726 1232 L729 1237 L716 1241 L700 1242 L688 1237 L681 1227 Z'
conk_left='M488 1377 C484 1386 469 1389 458 1394 L444 1399 L449 1405 C460 1413 470 1422 483 1425 L505 1423 L508 1409 L501 1391 Z'
conk_low='M499 1527 C488 1533 479 1538 470 1543 L464 1548 L470 1553 L483 1559 L494 1568 L512 1568 L522 1558 L533 1551 L530 1543 L515 1536 L511 1530 Z'
region('right-bracket-fungus-1228',conk_right,
       'Measured shelf projecting right from the trunk near y1228. The pale underside has several fine parallel source strokes.')
region('left-bracket-fungus-1402',conk_left,
       'Large leftward shelf near y1400; source cap extends to approximately x447. Include the turned underside below its horizontal bands.')
region('left-bracket-fungus-1549',conk_low,
       'Lower broad cap with pale underside and a narrow attachment. Do not replace its stepped source edge with an oval.')

peg_front='M475 1192 L484 1192 C512 1205 540 1221 567 1234 C577 1237 583 1244 580 1251 C576 1261 561 1264 550 1256 L536 1244 C514 1229 494 1215 476 1204 Z'
peg_long='M612 1015 C615 1006 623 1008 632 1017 L644 1027 C650 1040 652 1060 657 1077 L674 1134 L681 1156 L676 1162 L668 1150 L653 1108 L637 1067 L624 1046 L616 1030 Z'
region('broken-peg-and-collar-1247',peg_front,
       'The diagonal broken limb and its knot/collar. Source tip near x480,y1197; keep the narrow pale wood face and collar opening.')
region('long-splintered-peg-1015-1158',peg_long,
       'Long slender split peg over the weathered trunk. The faint outer edge is real source ink, not a missing branch to invent.')

region('dark-scar-947','M620 933 L631 934 L637 944 L635 959 L628 970 L615 966 L613 949 Z')
region('cavity-or-dark-scar-1104','M599 1072 L607 1070 L614 1078 L621 1080 L625 1095 L622 1110 L624 1125 L616 1131 L609 1146 L601 1138 L595 1117 L594 1090 Z',
       'Deep dark feature in the front face. The source does not establish whether every dark area is a cavity or bark scar; label cautiously.')
region('dark-scar-1450-1577','M590 1418 L599 1427 L600 1439 L606 1443 L603 1465 L601 1484 L605 1501 L600 1520 L602 1543 L593 1578 L579 1578 L578 1553 L581 1527 L579 1499 L578 1474 L581 1441 Z')
region('long-narrow-scar-1590-1671','M574 1580 L582 1577 L586 1592 L585 1614 L582 1638 L584 1658 L578 1677 L568 1672 L564 1651 L566 1624 L568 1599 Z')

peel_a='M664 1540 C673 1558 678 1576 680 1591 C684 1602 686 1612 684 1620 L678 1620 C673 1614 671 1602 669 1590 L661 1562 Z'
peel_b='M670 1627 C675 1625 678 1630 675 1640 C671 1660 670 1676 665 1691 L658 1702 L656 1687 L660 1659 Z'
region('detached-bark-flap-1570-1620',peel_a,
       'Source-visible curled slab beside the lower right trunk; the gap to the trunk remains open.')
region('detached-bark-flap-1630-1700',peel_b)

central_weathered='M589 1234 L602 1238 L612 1262 C620 1284 628 1304 632 1333 C636 1380 632 1413 632 1451 C632 1492 629 1535 629 1578 C629 1615 627 1664 628 1705 L628 1769 L617 1785 L600 1766 L586 1745 L575 1728 L562 1734 L551 1730 L538 1738 L521 1720 C519 1675 524 1627 528 1586 C532 1538 536 1490 546 1452 C552 1416 559 1385 564 1347 C567 1308 571 1263 589 1234 Z'
upper_weathered='M591 900 L639 900 L658 921 C658 958 655 997 655 1035 L664 1078 L672 1111 L669 1158 L655 1172 L636 1151 L615 1154 L597 1160 L587 1136 L587 1094 L583 1057 L583 1017 L590 983 L593 944 Z'
region('lower-exposed-weathered-wood',central_weathered,
       'Weathered front face including sparse bore marks and grain. Specific scars, peg and collar are assigned before this broad material region.')
region('middle-exposed-weathered-wood-900-1160',upper_weathered)

# Real roots / slabs, measured at their source intersections and tips.
left_root='M437 1752 L445 1755 L451 1766 C449 1791 438 1823 421 1852 C404 1874 377 1893 349 1907 L321 1920 L295 1930 L273 1939 L261 1943 L252 1936 L258 1927 C283 1902 307 1878 332 1852 L365 1821 L392 1803 C409 1786 419 1765 437 1752 Z'
right_root='M548 1843 C559 1838 567 1830 578 1832 C604 1838 625 1851 648 1862 L678 1880 L712 1899 L745 1912 L747 1917 L739 1928 L720 1927 L692 1922 L664 1911 L636 1902 L611 1888 L587 1876 L570 1863 Z'
front_slab='M405 1872 C452 1868 498 1872 542 1848 L552 1843 L567 1864 L575 1885 C564 1905 540 1916 510 1920 L463 1927 L417 1927 L406 1931 L381 1927 L359 1920 L346 1912 L357 1904 L379 1892 Z'
region('left-buttress-root',left_root,
       'Long diagonal root / exposed basal slab ending near x258,y1935. Root and bark grain come entirely from the original penwork.')
region('right-forward-basal-slab',right_root,
       'Prominent diagonal wood slab in front of the root flare; retains the source broad end and short fractured corners.')
region('front-central-basal-wood',front_slab,
       'Horizontal-grained basal wood in front of the trunk. The drawing alone does not resolve whether this is an attached root or fallen slab.')

root_flare='M450 1694 C469 1709 488 1726 511 1739 L531 1730 L548 1732 L558 1744 L572 1726 L582 1738 L593 1737 L605 1758 L617 1777 L638 1783 L657 1755 L665 1794 L673 1834 L693 1873 L676 1890 L645 1881 L610 1860 L579 1831 L550 1845 L525 1860 L483 1871 L440 1873 L411 1888 L393 1887 C420 1835 438 1770 450 1694 Z'
region('root-flare-and-basal-bark',root_flare,
       'Fluted living/decayed base behind the three foreground wood forms. The scalloped start of the bark at y1725–1780 is preserved in source ink.')

trunk='M541 900 L689 900 C690 941 688 977 687 1008 L689 1041 L686 1075 L687 1106 L684 1139 L685 1174 L683 1206 L682 1247 L678 1289 L678 1323 L674 1359 L673 1394 L670 1431 L666 1465 L665 1500 L668 1531 L670 1555 L671 1579 L668 1604 L669 1634 L665 1669 L661 1706 L661 1743 L662 1779 L667 1814 L674 1847 L665 1866 L639 1863 L614 1850 L581 1832 L552 1845 L519 1861 L475 1871 L434 1876 L409 1885 L418 1847 L432 1808 L442 1770 L449 1735 L457 1696 L463 1665 L470 1632 L476 1601 L479 1574 L482 1542 L487 1508 L490 1478 L495 1444 L499 1410 L503 1376 L509 1339 L512 1306 L517 1272 L522 1239 L526 1205 L528 1171 L530 1139 L533 1102 L536 1068 L537 1033 L539 1000 L541 970 L542 939 Z'
region('lower-trunk-bark-and-wood',trunk,
       'Measured main trunk envelope; loose outer bark flaps are separate. Do not use this mask to discard ink outside it: the global source-ink mask remains authoritative.')

# Thin foreground branch crosses the trunk. Corridors organise genuine source
# strokes, and their width deliberately includes nearby hanging lichens.
crossing_axes=[[(388,1300),(425,1321),(463,1334),(494,1340),(525,1341),(550,1355),(577,1373),(609,1390),(639,1405),(678,1409),(712,1415),(746,1420)],
               [(712,1415),(728,1413),(740,1407)]]
region('foreground-crossing-bough-1340-1420',corridor(crossing_axes,12),
       'Source bough and attached lichen crossing the face of the trunk. Intersections with bark are not inferred behind the visible source line.',
       measured_axes=crossing_axes,semantic_corridor_half_width=12)

main_sapling_axes=[
 [(716,1818),(733,1806),(742,1779),(748,1749),(754,1715),(760,1678),(766,1643),(768,1619),(762,1591),(751,1566),(744,1543)],
 [(763,1647),(749,1625),(737,1605),(724,1589),(716,1576)],
 [(739,1607),(733,1623)],
 [(756,1705),(738,1678),(720,1663),(700,1652),(687,1647)],
 [(737,1678),(716,1653),(700,1647)],
 [(725,1663),(700,1660),(689,1659)],
 [(748,1762),(772,1757),(794,1744),(815,1724),(832,1698),(851,1673),(869,1646)],
 [(832,1698),(829,1670)],
 [(772,1757),(783,1733),(792,1714)],
 [(741,1786),(722,1764),(704,1744),(684,1729),(671,1726)],
 [(712,1751),(692,1729),(677,1714)],
 [(707,1753),(685,1752),(673,1750)],
]
right_sapling_axes=[
 [(793,1817),(818,1799),(839,1788),(862,1774),(885,1755),(904,1734),(914,1719)],
 [(858,1776),(862,1757),(864,1738),(860,1715)],
 [(842,1786),(831,1770),(819,1760)],
 [(832,1773),(831,1759)],
 [(883,1758),(893,1734),(893,1710)],
 [(839,1788),(868,1780),(885,1769),(902,1761)],
 [(809,1808),(843,1804),(872,1796)],
]
region('basal-sapling-central-right',corridor(main_sapling_axes,8),
       'Manually measured axes of the taller bare sapling rooted just right of the snag. Narrow corridors avoid claiming the broad open spaces between twigs.',
       measured_axes=main_sapling_axes,semantic_corridor_half_width=8)
region('basal-sapling-far-right',corridor(right_sapling_axes,7),
       measured_axes=right_sapling_axes,semantic_corridor_half_width=7)

left_ground_axes=[
 [(88,1748),(96,1778),(111,1807),(130,1837),(152,1864),(173,1888)],
 [(117,1817),(95,1801),(80,1790),(69,1779)],
 [(111,1807),(102,1790)],
 [(172,1889),(150,1910),(127,1927),(102,1939)],
 [(150,1910),(153,1899),(145,1894)],
]
region('foreground-fallen-branch-left',corridor(left_ground_axes,7),
       measured_axes=left_ground_axes,semantic_corridor_half_width=7)

region('ground-stump-left','M157 1811 L167 1798 L175 1790 L178 1803 L186 1808 L191 1819 L177 1829 L163 1826 Z')
region('ground-stump-fork-behind-roots','M303 1790 L316 1792 L330 1807 L340 1812 L349 1804 L356 1794 L363 1793 L357 1812 L366 1821 L346 1827 L326 1825 L310 1817 Z',
       'Two short broken wood points below the toad caption. Do not extend the caption exclusion downward into these source-visible tips.')

region('ground-grass-tuft-left','M100 1869 L113 1879 L124 1884 L129 1919 L119 1925 L107 1918 Z',
       'Several hairline blades are weak in the source and may need a threshold review.')
region('ground-grass-tuft-centre-left','M223 1847 L239 1851 L251 1854 L271 1862 L267 1878 L257 1898 L247 1905 L233 1884 Z')
region('ground-grass-tuft-right','M785 1853 L800 1853 L809 1859 L831 1858 L833 1877 L821 1905 L816 1918 L799 1910 L789 1884 Z')

pebbles=[(548,1925,13,8),(549,1937,12,8),(574,1928,12,8),(585,1942,13,6),
         (618,1948,11,7),(642,1941,14,7),(681,1931,11,8),(752,1911,11,9),(854,1919,13,8)]
region('foreground-pebbles',' '.join(rect(x-rx,y-ry,x+rx,y+ry) for x,y,rx,ry in pebbles),
       'Individual source stones below the root ends. Their light inner marks are not synthetic texture.')

floor='M52 1806 L111 1810 L151 1818 L181 1814 L220 1816 L249 1811 L285 1816 L324 1811 L366 1822 L414 1817 L465 1811 L513 1819 L563 1813 L611 1818 L653 1813 L699 1815 L737 1813 L775 1820 L817 1826 L850 1834 L856 1848 L892 1854 L902 1867 L923 1879 L938 1888 L945 1899 L921 1904 L891 1901 L871 1909 L836 1904 L809 1913 L779 1906 L747 1915 L712 1910 L679 1918 L641 1911 L604 1917 L571 1922 L539 1914 L502 1924 L466 1925 L432 1931 L397 1924 L367 1918 L334 1915 L297 1913 L271 1907 L242 1901 L211 1904 L181 1910 L153 1906 L118 1918 L83 1913 L52 1914 Z'
region('forest-floor-and-fallen-wood',floor,
       'Grouping envelope for the original fragmented ground wood. This is NOT a white base: the open white spaces between fragments remain open.')

region('lower-left-dead-boughs',
       'M45 900H543L541 975L538 1045L533 1110L526 1190L518 1270L506 1350L495 1430L484 1515L476 1590L465 1660L449 1740H45Z',
       'Broad semantic fallback outside the trunk, subordinate to specific features. Portraits and caption boxes must be removed by the root mask first.')
region('lower-right-dead-boughs',
       'M690 900H976V1814H667L662 1730L668 1650L676 1600L671 1540L666 1475L671 1400L677 1330L683 1260L686 1180L688 1110L690 1030Z',
       'Broad semantic fallback for source-visible lower dead boughs and lichen. Specific basal sapling corridors are listed first.')

# Foreground bough precedes the broad material surfaces it visibly crosses.
crossing=next(item for item in regions if item['id']=='foreground-crossing-bough-1340-1420')
regions.remove(crossing)
regions.insert(next(i for i,item in enumerate(regions) if item['id']=='dark-scar-947'),crossing)

# White backing is deliberately conservative and restricted to solid wood.
# Roots are separate from the floor grouping; no large open-ground polygon.
# Selection masks above deliberately have a little margin around ink. These
# separate base paths stay INSIDE measured wood and do not reuse that margin.
trunk_inner='M551 900 L678 900 C680 1020 678 1130 674 1230 C670 1340 657 1450 660 1550 C664 1610 652 1700 654 1775 C655 1810 659 1838 666 1850 L641 1855 L615 1840 L580 1826 L550 1838 L512 1854 L475 1864 L436 1868 L424 1873 C432 1827 450 1763 462 1700 C474 1643 486 1580 493 1510 C503 1410 521 1300 531 1200 C539 1090 548 990 551 900 Z'
left_root_inner='M437 1758 C441 1758 444 1761 445 1767 C443 1790 432 1821 416 1848 C399 1871 373 1890 346 1903 L319 1916 L294 1927 L271 1935 L261 1938 L258 1935 L263 1930 C287 1906 310 1881 335 1856 L368 1825 L396 1807 C412 1791 422 1770 437 1758 Z'
right_root_inner='M556 1846 C563 1841 571 1835 578 1837 C602 1842 623 1856 645 1866 L675 1884 L709 1903 L736 1914 L739 1918 L735 1923 L721 1922 L694 1917 L667 1907 L638 1898 L613 1884 L590 1872 L573 1860 Z'
front_slab_inner='M410 1877 C454 1874 499 1878 542 1854 L550 1849 L562 1867 L569 1884 C558 1900 537 1911 509 1915 L463 1922 L418 1922 L408 1926 L383 1922 L363 1916 L353 1912 L361 1908 L381 1896 Z'
peg_front_inner='M481 1197 L486 1198 C512 1211 540 1226 566 1238 C574 1240 579 1244 576 1250 C572 1257 563 1260 553 1253 L539 1240 C515 1226 495 1211 482 1201 Z'
peg_long_inner='M620 1014 C623 1013 627 1016 630 1020 L640 1029 C647 1044 648 1060 653 1079 L670 1136 L676 1155 L672 1149 L657 1107 L642 1067 L628 1044 L621 1028 Z'
base('solid-lower-trunk',trunk_inner,
     'Conservative interior of solid trunk. Deliberately inset from the semantic envelope; outer curled slabs and spaces between sapling branches stay open.')
base('solid-left-buttress-root',left_root_inner,'Conservative interior of diagonal basal wood; no extension across the toad panel/caption exclusion.')
base('solid-right-forward-basal-slab',right_root_inner,'Conservative interior of foreground diagonal wood slab.')
base('solid-front-central-basal-wood',front_slab_inner,'Conservative interior of horizontal-grained basal wood visible in front of the trunk.')
base('solid-broken-peg-1247',peg_front_inner,'Interior of actual solid peg and collar; the white wood face belongs to the object.')
base('solid-long-splintered-peg',peg_long_inner,'Interior of actual narrow split-wood object, not its surrounding open gap.')

payload={
 'schema_version':1,
 'coordinate_system':{'viewBox':[0,0,1000,2997.159090909091],'source_native_pixels':[4576,13715],
                      'scope':[0,900,1000,1985],'units':'normalized full-poster width=1000; y uses the same scale'},
 'method':'Manual source measurements from the native scan and annotated grids. Regions organise fitted original ink; they never synthesize tree branches or texture.',
 'assignment':'first_matching_region',
 'regions':regions,
 'white_base_paths':bases,
 'source_exclusions':[
   {'id':'chickadee-panel-and-caption','box':[137,985,352,1222],'note':'Root should use its exact original portrait/caption boxes; no tree branch is invented behind the panel.'},
   {'id':'bear-panel-and-caption','box':[97,1265,359,1546],'note':'Entire original crop/frame and caption are excluded from tree ink.'},
   {'id':'toad-panel-and-caption','box':[188,1559,416,1791],'note':'The toad illustration protrudes left beyond its rectangular frame. Include the recovered left hind-foot ink down to approximately x190.5. Keep the caption cutoff above the two wood points beginning near y1793.'},
   {'id':'flying-squirrel-caption-overlap','box':[218,881,434,904],'note':'Small overlap at the top of this lower-tree scope.'},
 ],
 'preserve_source_features':[
   {'id':'original-illustrator-mark','note':'Preserve the original tree mark near x764–808,y1916–1933 in its own group. The small mark inside the toad panel belongs to that panel and is excluded from the tree.'},
   {'id':'fine-conk-underside-lines','note':'Inspect light parallel strokes under shelves at y1235,1415 and1558; they are visible source penwork.'},
   {'id':'thin-basal-twigs-and-grasses','note':'Fine sapling tips near x744,y1543; x892,y1710; and grass blades near x111,y1905 andx813,y1895 can drop at a strong threshold. Review against source before any manual restoration.'},
   {'id':'small-stones','note':'Light stone outlines around y1935–1955 are real source features, even when individual strokes are disconnected.'},
 ],
 'notes':[
   'The root-provided global source-ink mask remains authoritative. These masks are semantic labels, not permission to discard source-visible ink outside them.',
   'No missing branch section underneath a portrait is reconstructed.',
   'The outline of the source artist mark is not re-authored; only its measured selection region is provided.',
   'No ground-wide white backing is supplied, so gaps between wood fragments and twigs stay unfilled.',
   'Dark trunk shapes are labelled scars/cavities cautiously; the source drawing alone does not identify every dark patch biologically.',
 ],
}
(OUT/'tree-lower-regions.json').write_text(json.dumps(payload,indent=2))
print(OUT/'tree-lower-regions.json',len(regions),'regions',len(bases),'white bases')
