# One-ink BC Forest Service emblem — standardized squircle

These four PofBC study SVGs use **one shared, symmetrical superellipse** in place of an irregular, hand-fitted outer border. Parameters live in `parameters.json`. The static SVGs remain editable in Inkscape or Illustrator.

Run from the repository root:

```sh
node artwork/internal/forest-service-monochrome-squircle/rebuild.mjs
node artwork/internal/forest-service-monochrome-squircle/rebuild.mjs --check
```

The parameterized frame is independent of the original green seven-part master `src/internal/forest-service-emblem.svg`, which is retained unchanged, as are its poster usages.

The standardized exponent `3.25` and uniform border width `13.85` are **our reference-based construction**, not documented historical specifications. Against the two supplied black-and-white prints, the full-image overlap of the revised source-based *two-island* geometry is approximately **92.4%** and **90.8%**, compared with **92.2%** and **89.2%** before the correction (grayscale threshold 160, second image normalized to the first's badge bounds). Pixel overlap depends on printing/scanning artifacts and is not a claim that the outline was officially standardized.

**Do not connect the islands.** The two historical print crops each show two disconnected island marks. The existing PofBC coloured master, however, has **three separately editable island paths**. The new `forest-service-emblem-three-islands-separated.svg` deliberately adds a third independent middle fragment for comparison with the coloured master, clearly labelled as an interpretation, **not** a feature visible in the monochrome print. `forest-service-emblem-three-islands-green.svg` is its generated green treatment.

The monochrome study has a remeasured tree-opening right slope, its own narrow negative-space trunk, a fuller lower coastline and two independent island shapes. `rebuild.mjs` regenerates only the constant-width symmetric squircle from JSON parameters; it does not trace or alter the source-built mainland or islands.
