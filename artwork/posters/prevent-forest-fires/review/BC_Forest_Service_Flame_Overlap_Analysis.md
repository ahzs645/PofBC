# Flame-line overlap analysis — revision 5 to revision 6

Five yellow side ribbons were checked separately from the dark-ink tree analysis. Their path geometry is retained from revision 5; revision 6 concentrates its flame changes on the upper crest and narrow folds. Nearby crest or lettering changes can still affect a local colour mask. The rectified source photograph remains fixed at 1000 × 1440 pixels, and each vector preview is reduced once from 3000 × 4320 using Lanczos resampling. The large orange field is not included in a single overall score.

## Local yellow overlap

| Fixed review area | Before | Revised | Change |
|---|---:|---:|---:|
| Left long vein, isolated lower shaft | 84.3% | 84.3% | +0.0 percentage points |
| Left middle arc | 80.1% | 80.1% | +0.0 percentage points |
| Left lower tongue | 81.6% | 81.6% | +0.0 percentage points |
| Right oblique cut | 78.9% | 78.9% | +0.0 percentage points |
| Right lower edge flick | 79.7% | 79.7% | +0.0 percentage points |

The percentages are intersection-over-union of the locally classified yellow areas. They describe agreement at this fixed registration, with the stated colour rule. They do not establish exact historical ink colour or distinguish every feature of photographed print wear. The boxes can overlap; their counts are not added or presented as an overall flame score.

## Classifier and fixed scope

The same classifier, measurement boxes and exclusions are applied to both revisions. Scope and exclusions were settled before the first revision-5 flame-geometry edit. The exact definitions below are retained in `analysis/flames/regions_before_edits.json`.

```json
{
  "canvas": [
    1000,
    1440
  ],
  "registration": "same fixed rectified photograph as tree analysis",
  "primary_classifier": {
    "red_min": 150,
    "green_min": 140,
    "green_red_ratio_min": 0.74,
    "blue_red_ratio_max": 0.55
  },
  "sensitivity_green_red_ratio": [
    0.68,
    0.74,
    0.8
  ],
  "regions": {
    "left_long": {
      "name": "Left long vein, isolated lower shaft",
      "box": [
        28,
        405,
        80,
        530
      ],
      "context": [
        0,
        315,
        100,
        540
      ]
    },
    "left_mid": {
      "name": "Left middle arc",
      "box": [
        0,
        480,
        72,
        600
      ],
      "context": [
        0,
        450,
        85,
        610
      ]
    },
    "left_low": {
      "name": "Left lower tongue",
      "box": [
        0,
        650,
        42,
        775
      ],
      "context": [
        0,
        620,
        60,
        790
      ]
    },
    "right_oblique": {
      "name": "Right oblique cut",
      "box": [
        810,
        610,
        925,
        765
      ],
      "context": [
        805,
        600,
        935,
        775
      ],
      "polygon": [
        [
          910,
          610
        ],
        [
          925,
          625
        ],
        [
          878,
          690
        ],
        [
          840,
          765
        ],
        [
          810,
          765
        ],
        [
          832,
          700
        ],
        [
          869,
          645
        ]
      ]
    },
    "right_low": {
      "name": "Right lower edge flick",
      "box": [
        955,
        750,
        1000,
        845
      ],
      "context": [
        940,
        730,
        1000,
        860
      ]
    }
  },
  "exclude_outer_canvas_pixels": 3,
  "measurement_domain_notes": [
    "Boxes and domain exclusions fixed before any revision 5 flame edits.",
    "Exclude the outer 3 pixels of the registered canvas to avoid the photographed paper/print boundary.",
    "The oblique-ribbon polygon is a broad manually specified measurement window excluding nearby headline-outline discoloration; it does not define artwork geometry.",
    "Left-middle context/ROI also includes the lower tip of the long-left ribbon; regions are reported individually and not combined."
  ]
}
```

The wider colour crops show visual context. Measurement boxes may cover only a useful section of a ribbon; for example, the left long vein is assessed on its lower shaft. The difference images show shared yellow in dark gray, reference-only yellow in cyan, candidate-only yellow in magenta, and excluded areas in light gray.

## Coverage and excess

| Area | Reference covered, before → revised | Vector supported, before → revised | Missing pixels, before → revised | Extra pixels, before → revised |
|---|---:|---:|---:|---:|
| Left long vein, isolated lower shaft | 95.5% → 95.5% | 87.8% → 87.8% | 17 → 17 | 50 → 50 |
| Left middle arc | 84.7% → 84.7% | 93.6% → 93.6% | 142 → 142 | 54 → 54 |
| Left lower tongue | 84.4% → 84.4% | 96.2% → 96.2% | 102 → 102 | 22 → 22 |
| Right oblique cut | 88.7% → 88.7% | 87.7% → 87.7% | 71 → 71 | 78 → 78 |
| Right lower edge flick | 83.7% → 83.7% | 94.4% → 94.4% | 33 → 33 | 10 → 10 |

## Colour-threshold sensitivity

| Area | G/R ≥ 0.68 | G/R ≥ 0.74 | G/R ≥ 0.8 |
|---|---:|---:|---:|
| Left long vein, isolated lower shaft | 85.2% → 85.2% | 84.3% → 84.3% | 75.4% → 75.4% |
| Left middle arc | 79.9% → 79.9% | 80.1% → 80.1% | 78.4% → 78.4% |
| Left lower tongue | 79.5% → 79.5% | 81.6% → 81.6% | 82.2% → 82.2% |
| Right oblique cut | 78.2% → 78.2% | 78.9% → 78.9% | 75.0% → 75.0% |
| Right lower edge flick | 75.1% → 75.1% | 79.7% → 79.7% | 78.9% → 78.9% |

## Local right shoulder

The curved fork and narrow orange tongue introduced in revision 5 are retained. Revision 6 changes the adjacent orange neck and several other crest peaks, while keeping all five detached side-ribbon paths and `right-inside-shoulder` unchanged.

The shoulder is reviewed with fixed colour crops, grid crops and 50% overlays. No separate numerical yellow score is claimed because the canopy and surrounding yellow field interact in this crop. Both the scoped comparison and overview sheet use the delivered revision-5 render and final revision 6.

The scope, previous-delivery render and comparison images are in `analysis/flames/shoulder/`. The additional orange-field and script measurements are documented in the iteration review; those colour regions are not isolated-flame scores.


## Reproduce

Run from the unpacked package root with Python 3, Pillow, NumPy and SciPy:

```bash
python3 source/analyze_flame_edges.py --candidate analysis/before_preview.png --reference analysis/reference-rectified.png --scope analysis/flames/regions_before_edits.json --label before --output-dir analysis/flames/before
python3 source/analyze_flame_edges.py --candidate artwork/BC_Forest_Service_Preview.png --reference analysis/reference-rectified.png --scope analysis/flames/regions_before_edits.json --label after --output-dir analysis/flames/after
python3 source/make_flame_review.py
```

The artwork paths are authored independently in `source/flames_v2.py`. The diagnostic masks never create or trace vector contours.

The scoped shoulder comparison can be reproduced independently:

```bash
python3 source/make_shoulder_review.py --reference analysis/reference-rectified.png --before analysis/flames/shoulder/before_preview.png --candidate artwork/BC_Forest_Service_Preview.png --scope analysis/flames/shoulder/scope_before_edit.json --output-dir analysis/flames/shoulder/review
```
