# Northwest Community College: recovered vector logos

British Columbia, Canada. Recovered 27 November 2026.

## Contents

- `nwcc-logo-colour.svg`, `.pdf`, `.png`: full historical logo, directly extracted from the college's 2025 anniversary magazine.
- `nwcc-thunderbird-colour.svg`, `.pdf`, `.png`: the emblem isolated from that same vector artwork.
- `nwcc-logo-white.svg`, `.pdf`, `.png`: complete white logo, directly extracted from a college publication for the 19 June 2015 golf tournament.
- `nwcc-wordmark-2017-white.svg`, `.pdf`, `.png`: later wordmark without the Thunderbird, directly extracted from the back cover of the 2016-2017 Aboriginal Student Support report, published in 2017.
- `nwcc-logos-preview.png`: convenient visual reference. Its backgrounds and labels are presentation only.
- `provenance.json`: exact sources, extraction information, source checksums and verification results.

SVG is the main reusable format. All lettering is already outlined. The SVG and PDF assets contain original vector paths and no embedded bitmap logo or live font dependencies. PNG files are raster previews with transparent backgrounds. White files need a dark background to be visible.

## Original sources

1. **CMTN Connection, Spring 2025, 50th Anniversary Magazine**, PDF page 4, printed page 6 (left half of the 6-7 spread):
   https://www.coastmountaincollege.ca/docs/default-source/about/publications/2025-cmtn-connection-magazine_spread-min.pdf
2. **2015 Golf Tournament and Student Bursary Fundraiser sponsor sheet**, page 1:
   https://www.coastmountaincollege.ca/docs/default-source/about/cmtn-foundation/2015_ty_golf_smithers.pdf
3. **Aboriginal Student Support at Northwest Community College 2016-2017**, PDF page 41, back cover:
   https://www.coastmountaincollege.ca/docs/default-source/cmtn-reports-statements-reviews/indigenous-reports/aboriginal_student_support_report.pdf
4. **British Columbia announcement of the name change**, effective 18 June 2018:
   https://news.gov.bc.ca/releases/2018AEST0056-000708

## Recovery and fidelity

The existing artwork paths were copied from the PDFs, preserving their placement, colours, curves and clipping. Unrelated page objects were removed and a small transparent margin was added around each asset. Nothing was traced or redrawn. The source contains some duplicate letter paths; these remain to preserve rendering faithfully.

The colour extraction contains 52 artwork paths, zero embedded raster images and zero live text elements. It was rendered against the original source crop at 1200 x 304 pixels. Foreground shape overlap (intersection over union at 50% edge coverage) is 99.997209%. Small edge differences can arise from PDF-to-SVG coordinate precision and antialiasing.

The source magazine has a U.S. Web Coated (SWOP) v2 print output intent. The SVG and exported vector PDF retain the extracted RGB component values, so their on-screen colour can differ slightly from the print-managed source. The shape comparison accounts for this colour-management difference. Full numerical comparison results are in provenance.json.

## Colour and date qualifications

The recovered colour values are **#86A7AC** for the emblem/rule and **#163583** for the lettering, as stored in the 2025 PDF. These are not a claim about original Pantone specifications.

The magazine is a retrospective reproduction. Its placement beside the 1975 founding entry does not establish when this exact modern wordmark was introduced. The white full-logo layout is separately documented in the dated 2015 publication. The wordmark-only variant is documented in the 2017 report. NWCC became Coast Mountain College on 18 June 2018.

This is a recovery of historical institutional artwork, not a new logo design or an official editable master supplied by the college. Rights in the underlying artwork remain with their respective holders.
