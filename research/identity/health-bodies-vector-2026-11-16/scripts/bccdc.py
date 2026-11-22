"""BC Centre for Disease Control: CDC symbol and name, from the cover of the BCCDC Annual Research
Report 2020/2021 (InDesign 16.3, created 3 September 2021), page 1, lower right.

  python -I bccdc.py SOURCES_DIR

Keeps the two symbol paths and the 25 glyph paths of 'BC Centre for Disease Control' in the PDF's own
colour (MuPDF's sRGB rendering of the PDF colour). The endorsement line under the name ('Provincial
Health Services Authority') is left out so the artwork corresponds to the website logo, which has none.
"""
import sys
from pathlib import Path
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import drawings_in, svg_of

SRC = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parents[4]
p = fitz.open(SRC / "bccdc-research-2021.pdf")[0]
ds = drawings_in(p, (450, 712, 565, 750.5), lambda d: d.get("fill") is not None and d["rect"].width < 60)
print(len(ds), "paths")
(ROOT / "public/identity-expanded/sub-bc-centre-for-disease-control/bccdc-2021-research-report.svg").write_text(svg_of(
    ds, "BC Centre for Disease Control — CDC symbol and name",
    "Original vector paths from the cover of the BCCDC Annual Research Report 2020/2021 (PDF page 1); endorsement line omitted."))
