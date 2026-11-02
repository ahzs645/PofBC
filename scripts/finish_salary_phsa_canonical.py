#!/usr/bin/env python3
"""Validate explicit root canonical source decisions against pinned human records.

This module does not make human decisions, write candidates, or promote sources.
``validate(pin, source_id, pdf_sha256, original_provenance)`` checks one immutable
``phsa-canonical-source-closure-v1`` document. Its outcomes must come from named
fields of exact human decision records, and must reproduce the selected source
provenance. The prior eight reports require all three canonical target packets,
including explicit zero packets. FY2019 uses separately pinned bounded packets.
"""
from pathlib import PurePosixPath
import re

import finish_salary_phsa_ledger as ledger


SCHEMA = 'phsa-canonical-source-closure-v1'
PRIOR_SCOPE = 'prior-eight-three-packets'
CURRENT_SCOPE = 'phsa-2019-20-bounded-packets'
FIELDS = {'name', 'remuneration', 'expenses'}
PACKET_KINDS = ('qualified-name', 'direct-neither-name', 'positive-neither-money')
SOURCES = {f'phsa-{year}-{str(year + 1)[-2:]}' for year in range(2015, 2024)}
QUALIFIED = 'manual-qualified-source-typography'


def _integer(value):
    return type(value) is int and value > 0


def _reference(value):
    if (not isinstance(value, dict) or set(value) != {'path', 'sha256'}
            or not isinstance(value['path'], str) or not value['path']
            or '\\' in value['path'] or PurePosixPath(value['path']).is_absolute()
            or str(PurePosixPath(value['path'])) != value['path']
            or '..' in PurePosixPath(value['path']).parts
            or not isinstance(value['sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', value['sha256']) is None):
        raise ValueError('Canonical evidence requires an exact repository-relative byte pin')
    return value['path'], value['sha256']


def _document(reference, read):
    _reference(reference)
    value = read(reference)
    if not isinstance(value, dict):
        raise ValueError('Canonical evidence must be a JSON object')
    return value


def expected_packet_paths(source):
    base = (ledger.AREA / 'canonical-review').relative_to(ledger.ROOT)
    return {str(base / f'{source}-{kind}-source-only.json') for kind in PACKET_KINDS}


def _identity(row, source, source_sha, *, default_name=False):
    if not isinstance(row, dict):
        raise ValueError('Canonical target/decision must be an object')
    if ('sourceId' in row and row['sourceId'] != source
            or 'sourceSha256' in row and row['sourceSha256'] != source_sha):
        raise ValueError('Canonical row identifies another original source')
    page, number = row.get('physicalPage'), row.get('sourceRowOnPage')
    field = row.get('field', 'name' if default_name else None)
    if not _integer(page) or not _integer(number) or field not in FIELDS:
        raise ValueError('Canonical row requires an exact positive page/row and field')
    return page, number, field


def _family(value, alternatives):
    if (not isinstance(value, str) or not value or not isinstance(alternatives, list)
            or not alternatives or any(not isinstance(v, str) or not v for v in alternatives)
            or len(set(alternatives)) != len(alternatives) or value not in alternatives):
        raise ValueError('Canonical name family must explicitly contain the chosen literal once')
    return set(alternatives)


def _pointer(document, pointer):
    if not isinstance(pointer, str) or (pointer and not pointer.startswith('/')):
        raise ValueError('Human decision record requires a JSON Pointer')
    current = document
    for token in pointer.split('/')[1:] if pointer else []:
        if re.search('~(?![01])', token):
            raise ValueError('Invalid JSON Pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(current, list):
            if re.fullmatch('0|[1-9][0-9]*', token) is None:
                raise ValueError('Human record pointer has a noncanonical array index')
            index = int(token)
            if index >= len(current):
                raise ValueError('Human record pointer is outside its receipt')
            current = current[index]
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise ValueError('Human record pointer is absent from its pinned receipt')
    if not isinstance(current, dict):
        raise ValueError('Human decision pointer must identify a concrete row object')
    return current


def _no_open_human_flags(document):
    for flag in ('accepted', 'closed'):
        if flag in document and document[flag] is not True:
            raise ValueError('An explicitly unaccepted/open human receipt cannot close source review')
    for flag in ('unresolved', 'unresolvedFields', 'unresolvedMoneyFields'):
        if flag in document:
            value = document[flag]
            if value != [] and not (type(value) is int and value == 0):
                raise ValueError('Human receipt/record still declares unresolved source fields')


def _human_document(reference, source, source_sha, read):
    document = _document(reference, read)
    has_header = 'sourceId' in document or 'sourceSha256' in document
    if has_header and (document.get('sourceId'), document.get('sourceSha256')) != (source, source_sha):
        raise ValueError('Human receipt source header is incomplete or identifies another PDF')
    _no_open_human_flags(document)
    return document, has_header


def _targets(closure, source, source_sha, read):
    references = closure.get('targetPackets')
    if not isinstance(references, list) or not references:
        raise ValueError('Canonical source-only target packets are required')
    paths = [_reference(ref)[0] for ref in references]
    if len(set(paths)) != len(paths):
        raise ValueError('Repeated canonical target packet')
    scope = closure.get('scopeKind')
    prior = source != 'phsa-2019-20'
    if prior:
        if scope != PRIOR_SCOPE or set(paths) != expected_packet_paths(source):
            raise ValueError('Prior-eight closure must pin its exact three canonical target packets')
    elif scope != CURRENT_SCOPE:
        raise ValueError('FY2019 requires its explicitly bounded canonical target scope')
    targets = set()
    for reference in references:
        packet = _document(reference, read)
        if (packet.get('sourceId'), packet.get('sourceSha256')) != (source, source_sha):
            raise ValueError('Canonical target packet identifies another original PDF')
        if not any(packet.get(flag) is True for flag in ('sourceOnly', 'candidateValuesWithheld',
                                                         'expectedValuesWithheld')):
            raise ValueError('Canonical target packet is not explicitly source-only')
        rows = packet.get('rows')
        if not isinstance(rows, list):
            raise ValueError('Canonical target packet must enumerate rows, including an explicit empty list')
        for count in ('rowCount', 'fieldCount', 'qualifiedNameFields', 'directManualNeitherNameFields',
                      'positiveMonetaryFields'):
            if count in packet and (type(packet[count]) is not int or packet[count] != len(rows)):
                raise ValueError('Canonical target packet count differs from its actual rows')
        local = [_identity(row, source, source_sha, default_name=prior) for row in rows]
        if len(set(local)) != len(local):
            raise ValueError('Repeated target tuple within one canonical packet')
        if targets.intersection(local):
            raise ValueError('Canonical source-only packets repeat a target across scopes')
        if prior:
            is_money = reference['path'].endswith('-positive-neither-money-source-only.json')
            if any((identity[2] != 'name') != is_money for identity in local):
                raise ValueError('Canonical target packet mixes name and money scopes')
        targets.update(local)
    return targets


def _selected_rows(original, source, source_sha):
    if (original.get('sourceId'), original.get('sourceSha256')) != (source, source_sha):
        raise ValueError('Selected provenance identifies another original source')
    if not isinstance(original.get('pendingFields'), list) or original['pendingFields'] != []:
        raise ValueError('Selected provenance retains pending fields')
    rows = original.get('rows')
    if not isinstance(rows, list):
        raise ValueError('Selected provenance must contain original rows')
    selected = {}
    for row in rows:
        values = row.get('row')
        number = row.get('sourceRowOnPage')
        if not isinstance(values, list) or len(values) != 6 or not _integer(values[5]) or not _integer(number):
            raise ValueError('Selected provenance has an invalid physical row')
        key = values[5], number
        if key in selected:
            raise ValueError('Selected provenance repeats an original physical row')
        selected[key] = row
    return selected


def _selected_name(row):
    name = row['row'][1]
    field = row['fields']['name']
    evidence = field.get('evidence', {})
    qualification = evidence.get('nameTypographyQualification') if isinstance(evidence, dict) else None
    if field['status'] == QUALIFIED:
        if (not isinstance(qualification, dict) or qualification.get('caseProvenByPixels') is not False
                or qualification.get('chosenName', name) != name):
            raise ValueError('Selected qualified-name provenance has inconsistent source qualification')
        alternatives = qualification.get('visibleAlternatives')
        if not isinstance(alternatives, list) or any(not isinstance(v, str) or not v for v in alternatives):
            raise ValueError('Selected qualified-name provenance lacks exact alternatives')
        family = set(alternatives) | {name}
        if len(family) < 2:
            raise ValueError('Selected qualified name has no alternative source segmentation')
        return 'qualified', family
    if qualification is not None:
        raise ValueError('Selected direct literal retains an old glyph qualification')
    return 'direct', {name}


def validate(reference, source, source_sha, original, *, read=None):
    """Return checked per-source canonical facts; never infer or write acceptance.

    Each name outcome has value, status, and a complete visibleAlternatives list.
    Monetary outcomes are direct positive integers and have no name alternatives.
    Every outcome has decisionRecord {receipt, rowRecordPointer, valueField,
    finiteField}. finiteField is an explicit field name or null for a direct row.
    The pointer must select that exact source/page/row/field in a pinned current
    human receipt. The named value and full finite set must equal the outcome.
    """
    if source not in SOURCES or re.fullmatch('[0-9a-f]{64}', source_sha or '') is None:
        raise ValueError('Unknown canonical source or invalid original PDF hash')
    read = ledger.pinned if read is None else read
    closure = _document(reference, read)
    if (closure.get('schema') != SCHEMA
            or (closure.get('sourceId'), closure.get('sourceSha256')) != (source, source_sha)
            or closure.get('accepted') is not True or closure.get('closed') is not True
            or closure.get('unresolved') != []):
        raise ValueError('Root canonical source closure is missing identity or has an open gate')
    targets = _targets(closure, source, source_sha, read)
    selected = _selected_rows(original, source, source_sha)
    references = closure.get('humanReviewReceipts')
    if not isinstance(references, list) or not references:
        raise ValueError('Explicit pinned current human semantic review receipts are required')
    humans = {}
    for ref in references:
        identity = _reference(ref)
        if identity[0] in {key[0] for key in humans}:
            raise ValueError('Repeated human review receipt')
        humans[identity] = _human_document(ref, source, source_sha, read)
    outcomes = closure.get('outcomes')
    if not isinstance(outcomes, list):
        raise ValueError('Canonical closure must explicitly enumerate outcomes, including none')
    seen = set()
    used_receipts = set()
    qualified = 0
    for outcome in outcomes:
        _no_open_human_flags(outcome)
        identity = _identity(outcome, source, source_sha)
        if identity in seen or identity not in targets:
            raise ValueError('Canonical closure repeats or adds an unrequested outcome')
        seen.add(identity)
        page, number, field = identity
        if (page, number) not in selected:
            raise ValueError('Canonical outcome identifies an absent original row')
        row = selected[page, number]
        value, status = outcome.get('value'), outcome.get('status')
        if field == 'name':
            family = _family(value, outcome.get('visibleAlternatives'))
            expected_status, expected_family = _selected_name(row)
            if (status not in ('direct', 'qualified') or status != expected_status
                    or family != expected_family or value != row['row'][1]
                    or (status == 'direct') != (len(family) == 1)):
                raise ValueError('Selected name literal/status/full finite family differs from root source decision')
            qualified += status == 'qualified'
        else:
            selected_value = row['row'][3 if field == 'remuneration' else 4]
            selected_field = row.get('fields', {}).get(field)
            if (not _integer(value) or status != 'direct' or 'visibleAlternatives' in outcome
                    or not _integer(selected_value) or value != selected_value
                    or not isinstance(selected_field, dict)
                    or selected_field.get('status') == QUALIFIED
                    or selected_field.get('evidence', {}).get('nameTypographyQualification') is not None):
                raise ValueError('Selected positive literal amount differs or has a numeric qualification')
            family = None
        record = outcome.get('decisionRecord')
        if not isinstance(record, dict) or set(record) != {'receipt', 'rowRecordPointer', 'valueField', 'finiteField'}:
            raise ValueError('Each outcome must identify its exact final human semantic decision record')
        receipt = _reference(record['receipt'])
        if receipt not in humans:
            raise ValueError('Outcome decision receipt is not among pinned current human reviews')
        human, header_identity = humans[receipt]
        decision = _pointer(human, record['rowRecordPointer'])
        _no_open_human_flags(decision)
        if not header_identity and (decision.get('sourceId'), decision.get('sourceSha256')) != (source, source_sha):
            raise ValueError('Combined human receipt decision row lacks exact source identity')
        if _identity(decision, source, source_sha, default_name=field == 'name') != identity:
            raise ValueError('Human decision pointer identifies another requested field')
        value_field = record['valueField']
        if not isinstance(value_field, str) or value_field not in decision or decision[value_field] != value:
            raise ValueError('Root outcome literal differs from its pinned final human decision')
        if type(decision[value_field]) is not type(value):
            raise ValueError('Human decision changes the literal value type')
        finite_field = record['finiteField']
        if finite_field is None:
            if status != 'direct':
                raise ValueError('Qualified human source decision needs its explicit complete finite set')
        elif (field != 'name' or not isinstance(finite_field, str) or finite_field not in decision
                or _family(value, decision[finite_field]) != family):
            raise ValueError('Root source family differs from its pinned final human decision')
        used_receipts.add(receipt)
    if seen != targets:
        raise ValueError('Canonical closure omits requested source fields')
    if targets and used_receipts != set(humans):
        raise ValueError('Canonical closure contains an irrelevant/unmapped human review receipt')
    if not targets and any(not has_header for _, has_header in humans.values()):
        raise ValueError('Zero-target source closure still requires source-identified complete-scope human evidence')
    if source != 'phsa-2019-20':
        all_qualified = {(p, n, 'name') for (p, n), row in selected.items()
                         if row['fields']['name']['status'] == QUALIFIED}
        if not all_qualified <= targets:
            raise ValueError('Prior-eight canonical packets omit a selected qualified-name field')
    counts = {'targets': len(targets), 'nameTargets': sum(key[2] == 'name' for key in targets),
              'positiveMoneyTargets': sum(key[2] != 'name' for key in targets),
              'qualifiedNameTargets': qualified}
    if (closure.get('counts') != counts or not isinstance(closure.get('counts'), dict)
            or any(type(v) is not int for v in closure['counts'].values())):
        raise ValueError('Canonical closure counts differ from exact accepted target scope')
    return {'sourceId': source, 'sourceSha256': source_sha, 'scopeKind': closure['scopeKind'],
            'rootCanonicalClosure': reference, **counts}
