#!/usr/bin/env python3
"""Independent, read-only adversarial checks for the PHSA field classifier.

Uses the already image-reviewed first-table p2/r1 solely as a schema fixture.
All mutations are synthetic in-memory cases; none alleges an actual OCR error.
Does not open machine alternatives for the ninety blind holdout rows.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_policy as policy

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "research/salaries/queue-completion-phsa/evidence/phsa-2015-16-rows-p002.json.gzip"


def pin(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    page = json.loads(gzip.decompress(FIXTURE.read_bytes()))
    original = page["rows"][0]
    cases = []

    def check(label, field, expected, change=lambda row, page: None, name="Example,John"):
        item = copy.deepcopy(original)
        sample_page = copy.deepcopy(page)
        item["candidateRow"][1] = name
        item["candidateRow"][3:5] = [100001, 1]
        item["fieldConflicts"] = {
            "name": ["tesseract-name-confidence-below-85"],
            "remuneration": ["tesseract-pay-confidence-below-90"],
            "expenses": ["tesseract-expense-confidence-below-90"],
        }
        for engine in ("tesseract", "rapidocr"):
            item[engine]["name"] = name
            item[engine]["pay"] = {"kind": "number", "value": 100001, "raw": "100,001"}
            item[engine]["expense"] = {"kind": "number", "value": 1, "raw": "1"}
        item["expenseOriginalImage"]["blank"] = False
        item["expenseOriginalImage"]["matchesSourceCalibratedDashGeometry"] = False
        change(item, sample_page)
        before = copy.deepcopy((item, sample_page))
        result = policy.classify(item, sample_page)
        actual = result["fields"][field]["eligibleToResolveUnreservedConfidenceOnly"]
        cases.append({"case": label, "field": field, "expectedEligible": expected,
                      "actualEligible": actual, "passes": actual is expected,
                      "inputUnchanged": before == (item, sample_page),
                      "exclusions": result["fields"][field]["exclusions"]})

    for field in ("name", "remuneration", "expenses"):
        check("confidence-only exact agreement: " + field, field, True)
        check("unknown confidence-like flag: " + field, field, False,
              lambda r, p, f=field: r["fieldConflicts"][f].append("unparsed-confidence-below-unknown"))
        check("hard original flag: " + field, field, False,
              lambda r, p, f=field: r["fieldConflicts"][f].append("independent-disagreement"))
        check("reader missing: " + field, field, False, lambda r, p: r.update(rapidocr=None))
        check("no original flags is not a confidence resolution: " + field, field, False,
              lambda r, p, f=field: r["fieldConflicts"].pop(f))
        check("invalid date: " + field, field, False, lambda r, p: p.update(dateTitleNeedsReview=True))
        check("invalid geometry: " + field, field, False, lambda r, p: p.update(pageGeometryNeedsReview=True))
        check("render hash mismatch: " + field, field, False,
              lambda r, p: p.update(sourceImageSha256="0" * 64))
        check("original hash mismatch: " + field, field, False,
              lambda r, p: p.update(sourceSha256="0" * 64))
    for field, token, index in (("remuneration", "pay", 3), ("expenses", "expense", 4)):
        for value in (0, -1, 1.5, True):
            def change(row, page, v=value, t=token, i=index):
                row["candidateRow"][i] = v
                for engine in ("tesseract", "rapidocr"):
                    row[engine][t].update(value=v)
            check("nonpositive/noninteger both " + token + ": " + repr(value), field, False, change)
        for value in (True, 1.0):
            check("right numeric type must be strict integer: " + token + ": " + repr(value), field, False,
                  lambda r, p, v=value, t=token, i=index: (
                      r["candidateRow"].__setitem__(i, 1), r["tesseract"][t].update(value=1),
                      r["rapidocr"][t].update(value=v)))
            check("candidate numeric type must be strict integer: " + token + ": " + repr(value), field, False,
                  lambda r, p, v=value, t=token, i=index: (
                      r["candidateRow"].__setitem__(i, v), r["tesseract"][t].update(value=1),
                      r["rapidocr"][t].update(value=1)))
        check("independent value disagreement: " + token, field, False,
              lambda r, p, t=token: r["rapidocr"][t].update(value=999))
        check("candidate differs: " + token, field, False,
              lambda r, p, i=index: r["candidateRow"].__setitem__(i, 999))
        check("unparsed independent amount: " + token, field, False,
              lambda r, p, t=token: r["rapidocr"][t].update(kind="unparsed"))
    check("expense region blank", "expenses", False,
          lambda r, p: r["expenseOriginalImage"].update(blank=True))
    check("expense region calibrated dash", "expenses", False,
          lambda r, p: r["expenseOriginalImage"].update(matchesSourceCalibratedDashGeometry=True))
    for name in ("Example,Ian", "Example,John I.", "McIlhargey,John", "Example,AIl", "Example,John^",
                 "Al-Ibrahim,John", "D'Ippolito,John", "D’Ippolito,John",
                 "Example,Jo!hn", "Example,Jo¥hn", "Example,Jo§hn", "Example,John]", "Example,John*"):
        check("additional name guard: " + name, "name", False, name=name)
    for name in ("deHaan,John", "Example,lan", "Example,Jo|hn", "Example,John2", "Example.John", "Example,JohnPaul"):
        from finish_salary_phsa_stage import suspicious_name
        check("retained original name guard: " + name, "name", False,
              lambda r, p, n=name: r["fieldConflicts"]["name"].extend(suspicious_name(n)), name=name)
    check("existing comma/whitespace comparison allowed", "name", True,
          lambda r, p: r["rapidocr"].update(name=" Example ,  John "))
    reserved, reserved_rows = policy.reserved_fields()
    return {
        "reviewer": "/root/recovery_review",
        "method": "Read-only synthetic adversarial regression tests on an already independently image-reviewed schema fixture; no new source reading or holdout candidate inspection.",
        "script": pin(Path(__file__).resolve()), "classifier": pin(ROOT / "scripts/finish_salary_phsa_policy.py"),
        "classifierDependencies": [pin(ROOT / "scripts" / filename) for filename in (
            "finish_salary_phsa_calibration.py", "finish_salary_phsa_rows.py",
            "finish_salary_phsa_stage.py", "finish_salary_phsa_batches.py")],
        "fixture": pin(FIXTURE), "policy": pin(policy.POLICY),
        "cases": cases, "caseCount": len(cases), "failedCases": sum(not r["passes"] for r in cases),
        "allInputsUnchanged": all(r["inputUnchanged"] for r in cases),
        "reservedFieldCountAtAudit": len(reserved), "reservedRowCountAtAudit": len(reserved_rows),
        "limits": ["Synthetic parser-type/unknown-flag cases are defensive tests, not observed source errors.",
                   "Classifier tests do not establish that its caller enforces reservation, ledger closure, or source acceptance gates.",
                   "Independent holdout selection/integration and ninety original-image rows remain separate gates."]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
