# Independent full-image review: Richmond 2024, physical pages 62–75

**Pass for the complete assigned partition: all 573 source rows on all 14 pages were checked against the original images.** Every name, Base Salary, Benefits and Other, and Expense cell was compared with the corrected source candidates. No additional source-field error was found. Of these rows, **572 normalized observations** match exactly in all six published fields; **Young, Jim** remains held because the source base-salary cell is a dash. This is a full review of the assigned pages, not a spot check or a claim that OCR agreement alone establishes correctness.

The independently checked original SHA-256 is **`f63925088a6b381fe2ff96d9759c62a8c5316f59e2bf464ec532ba5d4409fde2`**. [Official source PDF](https://citycouncil.richmond.ca/__shared/assets/2024_Statement_of_Financial_Information77285.pdf), [official agenda index](https://citycouncil.richmond.ca/agendas/archives/council/2025/062325_agenda.htm). Full 300dpi page images are `/tmp/pofbc-history-lower-mainland/richmond-2024-ocr/p62.png` through `p75.png`; their hashes independently match the pinned source renders. The review's exact page inventory, all reviewed source fields, individual-page field hashes and relevant OCR adjudications are retained in [richmond-2024-pages-62-75.json](richmond-2024-pages-62-75.json).

| Physical page | Source rows reviewed | Accepted rows checked | First source name | Last source name |
|---:|---:|---:|---|---|
| 62 | 44 | 44 | Lowson, Kyle | Martin, Bryan |
| 63 | 44 | 44 | Martin, Melissa | Miller, Clay |
| 64 | 44 | 44 | Miller, Jesse | Naidu, Denis |
| 65 | 44 | 44 | Naidu, Jotishna | Oviedo, Frankie |
| 66 | 44 | 44 | Oviedo, Jose | Protz, Gregory |
| 67 | 44 | 44 | Prystay, Deborah | Rocha, Carlos |
| 68 | 44 | 44 | Rodriguez, Edgar | Sato, Kelly |
| 69 | 44 | 44 | Savoie, Gilbert | Sim, Ming Teck |
| 70 | 44 | 44 | Simkin, Eric | Streit, Hans-Peter |
| 71 | 44 | 44 | Strome, Chris | Tjepkema, Nicole |
| 72 | 44 | 44 | To, Tik Hang | Vo, Tuan |
| 73 | 44 | 44 | Vodchenko, Ivan | Williams, Lazar |
| 74 | 40 | 39 | Williams, Mary | Zhang, Ling Yi |
| 75 | 5 | 5 | Zhang, Zihang | Zwaag, Roeland |
| **Total** | **573** | **572** | | |

Every assigned page's heading explicitly says **Employee Earnings in Excess of $75,000 and Related Expenses for 2024**. Pages 62–73 have 44 original names each, page 74 has 40, and page 75 has five names before the controls. No name is omitted at a page transition, no subtotal is an individual, and the final five names end before the printed Total. No job-title column is published; normalized position fields are correctly null. Compound names, internal capitals and initials remain as printed, without inferred surname splitting or aliases.

The original **Base Salary** and **Benefits and Other** components remain distinct in supporting evidence. The repeated footnote defines the latter as taxable benefits and lump-sum payments including leave balances owed, union gratuities and union overtime. Page 75 explicitly defines remuneration as combining salary, taxable benefits and other lump-sum payouts. Numeric components can therefore form the published remuneration measure; the separate expense column is not added. The source cash-payment basis is not an annual base salary rate.

Low first-column amounts and large second-column amounts were read directly, including **McCluskey, Shawn** $17,871/$141,408 on page 63; **Schell, Terry** $9,650/$125,382 on page 69; and **Tait, Kyle** $787/$100,800 on page 71. These are actual original cells, not extra zeroes or omitted leading digits, and remain in the named cohort because the source threshold is for earnings rather than Base Salary alone. Single/double-digit numeric cells were also checked, including **Zhang, Zihang**'s $142 Benefits and Other on page 75. Expense dashes remain missing; small numeric expenses remain actual amounts rather than being discarded as noise.

**Young, Jim, page 74:** the image visibly prints a dash for Base Salary, **$94,619** for Benefits and Other, and a dash for Expenses. There is no numeric individual Total that could establish complete remuneration. The source row remains in evidence, while publication remains held. No missing component is assumed zero and no Benefits-and-Other amount is substituted for full remuneration. The other held row, Duncan, Scott on page 54, belongs to the separate peer/root review and is not claimed as visually checked here.

The embedded-reader candidates and fresh per-column Tesseract candidates were independently reproduced for this partition, with hashes checked against their pinned original renders and raw TSV inputs. Their guarded corrections agree in every source field. This review then compared all those fields directly with each complete page image, including OCR-disputed cells in the partition. Matching readers was corroboration, not a substitute for the full image review.

Finally, all **572 accepted normalized rows** on pages 62–75 were compared in source order against the reviewed name, null position, numeric component sum, expense/null and physical page. They match exactly. The complete Richmond source file has 1,231 accepted observations and data SHA-256 **`0d0fb9ee1f5ea6434d23af567a8cc7f72ad2da6cf0728df55abede131089b9a8`**. Both source and validation mark the employee schedule incomplete. The visible warning identifies the two held names and distinguishes complete-source known-component controls from the accepted subset.

The page-75 printed control cells were also visually read: Base Salary **$124,813,440**, Benefits and Other **$23,773,440**, Expenses **$577,893**, and separately combined named remuneration **$148,586,879**. The author's final source warning retains the full known-cell residuals **+$30 / −$28 / +$40**, the known-component sum **+$3** against combined named remuneration, and the **+$1** difference between the two printed component subtotals and that combined printed control. These residuals remain unresolved, with no balancing change to an individual. Root owns the full-source aggregate/definition review; this partition review does not certify the source's totals as reconciled.

The remaining pages were subsequently split again: this same reviewer independently completed **47–53** (308 source/accepted rows) in `richmond-2024-pages-47-53.md/json`; the other peer owns **54–61** (352 source rows) in `richmond-2024-pages-54-61.md/json`. This document does not claim the other peer's coverage or completion. **All assigned images, all assigned source fields, the held row and the final accepted subset pass. No colleague source, parser or collection data was edited.**
