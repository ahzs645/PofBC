#!/usr/bin/env python3
"""Independent read-only adversarial audit of historical PHSA closing gates.

All mutations are in memory. Existing reviews, raw evidence, overlays and source
files remain unchanged. This exercises parsers; it is not new image coverage.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
from unittest import mock

import finish_salary_phsa_finalize as finalizer
import finish_salary_phsa_ledger as ledger
import finish_salary_phsa_resolutions as resolutions
import finish_salary_phsa_supersessions as supersessions
import finish_salary_phsa_triangulation as triangulation

ROOT = Path(__file__).resolve().parents[1]
AREA = ledger.AREA


def pin(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    cases = []

    def accepts(label, function):
        function()
        cases.append({"case": label, "expected": "accept", "passed": True})

    def rejects(label, function):
        try:
            function()
        except (ValueError, AssertionError, KeyError, TypeError, IndexError) as exc:
            cases.append({"case": label, "expected": "reject", "passed": True,
                          "errorType": type(exc).__name__, "reason": str(exc)})
            return
        cases.append({"case": label, "expected": "reject", "passed": False})

    candidate_path = AREA / "candidates/phsa-2015-16-source-v3.json"
    candidate = json.loads(candidate_path.read_text())
    provenance_path = ledger.COLLECTION / candidate["provenanceFile"]
    provenance = json.loads(gzip.decompress(provenance_path.read_bytes()))
    source = provenance["originalRowsAndPerFieldResolution"]
    inventory = next(s for s in json.loads((AREA / "source-inventory.json").read_text())["sources"]
                     if s["id"] == source["sourceId"])
    accepts("complete actual FY2015/16 held source validates", lambda: finalizer.validate_source(source, inventory))

    def mutated_source(change):
        value = copy.deepcopy(source)
        change(value)
        return finalizer.validate_source(value, inventory)

    for label, change in [
        ("wrong source id", lambda s: s.update(sourceId="phsa-2023-24")),
        ("wrong original SHA", lambda s: s.update(sourceSha256="0" * 64)),
        ("pending source field", lambda s: s["pendingFields"].append({"field": "name"})),
        ("missing physical page", lambda s: s["physicalPages"].pop()),
        ("duplicate physical page", lambda s: s["physicalPages"].append(s["physicalPages"][-1])),
        ("missing payload row", lambda s: s["rows"].pop()),
        ("wrong row number", lambda s: s["rows"][0].update(sourceRowOnPage=2)),
        ("invented job title", lambda s: s["rows"][0]["row"].__setitem__(2, "Invented")),
        ("boolean remuneration", lambda s: s["rows"][0]["row"].__setitem__(3, True)),
        ("floating remuneration", lambda s: s["rows"][0]["row"].__setitem__(3, 100000.0)),
        ("unparsed remuneration", lambda s: s["rows"][0]["row"].__setitem__(3, None)),
        ("qualified money route", lambda s: s["rows"][0]["fields"]["remuneration"].update(status="manual-qualified-source-typography")),
        ("unknown route", lambda s: s["rows"][0]["fields"]["name"].update(status="probably-correct")),
    ]:
        rejects("finalizer: " + label, lambda c=change: mutated_source(c))

    spec = importlib.util.spec_from_file_location("independent_queue_gate", ROOT / "scripts/review-salary-queue-completion.py")
    queue = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(queue)
    rows = [entry["row"] for entry in source["rows"]]
    accepts("actual held source passes separate root provenance gate",
            lambda: queue.verify_phsa_provenance(candidate, rows, provenance))
    for label, change in [
        ("pending route", lambda p: p["originalRowsAndPerFieldResolution"]["rows"][0]["fields"]["name"].update(status="pending-source-image-review")),
        ("printed residual silently changed", lambda p: p["originalRowsAndPerFieldResolution"]["diagnosticControlResiduals"].__setitem__(0, 0)),
        ("field route counts incomplete", lambda p: p["originalRowsAndPerFieldResolution"]["fieldResolutionCounts"]["name"].clear()),
        ("missing fiscal layout holdout", lambda p: p["rootHoldoutComparisons"].clear()),
    ]:
        value = copy.deepcopy(provenance)
        change(value)
        rejects("root provenance: " + label,
                lambda v=value: queue.verify_phsa_provenance(candidate, rows, v))

    holdout_paths = sorted(ledger.REVIEWS.glob("root-phsa-history-*-holdout-source-comparison.json"))
    accepts("nine actual closed holdouts /222 fields /four reviewer rereads",
            lambda: (_ for _ in ()).throw(AssertionError("counts differ"))
            if tuple(map(len, ledger.holdout_fields()[:2])) != (222, 9) or ledger.holdout_fields()[2] != 4 else None)
    first_review = json.loads(holdout_paths[0].read_text())
    packet_reference = first_review["sourceOnlyPacket"]
    candidate_reference = first_review["candidate"]
    original_pinned = ledger.pinned
    for label, reference, change in [
        ("packet source mismatch", packet_reference, lambda p: p.update(sourceId="phsa-1900-01")),
        ("candidate source mismatch", candidate_reference, lambda p: p.update(sourceId="phsa-1900-01")),
        ("candidate outside declared packet", packet_reference, lambda p: p["fullCandidate"].update(sha256="0" * 64)),
        ("only nine selected rows", candidate_reference, lambda p: p["rows"].pop()),
        ("duplicate selected row", candidate_reference, lambda p: p["rows"].__setitem__(1, copy.deepcopy(p["rows"][0]))),
        ("widen requested field scope", candidate_reference, lambda p: p["rows"][0]["reviewTargetFields"].append("invented")),
    ]:
        def changed(ref, target=reference, operation=change):
            value = copy.deepcopy(original_pinned(ref))
            if ref == target:
                operation(value)
            return value
        with mock.patch.object(ledger, "pinned", side_effect=changed):
            rejects("holdout: " + label, ledger.holdout_fields)
    original_glob = Path.glob
    def missing_layout(path, pattern):
        if path == ledger.REVIEWS and pattern == "root-phsa-history-*-holdout-source-comparison.json":
            return iter(holdout_paths[:-1])
        return original_glob(path, pattern)
    with mock.patch.object(Path, "glob", missing_layout):
        rejects("holdout: eight layouts cannot imply all-nine pass", ledger.holdout_fields)

    closed_count = 0
    for path, digest in resolutions.CLOSED_CASE_POLICIES:
        policy = resolutions.pinned(path, digest)
        for authority in policy["approvedCases"]:
            review = {"sourceId": authority["sourceId"], "sourceSha256": authority["sourceSha256"],
                      "batch": authority["batch"], "closedSourceNameQualificationLedgers": [authority["exactCaseLedger"]]}
            accepts("exact closed authority: " + authority["sourceId"] + ":" + str(authority["physicalPage"]) + ":" + str(authority["sourceRowOnPage"]),
                    lambda v=review: resolutions.closed_source_cases(v))
            wrong = copy.deepcopy(review)
            wrong["batch"] += "-other"
            rejects("closed exception cannot move fiscal batch", lambda v=wrong: resolutions.closed_source_cases(v))
            closed_count += 1

    overlay_paths = sorted((AREA / "overlays").glob("phsa-*-*.json"))
    selected, selections = supersessions.selected(overlay_paths)
    accepts("old corrected overlay remains archived and effective v2 selected",
            lambda: (_ for _ in ()).throw(AssertionError("selection differs"))
            if AREA / "overlays/phsa-2018-19-manual-overlay-002.json" in selected
            or AREA / "overlays/phsa-2018-19-manual-overlay-002-v2.json" not in selected else None)
    confirmations = triangulation.confirmations()
    accepts("every existing monetary confirmation byte-replays pinned peer evidence", lambda: confirmations)
    confirmation_paths = sorted((AREA / "triangulation").glob("money-peer-confirmations-*.json"))
    if confirmation_paths:
        target = confirmation_paths[0]
        original_bytes, original_text = Path.read_bytes, Path.read_text
        value = json.loads(target.read_text())
        value["confirmations"][0]["confirmedValue"] += 1
        altered = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
        with mock.patch.object(Path, "read_bytes", lambda p: altered if p == target else original_bytes(p)), \
             mock.patch.object(Path, "read_text", lambda p, *a, **k: altered.decode() if p == target else original_text(p, *a, **k)):
            rejects("derived confirmation cannot change money while pinned original peer stays fixed", triangulation.confirmations)

    return {"reviewer": "/root/recovery_review", "method": "Independent read-only implementation assessment with actual held/source artifacts and synthetic in-memory negative cases.",
            "script": pin(Path(__file__).resolve()), "codeInputs": [pin(ROOT / "scripts" / name) for name in [
                "finish_salary_phsa_policy.py", "finish_salary_phsa_ledger.py", "finish_salary_phsa_finalize.py",
                "finish_salary_phsa_resolutions.py", "finish_salary_phsa_supersessions.py", "finish_salary_phsa_triangulation.py",
                "review-salary-queue-completion.py"]], "actualHeldSourceMetadata": pin(candidate_path),
            "actualHeldSourceProvenance": pin(provenance_path), "cases": cases,
            "caseCount": len(cases), "failedCases": sum(not c["passed"] for c in cases),
            "exactClosedCaseAuthoritiesChecked": closed_count, "effectiveOverlayRevisionSelections": selections,
            "monetaryConfirmationFieldsReplayedAtAudit": len(confirmations),
            "limits": ["No new literal original-image transcription or whole-source acceptance is claimed by code tests.",
                       "The consumers read pinned holdout data internally for validation; no literal holdout names or amounts are output or used for new blind readings.",
                       "All nine scopes still require complete manual/qualification/financial/source-control closures and root acceptance.",
                       "This snapshot does not certify later unreviewed implementation changes."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run()
    path = ROOT / args.out
    with path.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"path": str(path.relative_to(ROOT)), "sha256": pin(path)["sha256"],
                      "caseCount": result["caseCount"], "failedCases": result["failedCases"]}))
    if result["failedCases"]:
        raise SystemExit(1)
