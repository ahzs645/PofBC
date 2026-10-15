# One-ink BC Forest Service emblem — standardized squircle

These four PofBC study SVGs use **one shared, symmetrical superellipse** in place of an irregular, hand-fitted outer border. Parameters live in `parameters.json`. The static SVGs remain editable in Inkscape or Illustrator.

Run from the repository root:

```sh
node artwork/internal/forest-service-monochrome-squircle/rebuild.mjs
node artwork/internal/forest-service-monochrome-squircle/rebuild.mjs --check
```

The parameterized frame is independent of the original green seven-part master `src/internal/forest-service-emblem.svg`, which is retained unchanged, as are its poster usages.

The rounded exponent `3.25` and uniform border width `13.85` are **modern reference-fitting choices**, not historically attested specifications. Two monochrome newspaper/print specimens were compared using a fixed badge-bounds registration and a grayscale threshold of 160. Their full-logo overlaps improved from 91.4% and 88.8% to 92.1% and 89.3%; border-only overlaps improved from 89.6% and 89.8% to 91.0% and 90.7%. Such pixel scores are diagnostic and depend on scan conditions.

The two detached island fragments in the archival samples remain separate in the reference-inspired master. The joined-island geometry is a deliberately authored modern option, not asserted as an original historic badge.
