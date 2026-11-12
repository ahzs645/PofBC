# Railway logo history — 12 November 2026

This package expands the combined Pacific Great Eastern, British Columbia Railway and BC Rail
collection with **12 new logo specimens and four supporting context crops**. Together with two
previously collected PGE brochure specimens and the current BC Railway Company wordmark, the
gallery now holds **15 logo specimens across 13 design groups**. Twelve groups have artwork; the
BC Rail operating identity remains a documented group with an isolated master still sought.

The collection covers **1912–present, provincially owned from 1918**. These are company-history
dates. The earliest dated logo evidence identified here is a 1929 photograph. Equipment,
corporate-printing, passenger and advertising designs often overlapped, so the design groups do
not describe a succession of exclusive, company-wide identities.

## Package contents

| Record | Contents |
| --- | --- |
| [source-register.json](source-register.json) | Twelve accepted logo crops and four context crops, with source URLs, credits, page numbers, exact crop bounds, dimensions, processing notes and SHA-256 checksums |
| [history.json](history.json) | Thirteen design groups, 15 historical events, ten typed organizational connections and four supporting images |
| [sources.json](sources.json) | Nineteen source records with claim-level locators, cautions and further artwork leads |
| [Railway atlas events](../../atlas/events-railway-identity.json) | Twenty-one dated events, preserving the distinction between documented use, approximate introduction, legal events and public identity changes |
| [Cariboo crop review](cariboo-crop-review.jpg) | Contact sheet of the fourteen crops from the supplied issue: eleven logo reproductions and three context images |
| [Extraction script](../../../scripts/extract-railway-sources.py) | Reproduces and verifies all sixteen new PNGs from the three exact source files |

The new logo specimens comprise ten PGE illustrations from Greg M. Kennelly's article, one
British Columbia Railway dogwood masthead reproduction, and one archival photograph of the PGE
BC-map herald. The four context crops are the PGE dinner-plate landscape, two locomotive livery
diagrams, and a 1990 photograph showing the BC Rail graphic on locomotives. Context images are
kept outside the logo count.

Asset paths in the register are relative to `public/`. The files are under
`public/identity-collected/pacific-great-eastern-railway/` and
`public/identity-collected/bc-railway-company/`. The three previously held specimens keep their
existing identifiers and provenance; they are not newly extracted by this package's script.

## Source fidelity and attribution

The main source is [The Cariboo, Issue 3, January 1991][cariboo3], particularly Kennelly's
“Logos of the Pacific Great Eastern Railway” on PDF pages 5–8. The independently downloaded
public copy matches the user-supplied PDF's SHA-256 exactly. The issue's publication date,
historical dates discussed in the article, and this package's observation date are recorded
separately.

The magazine crops retain the printed paper background, scan texture and incidental marks.
PDF crops were rendered at 300 dpi from the available mixed-resolution scans. That rendering
resolution does not create detail absent from the source. Some illustrations were traced from
photographs by Kennelly before publication; those are identified as published reproductions.
This pass applied rectangular cropping only, with no new tracing, cleanup, recolouring,
sharpening, perspective correction or generated artwork.

The PGE map specimen comes from [Chuck Strawn's photograph of RCC2 at North Vancouver, circa
1970][pnra], Pacific Northwest Railroad Archive item
`US WaBuPNRA D0177A-010-014-001-005-Strawn0548`. Its equipment surface, rivets and perspective remain
visible. It is evidence of the herald in use, rather than isolated master artwork.

The BC Rail context photograph is credited to **John C. Benson / CRHA Archives, Fonds Bury,
BCR1-111**. Its caption dates the three new Dash 8-40CM locomotives at North Vancouver to
**21 July 1990**; the photograph was reproduced in [Canadian Rail 547][rail547], March–April 2012,
PDF page 28 / printed page 72. The crop preserves the complete photograph, while the caption's
date and credit remain in the register. Neither date establishes the graphic's introduction.

## Logo chronology

The table follows the design groups in `history.json`. Page references for *The Cariboo* use
one-based PDF page numbers, since the relevant article pages have no consistent typeset page
numbering.

| Documented period | Design group | Evidence and limits |
| --- | --- | --- |
| Documented by 1929 | Point Ellice diamond monogram | Kennelly identifies a photograph dated 19 September 1929 and reports use into the early 1950s. Don Davis is a recollected attribution, not a confirmed designer credit. [Cariboo 3][cariboo3], p. 5. |
| c. 1934; photographed 1935 | Square diamond equipment marks | Shaded and unshaded variants form one group. Around 1934 is the reported introduction; February 1935 photographs attest the shaded version. [Cariboo 3][cariboo3], pp. 5–6. |
| Attested 1935 | Circular script corporate monogram | The earliest pass seen by the author was dated 1935. That observation does not prove an introduction that year. No rolling-stock use was established. [Cariboo 3][cariboo3], p. 6. |
| From 1945; revised mid-1946 | Early caribou equipment herald | Reported on new locomotives in the second quarter of 1945. The early version was gradually phased out after revision; mid-1946 is not a confirmed end of use. [Cariboo 3][cariboo3], pp. 6–7. |
| From mid-1946 | Revised caribou equipment herald | The full-profile equipment design varied in size and detail. Kennelly traced the published example from a builder photograph of Mikado 163. [Cariboo 3][cariboo3], p. 8. |
| 30 September 1946–1948 | Corporate caribou with light lettering | The dated public timetable establishes the corporate-printing appearance, separately from equipment marks. [Cariboo 3][cariboo3], p. 7. |
| From 1947 | Roman lettering on passenger cars | The reported design introduction is 1947; the illustration records the preserved sleeper Clinton in 1973. Those dates describe different events. [Cariboo 3][cariboo3], p. 8. |
| 1948–1966 in corporate printing | Corporate caribou with bold lettering | The lettering change falls between 31 May and 26 September 1948. Front-cover replacement came on 7 June 1964; back-cover use continued until the map mark appeared on 19 January 1966. The existing colour brochure's printing year remains unverified. [Cariboo 3][cariboo3], p. 7. |
| From 1956 | Oval advertising caribou | Associated with the Howe Sound extension campaign and timetables 73C and 73L; the circular corporate mark returned by Timetable 75. The existing red brochure is a related specimen with an uncertain printing date. [Cariboo 3][cariboo3], p. 8. |
| Timetables from 1966; equipment c. 1970 | PGE and the map of British Columbia | The 19 January 1966 date applies to public timetables. The [PNRA photograph][pnra] documents equipment use circa 1970; neither establishes first use on every application. [Cariboo 3][cariboo3], p. 7. |
| New symbol documented 1972 | British Columbia Railway dogwood | A contemporary caption identifies the new symbol. The held artwork is a January 1991 newsletter masthead reproduction, which does not establish the date or continued railway use of that exact lockup. [Canadian Rail 248][rail248], pp. 18–19; [Cariboo 3][cariboo3], p. 1. |
| Name from 1984; graphic variants later | BC Rail operating identity — master sought | The public name is dated 19 June 1984. Later caboose research distinguishes white lettering in 1985 from red-and-blue heralds in 1986–1987 schemes. The 1990 context photo documents an application. [Canadian Rail 547][rail547], pp. 5, 28; [Cariboo 23][cariboo23], pp. 13, 15–16. |
| Current specimen; introduction undated | Continuing BC Railway Company | The existing specimen was collected from the [official website][bcrc-site] on 22 October 2026. Its design introduction date has not been established. |

Ed Aldridge won the 1945 competition with a landscape and motto. Kennelly cites a letter dated
15 June 1945 explaining the change to a caribou. The dinner-plate landscape is neither the
original submission nor an adopted logo; its connection to the unused idea is the author's
suggestion. The livery diagrams were reprinted from the June/July 1973 *Bulletin Board* and
remain context images, with their colour codes and credits recorded. These distinctions are
supported by [Cariboo 3][cariboo3], PDF pages 6 and 14.

## Company history and railway connections

The history panel keeps acquisitions, statutory continuity, subsidiary relationships, traffic
agreements and operating rights as distinct connection types.

| Date | Relationship or event | Source and interpretation |
| --- | --- | --- |
| 1907–1912 | Howe Sound, Pemberton Valley & Northern undertaking precedes PGE | The [1907 incorporation Act][howe-act] and [Whistler Museum account][whistler] support the predecessor connection and 1912 takeover. They do not establish a simple renaming of the same corporation. |
| 27 February 1912 | PGE incorporated; Grand Trunk Pacific junction and traffic agreement | The [incorporation Act][pge-act] and [agreement's Schedule B][gtp-agreement] establish the new company and intended connection. A conditional option to acquire control is not proof of an actual GTP subsidiary relationship. |
| 1918 | Province becomes sole owner | The [EAB corporate history][eab], PDF pp. 3–4, separates provincial ownership from the company's 1912 incorporation. |
| 1952 | PGE reaches Prince George | The [Central BC Railway and Forestry Museum][pgrfm] distinguishes PGE's route from the east–west GTP line, which arrived in 1914 and later formed part of CN. |
| 30 March / 1 April 1972 | Existing company renamed British Columbia Railway Company; public rollout follows | The [1972 Act][bcr-act] preserves corporate rights, liabilities and property. [Canadian Rail 248][rail248], PDF p. 5, dates the public name change to 1 April. |
| 31 October 1983 / 30 May 1985 | Harbours Board railway assets transfer; Board later dissolved | The [1985 Auditor General report][oag], PDF pp. 110–111 and 166, dates the asset transfers. [OIC 1061/1985][harbours-oic] supplies the distinct dissolution date. Other Board assets went to BC Development Corporation. |
| May–June 1984 | Operating and property subsidiaries organized | BCR Properties was incorporated on 18 May; S.C. Holdings became BC Rail Ltd. on 28 May; asset transfers followed on 12 June. The statutory parent continued. [EAB][eab], PDF pp. 3–4. |
| 19 June 1984 | BC Rail public name | [Canadian Rail 547][rail547], PDF p. 5 / printed p. 49, gives this date. [CIPO 0770811][cipo] is a later word-mark application claiming use from 18 May 1984; it does not date a graphic or palette. |
| 5 December 1997 | BCR Partnership created | [EAB][eab], PDF pp. 3–4, documents the group restructuring relevant to the later CN transaction. |
| 14 / 15 July 2004 | CN transaction closes; operational transition follows | The [government release][cn-close] dates closing to 14 July and identifies the BC Rail Ltd. shares and BCR Partnership units transferred. The [TSB account][tsb] uses 15 July for the system transition. BCRC continued to own the corridor and infrastructure. |
| 1 April 2010; status documented 31 March 2025 | BCRC becomes BCTFA subsidiary and continues holding railway and port interests | [BCTFA's financial statements][bctfa] date the ownership change. [BCRC's 2025 statements][bcrc-2025], PDF p. 9, record the infrastructure leased to CN, Port Subdivision and BCR Properties activities. |

The EAB decision's shorthand “Corporation” is not used as the 1972 legal name: the statute says
**Company**. The Auditor General URL's filename says 1984, but the document is the **1985** report.
The retained-assets account follows audited financial statements, since the centenary article
oversimplifies railway ownership after the CN transaction.

## Reproduce and verify the crops

Run from the repository root using Python with **PyMuPDF 1.26.6** and **Pillow 13.0.0**. Source
downloads are separate from extraction. The script rejects a changed input checksum before
rendering and compares every output's dimensions and SHA-256 against the register.

Download the three registered inputs into a temporary source directory:

```sh
python - <<'PY'
import json
import urllib.request
from pathlib import Path

register = json.loads(Path("research/identity/railway-history-2026-11-12/source-register.json").read_text())
source_dir = Path("/tmp/pofbc-railway-sources")
source_dir.mkdir(parents=True, exist_ok=True)
for source in register["inputs"].values():
    urllib.request.urlretrieve(source["url"], source_dir / source["filename"])
PY

python scripts/extract-railway-sources.py \
  --cariboo '/tmp/pofbc-railway-sources/Cariboo - Issue 3.pdf' \
  --pnra-image /tmp/pofbc-railway-sources/Strawn0548.jpg \
  --canadian-rail /tmp/pofbc-railway-sources/canadian-rail-547-2012.pdf \
  --check
```

`--check` renders in memory and checks the existing files under `public/` without writing them.
To reproduce into a separate directory, replace `--check` with
`--output-root /tmp/pofbc-railway-replay`. Omitting both options writes the registered paths under
`public/`. Changes to a publisher's source file or renderer output should be investigated rather
than bypassing the checksum gate.

| Input | SHA-256 |
| --- | --- |
| Cariboo Issue 3 | `c56778844ec827227151df1183bfeb9148bf01fe4d590ccd400302a8525f2b23` |
| PNRA Strawn0548 | `655fa53e9e5533701df1c0f736a9ac583b90f8285d5f28db21fd8caa430b61cf` |
| Canadian Rail 547 | `533cec28d5f15d68cef67c466cce91525a4047498f4b346b152da1b9950d1a88` |

PDF crop boxes are in page points, with one-based page numbers and 300-dpi rendering. The PNRA
box is in original image pixels. All bounds are stored in the register. After an intentional
source-data change, regenerate the collected gallery data with:

```sh
node scripts/build-collected-marks.mjs
```

## Validation and remaining work

The extraction check passed for all **16 crops**, including source hashes, crop dimensions and
output hashes. The resumed implementation pass also passed **90 focused tests** across five gallery test
files and the government atlas, lifecycle and lineage test files. A production bundle of the
actual `GalleryView` built through a temporary Vite preview entry using the repository's supported
TeX Gyre Heros font fallback. That check was limited to the gallery entry, not the full application.

Browser inspection was **not completed**: the executable Chromium attempt failed with a socket
`EPERM`, and the Cloud Browser could not connect to the local preview at `127.0.0.1`. The resumed
connected Chrome attempt also returned `ERR_CONNECTION_REFUSED` for the preview. No browser
layout or interaction pass is claimed here. An independent code review checked the preserved
gallery links, fragment navigation and atlas changes; it found no publication-blocking defect.

The main artwork gap is a verified, isolated BC Rail operating graphic. [Cariboo 23][cariboo23]
provides useful 1985–1987 caboose evidence, but its reproduced diagrams do not establish the first
company-wide use of the familiar red-and-blue graphic or supply a company master. The 1990
photograph remains supporting evidence. Earlier creation dates, most retirement dates, the
confirmation of the Don Davis attribution, the two brochure printing dates,
and the introduction date of the continuing company's current wordmark remain unresolved.

[cariboo3]: https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%203.pdf
[cariboo23]: https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%2023.pdf
[rail248]: https://exporail.org/canrail/canadian_rail_1962_1989/canadian-rail-248-1972.pdf
[rail547]: https://exporail.org/canrail/canadian_rail_1990_plus/canadian-rail-547-2012.pdf
[pnra]: https://atom.pnrarchive.org/index.php/pacific-great-eastern-railway-pge-remote-control-car-rcc2-pge-logo-detail-at-north-vancouver-british-columbia-circa-1970
[bcrc-site]: https://bcrco.com/
[howe-act]: https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstatspsl/1179256101
[whistler]: https://whistlermuseum.org/2019/11/19/the-beginnings-of-the-pacific-great-eastern-railway/
[pge-act]: https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/2046733804
[gtp-agreement]: https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1494461056
[eab]: https://www.bceab.ca/app/uploads/sites/717/2020/04/2000was018b.pdf
[pgrfm]: https://pgrfm.bc.ca/about-us/history/
[bcr-act]: https://free.bcpublications.ca/civix/document/id/hstats/hstats/980097910
[oag]: https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19840301-report-auditor-general-1984.pdf
[harbours-oic]: https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1061_1985
[cipo]: https://ised-isde.canada.ca/cipo/trademark-search/770811
[cn-close]: https://archive.news.gov.bc.ca/releases/archive/2001-2005/2004tran0051-000631.htm
[tsb]: https://tsb.gc.ca/eng/rapports-reports/rail/2005/r05v0141/r05v0141.html
[bctfa]: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2020-21/sup-e/bc-transportation-financing-authority-fs-2020-21.pdf
[bcrc-2025]: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/bc-railway-company-fs-2024-25.pdf
