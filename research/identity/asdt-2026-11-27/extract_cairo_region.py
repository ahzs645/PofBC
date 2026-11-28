# Usage: pdftocairo -svg -f N -l N source.pdf page.svg
#        python3 extract_cairo_region.py page.svg N x0 y0 x1 y1 out.svg   (PDF points from the top-left)
#
# Run scripts/pdf_vector_region.produce over pdftocairo's SVG of a page instead of MuPDF's, so that
# native PDF shadings stay radial gradients (MuPDF rasterises them). Same region filter, no redrawing.
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from pdf_vector_region import produce
svg_path, page, x0, y0, x1, y1, out = sys.argv[1], int(sys.argv[2]), *map(float, sys.argv[3:7]), sys.argv[7]
class Page:
    def get_svg_image(self, text_as_path=True):
        text = open(svg_path, encoding='utf-8').read()
        # Cairo places each glyph with x and y on its <use>; the filter reads transforms, so the same
        # offset is written as a translate (an identical placement).
        def move(m):
            tag = m.group(0)
            x = re.search(r' x="([^"]*)"', tag); y = re.search(r' y="([^"]*)"', tag)
            if not (x or y) or 'transform=' in tag:
                return tag
            tag = re.sub(r' [xy]="[^"]*"', '', tag)
            return tag.replace('<use', f'<use transform="translate({x.group(1) if x else 0} {y.group(1) if y else 0})"', 1)
        return re.sub(r'<use\b[^>]*>', move, text)
class Doc:
    def __getitem__(self, i):
        return Page()
data, box, counts = produce({'id': out, 'page': page, 'region': [x0, y0, x1, y1]}, Doc())
open(out, 'wb').write(data)
print(out, box, counts, len(data))
