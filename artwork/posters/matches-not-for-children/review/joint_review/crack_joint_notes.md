> Package location note: the inventory and worktree paths below describe the isolated joint development. Its listed PNG proofs and reference mask are preserved in `review/joint_review/`, and its QA script is `source/analysis_records/crack_joint_qa.py`. The current paint-integrated proofs are `BCFS_Child_Crack_Details.png` and `BCFS_Child_Crack_Overlay.png` at the package root. Final-master measurements are in `review/Joint_Measurements.json`; `source/analyze_revision4.py` is their portable regeneration entry point. The normalized photo is `review/Reference_Perspective_Normalized.png`, and the supplied detail crop is `source/Crack_Reference_Crop.png`.

# Revision 4 — the child's cracked match junction

## Stable deliverables

- `crack_joint.svg`: transparent 1000 × 1400 component, containing five paths.
- `crack_joint.py`: deterministic generator; Python standard library only.
- `crack_joint_qa.py`: separate diagnostic script for the registered photograph
  and saved V3 master. It does not generate the reconstruction geometry.
- `joint-analysis/joint-photo-v3-v4.png`: enlarged integration proof.
- `joint-analysis/joint-overlay-v3-v4.png`: registered source-ink comparison.
- `joint-analysis/joint-metrics.json`: main and sensitivity measurements.
- `joint-analysis/joint-validation.json`: change bounds and preservation checks.
- `joint-analysis/reference-ink-mask-125.png`: main fixed diagnostic mask.
- `joint-analysis/joint-v3-full.png` and `joint-v4-full.png`: native 1000 × 1400
  proof renders used for the measurements and change bounds.

The final component is stable. Its first clipped-redraw draft was rejected
because enlarged rendering revealed hairline antialias seams. The final SVG
has **no clip paths** and does not redraw the long shaft runs.

## Required integration

Keep `child-body-left-leg`, `child-right-leg-shaft`, and the other match
components in their existing positions. Remove only the obsolete final hip
entry from the `threads` list in `figures()`:

```python
('M330 779 L342 796 M336 778 L333 791 L325 785 M337 786 L341 776 M334 792 L330 800', 1.4)
```

After the remaining thread/tie group, append the children of `crack_joint.svg`
at the end of `figures()`. Equivalently, append
`crack_joint.joint_group(paper=PAPER, ink=INK)` when importing the generator.
The existing default colours are `#e7f3f2` and `#1d2424`, matching the master.
The obsolete star must be removed; leaving it underneath can leave small ink
remnants outside the deliberately narrow paper cutout.

No original long shaft path needs to be replaced. The component contains:

1. A small paper-coloured internal cutout that clears the old thick diagonal
   divider.
2. An 11-unit continuation of the existing upper right-leg rail, on exactly
   its original centreline, to preserve the rail across that cutout.
3. The torn upper shoulder.
4. The narrow irregular fracture seam.
5. The compact lower splinter silhouette.

## Photographic evidence and construction

The primary geometric reference is `work/reference-rectified.png`, using the
existing 1000 × 1400 perspective registration. The user-supplied
`upload/Screenshot 2026-11-20 at 6.26.59 PM.png` confirms the structural reading.
The photograph shows a small angular shoulder extending left from the torso's
right rail, a pinched pale opening, and a narrow irregular ink seam leading
into several tapered splinters. The former thick diagonal divider filled that
opening, and the former stroked star sat on top of it.

The replacement is manually authored from enlarged visual inspection. The
paper opening and connected ink shapes are rebuilt together, rather than
adding decorative lines to the previous divider. No bitmap tracing, automatic
contour extraction or random texture is used. The reference masks are kept
separate and used only for review.

## Fixed-registration measurements

The photograph and both artwork renders share the same existing registration.
Dark ink is classified by `max(R,G,B) < 125` for the main comparison. Separate
90, 110 and 140 thresholds check the result's sensitivity to the blurred
photographic boundary. The target is identical for both candidates at each
threshold. Distances are normalized source pixels.

| Region | V3 ink IoU | V4 ink IoU | V3 mean edge distance | V4 mean edge distance | V3 p95 | V4 p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Local joint, x=320–354 / y=763–804 | 68.24% | 81.22% | 0.89 | 0.56 | 2.85 | 1.41 |
| Fracture and splinters, x=325–345 / y=766–799 | 53.02% | 76.23% | 1.14 | 0.57 | 3.16 | 1.41 |
| Wider context, x=307–372 / y=758–826 | 74.29% | 80.74% | 0.82 | 0.65 | 2.00 | 1.41 |

Fracture-region IoU also improves at each sensitivity threshold:

| Threshold | V3 | V4 |
| --- | ---: | ---: |
| 90 | 51.23% | 73.42% |
| 110 | 53.63% | 75.00% |
| 125 | 53.02% | 76.23% |
| 140 | 53.56% | 77.12% |

These are localized photographic-fit diagnostics, not historical-authenticity
scores. Their precision is limited by the small number of source pixels and
photographic blur.

## Preservation and rendering checks

At the native 1000 × 1400 rendering, 353 pixels change between the V3 master
and this integrated candidate. Every changed pixel lies within the exclusive
bounds `[324,765,358,800]`; zero pixels change outside the declared local
envelope `[324,764,360,802]`.

The white cutout has zero pixels outside the existing V3 white reserve. Its
underlying artwork pixels are all paper, ink, or their antialias mixtures:
none differ from that colour segment by more than three RGB-code units of
Euclidean distance. This verifies that the cutout does not wipe coloured
pigment residue. The surrounding paint, outer white contour and long rails
remain unchanged.

Existing named elements retain their exact attributes. The integration removes
only the old unnamed hip-star path and adds the new local group. Enlarged
direct vector rendering confirms that the internal repair has no clipped-rail
seams. The SVG contains no raster image, text or filter elements. Regeneration
from `crack_joint.py` is byte-identical.

## Reproducibility and limits

The SVG generator has no external dependencies or absolute filesystem paths;
it writes the SVG beside itself. Regenerating the final component does not
require the photograph. Repeating the QA requires Python with NumPy, Pillow
and SciPy, plus Inkscape; the script expects this worktree's saved V3 master
and normalized reference at the paths noted above. All inputs needed for
understanding the manual construction are identified here; no font or hidden
source asset is used.

The photograph does not resolve microscopic wood fibres or the exact printed
edge of each thin tip. The reconstruction keeps only supported visible forms.
It does not establish physical poster dimensions, calibrated colour, or an
artist attribution.
