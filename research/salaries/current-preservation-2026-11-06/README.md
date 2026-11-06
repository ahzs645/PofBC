# Current consolidation preservation gate

Baseline: main commit `7399fde18d2b278f5e99e2e201b915adadc7a8e2`.

`baseline.json.gzip` was produced from `git archive` of that exact commit, not
from mutable working-tree exports. It freezes 1,440,498 observations as 1,668
source/employer/period multiset hashes. Each row fingerprint includes employer,
period, disclosed name and position, exact integer-cent remuneration and nullable
expenses, source ID, and physical PDF page. Sorted lists retain duplicates.
The manifest also freezes source metadata, original collection registration,
34,284 original research-file SHA-256 hashes, and published labelled name links.
It contains no duplicated full salary rows.

Only the top-level explanatory README, generated coverage/source inventories,
generated name-link decisions CSV and summary, and collection registration are
excluded from byte preservation. Collection registration must append exactly the
four approved imports, once each, without changing prior order or metadata.
Every original review receipt, including 461 source-backed decisions, stays pinned.

Run `python3 scripts/check_salary_current_preservation.py`. It requires no git
history and performs no writes. It proves all old rows remain, with only the
1,752 exact audited West Vancouver name/title splits reversed for comparison;
all 228,364 compiled observations remain; and exactly 4,960 approved observations
are added (2,428 provincial elected, 743 Assembly staff, 1,237 VPD, and 552 early
provincial administration observations (310 deputies and 242 cabinet rows)). Approved new
manifests and the exact correction list are pinned in the checker. Each manifest
must be accepted, normalized and original source bytes must match its SHA-256,
and the live rows must match its complete row multiset exactly once. Unknown
source IDs, held-source publication, monetary edits, duplicate additions,
anonymous-row loss, source metadata changes, and original research edits fail.
The original USD annotation/ranking policy and verified/likely link graph are
checked against current exports, not assumed from historical checks. The 599
obsolete name-plus-title aliases that collapse to the same audited clean name
are normalized only by the exact pinned correction list.

`confidence-withdrawals.json` pins exactly two automatic heuristic transitions
from verified to likely: Vancouver Police Palmer A A / Palmer A, and West
Vancouver Stuart Sharon / Stuart S. New official observations and restored titles
increase the number of title-holding name keys beyond the unchanged three-key
"distinctive title" limit. The old and current reasons and entire before/current
employer observation multisets are pinned. This withdraws unsupported certainty,
not the relationship, and does not assert different identities. All 461
source-backed review receipts remain byte-identical. No other confidence
withdrawal is allowed. Regression tests reject additional transitions, changed
observation evidence, and altered graph reasons.

`baseline-links.tar.gzip` contains byte-exact main link exports with normalized
archive metadata. `scripts/check_follow_through_name_replay.py --check` uses them
in an isolated historical context, reconstructing original-source people rows
from current rows with the exact audited inverse. It runs the unchanged original
source-copy receipt generator and repeat-review validator. It never rewrites old
receipts or treats changed global link-index metadata as new historical evidence.
The original sixteen frozen historical release gates remain separate in CI.

Held-review decisions also validate against the reconstructed byte-exact original
people cohort rather than expanded current name histories. The early deputy
import adds three exact-spelling Jessica L McDonald observations (2003/04 through
2005/06) to a name covered by one historical professional-identity spelling
receipt. That receipt, its original observations, and its validator remain
unchanged; the import does not issue a new review or add a new reviewed pair.
Regression tests ensure appended earlier rows do not rewrite receipts, while
changing or deleting any original row still fails reconstruction.

The maintainer-only `--freeze-from` option expects a checkout extracted with
`git archive` of the above baseline. The resulting SHA-256 must match the pinned
checker constant. It is not an automatic baseline refresh and is never used in CI.
