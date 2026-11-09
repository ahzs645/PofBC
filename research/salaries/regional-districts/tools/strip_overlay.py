"""Write a copy of a PDF with text objects drawn in a given base font removed (duplicate OCR overlay)."""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject

src, dst, basefont = sys.argv[1], sys.argv[2], sys.argv[3]
pages = [int(x) for x in sys.argv[4].split(',')]
r = PdfReader(src)
w = PdfWriter()
removed = 0
for i in pages:
    page = r.pages[i - 1]
    fonts = page['/Resources'].get('/Font', {})
    target = {k for k, v in fonts.items() if str(v.get_object().get('/BaseFont')) == '/' + basefont}
    cs = ContentStream(page.get_contents(), r)
    ops, inblock, block, keep = [], False, [], True
    cur_font = None
    for operands, op in cs.operations:
        if op == b'BT':
            inblock, block, drop = True, [(operands, op)], False
            continue
        if inblock:
            block.append((operands, op))
            if op == b'Tf' and operands[0] in target:
                drop = True
            if op == b'ET':
                inblock = False
                if drop:
                    removed += 1
                else:
                    ops.extend(block)
            continue
        ops.append((operands, op))
    cs.operations = ops
    page[NameObject('/Contents')] = cs
    w.add_page(page)
w.write(dst)
print('removed text objects:', removed, 'target fonts', target)
