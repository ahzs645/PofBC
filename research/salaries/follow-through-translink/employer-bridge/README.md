# Transit Police employer bridge and compiled entity review

The official [Policies and Procedures index](https://transitpolice.ca/news/plans-and-policies/) directly links [TSML Policy No. 029](https://transitpolice.ca/wp-content/uploads/_pda/2023/07/TSML-Policy-No.-029-Psychological-Health-and-Safety-Management-System-PHSMS.2022-01-27.WebsiteRedacted.pdf). The saved PDF is 1,305,806 bytes, four pages, SHA-256 `79adee0bafbc7b955c27452b92aff8c7ae4062e59a6ecf0c1d28477b6699261b`.

Physical page 2, section 3, explicitly defines:

> **Transit Police** – The South Coast British Columbia Transportation Authority Police Service, also known as the Metro Vancouver Transit Police.
>
> **TSML** – The TransLink Security Management Limited, a subsidiary of TransLink that is the entity for the Transit Police and employs Transit Police Personnel.

The policy also separately defines TransLink as the South Coast British Columbia Transportation Authority. This supports the six official employee schedules headed **TransLink Security Management Ltd.** using existing employer slug `transit-police`, display name **Transit Police (TransLink Security Management Ltd.)**, sector **Municipal police**. The legal report heading remains retained.

Both this agent and the parent independently viewed the rendered definitions. Review images are [the complete page](tsml-policy-029-page2.png) and [the focused definitions crop](tsml-policy-029-definitions-crop.png). The scanned page contains no native text; its empty native extraction, raw OCR text/TSV and manually checked literal definition transcription are saved separately. [policy-bridge-receipt.json](policy-bridge-receipt.json) pins every artifact and its source URL. [policy-index-receipt.json](policy-index-receipt.json) pins the downloaded official HTML and the exact PDF link. These are observations of the saved policy copy on November 2, 2026, without asserting every historical policy revision or person-level employment continuity.

The policy bridge does not establish that separate compiled observation groups are equivalent. Existing compiled `metro-vancouver-transit-police` observations remain distinct; no compiled observation is reassigned, deleted or redated.

[The compiled entity review](compiled-entity-review.md) compares all 12,464 original compiled `translink` observations with all reconstructed official cohorts, preserving exact names, amounts, source periods and null/zero distinctions. It documents partial financial overlap across multiple subsidiary schedules under compiled `translink`. The JSON summary pins its immutable baseline, every accepted/held cohort and the complete per-observation evidence gzip. No record movement or blanket fiscal-to-calendar redating follows from this review.

The TransLink tests pin the PDF and index HTML, verify every saved image/text hash, reject stale manifest/cohort input pins, and independently reproduce the compiled match counts. Run:

```sh
python scripts/follow_through_translink_bridge.py
python -m unittest scripts/test_follow_through_translink.py
```

The comparison command writes only the new bridge comparison evidence/docs. Neither it nor this bridge work changes accepted manifests, normalized salary data or shared exports.
