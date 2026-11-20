"""Build the openly licensed, named reconstruction working font.

Requires fontTools. The original source file and OFL are retained alongside
this script. Glyph outlines are unchanged from Jost; no tracing is involved.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
font = instantiateVariableFont(
    TTFont(HERE / "Jost-Italic-wght.ttf"), {"wght": 600}, inplace=False
)

# This current italic release already uses single-storey a by default.
# Unlike the upright font, ss01 selects the TWO-storey form. Disable that
# optional feature while keeping the default glyph outlines and Unicode map.
for record in font["GSUB"].table.FeatureList.FeatureRecord:
    if record.FeatureTag == "ss01":
        record.Feature.LookupListIndex = []
        record.Feature.LookupCount = 0

names = {
    1: "Forest Ad Sans",
    2: "SemiBold Italic",
    3: "ForestAdSans-SemiBoldItalic-1.1",
    4: "Forest Ad Sans SemiBold Italic",
    6: "ForestAdSans-SemiBoldItalic",
    16: "Forest Ad Sans",
    17: "SemiBold Italic",
    10: (
        "A reconstruction working font derived from Jost by the Jost Project "
        "Authors. Static weight 600 italic preserving the default single-storey "
        "a; the double-storey ss01 alternate is disabled. This modern substitute "
        "is not an authenticated historical typeface."
    ),
}
for record in list(font["name"].names):
    if record.nameID in names:
        record.string = names[record.nameID].encode(
            record.getEncoding(), errors="replace"
        )
for name_id, value in names.items():
    font["name"].setName(value, name_id, 3, 1, 0x409)
    font["name"].setName(value, name_id, 1, 0, 0)

font["OS/2"].usWeightClass = 600
font["OS/2"].fsSelection = (font["OS/2"].fsSelection | 1) & ~64 & ~32
font["head"].macStyle = (font["head"].macStyle | 2) & ~1
font.save(HERE / "ForestAdSans-SemiBoldItalic.ttf")
font.flavor = "woff"
font.save(HERE / "ForestAdSans-SemiBoldItalic.woff")
