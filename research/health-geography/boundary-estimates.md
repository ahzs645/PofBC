# Historical BC health boundaries: working estimates

Reviewed 2026-10-31. All 52 administrative labels have a working geometry and a separate source-drawing approximation. The twenty statistical regions have modern-LHA illustrations. None is a verified historical legal polygon.

## Other boundaries that help

Screening uses 89 current local health areas, 16 service delivery areas, 5 health authorities, 28 regional districts, 160 municipalities and 59 geographic school districts. Each score compares an independently traced historical drawing with a current feature. It does not compare a selected proxy with itself.

School districts have useful resemblance to several councils, including Arrow Lakes, Boundary, Quesnel, Sea to Sky, South Peace, Fort Nelson and Bulkley Valley. This supports further edge review; it does not establish unchanged historical school-district or health boundaries.

## What defines the territories

Original B.C. Reg. 293/2001 Schedule B supplies written descriptions for 11 boards and 33 councils. These use watershed divides, rivers, shorelines, cadastral district lots, survey plans, latitude/longitude and dated municipal boundaries. They postdate the 1997/98 map and require reconciliation with original orders and intervening amendments. M87/1997 is a partial amendment, not a complete schedule for all councils.

M191/1997 contains the related Nisga’a council definition. Its identity with the map’s differently labelled authority remains unresolved. The seven societies still need operative service-area agreements and schedules.

## Method and limits

The three main maps use the existing three-control BC Albers affine registration. Council polygons are extracted from gray fill boundaries and thin black linework, excluding text. Rasterization is 12 pixels per PDF point, with a 3-pixel local gap closure. Source-space seeds separate all 34 labels; a few coastal island components use explicit extra paths/seeds. No modern internal administrative edge is used to extract these source polygons. Comparisons use the full source footprint, without modern-land clipping. Only the four source-drawn best estimates are clipped for land display. Marine jurisdiction is not reconstructed.

Vancouver/Richmond correction: the earlier 29% comparison is withdrawn. Richmond main-map drawing 76 was omitted and incorrectly assigned to South Fraser. The corrected trace includes 76 and 193; South Fraser uses 198. The inset labels both Vancouver and Richmond with 9. A 5 km northward local display alignment is now applied to this trace following user review. The original global registration and source trace are retained. This is a provisional display choice; independent coastal controls and inset registration remain necessary.

Working choices use 28 single modern LHAs, 20 modern combinations and four source-drawn estimates. Snow Country is additionally capped at the independently documented 57th parallel, densified before projection. Insets and fine offshore details remain unresolved. Mixed-source estimates can overlap; they are not an exclusive certified partition. Three fitting controls do not provide independent registration accuracy. Scores are cartographic similarity, not legal verification.

## Source provenance

- [reg293-2001.html](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001)
- [m0087_1997.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0087_1997)
- [m0444_1996.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0444_1996)
- [m0432_1996.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0432_1996)
- [m0441_1996.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0441_1996)
- [lha-metadata.json](https://catalogue.data.gov.bc.ca/api/3/action/package_show?id=local-health-area-boundaries)
- [pgmaps-boundaries.json](https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/index.json)
- [pgmaps-regional-districts.geojson](https://pgmaps.ahmadjalil.com/data/boundaries/BC/regional_districts.geojson)
- [pgmaps-municipalities.geojson](https://pgmaps.ahmadjalil.com/data/boundaries/BC/municipalities.geojson)
- [m0191_1997.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0191_1997)
- [m0052_1997.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0052_1997)
- [m0062_1997.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0062_1997)
- [m0072_1997.pdf](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0072_1997)
- [official-school-districts.geojson](https://openmaps.gov.bc.ca/geo/pub/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub%3AWHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW&outputFormat=application%2Fjson&srsName=EPSG%3A4326)
- Current regionalDistricts: https://pgmaps.ahmadjalil.com/data/boundaries/BC/regional_districts.geojson; normalized snapshot SHA-256 `c6c675899aa1795ccc80ab70283e9542ba95a60f2e1cc78741afbfb78e463482`.
- Current municipalities: https://pgmaps.ahmadjalil.com/data/boundaries/BC/municipalities.geojson; normalized snapshot SHA-256 `c5af148e209892b9ddfde9a7281f7cc7f05b2993499a3ce5d5a4904b7cdbdb69`.
- Current schoolDistricts: https://openmaps.gov.bc.ca/geo/pub/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub%3AWHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW&outputFormat=application%2Fjson&srsName=EPSG%3A4326; normalized snapshot SHA-256 `599068a7634aeed69fd0b4a8d11453c1cf8a067fa00083004c6a4f6132054de9`.

## Area-by-area choices

### North Okanagan · boards 1

ID: `north-okanagan-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The North Okanagan candidate combines Armstrong/Spallumcheen, Vernon, Enderby, Revelstoke and Salmon Arm. It spans today's Okanagan and Thompson Cariboo Shuswap HSDAs; either modern HSDA alone is the wrong extent.

Modern comparison LHA codes: 135, 136, 139, 141, 142.

Independent source drawing / modern combination overlap: 89.3% intersection over union.

Written record: [North Okanagan Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Upper Arrow Lake; Pingston Creek; Whatshan River; Wauchope Creek; Lower Arrow Lake; Kettle River; Harris Creek; Duteau Creek; Kalamalka Lake; Okanagan Lake.

- Closest individual lha: Revelstoke (141); 40.6% drawing IoU.
- Closest individual hsda: Okanagan (13); 22.7% drawing IoU.
- Closest individual ha: Interior (1); 9.6% drawing IoU.
- Closest individual regionalDistricts: Regional District of North Okanagan (RDNO); 36.0% drawing IoU.
- Closest individual municipalities: The Corporation of the Township of Spallumcheen (240); 1.2% drawing IoU.
- Closest individual schoolDistricts: Revelstoke (19); 40.7% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Okanagan Similkameen · boards 2

ID: `okanagan-similkameen-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The candidate uses Southern Okanagan, Penticton, Keremeos, Princeton, Central Okanagan and Summerland. Today's Okanagan HSDA also includes northern areas that belonged to the separate North Okanagan board.

Modern comparison LHA codes: 131, 132, 133, 134, 137, 138.

Independent source drawing / modern combination overlap: 93.1% intersection over union.

Written record: [Okanagan Similkameen Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kettle River; Harris Creek; Duteau Creek; Kalamalka Lake; Okanagan Lake; Trout Creek; Siwash Creek; Dillard Creek; Similkameen River.

- Closest individual lha: Princeton (134); 33.4% drawing IoU.
- Closest individual hsda: Okanagan (13); 60.5% drawing IoU.
- Closest individual ha: Interior (1); 6.2% drawing IoU.
- Closest individual regionalDistricts: Regional District of Okanagan-Similkameen (RDOS); 73.2% drawing IoU.
- Closest individual municipalities: City of Kelowna (83); 1.9% drawing IoU.
- Closest individual schoolDistricts: Okanagan-Similkameen (53); 26.4% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Thompson · boards 3

ID: `thompson-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The candidate uses Kamloops, North Thompson, Lillooet, South Cariboo LHA 148 and Merritt. The current Thompson Cariboo Shuswap HSDA includes additional Cariboo and Shuswap areas. Historical South Cariboo council around 100 Mile House is a different area.

Modern comparison LHA codes: 143, 145, 147, 148, 149.

Independent source drawing / modern combination overlap: 93.1% intersection over union.

Written record: [Thompson Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Columbia River; Perry River; Craigellachie Creek; Anstey Arm; Shuswap Lake; Okanagan Lake; Trout Creek; Siwash Creek; Dillard Creek; Coldwater River.

- Closest individual lha: Kamloops (143); 29.7% drawing IoU.
- Closest individual hsda: Thompson Cariboo Shuswap (14); 42.3% drawing IoU.
- Closest individual ha: Interior (1); 23.8% drawing IoU.
- Closest individual regionalDistricts: Thompson-Nicola Regional District (TNRD); 73.0% drawing IoU.
- Closest individual municipalities: District of Logan Lake (156); 0.6% drawing IoU.
- Closest individual schoolDistricts: Kamloops-Thompson (73); 48.3% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Fraser Valley · boards 4

ID: `fraser-valley-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Fraser East is a strong comparison candidate: Statistics Canada explicitly equates January 2000 Fraser Valley with June 2002 Fraser Valley. This dated statistical correspondence still requires checking against the 1997 legal board boundary and modern changes.

Modern comparison LHA codes: 211, 212, 213, 214, 215.

Independent source drawing / modern combination overlap: 87.8% intersection over union.

Written record: [Fraser Valley Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Similkameen River; Coldwater River; Anderson River; Ainslie Creek; Fraser River; Nahatlatch River; Lillooet River; Billygoat Creek; Stave River.

- Closest individual lha: Hope (211); 36.5% drawing IoU.
- Closest individual hsda: Fraser East (21); 87.8% drawing IoU.
- Closest individual ha: Fraser (2); 73.1% drawing IoU.
- Closest individual regionalDistricts: Fraser Valley Regional District (FVRD); 82.1% drawing IoU.
- Closest individual municipalities: City of Abbotsford (90); 2.5% drawing IoU.
- Closest individual schoolDistricts: Fraser-Cascade (78); 64.6% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### South Fraser · boards 5

ID: `south-fraser-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Fraser South is a strong comparison candidate supported by the January 2000-to-June 2002 statistical correspondence. Modern Surrey subdivisions do not establish unchanged historical board edges.

Modern comparison LHA codes: 231, 232, 233, 234.

Independent source drawing / modern combination overlap: 46.1% intersection over union.

Written record: [South Fraser Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through rivers, lakes and shorelines, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Fraser River.

- Closest individual lha: Langley (231); 20.8% drawing IoU.
- Closest individual hsda: Fraser South (23); 46.1% drawing IoU.
- Closest individual ha: Fraser (2); 3.2% drawing IoU.
- Closest individual regionalDistricts: Metro Vancouver Regional District (MVRD); 15.0% drawing IoU.
- Closest individual municipalities: City of Surrey (119); 27.6% drawing IoU.
- Closest individual schoolDistricts: Surrey (36); 28.9% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Simon Fraser · boards 6

ID: `simon-fraser-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The candidate combines Burnaby, New Westminster, Maple Ridge/Pitt Meadows and Tri-Cities. The 1997 board combined former Simon Fraser and Burnaby areas; Statistics Canada also documents this merged correspondence to the 2002 Simon Fraser HSDA.

Modern comparison LHA codes: 221, 222, 223, 224.

Independent source drawing / modern combination overlap: 75.1% intersection over union.

Written record: [Simon Fraser Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Fraser River; Stave River; Pitt River; Indian River; Burrard Inlet.

- Closest individual lha: Maple Ridge/Pitt Meadows (223); 45.6% drawing IoU.
- Closest individual hsda: Fraser North (22); 75.2% drawing IoU.
- Closest individual ha: Fraser (2); 13.7% drawing IoU.
- Closest individual regionalDistricts: Metro Vancouver Regional District (MVRD); 28.1% drawing IoU.
- Closest individual municipalities: City of Maple Ridge (112); 11.2% drawing IoU.
- Closest individual schoolDistricts: Maple-Ridge Pitt-Meadows (42); 46.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Central Vancouver Island · boards 7

ID: `central-vancouver-island-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Today's Central Vancouver Island HSDA is a useful geographic candidate, supported by its constituent place names. Its matching name is not proof that its legal edge equals the 1997 board; later Vancouver Island health boundaries changed.

Modern comparison LHA codes: 421, 422, 423, 424, 425, 426.

Independent source drawing / modern combination overlap: 70.7% intersection over union.

Written record: [Central Vancouver Island Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Finlayson Arm; Juan de Fuca Strait; Muchalat Inlet; Moyeha River; Ash River; Cruickshank River; Deep Bay; Baynes Sound; Sabine Channel; Malaspina Strait.

- Closest individual lha: Alberni/Clayoquot (426); 41.5% drawing IoU.
- Closest individual hsda: Central Vancouver Island (42); 70.7% drawing IoU.
- Closest individual ha: Vancouver Island (4); 18.7% drawing IoU.
- Closest individual regionalDistricts: Regional District of Alberni-Clayoquot (RDAC); 45.5% drawing IoU.
- Closest individual municipalities: The Corporation of the District of North Cowichan (291); 0.7% drawing IoU.
- Closest individual schoolDistricts: Pacific Rim (70); 45.5% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Northern Interior · boards 8

ID: `northern-interior-regional-health-board`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Use Burns Lake, Nechako and Prince George as the candidate. Do not automatically use all of current Northern Interior HSDA 52: it also includes Quesnel, which was in the separate Cariboo area and had its own council.

Modern comparison LHA codes: 522, 523, 524.

Independent source drawing / modern combination overlap: 92.4% intersection over union.

Written record: [Northern Interior Regional Health Board Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Fraser River; Euchiniko River; Sakumtha River; Tahtsa Lake; Nanika River; Morice River; Buck Creek; McKilligan Creek; Bulkley River; Babine River.

- Closest individual lha: Prince George (524); 48.5% drawing IoU.
- Closest individual hsda: Northern Interior (52); 80.9% drawing IoU.
- Closest individual ha: Northern (5); 23.5% drawing IoU.
- Closest individual regionalDistricts: Regional District of Bulkley-Nechako (RDBN); 43.4% drawing IoU.
- Closest individual municipalities: City of Prince George (38); 0.2% drawing IoU.
- Closest individual schoolDistricts: Nechako Lakes (91); 43.6% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Vancouver/Richmond · boards 9

ID: `vancouver-richmond-health-board`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The candidate combines today's Vancouver and Richmond HSDAs. The historical institution amalgamated the predecessor Vancouver and Richmond regional health boards. Vancouver and Richmond remained separate labels in the 20-region statistical presentation. The 1996 legal schedule also incorporates specified electoral areas, so municipal names alone do not certify an exact match.

Modern comparison LHA codes: 311, 321, 322, 323, 324, 325, 326.

Independent source drawing / modern combination overlap: 40.6% intersection over union.

Written record: [Vancouver/Richmond Health Board Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through township/section survey grid, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

- Closest individual lha: Richmond (311); 45.0% drawing IoU.
- Closest individual hsda: Richmond (31); 45.0% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 0.3% drawing IoU.
- Closest individual regionalDistricts: Metro Vancouver Regional District (MVRD); 5.1% drawing IoU.
- Closest individual municipalities: City of Richmond (118); 43.6% drawing IoU.
- Closest individual schoolDistricts: Richmond (38); 28.7% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### North Shore · boards 10

ID: `north-shore-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

North Vancouver and West Vancouver/Bowen Island form the modern candidate. Today's North Shore/Coast Garibaldi HSDA is broader. The dated statistical correspondence combines North Shore with Coast Garibaldi; it does not independently validate LHA 331 and LHA 332 as the historical board boundary.

Modern comparison LHA codes: 331, 332.

Independent source drawing / modern combination overlap: 49.9% intersection over union.

Written record: [North Shore Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through rivers, lakes and shorelines, cadastral district lots, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Queen Charlotte Channel; Indian River; Burrard Inlet; Collingwood Channel.

- Closest individual lha: North Vancouver (331); 38.9% drawing IoU.
- Closest individual hsda: Vancouver (32); 6.0% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 0.9% drawing IoU.
- Closest individual regionalDistricts: Metro Vancouver Regional District (MVRD); 15.9% drawing IoU.
- Closest individual municipalities: The Corporation of the District of North Vancouver (125); 24.9% drawing IoU.
- Closest individual schoolDistricts: North Vancouver (44); 39.4% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Capital · boards 11

ID: `capital-health-region`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

South Vancouver Island's Greater Victoria, Western Communities, Saanich Peninsula and Southern Gulf Islands provide the candidate. The legal 1996 schedule remains the authority for the historical edge.

Modern comparison LHA codes: 411, 412, 413, 414.

Independent source drawing / modern combination overlap: 42.6% intersection over union.

Written record: [Capital Health Region](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Finlayson Arm; Juan de Fuca Strait; Houstoun Passage; Stuart Channel; Saanich Inlet.

- Closest individual lha: Western Communities (412); 48.3% drawing IoU.
- Closest individual hsda: South Vancouver Island (41); 42.6% drawing IoU.
- Closest individual ha: Vancouver Island (4); 2.3% drawing IoU.
- Closest individual regionalDistricts: Capital Regional District (CAPRD); 39.9% drawing IoU.
- Closest individual municipalities: District of Metchosin (263); 3.6% drawing IoU.
- Closest individual schoolDistricts: Sooke (62); 60.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Elk Valley and South Country · councils 1

ID: `elk-valley-and-south-country-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Fernie is a place-based candidate for Elk Valley and South Country; the current LHA label does not reproduce the historic legal description.

Modern comparison LHA codes: 111.

Independent source drawing / modern combination overlap: 92.3% intersection over union.

Written record: [Elk Valley and South Country Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Gold Creek; Little Sand Creek; Elk River.

- Closest individual lha: Fernie (111); 92.3% drawing IoU.
- Closest individual hsda: East Kootenay (11); 17.0% drawing IoU.
- Closest individual ha: Interior (1); 3.6% drawing IoU.
- Closest individual regionalDistricts: Regional District of East Kootenay (RDEK); 27.5% drawing IoU.
- Closest individual municipalities: District of Sparwood (214); 2.5% drawing IoU.
- Closest individual schoolDistricts: South East Kootenay (5); 60.7% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Cranbrook · councils 2

ID: `cranbrook-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Cranbrook is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 112.

Independent source drawing / modern combination overlap: 87.6% intersection over union.

Written record: [Cranbrook Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Gold Creek; Little Sand Creek; Bull River; Wild Horse River; Kootenay River; Perry Creek; Moyie River.

- Closest individual lha: Cranbrook (112); 87.6% drawing IoU.
- Closest individual hsda: East Kootenay (11); 9.4% drawing IoU.
- Closest individual ha: Interior (1); 2.0% drawing IoU.
- Closest individual regionalDistricts: Regional District of East Kootenay (RDEK); 14.8% drawing IoU.
- Closest individual municipalities: The Corporation of the City of Cranbrook (207); 0.7% drawing IoU.
- Closest individual schoolDistricts: South East Kootenay (5); 32.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Kimberley · councils 3

ID: `kimberley-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Kimberley is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 113.

Independent source drawing / modern combination overlap: 90.6% intersection over union.

Written record: [Kimberley Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kootenay River; Wild Horse River; Bull River; White River; Lussier River; Sandown Creek; Findlay Creek; Perry Creek.

- Closest individual lha: Kimberley (113); 90.6% drawing IoU.
- Closest individual hsda: East Kootenay (11); 9.3% drawing IoU.
- Closest individual ha: Interior (1); 1.9% drawing IoU.
- Closest individual regionalDistricts: Regional District of East Kootenay (RDEK); 14.8% drawing IoU.
- Closest individual municipalities: City of Kimberley (212); 1.5% drawing IoU.
- Closest individual schoolDistricts: Rocky Mountain (6); 14.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Columbia Valley · councils 4

ID: `columbia-valley-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Windermere is the modern LHA covering the Columbia Valley candidate; the differing name is preserved.

Modern comparison LHA codes: 114.

Independent source drawing / modern combination overlap: 94.6% intersection over union.

Written record: [Columbia Valley Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kootenay River; Bugaboo Creek; Duncan River; Findlay Creek; Sandown Creek; Lussier River; White River.

- Closest individual lha: Windermere (114); 94.6% drawing IoU.
- Closest individual hsda: East Kootenay (11); 23.7% drawing IoU.
- Closest individual ha: Interior (1); 5.0% drawing IoU.
- Closest individual regionalDistricts: Regional District of East Kootenay (RDEK); 38.2% drawing IoU.
- Closest individual municipalities: Village of Canal Flats (206); 0.1% drawing IoU.
- Closest individual schoolDistricts: Rocky Mountain (6); 37.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Creston and District · councils 5

ID: `creston-and-district-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Creston is the direct place-name candidate; district-level extent is not certified.

Modern comparison LHA codes: 115.

Independent source drawing / modern combination overlap: 84.9% intersection over union.

Written record: [Creston and District Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kootenay Lake; La France Creek; Moyie River.

- Closest individual lha: Creston (115); 84.9% drawing IoU.
- Closest individual hsda: East Kootenay (11); 7.4% drawing IoU.
- Closest individual ha: Interior (1); 1.6% drawing IoU.
- Closest individual regionalDistricts: Regional District of Central Kootenay (RDCK); 14.5% drawing IoU.
- Closest individual municipalities: Town of Creston (178); 0.2% drawing IoU.
- Closest individual schoolDistricts: Kootenay Lake (8); 22.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Nelson and Area · councils 6

ID: `nelson-and-area-health-council`. Choice: **modern-combination**, low confidence in display approximation. Historical legal boundary unverified.

Nelson plus Kootenay Lake is a candidate for Nelson and Area; the inclusion of all Kootenay Lake needs checking against the legal schedule.

Modern comparison LHA codes: 121, 122.

Independent source drawing / modern combination overlap: 90.1% intersection over union.

Written record: [Nelson and Area Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kootenay Lake; La France Creek; Duncan River; Healy Creek; Trout Lake; Mobbs Creek; Lardeau River; Slocan Lake; Enterprise Creek; Brahms Creek.

- Closest individual lha: Kootenay Lake (121); 52.2% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 37.4% drawing IoU.
- Closest individual ha: Interior (1); 5.1% drawing IoU.
- Closest individual regionalDistricts: Regional District of Central Kootenay (RDCK); 47.1% drawing IoU.
- Closest individual municipalities: The Corporation of the City of Nelson (174); 0.1% drawing IoU.
- Closest individual schoolDistricts: Kootenay Lake (8); 70.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Castlegar and District · councils 7

ID: `castlegar-and-district-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Castlegar is the direct place-name candidate; district-level extent is not certified.

Modern comparison LHA codes: 123.

Independent source drawing / modern combination overlap: 78.9% intersection over union.

Written record: [Castlegar and District Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Lower Arrow Lake; Johnston Creek; Worthington Creek; Octopus Creek; Norns Creek; Slocan River; Kootenay River; Columbia River.

- Closest individual lha: Castlegar (123); 78.9% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 6.3% drawing IoU.
- Closest individual ha: Interior (1); 0.9% drawing IoU.
- Closest individual regionalDistricts: Regional District of Central Kootenay (RDCK); 7.1% drawing IoU.
- Closest individual municipalities: City of Castlegar (182); 1.2% drawing IoU.
- Closest individual schoolDistricts: Kootenay-Columbia (20); 54.9% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Arrow Lakes/Upper Slocan Valley · councils 8

ID: `arrow-lakes-upper-slocan-valley-health-council`. Choice: **modern-single**, low confidence in display approximation. Historical legal boundary unverified.

Arrow Lakes is a starting candidate. Upper Slocan Valley is specifically named in the council and may not follow the modern Arrow Lakes LHA edge.

Modern comparison LHA codes: 124.

Independent source drawing / modern combination overlap: 91.2% intersection over union.

Written record: [Arrow Lakes/Upper Slocan Valley Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Upper Arrow Lake; Pingston Creek; Whatshan River; Wauchope Creek; Lower Arrow Lake; Johnston Creek; Worthington Creek; Octopus Creek; Beatrice Creek; Slocan Lake.

- Closest individual lha: Arrow Lakes (124); 91.2% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 24.9% drawing IoU.
- Closest individual ha: Interior (1); 3.4% drawing IoU.
- Closest individual regionalDistricts: Regional District of Central Kootenay (RDCK); 24.6% drawing IoU.
- Closest individual municipalities: Village of Nakusp (181); 0.1% drawing IoU.
- Closest individual schoolDistricts: Arrow Lakes (10); 91.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Greater Trail · councils 9

ID: `greater-trail-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Trail is the place-name candidate for Greater Trail; greater-area extent remains unverified.

Modern comparison LHA codes: 125.

Independent source drawing / modern combination overlap: 77.2% intersection over union.

Written record: [Greater Trail Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Pend d'Oreille River; Columbia River; Big Sheep Creek.

- Closest individual lha: Trail (125); 77.2% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 3.4% drawing IoU.
- Closest individual ha: Interior (1); 0.4% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kootenay Boundary (RDKB); 11.9% drawing IoU.
- Closest individual municipalities: City of Rossland (226); 5.5% drawing IoU.
- Closest individual schoolDistricts: Kootenay-Columbia (20); 29.9% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Boundary · councils 10

ID: `boundary-health-council`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Grand Forks plus Kettle Valley is the Boundary-area candidate; this is an inferred grouping of modern LHAs.

Modern comparison LHA codes: 126, 127.

Independent source drawing / modern combination overlap: 90.5% intersection over union.

Written record: [Boundary Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, land-title survey plans. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Big Sheep Creek; Lower Arrow Lake; Kettle River; Big Sheep River.

- Closest individual lha: Kettle Valley (127); 59.0% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 22.6% drawing IoU.
- Closest individual ha: Interior (1); 3.1% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kootenay Boundary (RDKB); 78.5% drawing IoU.
- Closest individual municipalities: Village of Midway (224); 0.2% drawing IoU.
- Closest individual schoolDistricts: Boundary (51); 90.4% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Golden · councils 11

ID: `golden-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Golden is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 116.

Independent source drawing / modern combination overlap: 95.0% intersection over union.

Written record: [Golden Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kootenay River; Bugaboo Creek; Duncan River; Beaver River; Baker Creek; Hugh Allen Creek.

- Closest individual lha: Golden (116); 95.0% drawing IoU.
- Closest individual hsda: East Kootenay (11); 28.7% drawing IoU.
- Closest individual ha: Interior (1); 6.1% drawing IoU.
- Closest individual regionalDistricts: Columbia Shuswap Regional District (CSRD); 43.3% drawing IoU.
- Closest individual municipalities: Town of Golden (195); 0.1% drawing IoU.
- Closest individual schoolDistricts: Rocky Mountain (6); 45.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### South Cariboo · councils 12

ID: `south-cariboo-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

This council was renamed from 100 Mile House & District. Use modern 100 Mile House LHA 144 as the candidate, not the differently located modern South Cariboo LHA 148.

Modern comparison LHA codes: 144.

Independent source drawing / modern combination overlap: 88.1% intersection over union.

Written record: [South Cariboo Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Fraser River; Bonaparte River; Young Lake; Scott Creek; Canimred Creek; Mahood Lake; Clearwater River; Chimney Lake.

- Closest individual lha: 100 Mile House (144); 88.1% drawing IoU.
- Closest individual hsda: Thompson Cariboo Shuswap (14); 8.8% drawing IoU.
- Closest individual ha: Interior (1); 4.9% drawing IoU.
- Closest individual regionalDistricts: Cariboo Regional District (CRD); 8.2% drawing IoU.
- Closest individual municipalities: District of 100 Mile House (19); 0.5% drawing IoU.
- Closest individual schoolDistricts: Cariboo-Chilcotin (27); 13.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Central Cariboo Chilcotin · councils 13

ID: `central-cariboo-chilcotin-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Cariboo/Chilcotin is the geographic candidate for Central Cariboo Chilcotin; identical legal boundaries are not established.

Modern comparison LHA codes: 146.

Independent source drawing / modern combination overlap: 92.5% intersection over union.

Written record: [Central Cariboo Chilcotin Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Clearwater Lake; Klinaklini Lake; Colwell Creek; Mosley Creek; Homathko River; Doran Creek; Chilko Lake; Lord River; Churn Creek; Fraser River.

- Closest individual lha: Cariboo/Chilcotin (146); 92.5% drawing IoU.
- Closest individual hsda: Thompson Cariboo Shuswap (14); 35.6% drawing IoU.
- Closest individual ha: Interior (1); 19.9% drawing IoU.
- Closest individual regionalDistricts: Cariboo Regional District (CRD); 51.0% drawing IoU.
- Closest individual municipalities: City of Williams Lake (22); 0.1% drawing IoU.
- Closest individual schoolDistricts: Cariboo-Chilcotin (27); 69.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Quesnel and District · councils 14

ID: `quesnel-and-district-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Quesnel is the direct place-name candidate. Its current placement in Northern Interior HSDA does not place the former council inside the old Northern Interior board.

Modern comparison LHA codes: 521.

Independent source drawing / modern combination overlap: 90.9% intersection over union.

Written record: [Quesnel and District Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Fraser River; Euchiniko River; Tautri Creek; Chilcotin River; Tingley Creek; Sheridan Creek; Beaver Creek; Victoria Creek; Cunningham Creek; Cariboo River.

- Closest individual lha: Quesnel (521); 90.9% drawing IoU.
- Closest individual hsda: Northern Interior (52); 13.3% drawing IoU.
- Closest individual ha: Northern (5); 3.7% drawing IoU.
- Closest individual regionalDistricts: Cariboo Regional District (CRD); 28.1% drawing IoU.
- Closest individual municipalities: District of Wells (21); 0.7% drawing IoU.
- Closest individual schoolDistricts: Quesnel (28); 90.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Bella Coola Valley and District · councils 15

ID: `bella-coola-and-district-transitional-health-authority`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Bella Coola Valley is the place-name candidate. The source map and later transitional-authority identity are preserved as separate evidence.

Modern comparison LHA codes: 336.

Independent source drawing / modern combination overlap: 82.8% intersection over union.

Written record: [Bella Coola and District Transitional Health Authority Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Sakumtha River; Kimsquit River; Kitlope River; Nascall River; Cascade Inlet; Dean Channel; Fisher Channel; Burke Channel; Nootum River; Koeye River.

- Closest individual lha: Bella Coola Valley (336); 82.8% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 39.0% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 38.8% drawing IoU.
- Closest individual regionalDistricts: Central Coast Regional District (CCRD); 34.9% drawing IoU.
- Closest individual schoolDistricts: Central Coast (49); 34.9% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Sunshine Coast · councils 16

ID: `sunshine-coast-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Sunshine Coast is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 333.

Independent source drawing / modern combination overlap: 64.5% intersection over union.

Written record: [Sunshine Coast Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Howe Sound; Collingwood Channel; First Narrows of Burrard Inlet; Malaspina Strait; Jervis Inlet; Hotham Sound; Baker Bay; Squamish River; Potlatch Creek.

- Closest individual lha: Sunshine Coast (333); 64.5% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 5.1% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 5.1% drawing IoU.
- Closest individual regionalDistricts: Sunshine Coast Regional District (SCRD); 60.2% drawing IoU.
- Closest individual municipalities: District of Sechelt (331); 1.0% drawing IoU.
- Closest individual schoolDistricts: Sunshine Coast (46); 60.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Powell River · councils 17

ID: `powell-river-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Powell River is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 334.

Independent source drawing / modern combination overlap: 73.5% intersection over union.

Written record: [Powell River Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Baker Bay; Jervis Inlet; Toba River; Orford River; Brem River; Toba Inlet; Pryce Channel; Homfray Channel; Desolation Sound; Lewis Channel.

- Closest individual lha: Powell River (334); 73.5% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 7.9% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 7.9% drawing IoU.
- Closest individual regionalDistricts: qathet Regional District (qRD); 62.0% drawing IoU.
- Closest individual municipalities: City of Powell River (323); 0.9% drawing IoU.
- Closest individual schoolDistricts: Powell RIver (47); 65.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Sea To Sky · councils 18

ID: `sea-to-sky-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Howe Sound is the modern geographic candidate for the Sea To Sky council; the changed name is not a boundary-equivalence assertion.

Modern comparison LHA codes: 335.

Independent source drawing / modern combination overlap: 83.4% intersection over union.

Written record: [Sea to Sky Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Queen Charlotte Channel; Indian River; Pitt River; Lillooet River; Billygoat Creek; Cayoosh Creek; Haylmore Creek; Wade Creek; Anderson Lake; Blackwater Creek.

- Closest individual lha: Howe Sound (335); 83.4% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 15.5% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 15.4% drawing IoU.
- Closest individual regionalDistricts: Squamish-Lillooet Regional District (SLRD); 47.8% drawing IoU.
- Closest individual municipalities: Resort Municipality of Whistler (145); 2.8% drawing IoU.
- Closest individual schoolDistricts: Sea to Sky (48); 83.7% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Comox Valley · councils 19

ID: `comox-valley-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Comox Valley is the direct place-name candidate; the 1997 schedule remains necessary for edge validation.

Modern comparison LHA codes: 431.

Independent source drawing / modern combination overlap: 62.1% intersection over union.

Written record: [Comox Valley Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Deep Bay; Woodhus Creek; Oyster River; Baynes Sound.

- Closest individual lha: Comox Valley (431); 62.1% drawing IoU.
- Closest individual hsda: North Vancouver Island (43); 3.2% drawing IoU.
- Closest individual ha: Vancouver Island (4); 2.8% drawing IoU.
- Closest individual regionalDistricts: Comox Valley Regional District (CMXRD); 45.9% drawing IoU.
- Closest individual municipalities: Village of Cumberland (281); 1.9% drawing IoU.
- Closest individual schoolDistricts: Comox Valley (71); 45.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Campbell River/Nootka · councils 20

ID: `campbell-river-nootka-community-health-council`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Greater Campbell River plus Vancouver Island West is a candidate for Campbell River/Nootka; this is an inferred modern aggregation.

Modern comparison LHA codes: 432, 433.

Independent source drawing / modern combination overlap: 66.9% intersection over union.

Written record: [Campbell River/Nootka Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, township/section survey grid. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Oyster River; Georgia Strait; Baker Passage; Lewis Channel; Desolation Sound; Homfray Channel; Pryce Channel; Toba Inlet; Brem River; Southgate River.

- Closest individual lha: Greater Campbell River (432); 53.2% drawing IoU.
- Closest individual hsda: North Vancouver Island (43); 32.8% drawing IoU.
- Closest individual ha: Vancouver Island (4); 25.2% drawing IoU.
- Closest individual regionalDistricts: Strathcona Regional District (STRD); 64.5% drawing IoU.
- Closest individual municipalities: City of Campbell River (338); 0.5% drawing IoU.
- Closest individual schoolDistricts: Campbell River (72); 51.6% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Mount Waddington · councils 21

ID: `mount-waddington-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Vancouver Island North is the geographic candidate for Mount Waddington; the district name alone does not establish the historical edge.

Modern comparison LHA codes: 434.

Independent source drawing / modern combination overlap: 67.7% intersection over union.

Written record: [Mount Waddington Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Queen Charlotte Sound; Silvester Bay; Takush River; Smokehouse Creek; Machmell River; Klinaklini River; Jobin Creek; Klinaklini Lake; Colwell Creek; Homathko River.

- Closest individual lha: Vancouver Island North (434); 67.7% drawing IoU.
- Closest individual hsda: North Vancouver Island (43); 38.2% drawing IoU.
- Closest individual ha: Vancouver Island (4); 28.3% drawing IoU.
- Closest individual regionalDistricts: Regional District of Mount Waddington (RDMW); 60.3% drawing IoU.
- Closest individual municipalities: Village of Port Alice (303); 0.1% drawing IoU.
- Closest individual schoolDistricts: Vancouver Island North (85); 60.3% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Central Coast · councils 22

ID: `central-coast-transitional-health-authority`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Central Coast is the direct place-name candidate, including the mainland geography missing from a Vancouver-Island-only selection.

Modern comparison LHA codes: 337.

Independent source drawing / modern combination overlap: 39.7% intersection over union.

Written record: [Central Coast Transitional Health Authority Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Hecate Strait; Caamano Sound; Campania Sound; Whale Channel; Oscar Passage; Salmon Bay; Kynoch Inlet; Nascall River; Cascade Inlet; Dean Channel.

- Closest individual lha: Central Coast (337); 39.7% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 14.0% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 14.0% drawing IoU.
- Closest individual regionalDistricts: Central Coast Regional District (CCRD); 16.8% drawing IoU.
- Closest individual municipalities: City of Campbell River (338); 0.1% drawing IoU.
- Closest individual schoolDistricts: Central Coast (49); 16.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### South Peace · councils 23

ID: `south-peace-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Peace River South is the modern place-name candidate for South Peace.

Modern comparison LHA codes: 531.

Independent source drawing / modern combination overlap: 90.9% intersection over union.

Written record: [South Peace Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Peace River; McGregor River; Upper Blue Lake; Murray River; Pine River.

- Closest individual lha: Peace River South (531); 90.9% drawing IoU.
- Closest individual hsda: Northeast (53); 13.9% drawing IoU.
- Closest individual ha: Northern (5); 4.3% drawing IoU.
- Closest individual regionalDistricts: Peace River Regional District (PRRD); 21.5% drawing IoU.
- Closest individual municipalities: District of Tumbler Ridge (61); 6.0% drawing IoU.
- Closest individual schoolDistricts: Peace River South (59); 89.4% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### North Peace · councils 24

ID: `north-peace-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Peace River North is the modern place-name candidate for North Peace.

Modern comparison LHA codes: 532.

Independent source drawing / modern combination overlap: 94.1% intersection over union.

Written record: [North Peace Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, surveyed latitude/longitude, dated municipal limits. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Peace River; Kechika River; Fox River; Collins Bay; Graham River; Halfway River; Williston Lake; Canty Creek; Parsnip River.

- Closest individual lha: Peace River North (532); 94.1% drawing IoU.
- Closest individual hsda: Northeast (53); 36.3% drawing IoU.
- Closest individual ha: Northern (5); 11.6% drawing IoU.
- Closest individual regionalDistricts: Peace River Regional District (PRRD); 58.4% drawing IoU.
- Closest individual municipalities: District of Hudsons Hope (65); 1.3% drawing IoU.
- Closest individual schoolDistricts: Peace River North (60); 75.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Fort Nelson-Liard · councils 25

ID: `fort-nelson-liard-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Fort Nelson is the modern geographic candidate for Fort Nelson-Liard.

Modern comparison LHA codes: 533.

Independent source drawing / modern combination overlap: 97.2% intersection over union.

Written record: [Fort Nelson-Liard Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Little Rancheria River; South Albert Creek; Cormier Creek; Sambo Creek; Dease River; Trepanier Creek; Black Angus Creek; Kechika River; Wadin Creek.

- Closest individual lha: Fort Nelson (533); 97.2% drawing IoU.
- Closest individual hsda: Northeast (53); 47.6% drawing IoU.
- Closest individual ha: Northern (5); 14.8% drawing IoU.
- Closest individual regionalDistricts: Stikine Region (Unincorporated) (Stikine Region); 1.7% drawing IoU.
- Closest individual municipalities: Northern Rockies Regional Municipality (59); 94.4% drawing IoU.
- Closest individual schoolDistricts: Fort Nelson (81); 94.3% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Bulkley Valley · councils 26

ID: `bulkley-valley-health-council`. Choice: **modern-single**, low confidence in display approximation. Historical legal boundary unverified.

Smithers is a starting candidate for Bulkley Valley. Coverage toward Houston and the old council's watershed limits must be checked; this is not a confirmed complete aggregation.

Modern comparison LHA codes: 514.

Independent source drawing / modern combination overlap: 80.1% intersection over union.

Written record: [Bulkley Valley Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Buck Creek; McKilligan Creek; Skeena River; Tahtsa Lake; Nanika River; Morice River; Bulkley River.

- Closest individual lha: Smithers (514); 80.1% drawing IoU.
- Closest individual hsda: Northwest (51); 3.5% drawing IoU.
- Closest individual ha: Northern (5); 1.5% drawing IoU.
- Closest individual regionalDistricts: Regional District of Bulkley-Nechako (RDBN); 11.4% drawing IoU.
- Closest individual municipalities: District of Houston (7); 0.8% drawing IoU.
- Closest individual schoolDistricts: Bulkley Valley (54); 82.8% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Upper Skeena · councils 27

ID: `upper-skeena-community-health-council`. Choice: **source-drawn**, low confidence in display approximation. Historical legal boundary unverified.

Use the independently traced source drawing as the working extent. Modern Upper Skeena remains a comparison candidate, but the 1997 definition follows multiple watershed divides and dated survey references; its edge identity is unverified.

Modern comparison LHA codes: 513.

Independent source drawing / modern combination overlap: 73.4% intersection over union.

Written record: [Upper Skeena Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Bulkley River; Babine River; Shegisic Creek; Cranberry River; Moonlit Creek; Burdick Creek; Skeena River.

- Closest individual lha: Upper Skeena (513); 73.4% drawing IoU.
- Closest individual hsda: Northwest (51); 1.6% drawing IoU.
- Closest individual ha: Northern (5); 0.7% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kitimat-Stikine (RDKS); 3.1% drawing IoU.
- Closest individual municipalities: District of New Hazelton (50); 0.6% drawing IoU.
- Closest individual schoolDistricts: Coast Mountains (82); 4.5% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Terrace and Area · councils 28

ID: `terrace-and-area-health-council`. Choice: **modern-single**, low confidence in display approximation. Historical legal boundary unverified.

Terrace is a starting candidate; 'and Area' must be checked against the historic legal description, particularly neighbouring Nisga'a and Kitimat areas.

Modern comparison LHA codes: 517.

Independent source drawing / modern combination overlap: 84.1% intersection over union.

Written record: [Terrace and Area Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: North Seaskinnish Creek; Ksedin Creek; Ishkheenickh River; Kateen River; Exchamsiks River; Skeena River; Serb Creek; Burdick Creek; Moonlit Creek; Cranberry River.

- Closest individual lha: Terrace (517); 84.1% drawing IoU.
- Closest individual hsda: Northwest (51); 5.3% drawing IoU.
- Closest individual ha: Northern (5); 2.2% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kitimat-Stikine (RDKS); 10.8% drawing IoU.
- Closest individual municipalities: City of Terrace (52); 0.4% drawing IoU.
- Closest individual schoolDistricts: Coast Mountains (82); 15.3% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Kitimat and Area · councils 29

ID: `kitimat-and-area-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Kitimat is the place-name candidate; district-level extent is not certified.

Modern comparison LHA codes: 515.

Independent source drawing / modern combination overlap: 61.9% intersection over union.

Written record: [Kitimat and Area Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Finlayson Channel; Oscar Passage; Salmon Bay; Kynoch Inlet; Nascall River; Kitlope River; Williams Creek; Skeena River; Ecstall River; Telegraph Passage.

- Closest individual lha: Kitimat (515); 61.9% drawing IoU.
- Closest individual hsda: Northwest (51); 5.1% drawing IoU.
- Closest individual ha: Northern (5); 2.1% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kitimat-Stikine (RDKS); 10.6% drawing IoU.
- Closest individual municipalities: District of Kitimat (48); 2.2% drawing IoU.
- Closest individual schoolDistricts: Coast Mountains (82); 15.1% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### North Coast · councils 30

ID: `north-coast-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Prince Rupert is the modern geographic candidate for North Coast; do not equate a present regional-district name with this council.

Modern comparison LHA codes: 512.

Independent source drawing / modern combination overlap: 61.9% intersection over union.

Written record: [North Coast Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Ecstall River; Telegraph Passage; Ogden Channel; Kitkatla Channel; Freeman Passage; Hecate Strait; Steamer Passage; Khutzeymateen Inlet; Khutzeymateen River; Exchamsiks River.

- Closest individual lha: Prince Rupert (512); 61.9% drawing IoU.
- Closest individual hsda: Northwest (51); 1.9% drawing IoU.
- Closest individual ha: Northern (5); 0.8% drawing IoU.
- Closest individual regionalDistricts: North Coast Regional District (NCRD); 8.3% drawing IoU.
- Closest individual municipalities: District of Port Edward (76); 2.8% drawing IoU.
- Closest individual schoolDistricts: Prince Rupert (52); 24.5% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Queen Charlotte Islands/Haida Gwaii · councils 31

ID: `queen-charlotte-islands-haida-gwaii-community-health-council`. Choice: **modern-single**, medium confidence in display approximation. Historical legal boundary unverified.

Haida Gwaii is the direct geographic candidate for Queen Charlotte Islands/Haida Gwaii; historical shore limits remain unverified.

Modern comparison LHA codes: 510.

Independent source drawing / modern combination overlap: 56.9% intersection over union.

Written record: [Queen Charlotte Islands/Haida Gwaii Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through rivers, lakes and shorelines. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Hecate Strait.

- Closest individual lha: Haida Gwaii (510); 56.9% drawing IoU.
- Closest individual hsda: Northwest (51); 2.8% drawing IoU.
- Closest individual ha: Northern (5); 1.2% drawing IoU.
- Closest individual regionalDistricts: North Coast Regional District (NCRD); 14.2% drawing IoU.
- Closest individual municipalities: Village of Daajing Giids (73); 0.7% drawing IoU.
- Closest individual schoolDistricts: Haida Gwaii (50); 21.3% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Nisga'a Health Authority · councils 32

ID: `nisgaa-source-area`. Choice: **modern-single**, low confidence in display approximation. Historical legal boundary unverified.

This is related Nisga'a geography only. The map's 'Nisga'a Health Authority' identity is not confirmed equivalent to the repository's community-health-council record.

Modern comparison LHA codes: 518.

Independent source drawing / modern combination overlap: 65.2% intersection over union.

Written record: [Nisga’a Community Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0191_1997#page=3). 1997 related council; identity with the map’s authority label remains unresolved.

M191/1997 supplies a written boundary for the separately recorded council. It cannot establish that the map’s authority label is the same legal body.

Related entity only: the Nisga’a map-label identity is unresolved.

- Closest individual lha: Nisga'a (518); 65.2% drawing IoU.
- Closest individual hsda: Northwest (51); 1.6% drawing IoU.
- Closest individual ha: Northern (5); 0.7% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kitimat-Stikine (RDKS); 3.3% drawing IoU.
- Closest individual schoolDistricts: Nisgaa (92); 74.2% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Snow Country · councils 33

ID: `snow-country-health-council`. Choice: **source-drawn**, low confidence in display approximation. Historical legal boundary unverified.

Use the source-drawn approximation, capped at the 57th parallel documented in M87/1997. The written description follows Nass/Kispiox watershed limits and the Alaska boundary. Modern Snow Country plus Telegraph Creek has a poor drawing fit and is retained only as a comparison.

Modern comparison LHA codes: 511, 519.

Independent source drawing / modern combination overlap: 45.9% intersection over union.

Written record: [Snow Country Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, cadastral district lots, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Cranberry River; Kispiox River; Nass River; Steamer Passage; Khutzeymateen Inlet; Khutzeymateen River; Ishkheenickh River; Kwinamass River; Portland Inlet; Observatory Inlet.

- Closest individual lha: Snow Country (511); 82.5% drawing IoU.
- Closest individual hsda: Northwest (51); 10.4% drawing IoU.
- Closest individual ha: Northern (5); 4.3% drawing IoU.
- Closest individual regionalDistricts: Regional District of Kitimat-Stikine (RDKS); 21.7% drawing IoU.
- Closest individual municipalities: District of Stewart (51); 2.1% drawing IoU.
- Closest individual schoolDistricts: Coast Mountains (82); 30.9% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### Stikine · councils 34

ID: `stikine-health-council`. Choice: **source-drawn**, low confidence in display approximation. Historical legal boundary unverified.

Use the source-drawn approximation. M52/1997 defines a perimeter with a 56th-parallel reference, river watershed divides and the provincial boundary. Modern Stikine is a comparison candidate, not a legally reconstructed perimeter.

Modern comparison LHA codes: 516.

Independent source drawing / modern combination overlap: 79.9% intersection over union.

Written record: [Stikine Health Council Area](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001). Original B.C. Reg. 293/2001, Schedule B, deposited 12 December 2001.

The operative 2001 schedule defines this territory through watershed divides, rivers, lakes and shorelines, surveyed latitude/longitude. Its relation to the 1997/98 map and modern polygons still requires an amendment and edge review.

Water features to trace: Kispiox River; Omineca River; Omineca Arm; Meslinka River; Ingenika River; Finlay River; Kechika River; Wadin Creek; Black Angus Creek; Trepanier Creek.

- Closest individual lha: Stikine (516); 79.9% drawing IoU.
- Closest individual hsda: Northwest (51); 60.1% drawing IoU.
- Closest individual ha: Northern (5); 25.5% drawing IoU.
- Closest individual regionalDistricts: Stikine Region (Unincorporated) (Stikine Region); 70.5% drawing IoU.
- Closest individual municipalities: Northern Rockies Regional Municipality (59); 0.1% drawing IoU.
- Closest individual schoolDistricts: Stikine (87); 79.0% drawing IoU.

**Remaining:** Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.

### East Kootenay · societies 1

ID: `east-kootenay-community-health-services-society`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Today's East Kootenay HSDA is a strong candidate. Statistics Canada documents unchanged January 2000-to-June 2002 East Kootenay statistical geography. Society jurisdiction is related evidence, not a legal identity of all polygon edges.

Modern comparison LHA codes: 111, 112, 113, 114, 115, 116.

Independent source drawing / modern combination overlap: 95.8% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Golden (116); 28.4% drawing IoU.
- Closest individual hsda: East Kootenay (11); 95.8% drawing IoU.
- Closest individual ha: Interior (1); 20.8% drawing IoU.
- Closest individual regionalDistricts: Regional District of East Kootenay (RDEK); 60.0% drawing IoU.
- Closest individual municipalities: District of Sparwood (214); 0.4% drawing IoU.
- Closest individual schoolDistricts: Rocky Mountain (6); 61.4% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### Central Kootenay · societies 2

ID: `kootenay-boundary-community-health-services-society`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The source map calls this society Central Kootenay. Today's Kootenay Boundary HSDA is a strong candidate; Statistics Canada connects the older West Kootenay-Boundary statistical region with the 2002 Kootenay/Boundary HSDA.

Modern comparison LHA codes: 121, 122, 123, 124, 125, 126, 127.

Independent source drawing / modern combination overlap: 96.0% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Arrow Lakes (124); 25.4% drawing IoU.
- Closest individual hsda: Kootenay Boundary (12); 95.9% drawing IoU.
- Closest individual ha: Interior (1); 13.2% drawing IoU.
- Closest individual regionalDistricts: Regional District of Central Kootenay (RDCK); 57.5% drawing IoU.
- Closest individual municipalities: City of Rossland (226); 0.2% drawing IoU.
- Closest individual schoolDistricts: Kootenay Lake (8); 33.4% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### Coast Garibaldi · societies 3

ID: `coast-garibaldi-community-health-services-society`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Sunshine Coast, Powell River and Howe Sound form the candidate. Do not use the whole present North Shore/Coast Garibaldi HSDA: North Shore was a separate board, and Bella Coola/Central Coast were associated with other former regions.

Modern comparison LHA codes: 333, 334, 335.

Independent source drawing / modern combination overlap: 76.3% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Howe Sound (335); 42.1% drawing IoU.
- Closest individual hsda: North Shore/Coast Garibaldi (33); 28.5% drawing IoU.
- Closest individual ha: Vancouver Coastal (3); 28.4% drawing IoU.
- Closest individual regionalDistricts: Squamish-Lillooet Regional District (SLRD); 31.4% drawing IoU.
- Closest individual municipalities: Resort Municipality of Whistler (145); 1.3% drawing IoU.
- Closest individual schoolDistricts: Sea to Sky (48); 42.3% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### Upper Island/Central Coast · societies 4

ID: `upper-island-central-coast-community-health-services-society`. Choice: **source-drawn**, low confidence in display approximation. Historical legal boundary unverified.

Use the society map drawing to retain its historical island/mainland arrangement. The modern North Vancouver Island plus Central Coast LHA combination is a useful comparison, but the 2002 coastal changes and unresolved original service-area schedule prevent treating current edges as the historical society extent.

Modern comparison LHA codes: 431, 432, 433, 434, 337.

Independent source drawing / modern combination overlap: 62.1% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Vancouver Island North (434); 31.8% drawing IoU.
- Closest individual hsda: North Vancouver Island (43); 59.1% drawing IoU.
- Closest individual ha: Vancouver Island (4); 48.6% drawing IoU.
- Closest individual regionalDistricts: Regional District of Mount Waddington (RDMW); 32.4% drawing IoU.
- Closest individual municipalities: City of Campbell River (338); 0.1% drawing IoU.
- Closest individual schoolDistricts: Vancouver Island North (85); 32.4% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### Cariboo · societies 5

ID: `cariboo-community-health-services-society`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

The candidate combines 100 Mile House, Cariboo/Chilcotin, Quesnel and Bella Coola Valley. These now span Interior, Northern and Vancouver Coastal health authorities. A contemporary Cariboo-labelled area is not an adequate substitute.

Modern comparison LHA codes: 144, 146, 521, 336.

Independent source drawing / modern combination overlap: 91.3% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Cariboo/Chilcotin (146); 41.2% drawing IoU.
- Closest individual hsda: Thompson Cariboo Shuswap (14); 32.0% drawing IoU.
- Closest individual ha: Interior (1); 20.6% drawing IoU.
- Closest individual regionalDistricts: Cariboo Regional District (CRD); 75.1% drawing IoU.
- Closest individual municipalities: District of Wells (21); 0.1% drawing IoU.
- Closest individual schoolDistricts: Cariboo-Chilcotin (27); 55.4% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### North West · societies 6

ID: `north-west-community-health-services-society`. Choice: **modern-combination**, low confidence in display approximation. Historical legal boundary unverified.

The source society map explicitly excludes Nisga'a Health Authority. The modern candidate therefore uses Northwest LHAs except Nisga'a LHA 518; the whole Northwest HSDA 51 would incorrectly fill that exclusion. Using the modern Nisga'a edge to represent the historical exclusion remains unverified, and the old Northwest statistical region is not identical to this society's jurisdiction.

Modern comparison LHA codes: 510, 511, 512, 513, 514, 515, 516, 517, 519.

Independent source drawing / modern combination overlap: 89.5% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Stikine (516); 51.7% drawing IoU.
- Closest individual hsda: Northwest (51); 88.7% drawing IoU.
- Closest individual ha: Northern (5); 38.5% drawing IoU.
- Closest individual regionalDistricts: Stikine Region (Unincorporated) (Stikine Region); 46.0% drawing IoU.
- Closest individual municipalities: District of Stewart (51); 0.2% drawing IoU.
- Closest individual schoolDistricts: Stikine (87); 52.8% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

### Peace Liard · societies 7

ID: `peace-liard-community-health-services-society`. Choice: **modern-combination**, medium confidence in display approximation. Historical legal boundary unverified.

Peace River South, Peace River North and Fort Nelson form the candidate. Statistics Canada documents the January 2000 Peace Liard to June 2002 Northeast statistical correspondence.

Modern comparison LHA codes: 531, 532, 533.

Independent source drawing / modern combination overlap: 96.9% intersection over union.

Written service-area agreement/schedule: still to obtain.

- Closest individual lha: Fort Nelson (533); 46.9% drawing IoU.
- Closest individual hsda: Northeast (53); 96.9% drawing IoU.
- Closest individual ha: Northern (5); 30.9% drawing IoU.
- Closest individual regionalDistricts: Peace River Regional District (PRRD); 46.2% drawing IoU.
- Closest individual municipalities: Northern Rockies Regional Municipality (59); 45.5% drawing IoU.
- Closest individual schoolDistricts: Fort Nelson (81); 45.5% drawing IoU.

**Remaining:** Check the historical service-area agreement and its geographic schedules.

## Twenty separate statistical illustrations

A complete illustrative aggregation of the 89 modern LHAs into the 20 named historical statistical regions. It is not recovered January 2000 GIS and does not establish the 1995 legal board boundaries. Northwest statistical geography includes Nisga’a; the separate society map expressly excludes it.

- 5901 East Kootenay: modern LHAs 111, 112, 113, 114, 115, 116; low-confidence illustration, unverified historical edges.
- 5902 West Kootenay-Boundary: modern LHAs 121, 122, 123, 124, 125, 126, 127; low-confidence illustration, unverified historical edges.
- 5903 North Okanagan: modern LHAs 135, 136, 139, 141, 142; low-confidence illustration, unverified historical edges.
- 5904 South Okanagan-Similkameen: modern LHAs 131, 132, 133, 134, 137, 138; low-confidence illustration, unverified historical edges.
- 5905 Thompson: modern LHAs 143, 145, 147, 148, 149; low-confidence illustration, unverified historical edges.
- 5906 Fraser Valley: modern LHAs 211, 212, 213, 214, 215; low-confidence illustration, unverified historical edges.
- 5907 South Fraser Valley: modern LHAs 231, 232, 233, 234; low-confidence illustration, unverified historical edges.
- 5908 Simon Fraser: modern LHAs 222, 223, 224; low-confidence illustration, unverified historical edges.
- 5909 Coast Garibaldi: modern LHAs 333, 334, 335; low-confidence illustration, unverified historical edges.
- 5910 Central Vancouver Island: modern LHAs 421, 422, 423, 424, 425, 426; low-confidence illustration, unverified historical edges.
- 5911 Upper Island / Central Coast: modern LHAs 431, 432, 433, 434, 337; low-confidence illustration, unverified historical edges.
- 5912 Cariboo: modern LHAs 144, 146, 521, 336; low-confidence illustration, unverified historical edges.
- 5913 North West: modern LHAs 510, 511, 512, 513, 514, 515, 516, 517, 518, 519; low-confidence illustration, unverified historical edges.
- 5914 Peace Liard: modern LHAs 531, 532, 533; low-confidence illustration, unverified historical edges.
- 5915 Northern Interior: modern LHAs 522, 523, 524; low-confidence illustration, unverified historical edges.
- 5916 Vancouver: modern LHAs 321, 322, 323, 324, 325, 326; low-confidence illustration, unverified historical edges.
- 5917 Burnaby: modern LHAs 221; low-confidence illustration, unverified historical edges.
- 5918 North Shore: modern LHAs 331, 332; low-confidence illustration, unverified historical edges.
- 5919 Richmond: modern LHAs 311; low-confidence illustration, unverified historical edges.
- 5920 Capital: modern LHAs 411, 412, 413, 414; low-confidence illustration, unverified historical edges.

## Records still needed

1. Original historical GIS/cartographic files and source metadata for the 1997/98 maps; public/archival retrieval first, then focused Ministry of Health FOI if unavailable.
2. Dated survey-plan and cadastral edges, watershed delineations and historical municipal/electoral-area limits referred to by the orders. Seek survey registry, DataBC and archived local-government records before FOI.
3. Society service-area agreements and geographic schedules; ask successor health authorities and society/registry record custodians.
4. Nisga’a map-entity identity and its relationship to the statutory council; obtain documentary confirmation rather than infer identity from geography.
5. Operative 2002 coastal-transfer records and completed service/asset transaction records; seek public instruments and successor files, then scoped FOI for unavailable provincial records.
6. January 2000 statistical GIS and official crosswalk metadata; request from Statistics Canada/provincial statistical custodians. The modern-LHA illustration does not replace these files.
7. PGMaps snapshot provenance and exact original dataset versions; recover from repository history or the source custodian.

The detailed research register and unsent draft requests are in records-to-obtain.md. No FOI, fee, access outcome or record holding is implied by this list.
