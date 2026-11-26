# Department of Recreation and Conservation, 1970–1973

The production SVGs of a reconstruction package of the department's identity, as supplied
(21 November 2026): 176 files in twelve folders, every one outlined vector with no live text,
embedded image or font dependency. The package's README, manifest, notes, construction scripts and
review sheets are in
[`research/identity/recreation-conservation-2026-11-21/`](../../research/identity/recreation-conservation-2026-11-21/README.md).

| Folder | Files | What |
|---|---:|---|
| `symbols/` | 25 | The five square symbols — department, Fish and Wildlife, Provincial Parks, Provincial Museum, Commercial Fisheries — each in black, the reports' dark and pale greens, white, and reversed on the reports' dark field |
| `related_emblems/` | 4 | The 1970 dogwood oval, the 1973 Fish and Wildlife emblem and its name panel, the 1973 Parks dogwood shield |
| `report_dividers/` | 10 | The annual reports' section dividers, 1971/1972 and 1973 generations |
| `branch_lockups/` | 5 | The divider bands for each branch, on their own |
| `cover_headers/`, `cover_stacks/` | 5 | The 1971–1973 cover blocks (photograph area left out) and back-cover symbol stacks |
| `wordmarks/` | 15 | Report lettering, outlined from Corporatus comparison outlines |
| `handbook_emblems/`, `handbook_labels/`, `handbook_templates/` | 89 | The Provincial Museum handbook series: subject emblems, outlined titles and numbers, and branding panels with open illustration fields |
| `park_symbols/` | 22 | The 1971 report's sheet of **proposed** park symbols; the proposal is not evidence they were adopted or installed |
| `supporting_arms/` | 1 | A period coat of arms used by the cover blocks |

**Used by the site:** the 20 square-symbol files in black, green, pale and white, the 1973 emblems,
and the green-and-cream dogwood oval are packaged by `npm run build:crown-marks` into `src/assets/crownMarks.js` and
shown in the gallery's **Recreation and Conservation** collection; the Parks spirals and shield are
also the first two eras of **BC Parks**, and the Provincial Museum's square the first of the **Royal
BC Museum**. The Fisheries symbol draws its three fish with `<use>`, which the build writes out in
full. The 22 `park_symbols/` are composed by `npm run build:park-symbols-sign` into
`src/signs/parks/proposed-park-symbols.svg`, the **Signs** view's *Proposed park symbols, 1971*,
four to a row as the report prints them. The `*_reverse.svg` files, with their dark field, and the
other folders are kept here as reference and are not shown.

The gallery’s 1970 dogwood oval uses the [supplied green-and-cream SVG](../../public/identity-recreation-conservation/drc-dogwood-oval-1970.svg).
The dogwood and letter outlines were drawn and fitted to the [supplied image](../../research/identity/recreation-conservation-2026-11-21/sources/related_emblems/oval_department_green_cream_reference.webp).
The SVG completes the cropped lower edge with a fitted ellipse. The historical typeface and the provenance of the green-and-cream image remain unverified.
The Department of Recreation and Conservation’s [1970 annual report, PDF page 10](https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1970.pdf#page=10) shows the badge in a monochrome page scan.

The Fish and Wildlife oval uses the supplied [black master](../../public/identity-recreation-conservation/drc-fw-oval-1973.svg),
copied from `artwork/FW_Master.svg` in the `FW_Vector_Reconstruction 2` package. The selectable
[white](../../public/identity-recreation-conservation/drc-fw-oval-1973-white.svg) and
[cream-on-orange](../../public/identity-recreation-conservation/drc-fw-oval-1973-orange.svg) versions
come from `FW_Emblem_White.svg` and `FW_Orange_Application.svg` in the same folder. The three files
share identical Bézier contours, including the transparent bear-eye opening. The orange is sampled
from the supplied reference and the cream is the reconstruction package’s presentation colour.
The Department of Recreation and Conservation’s [1973 annual report, PDF page 22](https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf#page=22)
documents the emblem in print. The production artwork for the insignia mentioned in the
department’s [1972 annual report](https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1972.pdf#page=57) remains an open lead.

The [paired lockup](../../public/identity-recreation-conservation/drc-fw-lockup-1973.svg) is assembled by
`npm run build:crown-marks`. It uses the same master at the height of the original left panel and
keeps the right-hand name panel’s outlines from the archived paired reconstruction.

The reconstructed SVGs were redrawn from scans of the printed reports and photographed handbooks.
Their colours approximate the scans. No designer or identity manual has
been found. They imply no affiliation with or rights in the historical designs.
