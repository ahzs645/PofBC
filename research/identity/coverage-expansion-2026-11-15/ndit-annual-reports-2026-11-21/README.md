# Northern Development Initiative Trust: logos from three annual reports (21 November 2026)

Four assets added to `northern-development-initiative-trust` in `../assets-manifest.json`:

| Asset | From | What it is |
| --- | --- | --- |
| `ndit-annual-report-2006-northern-trust` (SVG) | 2006 Annual Report, cover (p. 1) | Northern Trust identity, full colour, all vector |
| `ndit-annual-report-2007-northern-trust` (PNG) | 2007 Annual Report, back cover (p. 48) | the same design in the 2007 colours; its symbol is a 47×47 px image in the PDF, so it is kept as a 600 dpi render |
| `ndit-annual-report-2024-horizontal` (SVG) | Annual Report 2024, cover (p. 1) | Northern Development identity, horizontal, white name |
| `ndit-annual-report-2024-stacked` (SVG) | Annual Report 2024, back cover (p. 49) | the stacked lockup; the website's one-colour logo is filed as its version |

## Sources

The reports were supplied as files and checked against public copies, byte for byte (SHA-256):

- 2006: `81de478a…c47048`, the trust's own upload `northerndevelopment.bc.ca/uploads/files/2006AnnualReport.pdf`, Internet Archive capture of 15 June 2017.
- 2007: `3c6ec7ef…46243a50`, `…/uploads/files/2007AnnualReport.pdf`, same capture date.
- 2024: `7a98f14f…dce3cf343`, `northerndevelopment.bc.ca/wp-content/uploads/2025/05/NDIT_2024-AR_Web.pdf`.

Each page an asset comes from is preserved as a one-page PDF in `public/identity-expanded/_sources/`.

## Method

The 2006 and 2024 symbols are PDF axial shadings inside vector clips, so the logos are wholly
vector. Each page was converted with Poppler (`pdftocairo -svg`), which writes shadings as SVG
gradients, and `cut_region.mjs` kept only the drawing inside the logo's area (in PDF points):
2006 p. 1 `395,270,560,360`; 2024 p. 1 `66,70,245,125`; 2024 p. 49 `250,500,360,575`. Nothing was
traced, retyped or recoloured; colours are as Poppler converts the PDF's colour spaces. The 2007
render is PyMuPDF at 600 dpi of `255,531,362,581` on p. 48, with a transparent ground.
