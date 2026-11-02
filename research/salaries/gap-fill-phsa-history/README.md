# Earlier PHSA employee disclosures

Nine official Legislative Library originals add 22,796 named employee payment observations for fiscal 2006/07–2014/15. The original schedules publish no job titles. All existing compiled observations remain retained, with possible overlap disclosed.

The [methods and source qualifications](../gap-fill-2026-11-02/phsa_history/METHODS.md) explain the two-reader/native or raster extraction, complete payment censuses, bounded personal source review, explicit unknown expense dashes, original period/count contradictions and literal control residuals. The [source clarification ledger](../gap-fill-2026-11-02/phsa_history/remaining-source-clarifications.json) lists issues for possible later issuer clarification; no requests were sent.

Offline reconstruction: `python scripts/gap_phsa_history_build.py`. Regression checks: `python -m unittest discover -s scripts -p test_gap_phsa_history.py -v`. Both use committed evidence without live retrieval, OCR models or original PDF caches. Original processing scripts and exact source/model fingerprints are retained separately. Re-run processing only in an isolated research checkout; the producer evidence is frozen.
