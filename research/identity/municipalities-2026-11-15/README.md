# Municipal registry and gallery reconciliation (15 November 2026 audit)

`audit-report.md` and `audit-workbook.xlsx` are the gallery and municipal identity audit as
delivered, pinned to commit `8f95bd67`. `municipalities.json` is the registry the site reads
(`src/gallery/municipalSubjects.js`), extracted from the workbook's Municipalities and Source leads
sheets.

## What the registry holds

- **162 identities**: the 161 municipalities in the Province's
  [legally defined administrative areas layer](https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/3),
  joined to [CivicInfo BC's directory](https://www.civicinfo.bc.ca/municipalities), plus
  shíshálh Nation Government District, which is not in that layer and is kept separate from the
  District of Sechelt.
- Okanagan Falls (incorporated 6 November 2026, per the audit's Gazette citation) is current; its
  corporate logo is unestablished. Jumbo Glacier (dissolved 2021) is under `historical` only.
- Both Langleys and both North Vancouvers are separate records. Earlier names (Queen Charlotte,
  Fort Nelson, Sechelt Indian Government District) are searchable aliases, not separate subjects.
- **24 logo source leads** (4 inspected SVGs, 19 inspected rasters, Kitimat's guide lead).

## Collected logos (16 November 2026)

`assets-manifest.json` records 23 files for 21 municipalities, each downloaded on 16 November 2026
from the URL the audit located and archived byte-for-byte in `public/identity-municipal/`. For all
20 files the audit had checksummed, the bytes matched. Two further files are variants the audit
listed alongside: Quesnel's compact mobile logo and Vanderhoof's full-colour logo (the audit's
Vanderhoof file is the white header version). Dawson Creek's and Smithers' files are large rasters;
each has a resized `-preview.png` for the page, and the original stays the evidence.
`scripts/build-identity-expansion.mjs` verifies every checksum and the SVG safety rules, and
generates `src/gallery/municipalIdentityData.js`.

Not collected:

- **Vancouver** and **Kelowna**: the files returned a Cloudflare challenge page (HTTP 403) to
  this download; they remain source leads.
- **Kitimat**: only a brand-guide lead in a council agenda; the audit advises finding the final
  adopted guide first.

The observation date is not an adoption date. White versions (Coquitlam, Smithers, Surrey,
Vanderhoof's header version, and Kamloops' tagline) are shown on a dark ground.

## Checks made on import

Every link was checked against this repository's own data, and the tests keep checking it
(`src/gallery/municipalSubjects.test.js`):

| Link | Count | Checked against |
|---|---:|---|
| Salary employer slugs | 119 | `public/salaries/employers/index.json` |
| Council-pay labels | 160 | `public/salaries/council-pay.json` (6 spelled differently there, e.g. "Langley City", "Fort Nelson/N. Rockies", mapped explicitly) |
| Arms registrations | 72 on 59 municipalities | `research/identity/arms-register-2026-11-16/register.json` (3 granted to predecessors: District of Abbotsford, District of Matsqui, Town of Kinnaird) |

The provincial identifiers, CivicInfo matches and the Okanagan Falls incorporation were not
re-fetched here; they are as the audit recorded them.

## The gallery reconciliation

The audit found 53 of 291 gallery entries with no register subject. `src/gallery/reconciledSubjects.js`
adds an owner for each (WorkSafeBC, BC Parks, BC Timber Sales, JIBC, BC OnLine, Shared Services BC,
BC Cancer Foundation, and the program brands on the BC mark), and gives the 18 entries that had no
owner at all an explicit one. The coverage test now requires every held entry to have an owner.
