# Pass04 independent assessment

## Overall judgment

Prefer Pass04's curved lower boughs over Pass02. At native logo size the tree reads less mechanically cut; the upper/middle topology corrections remain clear improvements. No serious new topology defect appeared. The lower metric regression is largely about loss of ink weight at the base, not a reason to restore the earlier angular bough geometry.

## Region measurements at the same 0.75 dark-density threshold

| Native source region | Pass02 IoU | Pass04 IoU | Pass02 density MSE | Pass04 density MSE |
|---|---:|---:|---:|---:|
| Lower counter x0-24,y113-129 | 0.704 | 0.736 | 0.1150 | 0.0984 |
| Lower bowl x7-29,y129-138 | 0.773 | 0.733 | 0.0754 | 0.0960 |
| Bottom flick x0-34,y138-141 | 0.865 | 0.333 | 0.0562 | 0.0868 |

In the bottom-flick region, source has48 dark foreground pixels; Pass02 has49 and Pass04 only16. That local loss explains much of the lower-region threshold regression.

## Conservative final changes

1. **Restore some base depth while retaining the curve.** Pass04's model spine/base ends at about139.6, transformed to canvas y139.43 by the existing affine. This provides only around half coverage in native row139; the source row139 is mainly dark, while row140 is almost blank. An actual bottom around139.85-140.0 is a better target. Account for any whole-tree optical dy before editing. The lower curved bowl also lost some weight; it may need roughly0.4-0.5px additional depth aroundx14-21 if the whole-tree adjustment does not recover it.

2. **Optional modest counter narrowing.** The new counter is better than Pass02 by both measures, but still somewhat too wide/horizontal. Its source shape reads as a diagonal channel mostlyx10-17, from around(15.5,115.5) toward(10.5,121). The current counter extends roughlyx8-19. Bring its left wall in1-2px and reduce the rightward projection nearx18-20/y118, while retaining the curved tongue. This is optional if further edits introduce regressions.

## Stop judgment

After a conservative optical adjustment and restoring the base/bowl weight, I would stop detailed local surgery unless the final overlay reveals a new coherent shape problem. Remaining high-frequency differences include blurred edge coverage and tiny source marks that do not support confident reconstruction. Do not sacrifice the cleaner branch flow to improve a single threshold score.

## Review images

- pass02-pass04-native.png
- pass02-pass04-lower.png
- pass04-lower.png

No model files were edited.
