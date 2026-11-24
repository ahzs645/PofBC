# B.C. post-secondary identity expansion — 2026-11-24

## Coverage
- 11 current public colleges, seven additional universities, one institute, UBC Okanagan as a campus, and selected predecessor names/operations.
- 49 subjects, 26 direct published raster candidates (18 listing images, six Camosun retrospective images, two additional institutional publications).
- Historical member-logo leads: BCNET 2014–15 and BC Colleges 2019, plus individual archives. Source links are not accepted artwork.
- The 26 direct-image leads remain separate from the 13 source-only PDF specimens registered in [artwork-review-candidates.json](./artwork-review-candidates.json). The accepted manifest remains unchanged. A source or locally verified extraction is not a gallery holding or redistribution permission.

## Institutional chronology rules
Keep OUC's two successors distinct; TRU is legal continuation of UCC with transferred open-university operations, not the whole Open Learning Agency. Kwantlen and Langara split from continuing institutions. Royal Roads site continuity is not a corporate rename. A university-college mandate year is not automatically the date of its name change. Do not infer logo adoption from any legal date or image filename. Camosun's 1991 retrospective caption conflicts with a 1997 filename; 2021 is an anniversary mark. Historic logos are not filled with their successors' artwork.

## Acquisition
Run `python3 scripts/acquire-postsecondary-identities.py stage /tmp/pofbc-colleges` with Pillow installed. Open the images, verify attribution, variant, and source; edit `review.json` to mark reviewed specimens approved. Run `python3 scripts/acquire-postsecondary-identities.py accept /tmp/pofbc-colleges`, followed by `node scripts/build-identity-expansion.mjs` and `node scripts/build-identity-expansion.mjs --check`. Review changes and commit the public images, manifest and generated file together. Do not auto-approve a failed or wrong image, reconstruct historical marks from current logos, or label a raster as vector. The script does not fetch or extract PDF specimens; inspect those separately and preserve page/source evidence. Check institution-native SVG/PDF/EPS brand downloads before preferring listing rasters.

The registry supplies source references and exact image URLs. This is a first-pass scope, not a claim of complete historical artwork coverage. Legal instrument searches, publication chronology and rights/reuse review remain open.

### PDF evidence added for review

The review register names the publisher, publication date, exact one-based PDF page, and SHA-256 of the observed PDF edition. It records seven embedded images (six CAEN and one PVI) and six native vector regions (OUC, two readings of one UCC cover, and three Selkirk variants). PDF page numbers and publication dates are not logo adoption dates. Dates and evidence for institutional events are kept separately in the source register.

For local verification, download the cited PDF to a disposable directory outside the checkout and compare its SHA-256 with `sourceSha256`. A mismatch requires fresh review, not accepting the replacement automatically. With PyMuPDF, verify an image's object number against `doc[pdfPage - 1].get_images(full=True)`, then use `doc.extract_image(objectNumber)` and compare format, dimensions and the extracted SHA-256. For vectors, `rectPt` uses PyMuPDF's top-left page coordinate system, in points; preview the region with `page.get_pixmap(clip=fitz.Rect(rectPt))`. Retain the native drawing paths rather than tracing the preview. Review neighbouring page art, paint order, fill/stroke and clipping before exporting. Exclude unrelated cover photos and showcase backgrounds; retain the OUC blue panel because it is the recorded cover application. Use a dark preview backdrop for the Selkirk reverse mark, not part of the exported mark.

All entries in the PDF register are `source-only`. Public access to a cited report, logo guide, or archive does not by itself permit redistribution. These specimens must not be copied to `public/`, supplied to the direct-raster importer, or entered in the accepted manifest without documented reuse clearance. No PDFs or extracted images are included here.

## Coverage pass: source links on the 49 subject pages

The [artwork evidence ledger](./artwork-coverage-evidence.json) records additional institution-native artwork, historic reproductions, visual leads and independently documented shared identities. The subject detail links directly to each verified vector or source document; it does not embed external files. Where reliable artwork is still missing, the subject remains a research gap rather than inheriting its predecessor's or successor's mark.

The family count classifies each subject once: verified institutional vector, observed institutional nonvector only, or no independently verified logo artwork. A shared campus signature, athlete mark, campaign, unconfirmed cover or historic heraldic device stays labelled as such. The count of gallery holdings is separate. An artwork lead is not a native vector file, and a source-backed reconstruction would need a visible reconstruction label and clearance before inclusion.

No vector is manufactured from a current logo, an institutional name or an unconfirmed design description. Site publication and public access to downloads do not alone establish permission to copy, embed, or distribute the artwork. Only accept an asset into the separate held manifest after checking both identity and source-specific reuse terms.

The [College of New Caledonia evidence and extraction record](./cnc-identity-history.md) identifies the precise native drawings for its two logo forms and separates those specimens from the dated heraldic grant and provincial designation.
