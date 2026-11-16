"""BC Emergency Health Services: BCEHS letters, rule and name from the cover of the BCEHS Progress
Report 2023-24 (InDesign CS6, PDF created 2 November 2024), page 1, top right.

  python -I bcehs.py SOURCES_DIR

Keeps all the logo's paths (BCEHS letters, red rule, two-line name and the 'Provincial Health Services
Authority' endorsement line) in the PDF's own colours (MuPDF's sRGB rendering). This is the endorsed
lockup: its name is set larger relative to the letters than in the website PNG, so it is a related
variant, not the same artwork as the website logo.
"""
import sys
from pathlib import Path
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import drawings_in, svg_of

SRC = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parents[4]
p = fitz.open(SRC / "bcehs_progress_report_2023-24.pdf")[0]
ds = drawings_in(p, (420, 45, 605, 80), lambda d: d.get("fill") is not None)
print(len(ds), "paths")
(ROOT / "public/identity-expanded/bc-emergency-health-services/bcehs-2024-progress-report-endorsed.svg").write_text(svg_of(
    ds, "BC Emergency Health Services — logo with PHSA endorsement",
    "Original vector paths from the cover of the BCEHS Progress Report 2023-24 (PDF page 1)."))
