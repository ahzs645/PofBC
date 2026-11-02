#!/usr/bin/env python3
"""Independent additive audit of source-money replay and preserved first readings.

All adversarial changes are in memory. This adds checks to the immutable first
gate-audit helper and does not rewrite source evidence or existing receipts.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from unittest import mock

import finish_salary_phsa_quality_final_gates as previous
import finish_salary_phsa_money_peer as money
import finish_salary_phsa_ledger as ledger

ROOT = Path(__file__).resolve().parents[1]


def pin(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    base = previous.run()
    cases = []

    def accepts(label, callback):
        callback()
        cases.append({"case": label, "expected": "accept", "passed": True})

    def rejects(label, callback):
        try:
            callback()
        except (ValueError, AssertionError, KeyError, TypeError, IndexError) as exc:
            cases.append({"case": label, "expected": "reject", "passed": True,
                          "reason": str(exc), "errorType": type(exc).__name__})
            return
        cases.append({"case": label, "expected": "reject", "passed": False})

    original_pinned = ledger.pinned
    replayed = []
    inputs = []
    for path in sorted((ledger.AREA / "triangulation").glob("money-peer-confirmations-*.json")):
        document = json.loads(path.read_text())
        if document.get("adapter") != "count-independent-source-money-peer-v1":
            continue
        peer_ref = document["peerInputs"][0]
        overlay_ref = document["confirmations"][0]["effectiveAuthorOverlay"]
        peer = original_pinned(peer_ref)
        accepts("exact source-money replay " + path.name,
                lambda p=peer_ref, o=overlay_ref, d=document:
                (_ for _ in ()).throw(AssertionError("derived bytes differ"))
                if money.build(p, o) != d else None)
        replayed.append({"confirmation": pin(path), "fields": len(document["confirmations"]),
                         "receiptSchema": document["sourceReceiptSchema"]})
        inputs.extend([peer_ref, overlay_ref])

        def mutation(label, reference, change):
            def modified(ref):
                value = copy.deepcopy(original_pinned(ref))
                if ref == reference:
                    change(value)
                return value
            with mock.patch.object(ledger, "pinned", side_effect=modified):
                rejects(path.name + ": " + label,
                        lambda: money.build(peer_ref, overlay_ref))

        mutation("wrong overlay source", overlay_ref,
                 lambda d: d.update(sourceSha256="0" * 64))
        mutation("missing overlay money field", overlay_ref,
                 lambda d: next(r for r in d["overlays"]
                                if r["physicalPage"] == document["confirmations"][0]["physicalPage"]
                                and r["sourceRowOnPage"] == document["confirmations"][0]["sourceRowOnPage"])
                 ["reviewedFields"].remove(document["confirmations"][0]["field"]))

        if "freshOriginalImageFirstTranscript" in peer:
            raw_ref = peer["freshOriginalImageFirstTranscript"]
            choices_ref = peer["authorChoicesFrozenBeforePeerValuesOpened"]
            choices = original_pinned(choices_ref)
            packet_ref = choices["sourceOnlyPacket"]
            author_raw_ref = choices["independentOriginalImageFirstTranscript"]
            author_amendment_ref = choices["authorOwnPostComparisonSourceReread"]
            mutation("invented author first value", choices_ref,
                     lambda d: d["rows"][0].__setitem__("initialImageFirstValue",
                                                       d["rows"][0]["initialImageFirstValue"] + 1))
            mutation("invented author final value", choices_ref,
                     lambda d: d["rows"][0].__setitem__("finalAuthorSourceValue",
                                                       d["rows"][0]["finalAuthorSourceValue"] + 1))
            mutation("changed original peer first value", raw_ref,
                     lambda d: d["readingsInPacketOrder"].__setitem__(0,
                                                                   d["readingsInPacketOrder"][0] + 1))
            mutation("changed raw author source identity", author_raw_ref,
                     lambda d: d.update(sourceId="phsa-1900-01"))
            mutation("hidden author first-reading correction", author_amendment_ref,
                     lambda d: (d.get("ownCorrections") or [d["ownCorrection"]])[0]
                     .__setitem__("initialReading", 1))
            mutation("duplicate source target", packet_ref,
                     lambda d: d["rows"].append(copy.deepcopy(d["rows"][0])))
            mutation("missing source target", packet_ref, lambda d: d["rows"].pop())
            mutation("wrong source target identity", packet_ref,
                     lambda d: d.update(sourceSha256="0" * 64))
            mutation("forged original crop", packet_ref,
                     lambda d: d["rows"][0].update(originalFullRowCropSha256="0" * 64))
            mutation("source image moved to unrelated hash", choices_ref,
                     lambda d: d["rows"][0]["actual600SourceField"].update(sha256="0" * 64))
            mutation("first-pass freeze flag removed", raw_ref,
                     lambda d: d.update(authorOrOcrChoicesOpened=True))
        elif "independentImageFirstTranscript" in peer and "originalRootTranscript" in peer:
            raw_ref = peer["independentImageFirstTranscript"]
            raw = original_pinned(raw_ref)
            packet_ref = raw["sourceOnlyPacket"]
            mutation("duplicate mixed requested target", packet_ref,
                     lambda d: d["rows"].append(copy.deepcopy(d["rows"][0])))
            mutation("mixed peer missing requested name field", peer_ref,
                     lambda d: d["rows"].pop())
            mutation("mixed source peer opened choices", raw_ref,
                     lambda d: d.update(frozenBeforeRootAuthorOrOcrChoices=False))
            mutation("mixed source raw original differs", peer["originalRootTranscript"],
                     lambda d: d.update(frozenBeforeCandidateOpening=False))

    for value in [True, False, 1.0, 0, -1, None, "100000"]:
        rejects("fresh-positive money rejects " + repr(value), lambda v=value: money.positive(v))
    accepts("fresh-positive money accepts literal positive int", lambda: money.positive(100000))

    return {"reviewer": "/root/recovery_review", "reviewedOn": "2026-11-02",
            "method": "Independent implementation inspection plus actual pinned source-money replays and adversarial in-memory mutations. No evidence files mutated.",
            "script": pin(Path(__file__).resolve()), "previousHelper": pin(Path(previous.__file__).resolve()),
            "moneyPeerImplementation": pin(Path(money.__file__).resolve()),
            "currentGateImplementationPins": base["codeInputs"],
            "previousGateChecksReplayedAgainstCurrentImplementation": base,
            "sourceMoneyEvidenceInputs": inputs, "sourceMoneyReplays": replayed,
            "newCases": cases, "newCaseCount": len(cases),
            "combinedCaseCount": base["caseCount"] + len(cases),
            "failedCases": base["failedCases"] + sum(not c["passed"] for c in cases),
            "limits": ["This audit does not personally transcribe new source rows or certify a later implementation revision.",
                       "Source-image hashes prove evidence identity; literal glyph readings remain the independently frozen human records.",
                       "Zero, negative, missing and genuinely uncertain source money cannot use this positive-money adapter; they remain separately gated.",
                       "All-nine publication still requires complete effective field ledgers, exact qualifications, fresh-money closures and literal printed-control residuals."]}


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
                      "combinedCaseCount": result["combinedCaseCount"], "failedCases": result["failedCases"]}))
    if result["failedCases"]:
        raise SystemExit(1)
