#!/usr/bin/env python3
"""Offline, pinned reconstruction of the finite nine-original PHSA history batch.

Processing/OCR tools are intentionally absent from this module.  The committed
two-reader evidence, explicit image readings, independent review and source
context decisions must already exist before a normalized candidate is written.
"""
import argparse
import collections
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re

from gap_phsa_history_fetch import AREA, ROOT
from gap_phsa_history_select import run as replay_selection

COLLECTION = ROOT / 'research/salaries/gap-fill-phsa-history'
EMPLOYER = 'provincial-health-services-authority'
FIELDS = ['name', 'position', 'remuneration', 'expenses', 'pdfPage']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gzip') else raw)


def encoded(value):
    return gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)


def ref(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def pinned(reference):
    path = ROOT / reference['path']
    assert sha(path.read_bytes()) == reference['sha256'], ('stale evidence', reference['path'])
    return decode(path)


def source_name(value):
    assert isinstance(value, str) and value.strip()
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value).strip())


def number(value):
    if value is None:
        return None
    amount = Decimal(str(value))
    assert amount.is_finite()
    return int(amount) if amount == amount.to_integral_value() else float(amount)


def normalized_rows(key, evidence, input_kind):
    """Reconstruct literal published observations, preserving order and repeats."""
    if input_kind == 'native':
        assert not evidence['fieldDifferences']
        one, two = evidence['popplerRows'], evidence['mupdfRows']
        assert [[r[f] for f in FIELDS] for r in one] == [[r[f] for f in FIELDS] for r in two]
        rows = [{**r, 'position': None} for r in one]
    else:
        assert not evidence['pending'], ('unclosed source exceptions', key)
        replayed = replay_selection(key, evidence['candidateRevision'], 'offline-only', write=False)
        # Tuple benchmark pairs in memory are JSON lists on disk.
        assert json.loads(json.dumps(replayed)) == evidence, ('selection replay differs', key)
        rows = []
        for index, record in enumerate(evidence['rows'], 1):
            assert record['sequence'] == index and not record['pending']
            assert record['selected'] is not None
            rows.append({**record['selected'], 'position': None})
    result = [[EMPLOYER, source_name(r['name']), None, number(r['remuneration']), number(r['expenses']), r['pdfPage']] for r in rows]
    assert all(r[3] is not None and isinstance(r[5], int) and r[5] >= 3 for r in result)
    assert all(a[5] <= b[5] for a, b in zip(result, result[1:])), ('source order', key)
    return result


def validate_retention(source):
    assert source['retainCompiledPartition'] is True
    assert source['completeEmployeeSchedule'] is True
    assert source['validation']['completeEmployeeSchedule'] is True
    assert source['validation']['compiledPartitionRetained'] is True
    assert source['validation']['compiledPartitionRetentionReason']
    assert 'compiled' in source['publicWarning']


def validate_source_context(item, original, context):
    assert context['sourceSha256'] == original['sourceSha256']
    for field in ('periodStart', 'periodEnd', 'printedEmployeeNarrativeCount', 'conflictingNarrativeCount', 'conflictingNarrativeCountPeriodEnd'):
        assert item[field] == context[field], ('context decision differs', item['key'], field)
    for field in ('remuneration', 'expenses'):
        assert item['printedNamedControls'][field] == context['printedNamedControls'][field]
    assert item['printedNamedControls']['physicalPage'] == context['controlPhysicalPage']


def main():
    index_path = AREA / 'source-acceptance-index.json'
    index = decode(index_path)
    assert len(index['sources']) == 9 and index['noOutreach'] is True
    assert not index.get('pendingPeerScopes'), 'Independent whole-source peer review is unfinished'
    inventory = {s['key']: s for s in pinned(index['inventory'])['sources']}
    context = pinned(index['sourceContextAcceptance'])
    assert context['acceptedContextScope'] is True
    contexts = {s['key']: s for s in context['sources']}
    COLLECTION.mkdir(exist_ok=True)
    sources, summary = [], []
    for item in index['sources']:
        key = item['key']
        original = inventory[key]
        validate_source_context(item, original, contexts[key])
        evidence = pinned(item['selectedInput'])
        assert evidence['source']['sourceSha256'] == original['sourceSha256'] if item['inputKind'] == 'native' else evidence['sourceSha256'] == original['sourceSha256']
        assert item['peerReviews']
        for reference in item['peerReviews']:
            pinned(reference)
        for reference in item['pageCensusEvidence']:
            pinned(reference)
        values = normalized_rows(key, evidence, item['inputKind'])
        assert len(values) == item['actualNamedRows']
        sums = [sum(Decimal(str(row[column])) for row in values if row[column] is not None) for column in (3, 4)]
        controls = item['printedNamedControls']
        residuals = [str(amount - Decimal(str(controls[field]))) for amount, field in zip(sums, ['remuneration', 'expenses'])]
        filename = key + '-employees.json.gzip'
        raw = encoded(values)
        (COLLECTION / filename).write_bytes(raw)
        proof = {
            'sourceSha256': original['sourceSha256'], 'sourceSelection': item['selectedInput'],
            'independentPeerReviews': item['peerReviews'], 'sourceContextAcceptance': index['sourceContextAcceptance'],
            'fullOriginalPageCensusEvidence': item['pageCensusEvidence'],
            'normalization': 'Only source whitespace/comma spacing and finite numeric representation are standardized. No identities, titles, amounts or absent observations are inferred.',
            'literalRowsRemainInPrintedOrderIncludingRepeatedObservations': True,
            'sourceTypographyQualification': 'Capital I/l choices follow same-source rendered mixed-case typography and calibration. Identical painted glyphs do not prove an underlying Unicode character or a real-world identity.',
            'rows': [{'rowIndex': i, 'pdfPage': r[5], 'name': r[1], 'sourceFootnoteMarker': evidence['popplerRows'][i - 1].get('sourceFootnoteMarker') if item['inputKind'] == 'native' else None} for i, r in enumerate(values, 1)],
            'noOutreach': True,
        }
        if item['inputKind'] == 'scan':
            proof['primaryImageReceipts'] = evidence['primaryPersonalReceipts']
            proof['primaryPersonallyReadRows'] = evidence['primaryPersonallyReadRows']
            proof['finiteSourceGuard'] = evidence['finiteSourceGuard']
            proof['primaryCorrections'] = evidence['primaryCorrections']
            proof['readingMethod'] = 'Two independently parsed original-raster OCR streams, complete original payment-band census and source-specific full-cell ink guards. All true flags plus finite benchmarks/challenges were personally source-read and independently reviewed; the remainder uses explicitly bounded guarded agreement. This is not an all-row manual transcription or an accuracy guarantee.'
        else:
            proof['readingMethod'] = 'Independent native Poppler physical-layout and MuPDF word-geometry readers; complete original payment census and independent bounded actual-image review.'
        provenance_file = key + '-provenance.json.gzip'
        provenance = encoded(proof)
        (COLLECTION / provenance_file).write_bytes(provenance)
        start = int(key[5:9]); year = f'{start}/{str(start + 1)[-2:]}'
        assert item['periodStart'] == f'{start}-04-01' and item['periodEnd'] == f'{start + 1}-03-31'
        warning = ('Official Legislative Library archival download includes an added catalogue cover at physical page 1; citations identify this delivered copy. The delivered SHA-256 is recorded separately from the catalogue stored-bitstream checksum and byte count; no byte identity is claimed. These are threshold payment disclosures, not annual base salary rates or a complete workforce roster. Published remuneration includes actual payments and taxable compensation; separate expenses may be paid directly or through third parties. Printed expense dashes remain unknown, explicit numeric zero remains zero, and no missing value is supplied from a total. ')
        if any(Decimal(v) != 0 for v in residuals):
            warning += f'Literal named observations differ from the printed named controls by {residuals[0]} dollars remuneration and {residuals[1]} dollars known expenses. No cell is adjusted and no cause is established. '
        if key == 'phsa-2006-07':
            warning += 'The source narrative counts 1,280 employees above the threshold, while both complete named-table censuses find 1,267 observations. The unexplained difference remains explicit; no employee or payment is invented. '
        if key == 'phsa-2009-10':
            warning += 'The definition-page narrative says March 31, 2009, conflicting with its own heading and the repeated salary-table year-end March 31, 2010. This cohort follows the actual repeated salary-table period; the contradictory narrative is retained without an assumed cause. Its 1,800 employee narrative count is not adopted as a 2010 table count control. '
        if item.get('sourceFootnotes'):
            warning += 'Source-specific footnotes are preserved in the supporting provenance and notes. '
        warning += 'Existing compiled observations are retained and may overlap this official schedule; no complete-copy, reporting-period or identity equivalence is assumed.'
        source = {
            'id': 'gap-phsa-history-' + key, 'employerSlug': EMPLOYER,
            'employerName': 'Provincial Health Services Authority', 'sector': 'Health authorities',
            'year': year, 'periodType': 'fiscal', 'periodStart': f'{start}-04-01', 'periodEnd': f'{start + 1}-03-31',
            'periodEvidence': 'Actual internally printed March 31 year-end on the original salary schedule, independently image-reviewed. April 1 is the conventional twelve-month fiscal start; catalogue dates are discovery evidence only.',
            'title': 'Provincial Health Services Authority employee remuneration ' + year + ' (official Legislative Library copy)',
            'sourceUrl': original['sourceUrl'], 'indexUrl': original['officialCatalogueHandle'],
            'sha256': original['sourceSha256'], 'pdfBytes': original['bytes'],
            'file': filename, 'dataSha256': sha(raw), 'rowCount': len(values),
            'status': 'source-reviewed-awaiting-root-adoption', 'sourceKind': 'official',
            'category': 'employee-remuneration', 'scope': 'employee-remuneration', 'currency': 'CAD',
            'threshold': 75000, 'thresholdComparison': 'as-published',
            'completeEmployeeSchedule': True, 'retainCompiledPartition': True,
            'notes': ['No job titles are published in this salary schedule; position remains null.', 'Disclosed names are literal source strings, not resolved identities. Every printed observation is retained in source order, including repeats.', 'Remuneration covers physical payments to or on behalf of the employee, including salaries/wages, taxable benefits, bonuses, stipends and applicable on-call/sessionals. Expenses may be direct or through third parties.'] + item.get('sourceFootnotes', []),
            'publicWarning': warning, 'provenanceFile': provenance_file, 'provenanceSha256': sha(provenance),
            'validation': {
                'candidateOnly': True, 'completeEmployeeSchedule': True, 'completePrintedNamedScope': True,
                'compiledPartitionRetained': True,
                'compiledPartitionRetentionReason': 'No separate complete-copy comparison proves that this official cohort replaces a retained compiled partition. Preserve all compiled observations.',
                'actualNamedObservations': len(values), 'printedEmployeeNarrativeCount': item['printedEmployeeNarrativeCount'],
                'printedNarrativeCountIsReportingPeriodControl': key != 'phsa-2009-10',
                'conflictingNarrativeCount': item.get('conflictingNarrativeCount'),
                'conflictingNarrativeCountPeriodEnd': item.get('conflictingNarrativeCountPeriodEnd'),
                'literalRemunerationSum': str(sums[0]), 'literalKnownExpenseSum': str(sums[1]),
                'printedNamedControls': controls, 'literalNamedControlResiduals': residuals,
                'residualCauseEstablished': False, 'allKnownSalaryAmountsRemainLiteral': True,
                'initialAndSupersededReaderEvidenceRetained': True,
                'independentPeerReviews': item['peerReviews'],
                'sourceContextAcceptance': index['sourceContextAcceptance'],
                'sourceSelection': item['selectedInput'], 'fullOriginalPageCensusEvidence': item['pageCensusEvidence'],
                'pendingGates': ['root final normalized reconstruction and adoption', 'producer freeze'],
            },
        }
        validate_retention(source)
        sources.append(source)
        summary.append({'key': key, 'rowCount': len(values), 'nullExpenseRows': sum(r[4] is None for r in values), 'literalNamedControlResiduals': residuals, 'dataSha256': sha(raw), 'provenanceSha256': sha(provenance), 'namedRowsByPhysicalPage': dict(collections.Counter(r[5] for r in values))})
    manifest = {'schemaVersion': 1, 'status': 'nine original PHSA employee cohorts source-reviewed; root adoption pending', 'noOutreach': True, 'sources': sources}
    path = COLLECTION / 'sources-candidate.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (AREA / 'normalized-candidate-summary.json').write_text(json.dumps({'sourceAcceptanceIndex': ref(index_path), 'manifest': ref(path), 'sources': summary, 'cohorts': len(sources), 'rows': sum(s['rowCount'] for s in sources), 'noOutreach': True}, indent=2) + '\n')
    print(json.dumps({'cohorts': len(sources), 'rows': sum(s['rowCount'] for s in sources), 'manifestSha256': sha(path.read_bytes())}))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()
