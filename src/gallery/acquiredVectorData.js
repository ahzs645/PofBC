// Reviewed source vectors recovered for existing gallery designs.
const kelownaPublication = 'https://hdp-ca-prod-app-kelowna-involved-files.s3.ca-central-1.amazonaws.com/6417/1562/8132/Kelowna_SUFS_May_2024_for_Engagement.pdf'
const kelownaGeometry = {
  publisher: 'City of Kelowna',
  sourcePage: kelownaPublication + '#page=1',
  sourceUrl: kelownaPublication,
  sourceFile: 'Urban Forest Strategy, May 2024 draft',
  sourceLocator: 'PDF page 1, lower-right city signature',
  observedDate: '2026-11-27',
  sourceGround: 'light',
  extraction: {
    method: 'Retained the 73 native filled paths of the cover signature, including the outlined lettering, and trimmed the viewBox to their bounds.',
    page: 1,
    pdfBounds: [459.00027, 678.59979, 584.99969, 771.25983],
    sourceSha256: '162fb6ffa9426550c161e308d09789c0dd9282c36887c232de6c0c93399d7c6a'
  }
}

export const ACQUIRED_VECTORS = {
  'source-recovered-municipal-kelowna-website-logo': {
    prefer: true,
    designLabel: 'City of Kelowna — stacked civic signature',
    asset: {
      ...kelownaGeometry,
      id: 'municipal-kelowna-urban-forest-web-colours',
      label: 'City of Kelowna — website colours',
      versionLabel: 'Website colours · publication outlines',
      file: 'identity-recovered/municipalities/kelowna/urban-forest-geometry-web-colours.svg',
      evidenceType: 'website-colours-on-source-vector',
      colourSourceUrl: 'https://www.kelowna.ca/sites/all/themes/kelowna/images/kelowna-logo-main.png',
      notes: 'Uses the segmented ring and stacked city name seen on the municipal website.',
      fidelityNote: 'The eight fill values come from the opaque pixels of the municipal website PNG. The May 2024 publication supplies all 73 paths. Both published specimens are available as separate versions.',
      sha256: '62b6558e0340cca89e352aed2472c6c949bc4253a33e4d8b4d6f9ed5835c262e',
      bytes: 12535
    },
    alternates: [{
      ...kelownaGeometry,
      id: 'municipal-kelowna-urban-forest-print',
      label: 'City of Kelowna — Urban Forest Strategy',
      versionLabel: 'Print colours · May 2024',
      file: 'identity-recovered/municipalities/kelowna/urban-forest-2024-colour.svg',
      specimenDate: '2024-05',
      notes: 'The draft strategy cover carries the full-colour city signature.',
      fidelityNote: 'Preserves the eight source fills, including the near-black lettering. All triangles and letter outlines come from the publication.',
      sha256: 'de6cebb3da4b2c788ee0b1be1b4b9e89624ef8a5137654ee30caae79ba254106',
      bytes: 12535
    }]
  },
  "source-recovered-municipal-duncan-website-logo": {
    "prefer": true,
    "designLabel": "Duncan — Clock tower signature",
    "asset": {
      "id": "municipal-duncan-annual-report-2025-clock-tower-colour",
      "label": "Duncan — Clock tower signature with black lettering",
      "versionLabel": "Black lettering · annual report",
      "publisher": "City of Duncan",
      "file": "identity-recovered/municipalities/duncan/annual-report-2025-clock-tower-colour.svg",
      "bytes": 12950,
      "sha256": "d944d7f60f463a2290f8b30d1f36f0a98ee5ceb1a7c2bad0d5ec0e631d4c848c",
      "sourcePage": "https://bigconversations.duncan.ca/50883/widgets/215742/documents/169895#page=1",
      "sourceUrl": "https://bigconversations.duncan.ca/50883/widgets/215742/documents/169895",
      "sourceFile": "2025 Annual Report",
      "sourceLocator": "PDF page 1, upper-right front-cover logo",
      "specimenDate": "2026-06",
      "sourceGround": "light",
      "dateNote": "The fiscal year is 2025. This edition was published in June 2026.",
      "notes": "The colour clock tower and teal arcs sit above the outlined city name in black, matching the website lockup.",
      "fidelityNote": "Isolated 38 native filled paths with PyMuPDF, preserving the clock tower, arcs and outlined lettering while omitting the photograph and page field.",
      "extraction": {
        "method": "Isolated 38 native filled paths with PyMuPDF, preserving the clock tower, arcs and outlined lettering while omitting the photograph and page field.",
        "page": 1,
        "pdfBounds": [
          544,
          61,
          760,
          151
        ],
        "sourceSha256": "b5c5b73d844a5598a7169b6a506a5ea6a2ec9778608fa5bc3653d74847487098"
      },
      "darkVariant": "municipal-duncan-annual-report-2025-clock-tower-white-lettering"
    },
    "alternates": [
      {
        "id": "municipal-duncan-annual-report-2025-clock-tower-white-lettering",
        "label": "Duncan — Clock tower signature with white lettering",
        "versionLabel": "White lettering · annual report",
        "publisher": "City of Duncan",
        "file": "identity-recovered/municipalities/duncan/annual-report-2025-clock-tower-white-lettering.svg",
        "bytes": 12617,
        "sha256": "cfbf99513f381973ccc59b977a299e50a5fc13688b3d207e7335a04e00786acf",
        "sourcePage": "https://bigconversations.duncan.ca/50883/widgets/215742/documents/169895#page=4",
        "sourceUrl": "https://bigconversations.duncan.ca/50883/widgets/215742/documents/169895",
        "sourceFile": "2025 Annual Report",
        "sourceLocator": "PDF page 4, upper-right introduction logo",
        "specimenDate": "2026-06",
        "sourceGround": "dark",
        "dateNote": "The fiscal year is 2025. This edition was published in June 2026.",
        "notes": "The introduction keeps the colour clock tower and teal arcs, with the city name in white.",
        "fidelityNote": "Isolated 39 native filled paths with PyMuPDF, preserving the clock tower, arcs and outlined lettering while omitting the photograph and page field.",
        "extraction": {
          "method": "Isolated 39 native filled paths with PyMuPDF, preserving the clock tower, arcs and outlined lettering while omitting the photograph and page field.",
          "page": 4,
          "pdfBounds": [
            548,
            30,
            768,
            120
          ],
          "sourceSha256": "b5c5b73d844a5598a7169b6a506a5ea6a2ec9778608fa5bc3653d74847487098"
        }
      }
    ]
  },
  "source-recovered-municipal-clinton-website-logo": {
    "prefer": true,
    "designLabel": "Clinton — Stagecoach signature",
    "asset": {
      "id": "municipal-clinton-walking-tour-2021-colour",
      "label": "Clinton — Colour stagecoach signature",
      "versionLabel": "Blue and brown · walking tour",
      "publisher": "Village of Clinton",
      "file": "identity-recovered/municipalities/clinton/walking-tour-2021-colour.svg",
      "sha256": "6043a1aa74d98a355f211464d598297addd914bb260ee2aa4411d6bbc8d0e940",
      "bytes": 75913,
      "sourcePage": "https://village.clinton.bc.ca/wp-content/uploads/2022/01/Clinton_WalkingTour_2021_Online.pdf#page=1",
      "sourceUrl": "https://village.clinton.bc.ca/wp-content/uploads/2022/01/Clinton_WalkingTour_2021_Online.pdf",
      "sourceFile": "Historic Walking Tour",
      "sourceLocator": "PDF page 1, front cover",
      "specimenDate": "2022-01",
      "sourceGround": "light",
      "notes": "The stagecoach and arched Village of lettering appear in brown above the blue Clinton name.",
      "fidelityNote": "Isolated the native artwork and converted the PDF’s embedded font glyphs to outlines with PyMuPDF. The cover background and adjacent artwork are omitted.",
      "extraction": {
        "method": "Isolated the native artwork and converted the PDF’s embedded font glyphs to outlines with PyMuPDF. The cover background and adjacent artwork are omitted.",
        "page": 1,
        "pdfBounds": [
          92,
          130,
          313,
          210
        ],
        "sourceSha256": "6bd536e17b13fcba9705a8e67c0e0ae06ac6d2d791a63b0df612f0017f04572b"
      },
      "darkVariant": "municipal-clinton-community-profile-2022-white"
    },
    "alternates": [
      {
        "id": "municipal-clinton-community-profile-2022-white",
        "label": "Clinton — White stagecoach signature",
        "versionLabel": "White · community profile",
        "publisher": "Village of Clinton",
        "file": "identity-recovered/municipalities/clinton/community-profile-2022-white.svg",
        "sha256": "95875248ac7a04af30579a17efafef2322dc89d50148915858e1a45153a977b0",
        "bytes": 76299,
        "sourcePage": "https://village.clinton.bc.ca/wp-content/uploads/2022/05/ClintonCommunityProfile_Design_Online.pdf#page=10",
        "sourceUrl": "https://village.clinton.bc.ca/wp-content/uploads/2022/05/ClintonCommunityProfile_Design_Online.pdf",
        "sourceFile": "Community Economic Profile",
        "sourceLocator": "PDF page 10, back cover, above the contact information",
        "specimenDate": "2022-05",
        "sourceGround": "dark",
        "notes": "The white outlined name and stagecoach match the website lockup. The website artwork adds a shadow.",
        "fidelityNote": "Isolated 21 native white paths with PyMuPDF, omitting the photograph and contact text.",
        "extraction": {
          "method": "Isolated 21 native white paths with PyMuPDF, omitting the photograph and contact text.",
          "page": 10,
          "pdfBounds": [
            181,
            523,
            430,
            614
          ],
          "sourceSha256": "d748c15cb3593087423f0c9e7cd59cc1115b6dbb30c82eebc37abba9c2d1be01"
        }
      }
    ]
  },
  "source-recovered-municipal-cumberland-website-logo": {
    "prefer": true,
    "designLabel": "Cumberland — Solid-leaf crest",
    "asset": {
      "id": "municipal-cumberland-annual-report-2023-website-grey-crest",
      "label": "Cumberland — Website grey crest",
      "versionLabel": "Website grey · SVG",
      "file": "identity-recovered/municipalities/cumberland/annual-report-2023-website-grey-crest.svg",
      "sha256": "7cf6728011d6e175a0474430d21f3ba184aa4f72950c19a678a83736eed23699",
      "bytes": 92879,
      "publisher": "Village of Cumberland",
      "sourcePage": "https://cumberland.ca/wp-content/uploads/2024/05/2023-Annual-Report-FINAL.pdf#page=1",
      "sourceUrl": "https://cumberland.ca/wp-content/uploads/2024/05/2023-Annual-Report-FINAL.pdf",
      "sourceFile": "2023 Annual Report",
      "sourceLocator": "PDF page 1, front cover, upper-left crest",
      "specimenDate": "2024-05",
      "sourceGround": "light",
      "notes": "The annual report’s solid-leaf crest in the grey used by the website footer.",
      "fidelityNote": "Applied the website PNG’s sampled solid grey to the annual report’s native white crest paths. Original path geometry is unchanged.",
      "extraction": {
        "method": "Applied the website PNG’s sampled solid grey to the annual report’s native white crest paths. Original path geometry is unchanged.",
        "page": 1,
        "pdfBounds": [
          120,
          46,
          232,
          157
        ],
        "sourceSha256": "7d703f88713458d60f50dc66ee828f7bcb0b504578c360d76bd86b7c83078138"
      },
      "evidenceType": "website-colours-on-source-vector",
      "colourReferenceUrl": "https://cumberland.ca/wp-content/themes/village-of-cumberland/img/footer-crest.png",
      "darkVariant": "municipal-cumberland-annual-report-2023-white-crest",
      "alsoSeen": [
        {
          "label": "Website crest used for the grey colour match",
          "source": "https://cumberland.ca/wp-content/themes/village-of-cumberland/img/footer-crest.png"
        }
      ]
    },
    "alternates": [
      {
        "id": "municipal-cumberland-annual-report-2023-white-crest",
        "label": "Cumberland — White crest, solid leaves",
        "versionLabel": "White with solid leaves · annual report",
        "file": "identity-recovered/municipalities/cumberland/annual-report-2023-white-crest.svg",
        "sha256": "e73c89c4aa3553944271ec05ece011756c1f1673e822652ff5cdc397ddd57166",
        "bytes": 92872,
        "publisher": "Village of Cumberland",
        "sourcePage": "https://cumberland.ca/wp-content/uploads/2024/05/2023-Annual-Report-FINAL.pdf#page=1",
        "sourceUrl": "https://cumberland.ca/wp-content/uploads/2024/05/2023-Annual-Report-FINAL.pdf",
        "sourceFile": "2023 Annual Report",
        "sourceLocator": "PDF page 1, front cover, upper-left crest",
        "specimenDate": "2024-05",
        "sourceGround": "dark",
        "notes": "The cover uses the white Village crest with solid maple and oak leaves around the lamp, pick and shovel.",
        "fidelityNote": "Isolated 138 native fills and strokes with PyMuPDF, preserving the original crest geometry and omitting the red cover field.",
        "extraction": {
          "method": "Isolated 138 native fills and strokes with PyMuPDF, preserving the original crest geometry and omitting the red cover field.",
          "page": 1,
          "pdfBounds": [
            120,
            46,
            232,
            157
          ],
          "sourceSha256": "7d703f88713458d60f50dc66ee828f7bcb0b504578c360d76bd86b7c83078138"
        }
      }
    ]
  },
  "source-recovered-municipal-colwood-website-logo": {
    "prefer": true,
    "designLabel": "Colwood — Civic signature",
    "asset": {
      "id": "municipal-colwood-annual-report-2023-website-colours",
      "label": "Colwood — Website colours",
      "versionLabel": "Website colours · SVG",
      "file": "identity-recovered/municipalities/colwood/annual-report-2023-website-colours.svg",
      "sha256": "028a1bfb372ddb8ecb4814dc162a19bdbe7bd39663b32d1225a179b0b739ef92",
      "bytes": 8234,
      "publisher": "City of Colwood",
      "sourcePage": "https://www.colwood.ca/sites/default/files/2025-02/Annual%20Report%202023%20finalized.pdf#page=1",
      "sourceUrl": "https://www.colwood.ca/sites/default/files/2025-02/Annual%20Report%202023%20finalized.pdf",
      "sourceFile": "2023 Annual Report",
      "sourceLocator": "PDF page 1, lower-right cover signature",
      "specimenDate": "2023",
      "sourceGround": "light",
      "notes": "The annual report’s Colwood signature with the website artwork’s charcoal lettering and six emblem colours.",
      "fidelityNote": "Applied solid colours sampled from opaque interior pixels of the website PNG to the matching outlined artwork in the annual report. The path geometry is unchanged.",
      "extraction": {
        "method": "Applied solid colours sampled from opaque interior pixels of the website PNG to the matching outlined artwork in the annual report. The path geometry is unchanged.",
        "page": 1,
        "pdfBounds": [
          399,
          702,
          551,
          760
        ],
        "sourceSha256": "f92aad89c09b23eabc97346086936c2b37c437d3d2d392fbf699dfebdee409be"
      },
      "evidenceType": "website-colours-on-source-vector",
      "colourReferenceUrl": "https://www.colwood.ca/sites/default/files/colwood-logo.png",
      "darkVariant": "municipal-colwood-annual-report-2023-reverse",
      "alsoSeen": [
        {
          "label": "Official website image used for the colour match",
          "source": "https://www.colwood.ca/sites/default/files/colwood-logo.png"
        }
      ]
    },
    "alternates": [
      {
        "id": "municipal-colwood-annual-report-2023-reverse",
        "label": "Colwood — Colour emblem, white lettering",
        "versionLabel": "Colour emblem and white lettering · annual report",
        "file": "identity-recovered/municipalities/colwood/annual-report-2023-colour-white-lettering.svg",
        "sha256": "69c6e22ed450964514dc1262d14c16f6c35e7a8a6caf1c2d71dc2ee9f8b7771f",
        "bytes": 8252,
        "publisher": "City of Colwood",
        "sourcePage": "https://www.colwood.ca/sites/default/files/2025-02/Annual%20Report%202023%20finalized.pdf#page=1",
        "sourceUrl": "https://www.colwood.ca/sites/default/files/2025-02/Annual%20Report%202023%20finalized.pdf",
        "sourceFile": "2023 Annual Report",
        "sourceLocator": "PDF page 1, lower-right cover signature",
        "specimenDate": "2023",
        "sourceGround": "dark",
        "notes": "The report prints the colour castle emblem above white lettering. The back cover also shows this design, as an embedded image.",
        "fidelityNote": "Isolated 16 native paths with PyMuPDF, including the coloured emblem and outlined wordmark. The surrounding document field and separate location line are omitted.",
        "extraction": {
          "method": "Isolated 16 native paths with PyMuPDF, including the coloured emblem and outlined wordmark. The surrounding document field and separate location line are omitted.",
          "page": 1,
          "pdfBounds": [
            399,
            702,
            551,
            760
          ],
          "sourceSha256": "f92aad89c09b23eabc97346086936c2b37c437d3d2d392fbf699dfebdee409be"
        }
      },
      {
        "id": "municipal-colwood-draft-strategic-plan-2025-white",
        "label": "Colwood — All-white signature",
        "versionLabel": "All white · draft strategic plan",
        "file": "identity-recovered/municipalities/colwood/draft-strategic-plan-2025-white.svg",
        "sha256": "ccc8f0b42f6a1bc32723c6c519748de8f84b30ae64acc53320b40851c3a66bdc",
        "bytes": 9918,
        "publisher": "City of Colwood",
        "sourcePage": "https://www.colwood.ca/media/file/draft-strategic-plan-10jul2025-v2pdf#page=1",
        "sourceUrl": "https://www.colwood.ca/media/file/draft-strategic-plan-10jul2025-v2pdf",
        "sourceFile": "Draft 2025–2027 Strategic Plan",
        "sourceLocator": "PDF page 1, upper-right heading signature",
        "specimenDate": "July 2025",
        "sourceGround": "dark",
        "notes": "The draft strategic plan prints both the emblem and wordmark in white.",
        "fidelityNote": "Isolated the 13 visible native filled paths with PyMuPDF. Transparent strokes and the header photograph are omitted.",
        "extraction": {
          "method": "Isolated the 13 visible native filled paths with PyMuPDF. Transparent strokes and the header photograph are omitted.",
          "page": 1,
          "pdfBounds": [
            456,
            23,
            580,
            71
          ],
          "sourceSha256": "582c5d82659bcc6343f74849b5e594b9d26e56984859a7f0fd97bbdb8122956d"
        }
      }
    ]
  },
  "source-recovered-municipal-anmore-website-logo": {
    "prefer": true,
    "designLabel": "Anmore — Horizontal signature",
    "asset": {
      "id": "municipal-anmore-handbook-2025-horizontal-colour",
      "label": "Anmore — Horizontal signature, colour",
      "versionLabel": "Colour · resident handbook",
      "file": "identity-recovered/municipalities/anmore/resident-handbook-2025-horizontal-colour.svg",
      "sha256": "4db11625bade489bc33019c474c326f3a07c049f5b4cc10977b66137bcbc4e9b",
      "bytes": 1826553,
      "publisher": "Village of Anmore",
      "sourcePage": "https://anmore.com/wp-content/uploads/2024/05/Welcome-to-Anmore-Handbook-2025-Digital.pdf#page=4",
      "sourceUrl": "https://anmore.com/wp-content/uploads/2024/05/Welcome-to-Anmore-Handbook-2025-Digital.pdf",
      "sourceFile": "2025 Welcome to Anmore Handbook",
      "sourceLocator": "PDF page 4, resident welcome section",
      "specimenDate": "2025",
      "sourceGround": "light",
      "notes": "The blue Village of Anmore wordmark sits to the left of the textured blue and green A. The website publishes a white version with the same horizontal placement and lettering.",
      "fidelityNote": "Isolated 2745 native filled paths, including the multicolour texture and outlined lettering, with PyMuPDF.",
      "extraction": {
        "method": "Isolated 2745 native filled paths, including the multicolour texture and outlined lettering, with PyMuPDF.",
        "page": 4,
        "pdfBounds": [
          204,
          376,
          356,
          419
        ],
        "sourceSha256": "fec5fa6f454b0ee30ada849af62bfbc4315ef290978fdfe23b0e1ea7553b6b4e"
      }
    }
  },
  "source-recovered-municipal-barriere-website-logo": {
    "prefer": true,
    "designLabel": "Barriere — Grow with us signature",
    "asset": {
      "id": "municipal-barriere-industrial-park-prospectus-2015-logo",
      "label": "Barriere — Grow with us signature",
      "versionLabel": "Colour · industrial park prospectus",
      "file": "identity-recovered/municipalities/barriere/louis-creek-industrial-park-prospectus-2015-logo.svg",
      "sha256": "4c5b385e743dd15719d4a011d56854aca072e9b092b75d10a04f42e85a11d73a",
      "bytes": 39396,
      "publisher": "District of Barriere",
      "sourcePage": "https://www.barriere.ca/Home/DownloadDocument?docId=3c6e5d5c-c1d2-4ffb-9dcd-95519b65d0d4#page=1",
      "sourceUrl": "https://www.barriere.ca/Home/DownloadDocument?docId=3c6e5d5c-c1d2-4ffb-9dcd-95519b65d0d4",
      "sourceFile": "Louis Creek Industrial Park Lots prospectus",
      "sourceLocator": "PDF page 1, upper-right cover signature",
      "specimenDate": "2015",
      "sourceGround": "light",
      "notes": "The stacked tree, orange “grow with us” tagline and District wordmark match the website specimen.",
      "fidelityNote": "Isolated 38 native logo paths with PyMuPDF, preserving the symbol, lettering and PDF fills.",
      "extraction": {
        "method": "Isolated 38 native logo paths with PyMuPDF, preserving the symbol, lettering and PDF fills.",
        "page": 1,
        "pdfBounds": [
          453,
          9,
          592,
          183
        ],
        "sourceSha256": "94b781a3ffda8b715768cdf1084ff9b8e67c234f505d3177194bec009e74484a"
      }
    }
  },
  "source-recovered-municipal-bowen-island-website-logo": {
    "prefer": true,
    "designLabel": "Bowen Island — Horizontal tree signature",
    "asset": {
      "id": "municipal-bowen-island-brand-standards-2017-horizontal",
      "label": "Bowen Island — Horizontal tree signature, dark lettering",
      "versionLabel": "Dark lettering and green · graphic standards",
      "file": "identity-recovered/municipalities/bowen-island/community-brand-standards-2017-horizontal.svg",
      "sha256": "cf0477c18e4f1e444e9ae441e1e4ba8aad066d0d42a3fecc73104712b96a0f93",
      "bytes": 89829,
      "publisher": "Bowen Island Municipality",
      "sourcePage": "https://bowenislandmunicipality.ca/wp-content/uploads/2022/04/Bowen-Island-Community-Brand-Standards.pdf#page=17",
      "sourceUrl": "https://bowenislandmunicipality.ca/wp-content/uploads/2022/04/Bowen-Island-Community-Brand-Standards.pdf",
      "sourceFile": "2017 Bowen Island Graphic Standards",
      "sourceLocator": "PDF page 17, section 3.4, upper horizontal brand mark",
      "specimenDate": "2017",
      "sourceGround": "light",
      "notes": "The standards document dark lettering and green trees for light backgrounds. Council approved the community brand on June 27, 2016.",
      "fidelityNote": "Isolated 24 native paths with PyMuPDF, preserving the geometry and published dark and green fills.",
      "extraction": {
        "method": "Isolated 24 native paths with PyMuPDF, preserving the geometry and published dark and green fills.",
        "page": 17,
        "pdfBounds": [
          221,
          222,
          495,
          313
        ],
        "sourceSha256": "51cfd3a5f9c05258ad3ee57d02bf3da5ddc6648219644a5180885b117cd74474"
      },
      "darkVariant": "municipal-bowen-island-evacuation-plan-2020-horizontal-white"
    },
    "alternates": [
      {
        "id": "municipal-bowen-island-evacuation-plan-2020-horizontal-white",
        "label": "Bowen Island — Horizontal tree signature, white lettering",
        "versionLabel": "White and green · evacuation plan",
        "file": "identity-recovered/municipalities/bowen-island/evacuation-plan-2020-horizontal-white.svg",
        "sha256": "7d9b85f04532cfee8b03d60dd38cd9eb34264331cca71523ecbf3ec42f56a3cd",
        "bytes": 89356,
        "publisher": "Bowen Island Municipality",
        "sourcePage": "https://bowenisland.civicweb.net/document/227102/#page=1",
        "sourceUrl": "https://bowenisland.civicweb.net/document/227102/",
        "sourceFile": "2020 Evacuation Plan",
        "sourceLocator": "PDF page 1, front cover, bottom centre",
        "specimenDate": "2020",
        "sourceGround": "dark",
        "notes": "The evacuation plan pairs white outlined lettering with the green tree symbols used in the website signature.",
        "fidelityNote": "Isolated 2 compound native paths with PyMuPDF, retaining the original lettering and tree fills.",
        "extraction": {
          "method": "Isolated 2 compound native paths with PyMuPDF, retaining the original lettering and tree fills.",
          "page": 1,
          "pdfBounds": [
            186,
            698,
            423,
            775
          ],
          "sourceSha256": "03799ba2d0f784992e277ab0dfc57b6e91941c52022c7d80c1c9258b3c39a5c7"
        }
      }
    ]
  },
  "source-recovered-municipal-canal-flats-website-logo": {
    "prefer": true,
    "designLabel": "Canal Flats — Village signature",
    "asset": {
      "id": "municipal-canal-flats-streetscape-beautification-plan-2021-logo",
      "label": "Canal Flats — Village signature",
      "versionLabel": "Colour · streetscape plan",
      "file": "identity-recovered/municipalities/canal-flats/streetscape-beautification-plan-2021-logo.svg",
      "sha256": "dde67d926aa94ffa4cae19ad55b44d547ef4a40f6903f6242514eba5bdb32964",
      "bytes": 14559,
      "publisher": "Village of Canal Flats",
      "sourcePage": "https://canalflats.civicweb.net/filepro/document/18118/CF-Streetscape%20FINAL%20Beautification%20Report-2021012.pdf?handle=DFF91E761FEC4C4582DF7E9F07BE70FC#page=1",
      "sourceUrl": "https://canalflats.civicweb.net/filepro/document/18118/CF-Streetscape%20FINAL%20Beautification%20Report-2021012.pdf?handle=DFF91E761FEC4C4582DF7E9F07BE70FC",
      "sourceFile": "Downtown Streetscape Beautification Plan",
      "sourceLocator": "PDF page 1, front cover, first signature in the lower-right logo row",
      "specimenDate": "January 2021",
      "sourceGround": "light",
      "notes": "The multicolour symbol and both lines of outlined lettering match the website logo.",
      "fidelityNote": "Isolated 33 native paths with PyMuPDF. The SVG preserves the logo geometry and PDF fills.",
      "extraction": {
        "method": "Isolated 33 native paths with PyMuPDF. The SVG preserves the logo geometry and PDF fills.",
        "page": 1,
        "pdfBounds": [
          608,
          651,
          905,
          758
        ],
        "sourceSha256": "341a9120770b22507888da3bb408f4372e5e04b2b97882b11c025ce64a20fe51"
      }
    }
  },
  "source-recovered-municipal-100-mile-house-website-logo": {
    "prefer": true,
    "designLabel": "100 Mile House — District signature",
    "asset": {
      "id": "municipal-100-mile-house-community-profile-2023-logo",
      "label": "100 Mile House — District signature, dark lettering",
      "versionLabel": "Dark lettering · front cover",
      "file": "identity-recovered/municipalities/100-mile-house/community-profile-2023-logo.svg",
      "publisher": "District of 100 Mile House",
      "sourcePage": "https://www.100milehouse.com/sites/default/files/2023-03/100MileHouse_CommunityProfile2023_amended_Mar2023.pdf#page=1",
      "sourceUrl": "https://www.100milehouse.com/sites/default/files/2023-03/100MileHouse_CommunityProfile2023_amended_Mar2023.pdf",
      "sourceFile": "2023 Community Profile",
      "sourceLocator": "PDF page 1, front cover",
      "specimenDate": "March 2023",
      "sourceGround": "light",
      "darkVariant": "municipal-100-mile-house-community-profile-2023-logo-reverse",
      "notes": "The front cover pairs the gold, dark blue and green landscape emblem with dark blue lettering in the same layout as the District’s website logo.",
      "fidelityNote": "Isolated the logo’s 28 native paths from the PDF with PyMuPDF, retaining the geometry and fills as converted to RGB. Compared the SVG with the cover and the website logo.",
      "sha256": "7286338e1eeae5ac358014b75889aedb1a8f9ff5a8c1f2518497b7ddfde30b09",
      "bytes": 25463,
      "extraction": {
        "method": "Isolated the 28 native logo paths and exported their geometry and fills to SVG with PyMuPDF.",
        "page": 1,
        "pdfBounds": [38, 321, 306, 381],
        "sourceSha256": "a42996c7fa919639969318a6e254d8970eaffc463a57c3cd7e43aa8e6afe9ddb"
      }
    },
    "alternates": [
      {
        "id": "municipal-100-mile-house-community-profile-2023-logo-reverse",
        "label": "100 Mile House — District signature, white lettering",
        "versionLabel": "White lettering · back cover",
        "file": "identity-recovered/municipalities/100-mile-house/community-profile-2023-logo-reverse.svg",
        "publisher": "District of 100 Mile House",
        "sourcePage": "https://www.100milehouse.com/sites/default/files/2023-03/100MileHouse_CommunityProfile2023_amended_Mar2023.pdf#page=24",
        "sourceUrl": "https://www.100milehouse.com/sites/default/files/2023-03/100MileHouse_CommunityProfile2023_amended_Mar2023.pdf",
        "sourceFile": "2023 Community Profile",
        "sourceLocator": "PDF page 24, back cover",
        "specimenDate": "March 2023",
        "sourceGround": "dark",
        "darkBackground": true,
        "notes": "The back cover prints the same landscape emblem with white lettering on a dark ground.",
        "fidelityNote": "Isolated the 28 native logo paths from the PDF with PyMuPDF. Retained the geometry and the source fills, including the white lettering.",
        "sha256": "b417a8f74efdad29652650c3a0a04204d139d9a03625e6239eb0db38fccfe00e",
        "bytes": 25973,
        "extraction": {
          "method": "Isolated the 28 native logo paths and exported their geometry and fills to SVG with PyMuPDF.",
          "page": 24,
          "pdfBounds": [227, 720, 400, 760],
          "sourceSha256": "a42996c7fa919639969318a6e254d8970eaffc463a57c3cd7e43aa8e6afe9ddb"
        }
      }
    ]
  },
  "geoscience-bc-three-colours": {
    "prefer": true,
    "asset": {
      "id": "geoscience-bc-mountains-2019",
      "label": "Three-colour mountain signature — 2019 annual report SVG",
      "versionLabel": "2019 annual report SVG",
      "file": "identity-collected/geoscience-bc/geoscience-bc-mountains-2019.svg",
      "publisher": "Geoscience BC",
      "sourcePage": "https://cdn.geosciencebc.com/pdf/AR%202019%20Web%20Version.pdf#page=24",
      "sourceLocator": "2019 Annual Report, PDF page 24",
      "notes": "Three-colour mountains and dark lettering in the launch-era layout. The mountains are paths and the wordmark uses embedded PDF fonts.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "d296c211ee27db298d1cd10a6f01f18530f44789ee8be2462bd8e02d847ddc64",
      "bytes": 11267,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 24,
        "pdfBounds": [
          81.4,
          602.2,
          259.1,
          668.0
        ],
        "sourceSha256": "94dda5d200cc3d36107f792a405abaddc658ee673e9555e5db9982307066b096"
      },
      "sourceDate": "2019"
    }
  },
  "source-recovered-municipal-penticton-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-penticton-annual-report-2016",
      "label": "Penticton: Website logo — Annual report SVG",
      "versionLabel": "Annual report SVG",
      "file": "identity-recovered/municipalities/penticton/municipal-penticton-annual-report-2016.svg",
      "publisher": "The Corporation of the City of Penticton",
      "sourcePage": "https://www.penticton.ca/sites/default/files/uploads/financial-reports/2016_Annual_Report_full_2.pdf#page=2",
      "sourceLocator": "2016 Annual Report, PDF page 2",
      "notes": "Colour civic signature, including the fruit, landscape and lettering. The gradients are represented by native PDF shadings.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "a17e203a1447d330fd94de214eb37788d195ea75a6f66cdaf73d38b223bf7916",
      "bytes": 386809,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 2,
        "pdfBounds": [
          53.9,
          490.8,
          247.0,
          549.9
        ],
        "sourceSha256": "bb14c9f0b411cad164301a690ab8c3ccf9a0bb6cf4220bd6408fd11f89df00ba"
      },
      "sourceDate": "2016"
    }
  },
  "source-recovered-municipal-north-vancouver-city-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-north-vancouver-city-logo-quicksheet",
      "label": "North Vancouver (City): Website logo — Full-colour SVG",
      "versionLabel": "Full-colour SVG",
      "file": "identity-recovered/municipalities/north-vancouver-city/municipal-north-vancouver-city-logo-quicksheet.svg",
      "publisher": "City of North Vancouver",
      "sourcePage": "https://www.cnv.org/-/media/city-of-north-vancouver/documents/news-room/official-logos/cnv-logo-usage-quicksheet.pdf#page=1",
      "sourceLocator": "Logo Usage Quicksheet, PDF page 1",
      "notes": "The blue and black stacked mark is among the vector examples. The guide also identifies the official EPS format.",
      "fidelityNote": "19 original filled paths extracted from the PDF with MuPDF. Native vector artwork compared with the original gallery specimen.",
      "sha256": "d382a92da1aa310c48d260cde5dfa315b3ecc517aa870b86d3da1cd49d231a7d",
      "bytes": 7495,
      "extraction": {
        "method": "19 original filled paths extracted from the PDF with MuPDF.",
        "page": 1,
        "pdfBounds": [
          363.6,
          425.6,
          410.2,
          460.2
        ],
        "sourceSha256": "b3240ccf158cedb326bcbd9a98b1075babe581d54884f58addc229b4b21986c1"
      },
      "sourceDate": "PDF metadata records December 2014"
    }
  },
  "source-recovered-municipal-west-kelowna-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-west-kelowna-annual-report-2019",
      "label": "West Kelowna: Website logo — Annual report SVG",
      "versionLabel": "Annual report SVG",
      "file": "identity-recovered/municipalities/west-kelowna/municipal-west-kelowna-annual-report-2019.svg",
      "publisher": "City of West Kelowna",
      "sourcePage": "https://media-003-ca.cdn.govstack.com/westkelownacity-ca/media/kjmadmfp/2019annualreport-reduced-file-size.pdf#page=1",
      "sourceLocator": "2019 Annual Report, PDF page 1",
      "notes": "Same mountain, municipal lettering and waves. The print blues and greens differ slightly from the website image.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "c868ac30fcc4bba890a354a9527c32de8edb0839ab86d8c666316b520c42d5ca",
      "bytes": 36908,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 1,
        "pdfBounds": [
          417.4,
          611.7,
          562.3,
          741.3
        ],
        "sourceSha256": "e1cba9cc1e8bcfdbcc28cec69e321ec192062ca4473b78c6e214f39f2a366281"
      },
      "sourceDate": "2019"
    }
  },
  "source-recovered-municipal-pitt-meadows-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-pitt-meadows-strategic-plan-2023",
      "label": "Pitt Meadows: Website logo — Strategic plan SVG",
      "versionLabel": "Strategic plan SVG",
      "file": "identity-recovered/municipalities/pitt-meadows/municipal-pitt-meadows-strategic-plan-2023.svg",
      "publisher": "City of Pitt Meadows",
      "sourcePage": "https://www.pittmeadows.ca/sites/default/files/2023-05/Strategic%20Plan%202023-2026.pdf#page=1",
      "sourceLocator": "2023–2026 Strategic Plan, PDF page 1",
      "notes": "The heron and “The Natural Place” line are part of the same blue-grey lockup.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "574f58b031f19b1cd3b2f63e49838f77bf519e44e830311ef1610cc4eb56b86e",
      "bytes": 62263,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 1,
        "pdfBounds": [
          1048.3,
          729.5,
          1199.4,
          766.0
        ],
        "sourceSha256": "f25a0b9f8d4035e85676ae8f84eb6083cc21ad4ad84599c4edabd9ce8d1fc7a5"
      },
      "sourceDate": "2023"
    }
  },
  "source-recovered-municipal-creston-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-creston-annual-report-2025",
      "label": "Creston: Website logo — Annual report SVG",
      "versionLabel": "Annual report SVG",
      "file": "identity-recovered/municipalities/creston/municipal-creston-annual-report-2025.svg",
      "publisher": "Town of Creston",
      "sourcePage": "https://www.creston.ca/sites/default/files/2026-07/Annual%20report%202025.pdf#page=1",
      "sourceLocator": "2025 Annual Report, PDF page 1",
      "notes": "Blue icon, Creston Valley wordmark and Town of Creston subline.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "817468e4e9013ee17583378f958e49819ac5984447c38331c0b0664ea3ecf024",
      "bytes": 17061,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 1,
        "pdfBounds": [
          203.3,
          685.8,
          407.8,
          745.7
        ],
        "sourceSha256": "d6c56aeb1530b15ef23b9b5167edc6632b637ca728afad20de3955d68f43c521"
      },
      "sourceDate": "2025"
    }
  },
  "source-recovered-municipal-esquimalt-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-esquimalt-annual-report-2009",
      "label": "Esquimalt: Website logo — Annual report SVG",
      "versionLabel": "Annual report SVG",
      "file": "identity-recovered/municipalities/esquimalt/municipal-esquimalt-annual-report-2009.svg",
      "publisher": "Corporation of the Township of Esquimalt",
      "sourcePage": "https://www.esquimalt.ca/sites/default/files/docs/municipal-hall/annual_report_2009_web.pdf#page=58",
      "sourceLocator": "2009 Annual Report, PDF page 58",
      "notes": "Blue Township of Esquimalt lettering with the two waves.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "6e46f2d9e11b9d9926a41fd57c2541b9580d3cbfc52df4bcca59210ec5c2fba4",
      "bytes": 21358,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 58,
        "pdfBounds": [
          152.3,
          602.4,
          446.1,
          691.5
        ],
        "sourceSha256": "56797e5817719086080e06872e9fb2f721713d0a50f6114048c362e7ddf7d9e6"
      },
      "sourceDate": "2009"
    }
  },
  "shared-services-bc-2015-rebuilt": {
    "prefer": true,
    "asset": {
      "id": "shared-services-bc-2015-brochure-vector",
      "label": "Shared Services BC — Reversed, without tagline, 2015 — Brochure SVG",
      "versionLabel": "Brochure SVG",
      "file": "identity-collected/shared-services-bc/shared-services-bc-2015-brochure-vector.svg",
      "publisher": "Shared Services BC, Real Property Division",
      "sourcePage": "https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/real-estate-space/rpd_brochure.pdf#page=16",
      "sourceLocator": "Real Property Division brochure, PDF page 16",
      "notes": "The reversed Shared Services BC signature without a tagline, on the brochure’s blue field.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "df67b260dd139ae2c3f30c9a283f78578a50abc9dee6ff284b980ce413648d21",
      "bytes": 78086,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 16,
        "pdfBounds": [
          310.4,
          696.2,
          559.3,
          764.6
        ],
        "sourceSha256": "e98d31db92baac32b641a56b7c9da4ed1dced52baef9c3bdb315b0210985a161"
      },
      "sourceDate": "2015",
      "darkBackground": true
    },
    "designLabel": "Shared Services BC — Reversed, without tagline, 2015"
  },
  "source-recovered-quickpass-publication": {
    "prefer": false,
    "asset": {
      "id": "quickpass-2009-black-vector",
      "label": "Quickpass: grey and blue wordmark — Black SVG",
      "versionLabel": "Black SVG",
      "file": "identity-recovered/quickpass/quickpass-2009-black-vector.svg",
      "publisher": "TransLink",
      "sourcePage": "https://buzzer.translink.ca/wp-content/uploads/2009/11/2009-11-19-quickpass-geb-media-tour-handout.pdf#page=19",
      "sourceLocator": "Golden Ears Bridge media-tour handout, PDF page 19",
      "notes": "Same symbol and wordmark in black. The grey-and-blue sample on p. 2 is an embedded image.",
      "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
      "sha256": "6536eebe827d2e73c1f37271e18fff21bb06d7be47a0df1ea87228e56283ebcd",
      "bytes": 11530,
      "extraction": {
        "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
        "page": 19,
        "pdfBounds": [
          30.4,
          36.6,
          169.7,
          86.0
        ],
        "sourceSha256": "c921b076fa7352a45cd8aa16e8a20dfcc6d165442c47524fe84e5a457f227982"
      },
      "sourceDate": "2009-11"
    }
  },
  "source-recovered-municipal-castlegar-website-logo": {
    "prefer": true,
    "designLabel": "Castlegar — Civic wordmark",
    "asset": {
      "id": "municipal-castlegar-community-plan-v5-wordmark-website-blue",
      "label": "City of Castlegar — Website colours",
      "versionLabel": "Website colours · SVG",
      "file": "identity-recovered/municipalities/castlegar/community-plan-version-5-wordmark-website-blue.svg",
      "sha256": "e3af94948b6a32d541dfbb40d5821b1b1f076d5c03e091266dfc98a829a15877",
      "bytes": 3223,
      "publisher": "City of Castlegar",
      "sourcePage": "https://castlegar.ca/wp-content/uploads/2024/04/CASTLEGAR-OCP_v5.0_Reduced.pdf#page=1",
      "sourceUrl": "https://castlegar.ca/wp-content/uploads/2024/04/CASTLEGAR-OCP_v5.0_Reduced.pdf",
      "sourceFile": "Community Plan, Version 5 (2023)",
      "sourceLocator": "PDF page 1, front cover, below the campaign lockup",
      "specimenDate": "April 2024",
      "sourceGround": "light",
      "notes": "The Community Plan wordmark geometry with the blue sampled from the City’s website image.",
      "fidelityNote": "Applied solid colour samples from the corresponding opaque interiors of the website raster to the original outlined PDF paths. The geometry is unchanged.",
      "extraction": {
        "method": "Applied solid colour samples from the corresponding opaque interiors of the website raster to the original outlined PDF paths. The geometry is unchanged.",
        "page": 1,
        "pdfBounds": [
          37,
          741,
          167,
          762
        ],
        "sourceSha256": "c95a301b544e7e9613b9173f56e7d65ebc8a8326a74681266b421843768e423f"
      },
      "evidenceType": "website-colours-on-source-vector",
      "colourReferenceUrl": "https://castlegar.ca/wp-content/uploads/2023/02/logo-castlegar.png",
      "alsoSeen": [
        {
          "label": "Official website image used for the colour match",
          "source": "https://castlegar.ca/wp-content/uploads/2023/02/logo-castlegar.png"
        }
      ],
      "darkVariant": "municipal-castlegar-community-plan-v5-white-wordmark"
    },
    "alternates": [
      {
        "id": "municipal-castlegar-community-plan-v5-white-wordmark",
        "label": "Castlegar — White wordmark",
        "versionLabel": "White · Community Plan",
        "file": "identity-recovered/municipalities/castlegar/community-plan-version-5-white-wordmark.svg",
        "sha256": "9d3b35fd1c493a2c0f243e779c9270cc16abf2d8ed615412d54588210f1192be",
        "bytes": 3222,
        "publisher": "City of Castlegar",
        "sourcePage": "https://castlegar.ca/wp-content/uploads/2024/04/CASTLEGAR-OCP_v5.0_Reduced.pdf#page=1",
        "sourceUrl": "https://castlegar.ca/wp-content/uploads/2024/04/CASTLEGAR-OCP_v5.0_Reduced.pdf",
        "sourceFile": "Community Plan, Version 5 (2023)",
        "sourceLocator": "PDF page 1, front cover, below the campaign lockup",
        "specimenDate": "April 2024",
        "sourceGround": "dark",
        "notes": "The white CASTLEGAR wordmark is printed beneath the “Our Way to 2033” lockup. The SVG isolates the civic wordmark.",
        "fidelityNote": "Isolated 1 compound native path with PyMuPDF, preserving the outlined lettering and omitting the campaign artwork and background.",
        "extraction": {
          "method": "Isolated 1 compound native path with PyMuPDF, preserving the outlined lettering and omitting the campaign artwork and background.",
          "page": 1,
          "pdfBounds": [
            37,
            741,
            167,
            762
          ],
          "sourceSha256": "c95a301b544e7e9613b9173f56e7d65ebc8a8326a74681266b421843768e423f"
        }
      },
      {
        "id": "municipal-castlegar-white-wordmark",
        "label": "Castlegar: Website logo — White SVG",
        "versionLabel": "White · Strategic Plan",
        "file": "identity-recovered/municipalities/castlegar/municipal-castlegar-white-wordmark.svg",
        "publisher": "City of Castlegar",
        "sourcePage": "https://castlegar.ca/wp-content/uploads/2024/05/05-08-2024-Strategic-Plan-Rev-1-FINAL-reduced.pdf#page=16",
        "sourceLocator": "2023–2027 Strategic Plan, PDF page 16",
        "notes": "The same Castlegar wordmark in white. The strategic plan sets it on blue.",
        "fidelityNote": "9 original filled paths extracted from the PDF with MuPDF. The surrounding blue document field is omitted. Native vector artwork compared with the original gallery specimen.",
        "sha256": "ea4f91c07f659228e710f18249396c6a50eba301c0d7da87f053b740a13bf935",
        "bytes": 3698,
        "extraction": {
          "method": "9 original filled paths extracted from the PDF with MuPDF. The surrounding blue document field is omitted.",
          "page": 16,
          "pdfBounds": [
            63.0,
            438.8,
            200.8,
            457.1
          ],
          "sourceSha256": "7235072883120d31528fbfc5a4fe5254353ba4f489eb806028d15f3bb9f668a4"
        },
        "sourceDate": "2024",
        "darkBackground": true,
        "sourceGround": "dark"
      }
    ]
  },
  "source-recovered-municipal-central-saanich-website-logo": {
    "prefer": true,
    "designLabel": "Central Saanich — Horizontal signature",
    "asset": {
      "id": "municipal-central-saanich-annual-report-2025-horizontal-website-colours",
      "label": "District of Central Saanich — Website colours",
      "versionLabel": "Website colours · SVG",
      "file": "identity-recovered/municipalities/central-saanich/annual-report-2025-horizontal-website-colours.svg",
      "sha256": "287148294e118bb80f6f16ffc23c1099124102d40d7d1aa82644909c24c9da17",
      "bytes": 23197,
      "publisher": "District of Central Saanich",
      "sourcePage": "https://www.centralsaanich.ca/sites/default/files/2026-07/2025%20Central%20Saanich%20Annual%20Report%20FINAL.pdf#page=74",
      "sourceUrl": "https://www.centralsaanich.ca/sites/default/files/2026-07/2025%20Central%20Saanich%20Annual%20Report%20FINAL.pdf",
      "sourceFile": "2025 Annual Report",
      "sourceLocator": "PDF page 74, back cover, lower centre",
      "specimenDate": "2025",
      "sourceGround": "light",
      "notes": "The report’s horizontal logo in the website image’s blue, teal and green. The white report original remains available as a version.",
      "fidelityNote": "Applied solid colour samples from the corresponding opaque interiors of the website raster to the original outlined PDF paths. The geometry is unchanged.",
      "extraction": {
        "method": "Applied solid colour samples from the corresponding opaque interiors of the website raster to the original outlined PDF paths. The geometry is unchanged.",
        "page": 74,
        "pdfBounds": [
          142,
          692,
          484,
          748
        ],
        "sourceSha256": "39081791e088492c4e9b566d88bac47deffc32547a2126f61b1a65d667f1d843"
      },
      "evidenceType": "website-colours-on-source-vector",
      "colourReferenceUrl": "https://www.centralsaanich.ca/sites/default/files/central-saanich-logo.png",
      "alsoSeen": [
        {
          "label": "Official website image used for the colour match",
          "source": "https://www.centralsaanich.ca/sites/default/files/central-saanich-logo.png"
        }
      ],
      "darkVariant": "municipal-central-saanich-annual-report-2025-horizontal-white"
    },
    "alternates": [
      {
        "id": "municipal-central-saanich-annual-report-2025-horizontal-white",
        "label": "Central Saanich — Horizontal signature, white",
        "versionLabel": "White · back cover",
        "file": "identity-recovered/municipalities/central-saanich/annual-report-2025-horizontal-white.svg",
        "sha256": "9f06eba6366c4e8a6ca88b9559239250a6ac79074730ec676bb238ac172c3853",
        "bytes": 23208,
        "publisher": "District of Central Saanich",
        "sourcePage": "https://www.centralsaanich.ca/sites/default/files/2026-07/2025%20Central%20Saanich%20Annual%20Report%20FINAL.pdf#page=74",
        "sourceUrl": "https://www.centralsaanich.ca/sites/default/files/2026-07/2025%20Central%20Saanich%20Annual%20Report%20FINAL.pdf",
        "sourceFile": "2025 Annual Report",
        "sourceLocator": "PDF page 74, back cover, lower centre",
        "specimenDate": "2025",
        "sourceGround": "dark",
        "notes": "The farmhouse, trees and fields sit to the left of the district name in the horizontal signature.",
        "fidelityNote": "Isolated 23 native white paths with PyMuPDF. The surrounding cover field is omitted.",
        "extraction": {
          "method": "Isolated 23 native white paths with PyMuPDF. The surrounding cover field is omitted.",
          "page": 74,
          "pdfBounds": [
            142,
            692,
            484,
            748
          ],
          "sourceSha256": "39081791e088492c4e9b566d88bac47deffc32547a2126f61b1a65d667f1d843"
        }
      }
    ]
  },
  "source-recovered-municipal-vernon-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-vernon-strategic-plan-colour",
      "label": "Full-colour signature",
      "versionLabel": "Full-colour signature",
      "file": "identity-recovered/municipalities/vernon/municipal-vernon-strategic-plan-colour.svg",
      "publisher": "City of Vernon",
      "sourcePage": "https://www.vernon.ca/sites/default/files/2023-08/COV_Council-Strategic-Plan_2023-2026-Snapshot.pdf#page=1",
      "sourceLocator": "2023–2026 Council Strategic Plan Snapshot, PDF page 1",
      "notes": "Four coloured figures and the blue City of Vernon wordmark match the website signature.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
      "sha256": "f8d2b4e37be119537328433e987dba2ccdc1b7c05530f5a7b74b0037314b3889",
      "bytes": 9167,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
        "page": 1,
        "pdfBounds": [
          940.7665658004328,
          49.26142308614432,
          1176.985270910428,
          116.77983032528819
        ],
        "sourceSha256": "607760081d129394a2b17c67560796feecebf646b2f260608210482a083d1ecf"
      },
      "sourceDate": "2023"
    },
    "alternates": [
      {
        "id": "municipal-vernon-monochrome-wordmark",
        "label": "Vernon: Website logo — Monochrome SVG",
        "versionLabel": "Monochrome SVG",
        "file": "identity-recovered/municipalities/vernon/municipal-vernon-monochrome-wordmark.svg",
        "publisher": "The Corporation of the City of Vernon",
        "sourcePage": "https://www.vernon.ca/sites/default/files/2025-06/2025%20Strategic%20Plan%20Update.pdf#page=2",
        "sourceLocator": "2025 Strategic Plan Update, PDF page 2",
        "notes": "The strategic plan update prints the same symbol and arrangement in a single dark ink.",
        "fidelityNote": "Poppler PDF-to-SVG conversion after clipping the page to the logo. Native vector artwork compared with the original gallery specimen.",
        "sha256": "a81366eedfcbd11ff47ce1f7032ba7583371b962e189ed3b0d97bf1e15c751c5",
        "bytes": 13894,
        "extraction": {
          "method": "Poppler PDF-to-SVG conversion after clipping the page to the logo.",
          "page": 2,
          "pdfBounds": [
            696.2,
            18.0,
            774.1,
            40.3
          ],
          "sourceSha256": "00bd57ade153b778f0d3f3b5c2adc5530bf6baad64dd4db4a7c54e66e101b6ad"
        },
        "sourceDate": "2025"
      }
    ]
  },
  "source-recovered-municipal-courtenay-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-courtenay-delegation-colour",
      "label": "Full-colour crest and wordmark",
      "versionLabel": "Full-colour crest and wordmark",
      "file": "identity-recovered/municipalities/courtenay/municipal-courtenay-delegation-colour.svg",
      "publisher": "City of Courtenay",
      "sourcePage": "https://cvrdagendaminutes.comoxvalleyrd.ca/Agenda_minutes/CVRDCommittees/CVRC/13-Jan-26/Delegation%20Courtenay%20Saunders%20REC%2013Jan26.pdf#page=47",
      "sourceLocator": "Recreation project delegation to the Comox Valley Regional District, PDF page 47",
      "notes": "Pale teal crest and dark teal two-line City of Courtenay wordmark in the same arrangement as the website signature.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
      "sha256": "9b4086d4ac5e04c8e6451a029e59879333265d7f2338888687299596fc374b03",
      "bytes": 44946,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
        "page": 47,
        "pdfBounds": [
          34.6,
          43.1,
          132.3,
          79.2
        ],
        "sourceSha256": "2f7ba4e2655595c7d948bd512c20c02ba3757c2b1098f4375b3c0b7030ff8872"
      },
      "sourceDate": "2026-01-13"
    },
    "alternates": [
      {
        "id": "municipal-courtenay-annual-report-reverse",
        "label": "White crest and wordmark",
        "versionLabel": "White crest and wordmark",
        "file": "identity-recovered/municipalities/courtenay/municipal-courtenay-annual-report-reverse.svg",
        "publisher": "City of Courtenay",
        "sourcePage": "https://www.courtenay.ca/media/file/city-courtenay-2025-annual-report-draft#page=1",
        "sourceLocator": "2025 Annual Report draft, PDF page 1",
        "notes": "The draft annual report places the white version of the same signature on a green field.",
        "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
        "sha256": "8b09d7113b60c8a7eae92dae666dae47a1326f7065be968004b0b5953ea3e3bb",
        "bytes": 43013,
        "extraction": {
          "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
          "page": 1,
          "pdfBounds": [
            34.9,
            35.6,
            241.7,
            113.0
          ],
          "sourceSha256": "89b0a224277f6792ceb5327f1733073acc24614e644bee30a31f4cd59d086fe8"
        },
        "sourceGround": "dark",
        "darkBackground": true
      }
    ]
  },
  "source-recovered-municipal-delta-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-delta-annual-report-teal",
      "label": "Teal wordmark",
      "versionLabel": "Teal wordmark",
      "file": "identity-recovered/municipalities/delta/municipal-delta-annual-report-teal.svg",
      "publisher": "City of Delta",
      "sourcePage": "https://www.delta.ca/annualreport#page=9",
      "sourceLocator": "2025 Annual Report, PDF page 9",
      "notes": "The teal Delta wordmark with the cattail letterform matches the standalone website design.",
      "fidelityNote": "Extracted the five wordmark fills with PyMuPDF. The separately painted CITY OF line is omitted.",
      "sha256": "d42b1ca4b972b7fcb77f64da214e2170b372005fb95e76eb2405ed62f2b5bca4",
      "bytes": 7012,
      "extraction": {
        "method": "Extracted the five wordmark fills with PyMuPDF. The separately painted CITY OF line is omitted.",
        "page": 9,
        "pdfBounds": [
          53.4,
          43.9,
          147.1,
          95.1
        ],
        "sourceSha256": "79e19fe17d79a5e365cf08fabaaba48ce2584e07e4255ca18f0c065db52f19c6"
      },
      "sourceDate": "2025"
    },
    "alternates": [
      {
        "id": "municipal-delta-budget-wordmark-reverse",
        "label": "White wordmark",
        "versionLabel": "White wordmark",
        "file": "identity-recovered/municipalities/delta/municipal-delta-budget-wordmark-reverse.svg",
        "publisher": "City of Delta",
        "sourcePage": "https://hdp-ca-prod-app-delta-letstalk-files.s3.ca-central-1.amazonaws.com/3417/7676/6446/992840ca9827f20b6131a77b8bdc5571_Attachment_B_-_Phase_1_2025_Budget_Community_Engagement_Report.pdf#page=26",
        "sourceLocator": "2025 Budget Community Engagement Report, PDF page 26",
        "notes": "White version of the standalone Delta and cattail wordmark, printed on teal.",
        "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
        "sha256": "10fdd3d4f6a03d7696267211500e7fcf1f2ccc120375cace2b884d953be02a29",
        "bytes": 5715,
        "extraction": {
          "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
          "page": 26,
          "pdfBounds": [
            259.4,
            617.3,
            352.7,
            668.8
          ],
          "sourceSha256": "a16e7e42403b3f6afe05cd9814a78b9ff0f824e444873457c8315359d6be9bec"
        },
        "sourceGround": "dark",
        "darkBackground": true
      }
    ]
  },
  "source-recovered-municipal-fernie-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-fernie-consultation-script",
      "label": "Black Fernie script",
      "versionLabel": "Black Fernie script",
      "file": "identity-recovered/municipalities/fernie/municipal-fernie-consultation-script.svg",
      "publisher": "City of Fernie",
      "sourcePage": "https://hdp-ca-prod-app-fernie-letstalk-files.s3.ca-central-1.amazonaws.com/7217/6827/9187/site-logo.svg",
      "sourceLocator": "Official consultation site, site-logo.svg, first group paths 13–18",
      "notes": "Standalone black Fernie script from the City’s consultation site artwork.",
      "fidelityNote": "Retained the six native SVG paths of the standalone script. Removed the separate CITY OF FERNIE line.",
      "sha256": "48ac8d4d4eb6e656f7dfe4db2e76b38d538d660f1803c26b0da70a7512cf1360",
      "bytes": 6090,
      "extraction": {
        "method": "Retained the six native SVG paths of the standalone script. Removed the separate CITY OF FERNIE line.",
        "sourceSha256": "17b7e4e278da7b172130be2311fe52fe2ee69e6e18227b666a993a8d09564af2"
      },
      "evidenceType": "official-vector-master-conversion"
    }
  },
  "source-recovered-municipal-langley-city-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-langley-city-annual-report-colour",
      "label": "Full-colour signature",
      "versionLabel": "Full-colour signature",
      "file": "identity-recovered/municipalities/langley-city/municipal-langley-city-annual-report-colour.svg",
      "publisher": "Langley City",
      "sourcePage": "https://www.langleycity.ca/sites/default/files/2024-08/import/Annual%20Report%202017-smallest%20size.pdf#page=4",
      "sourceLocator": "2017 Annual Report, PDF page 4",
      "notes": "The multicolour LC monogram and Langley City wordmark have the same “THE PLACE TO BE” line as the website version.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
      "sha256": "4f477d1bf04a9fc7a207e1e605d0b1b9d19e09d411d1a0e8044aef8c387c672e",
      "bytes": 11765,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
        "page": 4,
        "pdfBounds": [
          62.2,
          71.3,
          199.9,
          108.3
        ],
        "sourceSha256": "e43ad1427e858e34e1480a33d8d6fa969a4ea1ac9f6c0e7117599b4e07735e45"
      },
      "sourceDate": "2017"
    },
    "alternates": [
      {
        "id": "municipal-langley-city-annual-report-reverse",
        "label": "White signature",
        "versionLabel": "White signature",
        "file": "identity-recovered/municipalities/langley-city/municipal-langley-city-annual-report-reverse.svg",
        "publisher": "Langley City",
        "sourcePage": "https://www.langleycity.ca/2024AnnualReport#page=58",
        "sourceLocator": "2024 Annual Report, PDF page 58",
        "notes": "The white monogram, name and tagline appear together on a dark blue field.",
        "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
        "sha256": "a70216b467a46548ee9b50b1a992f884666da0581fa23128064485b57492ad71",
        "bytes": 11371,
        "extraction": {
          "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
          "page": 58,
          "pdfBounds": [
            36.0,
            665.9,
            220.3,
            715.4
          ],
          "sourceSha256": "7be554fb6e00ad2c1822f291c799a3a41c836fe2b89fa1d7c9bc286a5969d2a0"
        },
        "sourceDate": "2024",
        "sourceGround": "dark",
        "darkBackground": true
      }
    ]
  },
  "source-recovered-municipal-maple-ridge-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-maple-ridge-annual-report-colour",
      "label": "Full-colour signature",
      "versionLabel": "Full-colour signature",
      "file": "identity-recovered/municipalities/maple-ridge/municipal-maple-ridge-annual-report-colour.svg",
      "publisher": "City of Maple Ridge",
      "sourcePage": "https://www.mapleridge.ca/sites/default/files/2025-06/2024%20Annual%20Report-web%20FINAL.pdf#page=78",
      "sourceLocator": "2024 Annual Report, PDF page 78",
      "notes": "The outlined name and the bright mountain, sun and river emblem match the website’s horizontal signature.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
      "sha256": "5ae586fd492a9ed72d726285fbf0cd355c9951e5bb87f50332f35494a6377fa9",
      "bytes": 9891,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
        "page": 78,
        "pdfBounds": [
          36.9,
          104.9,
          189.3,
          135.0
        ],
        "sourceSha256": "f183f1c2433b27eaae9ab38cd6b3202461e0999c7aeea9f672743aa9fa3cf6fa"
      },
      "sourceDate": "2024"
    }
  },
  "source-recovered-municipal-port-moody-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-port-moody-annual-report-colour",
      "label": "Blue wordmark with green rule",
      "versionLabel": "Blue wordmark with green rule",
      "file": "identity-recovered/municipalities/port-moody/municipal-port-moody-annual-report-colour.svg",
      "publisher": "City of Port Moody",
      "sourcePage": "https://www.portmoody.ca/media/efvcoyu2/2024-city-of-port-moody-annual-report-web.pdf#page=21",
      "sourceLocator": "2024 Annual Report, PDF page 21",
      "notes": "Blue lettering and a pale green rule in the horizontal “CITY OF THE ARTS” signature.",
      "fidelityNote": "Cropped the PDF around the mark and converted it with Poppler, preserving the native letter paths and horizontal stroke.",
      "sha256": "4f3c6b1d50e584c8918c91c263ad0d807986a550a2c1af36bfc84ccd7df2b0c8",
      "bytes": 24676,
      "extraction": {
        "method": "Cropped the PDF around the mark and converted it with Poppler, preserving the native letter paths and horizontal stroke.",
        "page": 21,
        "pdfBounds": [
          53.8,
          72.0,
          173.8,
          99.0
        ],
        "sourceSha256": "6398d4f7a3adb13cf61116dfdbd75bf202653d20bb224f4e7310c222cd4ce315"
      },
      "sourceDate": "2024"
    }
  },
  "source-recovered-municipal-west-vancouver-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-west-vancouver-annual-report-notice-colour",
      "label": "Blue and black signature",
      "versionLabel": "Blue and black signature",
      "file": "identity-recovered/municipalities/west-vancouver/municipal-west-vancouver-annual-report-notice-colour.svg",
      "publisher": "District of West Vancouver",
      "sourcePage": "https://westvancouver.ca/sites/default/files/media/documents/250528_AnnualReportAd-2%20%281%29.pdf#page=1",
      "sourceLocator": "Notice of availability of the 2024 Annual Report, PDF page 1",
      "notes": "Municipal signature with the blue wave above a blue and black wordmark.",
      "fidelityNote": "Cropped the PDF to the signature and converted it with Poppler, preserving the vector wave and the native lettering.",
      "sha256": "82f8b3f3f8f3552a0d79abbe5288116654e81f12477cb0389b70bdc041f665cc",
      "bytes": 13371,
      "extraction": {
        "method": "Cropped the PDF to the signature and converted it with Poppler, preserving the vector wave and the native lettering.",
        "page": 1,
        "pdfBounds": [
          213.8,
          312.5,
          321.8,
          333.0
        ],
        "sourceSha256": "dfc2a6b6f8270bca0e5a95f2aaa83961b1b46c6169d5653657162606d774163f"
      },
      "sourceDate": "2025"
    },
    "alternates": [
      {
        "id": "municipal-west-vancouver-annual-report-reverse",
        "label": "White signature",
        "versionLabel": "White signature",
        "file": "identity-recovered/municipalities/west-vancouver/municipal-west-vancouver-annual-report-reverse.svg",
        "publisher": "District of West Vancouver",
        "sourcePage": "https://westvancouver.ca/sites/default/files/media/documents/the2025annualreport.pdf#page=115",
        "sourceLocator": "2025 Annual Report, PDF page 115",
        "notes": "The white wave and wordmark appear on the blue annual report page.",
        "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
        "sha256": "505222eb82dcd4f948bc9605e9e1822179b0ea93c163653a545ee4f6abc44412",
        "bytes": 6477,
        "extraction": {
          "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
          "page": 115,
          "pdfBounds": [
            252.0,
            717.5,
            360.0,
            738.0
          ],
          "sourceSha256": "ea6d6b69f2099653c2b6a53f27ba76ece09ff4a099c98c0cf30b4c214fda52bc"
        },
        "sourceDate": "2025",
        "sourceGround": "dark",
        "darkBackground": true
      }
    ]
  },
  "source-recovered-municipal-white-rock-website-logo": {
    "prefer": false,
    "asset": {
      "id": "municipal-white-rock-annual-report-reverse",
      "label": "White “City by the Sea” signature",
      "versionLabel": "White “City by the Sea” signature",
      "file": "identity-recovered/municipalities/white-rock/municipal-white-rock-annual-report-reverse.svg",
      "publisher": "City of White Rock",
      "sourcePage": "https://www.whiterockcity.ca/Archive/ViewFile/Item/156#page=100",
      "sourceLocator": "2025 Annual Report, PDF page 100",
      "sourceDate": "2025",
      "notes": "The annual report prints the “City by the Sea” signature in white on blue.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
      "sha256": "9ed77ff47cadbde685ceabf130751eeda90c8ad537ca25031939fe7a7e13623e",
      "bytes": 29881,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours. The surrounding document field is omitted.",
        "page": 100,
        "pdfBounds": [
          404.0,
          695.2,
          544.9,
          736.1
        ],
        "sourceSha256": "d92b7f3267c2f1ed1f9e543b857211bb956fa2fe972a451c195bbb850b17a966"
      },
      "sourceGround": "dark",
      "darkBackground": true
    }
  },
  "source-recovered-municipal-ladysmith-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-ladysmith-strategic-plan-heritage-window",
      "label": "Black heritage window and wordmark",
      "versionLabel": "Black heritage window and wordmark",
      "file": "identity-recovered/municipalities/ladysmith/municipal-ladysmith-strategic-plan-heritage-window.svg",
      "publisher": "Town of Ladysmith",
      "sourcePage": "https://www.ladysmith.ca/docs/default-source/brochures-other-publications-2021/2023-2026-strategic-plan.pdf?sfvrsn=5b48f7db_4#page=1",
      "sourceLocator": "2023–2026 Strategic Plan, PDF page 1",
      "notes": "The black heritage streetscape and Ladysmith wordmark match the Town’s website image.",
      "fidelityNote": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
      "sha256": "372ee941fb49509f291d4a139a07b15111366125bcce833426f1a7142a6b6b10",
      "bytes": 585089,
      "extraction": {
        "method": "Extracted the publisher’s foreground path geometry with PyMuPDF, preserving the PDF’s shapes and colours.",
        "page": 1,
        "pdfBounds": [
          511.1324134592853,
          482.6770228687385,
          583.4006807422761,
          585.0245166080974
        ],
        "sourceSha256": "b8db44ad319abcff8689473c3dc0fbbd53466b624e5a47d3651190f5b9134ab8"
      }
    }
  },
  "source-recovered-municipal-sechelt-website-logo": {
    "prefer": true,
    "asset": {
      "id": "municipal-sechelt-consultation-site-colour",
      "label": "Colour signature with teal lettering",
      "versionLabel": "Colour signature with teal lettering",
      "file": "identity-recovered/municipalities/sechelt/municipal-sechelt-consultation-site-colour.svg",
      "publisher": "District of Sechelt",
      "sourcePage": "https://hdp-ca-prod-app-sech-yoursay-files.s3.ca-central-1.amazonaws.com/6717/3681/7268/site-logo.svg",
      "sourceLocator": "Your Say Sechelt, site-logo.svg",
      "notes": "The District’s consultation site uses the segmented S with teal lettering in the same horizontal arrangement as the white-lettered website logo.",
      "fidelityNote": "The original, self-contained SVG served by the District’s consultation site.",
      "sha256": "ee6d713113d65fea9a85e9a1646eaebabd95cc771cf0ef6eea11dd0144063a85",
      "bytes": 40373,
      "extraction": {
        "method": "The original, self-contained SVG served by the District’s consultation site.",
        "sourceSha256": "ee6d713113d65fea9a85e9a1646eaebabd95cc771cf0ef6eea11dd0144063a85"
      },
      "evidenceType": "official-website-svg"
    }
  },
  "source-municipal-prince-rupert-website-logo": {
    "prefer": false,
    "asset": {
      "id": "municipal-prince-rupert-2024-wordmark-reverse",
      "label": "White standalone wordmark",
      "versionLabel": "White standalone wordmark",
      "file": "identity-municipal/prince-rupert/municipal-prince-rupert-2024-wordmark-reverse.svg",
      "publisher": "City of Prince Rupert",
      "sourcePage": "https://www.princerupert.ca/sites/7/files/2024-12/PR%20Complete%20Community%20Assessment%20&%20Plan.pdf#page=118",
      "sourceLocator": "Complete Community Assessment & Plan, Appendix B, PDF page 118",
      "notes": "White printing of the same standalone wordmark. The wordmark is isolated from the arch that the report places above it.",
      "fidelityNote": "Extracted the 21 native wordmark fills. The larger arch and red document field are omitted. The surrounding document field is omitted.",
      "sha256": "e8240c496bfc8b253fba51cb6b4a1116f212d59b8f0dc1f10ee71986430905bc",
      "bytes": 6693,
      "extraction": {
        "method": "Extracted the 21 native wordmark fills. The larger arch and red document field are omitted. The surrounding document field is omitted.",
        "page": 118,
        "pdfBounds": [
          336.5621562843527,
          413.1450930712797,
          455.1634275289792,
          461.80149566019406
        ],
        "sourceSha256": "4c3d1895aa4a8e4011b2df8b4dce3bac2e8bb49da9b6b60e57a2a31d1ac221a0"
      },
      "sourceDate": "2024",
      "sourceGround": "dark",
      "darkBackground": true
    }
  }
}
