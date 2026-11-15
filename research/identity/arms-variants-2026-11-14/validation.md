# Validation

Validated 14 November 2026. This reconciliation starts from PR #64 commit
`7f400f96e9ba65c5b1f0ee8f3ae37858040d602a` and incorporates the identified order
held in the Historic continuation at
`d3e4fbf55538e3991179a9868496dcf2e28a68c5`.

- **32** unique illustrated entries and **30** source records; every entry links
  to an existing source. S30 adds the complete OIC 1121/1978; the original supplied
  image attribution remains S20.
- All **32** reference images decode, match their recorded dimensions and SHA-256
  hashes, and are byte-for-byte unchanged from the original PR #64 candidate.
- The held OIC PDF has four pages. Its SHA-256 matches the continuation's register.
  Pages **1** and **4** were rendered and visually inspected again: the government
  heading and approval date match page 1; the blackletter map heading, Crown Grant
  No. 8498 and district/corporation labels match page 4.
- Entry 21 distinguishes the containing order's date from the unknown map
  creation, original grant issue and engraving dates. The split-serif source
  remains unidentified and undated. The inventory retains these distinctions as
  explicit fields as well as readable captions.
- The regenerated **nine-page** PDF contains all 32 entry titles and **72** active
  source hyperlinks covering all **30** source URLs. Source-index inter-entry
  spacing is 6 points instead of 10; font sizes are unchanged.
- PDF pages **5, 6 and 9** were rendered with Poppler and visually checked after
  the final edits. Captions, dates, page references, credits and source links fit
  without overlap or clipping. Text bounds remain within each page. Pages
  **1-4, 7 and 8** render identically to the earlier reviewed PDF.
- The overview and dated-print comparison are unchanged. Their images are fitted
  independently, not at a common physical scale. The README selects the 1960
  museum report cover (printed 1961) as the first composition/proportion target,
  while retaining the source-resolution limit and unknown fine details.
- Historical distinctions from the original review are preserved: report versus
  imprint dates, 1906 shield versus assumed full arms, 1987 augmentation versus
  1990 registration, and undated artwork versus a dated occurrence.
- `git diff --check` passes. The update is confined to this research directory;
  application/runtime tests are not applicable.

Rebuild the catalogue with:

```sh
python research/identity/arms-variants-2026-11-14/build_catalogue.py \
  research/identity/arms-variants-2026-11-14/catalogue.json --compact
```

The catalogue records image and dating limits. Identifying a document establishes
provenance; it does not recover a printer's master or establish identical blocks.

## Independent continuation review

Reviewed again on 14 November 2026 from reconciled commit
`c952adf67280171f2f3749992d71233a09f502b0` in an isolated checkout.

- All nine committed PDF pages were freshly rendered with Poppler and visually
  inspected. No overlap, clipped captions, missing images or broken source-index
  layout was found.
- A fresh local rebuild from `catalogue.json` produced identical extracted text
  and rendered pixels on every page. The committed PDF SHA-256 is
  `70a25f95121aacdc875d00eee3ac936e26913127546b574bef9675231f457640`.
- The 32 reference-image checksums, dimensions and original-PR byte comparisons
  were independently repeated. All passed. All 32 titles appear in the PDF;
  its 72 active source links cover all 30 source URLs.
- The retained OIC checksum and four-page count were checked again, and pages 1
  and 4 were rendered directly from that PDF. They confirm the government
  heading and blackletter map attachment recorded in entries 20 and 21.
- The selected 1960 report PDF matches its recorded source checksum. Its cover
  contains a 2179 x 3162 pixel image; its final page bears the 1961 imprint.
  This confirms the report/imprint distinction and does not establish a
  higher-resolution arms master.

No further catalogue wording, source-image or PDF correction was required by
this review. The application and its browser acceptance are tracked separately.
