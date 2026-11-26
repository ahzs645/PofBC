# British Columbia airports and branding

Research snapshot dated November 25, 2026. The inventory covers the full BC Airports data layer. The branding registers prioritize land airports the Province labels certified, Masset, and selected community airfields, floatplane terminals and heliports.

## Facility inventory

| File | Coverage |
| --- | --- |
| [Provincial inventory](provincial-inventory.csv) | All 451 provincial records, including 198 land facilities, 121 water facilities, 131 helicopter facilities and one unclassified point. |
| [Supplemental leads](supplemental-leads.csv) | 135 OurAirports listings without an exact provincial location code match. Forty-one have a same-type provincial point within 1.5 km and need a name and facility check before inclusion. |

The provincial records use the layer’s `SEQUENCE_ID` as `bc_record_id`. Source names, classifications and codes are preserved with whitespace normalized. Use the four-letter ICAO or Transport Canada location identifier to connect to the branding records where present. Where the province put a four-letter ICAO code in its local-code field, such as `CYLW`, match across both columns. The provincial IATA field and supplementary IATA field are shown side by side. The base layer is published by GeoBC under the Open Government Licence – British Columbia. [Data catalogue](https://catalogue.data.gov.bc.ca/dataset/bc-airports), [GeoBC data query](https://openmaps.gov.bc.ca/geo/pub/WHSE_IMAGERY_AND_BASE_MAPS.GSR_AIRPORTS_SVW/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub%3AWHSE_IMAGERY_AND_BASE_MAPS.GSR_AIRPORTS_SVW&outputFormat=application%2Fjson), [Open Government Licence](https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc).

OurAirports contributes additional leads and IATA cross-references by exact match on published location identifiers. The supplement excludes entries that OurAirports explicitly labels closed. The nearest same-type point is a potential duplicate, and a blank nearest-point field can still require reconciliation. The provincial layer also includes private sites, aliases, operator docks and records sourced from older surveys. Directory and operating status require current operator or federal evidence. [OurAirports open data](https://ourairports.com/data/), [Field definitions](https://ourairports.com/help/data-dictionary.html), [NAV CANADA aeronautical publications](https://www.navcanada.ca/en/aeronautical-information.aspx).

### Names and status to carry into the gallery

- Use **K’il Kun Xidgwangs Daanaay Airport** as the current title for `CYZP`. Keep Sandspit Airport as an alias. [Joint renaming announcement](https://www.canada.ca/en/transport-canada/news/2024/03/the-council-of-the-haida-nation-and-the-minister-of-transport-announces-the-renaming-of-sandspit-airport-to-kil-kun-xidgwangs-daanaay.html).
- Treat 37 as the number of provincial *records* labelled certified for land airports. That count includes **Avey Field (69S)**, a cross-border facility near Laurier, Washington. The layer labels **Masset (CZMT)** registered, while an earlier provincial study lists it among certified airports. Confirm current regulatory status separately. [WSDOT airport listing](https://wsdot.wa.gov/travel/aviation/airports-list/avey-field), [Provincial aviation study, figure 2](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/reports-and-reference/reports-and-studies/air-and-rail/pwc-report-socio-economic-contribution-of-bcs-aviation-and-aerospace-sector.pdf#page=12).
- **Victoria Harbour Water Airport (CYWH)** is identified as certified by Transport Canada. The provincial layer says registered. Keep it distinct from the Victoria Harbour heliport and Victoria International Airport. [Transport Canada Port of Victoria](https://tc.canada.ca/en/marine-transportation/ports-harbours-anchorages/port-victoria).
- Keep **Bella Coola (CYBD)** linked by its ICAO code. The provincial row carries YBD in its IATA field. Pacific Coastal Airlines lists it as QBC. [Pacific Coastal Airlines destination page](https://flights.pacificcoastal.com/en/flights-to-bella-coola).

## Branding research

The two registers cover 87 facilities. Twelve have verified source vector artwork and 16 have verified standalone raster artwork. Two have a documented lead for a standalone mark, and two have branded website composites. For the other 55, the records describe shared, carrier or operator branding, a brand in development, or the sources checked for a separate mark.

- [Priority airport branding](branding-sources.json) records the primary publisher, evidence, file or page locator, artwork format and open leads for the priority airport group.
- [Community airports and terminals](community-branding-sources.json) records evidence for additional facilities, including standalone art for Atlin, Creston Valley, Dease Lake and Fairmont Hot Springs, native vectors for Fort Langley Airport and Vancouver Harbour Flight Centre, and the Courtenay Airpark roundel visible in a dated publication.

The most direct gallery candidates have a verified source vector or verified airport-specific raster. Strip-level points, terminals with shared branding, and marks belonging to district governments, operators or airlines can be documented with the linked facility evidence. An unreviewed row or an unresolved search gives no basis for concluding an airport lacks an identity.

When adding artwork, compare the source file to the documented logo treatment and check for native geometry in PDF and SVG sources. Keep dated layouts and documented colourways selectable. If a verified vector matches an already catalogued raster, preserve the design ID and set its `preferredVector`. Generate light and dark display copies with `scripts/build_collected_display.py` and verify the gallery card, details and downloads in both themes.

## Gallery and airport directory

The Airports view at `/dev/data?view=airports` includes the provincial inventory and the supplemental listings. The Airports section of the Logos gallery holds 34 collections. The 92 local artwork files include website originals, colourways, native PDF vector extractions, embedded bitmap extracts and source publication crops. The catalogue records each method and source. Kitimat Airpark and Vancouver Harbour Heliport are represented by clearly identified operator marks.

Courtenay Airpark uses the association’s archived 1831 × 1187 JPEG as the default artwork and retains the September 2024 *Totem Times* specimen as a selectable version. [Archived association JPEG](https://web.archive.org/web/20240122181055id_/https://courtenayairpark.com/resources/Pictures/Courtenay%20Airpark%20final%20logo%20JPG.jpg).

Kelowna uses the native vector from its 2024 financial statements as the default for the stacked colour signature. Pages 11 and 15 of the City’s archived 2025 guide supply twelve embedded bitmap specimens, including the horizontal and vertical layouts, matching black and reversed versions, and three wordmarks. [Archived City of Kelowna guide](https://web.archive.org/web/20250405012450id_/https://www.kelowna.ca/sites/files/1/docs/city-hall/brand/city_of_kelowna_visual_identity_guide_2025_v6.1.pdf).
