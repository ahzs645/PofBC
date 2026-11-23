# handyDART, 1985: vector reconstruction, 23 November 2026

BC Transit's handyDART lockup as the cover of its March 1985 pamphlet shows it (Museum of
Vancouver H2015.37.362): the red double arrow beside an italic lower-case "handy" and capital
"DART", between two rules. It is a separate, earlier design from the TransLink circle and wordmark
the gallery already holds, so it sits beside that entry rather than taking it as a version
(`targetAssetId` is null).

The two drawings were first written straight into `src/gallery/expandedIdentityData.js`, which
`scripts/build-identity-expansion.mjs` generates. With no record behind them, the generator's
`--check` reported the file as stale and the Pages build stopped at `npm test`. This package is
that record: `proposed-assets.json` holds both entries unchanged, apart from `search`, and the
generator merges them into the handyDART body like the other vector searches.

| Asset | File | Colour |
|---|---|---|
| `rebuild-expanded-handydart-1985-brochure` | `public/identity-expanded/handydart/brochure-1985-rebuilt.svg` | #E44E5B, approximating the scan's red |
| `rebuild-expanded-handydart-1985-brochure-paper-model-red` | `public/identity-expanded/handydart/brochure-1985-rebuilt-paper-model-red.svg` | #F31410, the Gallery In Transit paper bus's arrow red |

The double arrow is the paper bus's two arrow paths (see `../bc-transit-double-arrow-2026-11-22/`),
only scaled, placed and recoloured. The wordmark is new outlined lettering from Liberation Sans
Italic fitted to the 500 × 319 scan; the original typeface is not identified. The rules are drawn
anew. March 1985 is the date marked on the pamphlet, not an adoption date.
