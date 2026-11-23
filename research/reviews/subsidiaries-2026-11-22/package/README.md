# PofBC – historical corporate subsidiaries and ownership research

**Research package:** 22 November 2026  
**Project:** https://github.com/ahzs645/PofBC  
**Site/repository changes:** NONE (research handback only)

## What changed

The previous research package is preserved byte-for-byte in `baseline/`. It has **45 records**, which are historical evidence candidates and are not synonymous with 45 unique, newly discovered legal subsidiaries. This continuation adds **8 additional company candidates**, giving **53 inventory records** total, plus **25 dated/period-specific research events** and a registry/source register.

The new batch focuses on government-owned transit operators and holding companies (T.S. Holdings; Vancouver Island Transit), the 1970s food-industry investment and disposition chain (Swan Valley Foods, Chef Ready, Kootenay Dehydrators, South Peace Dehy), an additional wind-up (Crown Development Corporation) and government-funded Thompson-Okanagan Transit. **Some of these are minority investments or financed companies — not subsidiaries.** `data/new_entities.csv` identifies these classifications explicitly.

## Read in this order

1. `CONTINUATION_FINDINGS.md` – historical findings and evidence links.
2. `data/events.csv` – 25 atomic facts, with exact/partial dates and source IDs.
3. `data/new_entities.csv` – 8 new company candidates, role and confidence.
4. `data/combined_inventory_53.csv` – all 53 candidate inventory records (45 legacy + 8 new).
5. `data/source_register.csv` – 20 sources with original public URLs and page locators.
6. `REVIEW_AND_INTEGRATION.md` – how to add records safely, hold uncertain relationships, and prioritize verification.
7. `data/review_queue.csv` – next investigative tasks.
8. `data/dunhill_legal_identity.json` – both Dunhill registration numbers and legal-name events.
9. `baseline/` – original report and JSON (unchanged).
10. `SHA256SUMS.txt` – reproducibility and content integrity checks.

## Key guardrails

- `observed_at` is a **financial statement observation date**, not automatically incorporation date.
- The ended fiscal year is not a precise dissolution day.
- `provision for doubtful recoveries` or an investment write-down is **not** sale of shares or legal dissolution.
- Financing, service agreements and administered programs are not ownership of a company.
- A business asset transfer is not a transfer of shares or a legal rename.
- The 1977-12-01 Standard Brands share purchase, 1978-01-06 federal continuance and 1978-04-28 amalgamation are three separate events for Swan Valley Foods.
- `Venture Realty` in the 1978 Statistics Canada publication **may or may not** be `Ventures Realty Ltd.` in the 1974 Dunhill list.
- The two historical Dunhill companies, No.73385 and No.91003, must never be merged.
- Source PDFs are linked, **not reproduced** inside this ZIP (remote sources may be large, licensed or change URLs). Where visually read via live source, original page coordinates are provided. No original archival documents were invented or fabricated.

**Implementation status:** No source code changes, PR or deployment. This is a research-only package. All new names were checked by exact-name against `src/government/historyData.js` on the repository default branch at research time; an absent exact string does not prove the entity is nowhere else in the repository. The previous audit already had research references for certain entities.
