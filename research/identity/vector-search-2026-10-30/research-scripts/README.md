# Extraction and verification scripts

These scripts document the exact extraction methods used for the supplied artwork. They use the original research workspace layout. They are not one-click installers: source PDFs and the GSC artwork bundle must first be downloaded from the URLs in the source register and research logs, placed at the relative source paths expected by the scripts, and checked against their recorded SHA-256 hashes.

Dependencies used: Python 3, PyMuPDF (`fitz`), Pillow, lxml, NumPy, and Inkscape for the package previews. Original SVG downloads need no conversion.

The source register and detailed findings are the authority for supplied file hashes and source attribution. Running extractions with a different PDF library version can change serialization or colour conversion.
