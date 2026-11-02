"""Freeze or verify the completed PHSA2011/12 +2012/13 peer handoff."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
FREEZE = BASE / 'phsa-history-peer-freeze.json'
HANDOFF = BASE / 'handoff.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=sha(path))


def files():
    local = [p for p in BASE.rglob('*') if p.is_file() and p not in [FREEZE, HANDOFF]
             and 'integration' not in p.relative_to(BASE).parts]
    return sorted(local + list((ROOT / 'scripts').glob('gap_school_north_peer_phsa*.py')))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        freeze = json.loads(FREEZE.read_text())
        assert [pin(p) for p in files()] == freeze['files']
        handoff = json.loads(HANDOFF.read_text())
        assert handoff['freeze'] == pin(FREEZE)
        for source in handoff['sources']:
            receipt = ROOT / source['independentReceipt']['path']
            assert pin(receipt) == source['independentReceipt']
            accepted = json.loads(receipt.read_text())
            assert pin(ROOT / accepted['selectedSnapshot']['path']) == accepted['selectedSnapshot']
            for reference in accepted['primaryReceiptPins']:
                assert pin(ROOT / reference['path']) == reference
        print(json.dumps(dict(status='passed', peerFiles=len(freeze['files']), namedRows=handoff['namedRows'],
                              freezeSha256=sha(FREEZE), handoffSha256=sha(HANDOFF))))
        return
    assert not FREEZE.exists() and not HANDOFF.exists()
    sources = []
    for key in ['phsa-2011-12', 'phsa-2012-13']:
        path = BASE / f'{key}-independent-bounded-source-review.json'
        receipt = json.loads(path.read_text())
        assert receipt['allPersonallyReadFieldsMatchFinal'] and receipt['residualComputedMinusPrinted'] == [0, 0]
        sources.append(dict(sourceKey=key, status='accepted-bounded-independent-source-review',
                            sourceSha256=receipt['sourceSha256'], namedRows=receipt['namedRows'],
                            uniquePersonallyReadRows=receipt['uniquePersonallyReadRows'],
                            selectedSnapshot=receipt['selectedSnapshot'], independentReceipt=pin(path),
                            printedAndComputedNamedComponents=receipt['literalComputedNamedComponents'],
                            nullExpenses=receipt['selectedNullExpenses']))
    FREEZE.write_text(json.dumps(dict(scope='Only new PHSA peer files; previously frozen north/south/board inputs unchanged.',
                                      excludedReservedSubtree='integration/', files=[pin(p) for p in files()]), indent=2) + '\n')
    HANDOFF.write_text(json.dumps(dict(status='ready-for-root-integration', sources=sources, namedRows=6774,
                                       uniquePersonallyReadRows=878, personalReadingsIncludingOverlaps=897,
                                       allInitialSourceOnlyTargetsReadBeforeRawCandidateAccess=804,
                                       additionalSourceOnlyAdaptiveTargets=25, independentHoldouts=40,
                                       independentExpenseCalibrationRows=28, trueFieldGeometryFlags=581,
                                       completeOriginalPaymentCensus=True, completeRawReaderReplay=True,
                                       completeOriginal300dpiRasterReplay=True, completeTargetCropPixelReplay=True,
                                       remainingSourceReviewBlockers=[], noOutreach=True,
                                       controls='Both named remuneration/expense totals match source literally; no balancing adjustments.',
                                       sourceQualifications=['Payment disclosures above75000, not complete employee rosters or annual base rates.',
                                                             'Positions undisclosed; aggregate occupational counts do not assign individual jobs.',
                                                             'Personal field review is bounded to the exact878 unique rows. All6774 rows have independent source payment-band census and two retained raw-reader replay; no infallibility claim.',
                                                             'Exactly2397 source-dash expense cells stay null; all nine observed numeric expenses below10 personally source-read.',
                                                             'Initial peer transcription errors, primary Moosa271 expense omission, clipping and isolated blank-page scan speck are retained and resolved additively from originals.'],
                                       downstreamRootTask='Map accepted selected payloads exactly to normalized data/provenance, retain compiled partitions unless separately proved, adopt receipts and integrate. This handoff does not edit a global registry or public outputs.',
                                       futureMappingOverlayLocation=str((BASE / 'integration').relative_to(ROOT)),
                                       checks=['python scripts/gap_school_north_peer_phsa_handoff.py --check',
                                               'python scripts/gap_school_north_peer_phsa_acceptance.py --key phsa-2011-12 --selected research/salaries/gap-fill-2026-11-02/phsa_history/phsa-2011-12-scan-selected-v2.json.gzip --revision v2 --check',
                                               'python scripts/gap_school_north_peer_phsa_acceptance.py --key phsa-2012-13 --selected research/salaries/gap-fill-2026-11-02/phsa_history/phsa-2012-13-scan-selected-v2.json.gzip --revision v2-source-reread --check',
                                               'python scripts/gap_school_north_peer_phsa_crop_replay.py --check',
                                               'python scripts/gap_school_north_peer_phsa_crop_replay.py --adaptive2012 --check',
                                               'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/held-health-ocr/venv/bin/python scripts/gap_school_north_peer_phsa_replay.py --check'],
                                       freeze=pin(FREEZE)), indent=2) + '\n')
    print(json.dumps(dict(status='frozen', freeze=pin(FREEZE), handoff=pin(HANDOFF))))


if __name__ == '__main__':
    main()
