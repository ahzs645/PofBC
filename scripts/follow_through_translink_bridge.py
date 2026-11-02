#!/usr/bin/env python3
"""Reproduce read-only entity-overlap analysis; writes bridge evidence/docs only."""
from collections import Counter,defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/follow-through-translink'
OUT=AREA/'employer-bridge'
BASELINE=ROOT/'research/salaries/compiled-baseline.json.gzip'
BASELINE_SHA='410bcae27c9755e387c473ab44d62081a50b46e7330f4d6d5c0b74979d392760'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def key(row):return (row[1],row[3],row[4])


def compare():
    assert sha(BASELINE)==BASELINE_SHA
    baseline=read(BASELINE)
    compiled=next(e for e in baseline['employers'] if e['slug']=='translink')
    assert len(compiled['rows'])==12464 and compiled['counts']==[3237,4043,5184]
    manifest_path=AREA/'sources.json';manifest=json.loads(manifest_path.read_text())
    exact=defaultdict(list);pay_only=defaultdict(list);held_exact=defaultdict(list)
    cohorts=[];pins=[]
    for accepted,sources in [(True,manifest['sources']),(False,manifest.get('unparsedSources',[]))]:
        for source in sources:
            file=source['file'] if accepted else source['candidateFile'];p=AREA/file
            assert sha(p)==source['dataSha256']
            rows=read(p)
            pin={'sourceId':source['id'],'file':file,'dataSha256':sha(p),'accepted':accepted,
                 'employerSlug':source['employerSlug'],'sourcePeriod':source['year'],'rowCount':len(rows)}
            pins.append(pin)
            named=[r for r in rows if r[1] is not None]
            cohorts.append({**pin,'namedRows':len(named),'anonymousRows':len(rows)-len(named),
                            'uniqueNamedFinancialTuples':len({key(r) for r in named})})
            for rn,row in enumerate(rows,1):
                if row[1] is None:continue
                hit={'sourceId':source['id'],'employerSlug':source['employerSlug'],'sourcePeriod':source['year'],
                     'sourceRowNumber':rn,'pdfPage':row[5],'name':row[1],'position':row[2],
                     'remuneration':row[3],'expenses':row[4]}
                if accepted:
                    exact[key(row)].append(hit);pay_only[(row[1],row[3])].append(hit)
                else:held_exact[key(row)].append(hit)
    results=[];groups=[]
    for yi,label in enumerate(baseline['years']):
        group=[(i+1,r) for i,r in enumerate(compiled['rows']) if r[4]==yi]
        matrix=Counter();pay_matrix=Counter();unique_matrix=Counter();mismatches=Counter()
        any_exact=0;unique_occurrence=0;unique_entity_period=0;unique_entity=0;ambiguous_entity=0;anonymous=0;any_pay=0
        for rn,row in group:
            name,position,remuneration,expenses,_=row
            hits=exact.get((name,remuneration,expenses),[]) if name is not None else []
            partial=pay_only.get((name,remuneration),[]) if name is not None else []
            held=held_exact.get((name,remuneration,expenses),[]) if name is not None else []
            entity_periods={(h['employerSlug'],h['sourcePeriod']) for h in hits}
            entities={h['employerSlug'] for h in hits}
            partial_periods={(h['employerSlug'],h['sourcePeriod']) for h in partial}
            for p in entity_periods:matrix[p]+=1
            for p in partial_periods:pay_matrix[p]+=1
            if name is None:anonymous+=1
            if hits:any_exact+=1
            if partial:any_pay+=1
            if len(hits)==1:unique_occurrence+=1
            if len(entity_periods)==1:
                unique_entity_period+=1;unique_matrix[next(iter(entity_periods))]+=1
            if len(entities)==1:unique_entity+=1
            if len(entities)>1:ambiguous_entity+=1
            if partial and not hits:
                expense_values={h['expenses'] for h in partial}
                if expenses==0 and expense_values=={None}:mismatches['compiledZeroVersusOfficialNull']+=1
                elif expenses is None and expense_values=={0}:mismatches['compiledNullVersusOfficialZero']+=1
                else:mismatches['otherExpenseDifference']+=1
            results.append({'compiledBaselineRowNumber':rn,'compiledEmployerSlug':'translink','compiledEditionLabel':label,
                            'publishedCompiledName':name,'publishedCompiledPosition':position,
                            'financialTuple':[name,remuneration,expenses],
                            'exactAcceptedOfficialMatches':hits,'exactHeldCandidateMatches':held,
                            'supplementalNameAndRemunerationMatches':partial if not hits else [],
                            'uniquelyMatchedAcceptedEntityPeriod':list(next(iter(entity_periods))) if len(entity_periods)==1 else None,
                            'anonymousExcludedFromEntityProof':name is None})
        grouped=lambda c:[{'employerSlug':e,'sourcePeriod':y,'compiledFinancialTuples':n} for (e,y),n in sorted(c.items())]
        groups.append({'compiledEditionLabel':label,'compiledRows':len(group),
                       'compiledNamedRows':len(group)-anonymous,'compiledAnonymousRows':anonymous,
                       'uniqueCompiledFinancialTuples':len({(r[0],r[2],r[3]) for _,r in group}),
                       'exactAcceptedNamedFinancialTupleMatches':any_exact,
                       'uniqueAcceptedOccurrenceMatches':unique_occurrence,
                       'uniqueAcceptedEntityPeriodMatches':unique_entity_period,'uniqueAcceptedEntityMatches':unique_entity,
                       'ambiguousAcceptedEntityMatches':ambiguous_entity,
                       'exactAcceptedMatchesByEntityAndSourcePeriod':grouped(matrix),
                       'uniqueAcceptedEntityPeriodMatchesByGroup':grouped(unique_matrix),
                       'supplementalNameAndRemunerationMatches':any_pay,
                       'supplementalNameAndRemunerationByEntityAndSourcePeriod':grouped(pay_matrix),
                       'expenseDifferencesAmongSupplementalOnlyMatches':dict(mismatches),
                       'noExactAcceptedNamedFinancialTupleMatch':len(group)-anonymous-any_exact,
                       'matchedAcceptedEntities':sorted({e for e,y in unique_matrix}),
                       'provenMixedAcceptedEntityFinancialTuples':len({e for e,y in unique_matrix})>1})
    report={
        'version':1,'checkedOn':'2026-11-02','compiledEmployerSlug':'translink','compiledRows':12464,
        'uniqueCompiledFinancialTuples':len({(r[0],r[2],r[3]) for r in compiled['rows']}),
        'compiledAnonymousRowsExcludedFromEntityProof':sum(r[0] is None for r in compiled['rows']),
        'baseline':{'file':str(BASELINE.relative_to(ROOT)),'sha256':BASELINE_SHA,'sourceId':baseline['provenance']['sourceId'],
                    'snapshotRepositoryCommit':baseline['provenance']['repositoryCommit'],'compiledEditionLabels':baseline['years']},
        'officialManifest':{'file':str(manifest_path.relative_to(ROOT)),'sha256':sha(manifest_path)},
        'officialCohortPins':pins,'officialCohorts':cohorts,
        'comparisonRules':[
            'Exact financial tuple = literal published name, remuneration, expenses. Original name case/spelling and null/zero distinctions are preserved. Position is separately retained but excluded from this financial comparison because compiled titles contain editorial employer/role annotations.',
            'All three compiled edition labels are compared against all six official calendar periods independently. No label-to-year alignment, same-person assumption, fuzzy name matching, null-to-zero conversion, row reassignment or redating is performed.',
            'All 29 accepted cohorts and the one held CMBC2024 candidate cohort are inventoried separately. Held-candidate matches never count as accepted proof.',
            'Anonymous compiled observations are accounted for but excluded from entity attribution proof; amount-only coincidence cannot identify their employer/person.',
            'Supplemental name-plus-remuneration matches ignore expenses and are reported separately as partial financial overlap only. Expense differences are never silently normalized.',
            'Financial overlap proves that a compiled group mixes published observations from distinct official entity schedules; it does not establish original source provenance, person identity, employment continuity or complete compiled-cohort equivalence.',
        ],
        'compiledEditionGroups':groups,'compiledObservationComparisons':results,
        'decision':{'reassignCompiledRows':False,'deleteCompiledRows':False,'redateCompiledRows':False,
                    'reason':'Mixed entity schedules and partial financial overlap are documented. Retain every baseline employer, compiled edition label and occurrence; investigate complete source scope and exceptions separately.'}}
    return report


def main():
    OUT.mkdir(exist_ok=True)
    r=compare()
    observations=r.pop('compiledObservationComparisons')
    raw=(json.dumps(observations,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    observation_path=OUT/'compiled-entity-observations.json.gzip';observation_path.write_bytes(gzip.compress(raw,mtime=0))
    r['observationEvidence']={'file':observation_path.name,'rowCount':len(observations),'sha256':sha(observation_path),
                              'normalizedSha256':hashlib.sha256(raw).hexdigest()}
    dump(OUT/'compiled-entity-review.json',r)
    lines=['# Compiled TransLink entity review','',
           'All **12,464** immutable compiled `translink` observations are compared with all 29 accepted official employer/calendar cohorts and the separately held CMBC 2024 candidate cohort. The baseline contains 12,464 unique literal financial tuples across its three edition labels. Its 156 anonymous observations are accounted for and excluded from entity attribution proof.','',
           'An exact financial tuple means **published name + remuneration + expenses**, retaining literal spelling, case, null and numeric zero. Position is retained as evidence but omitted from financial matching because compiled titles contain editorial employer/role annotations. Every compiled edition is compared against every actual official calendar period; no year alignment is assumed.','',
           '| Compiled edition label | Rows | Exact named financial matches | Uniquely matched entity/period | Distinct accepted entities | Name/pay matches, including exact |','|---|---:|---:|---:|---:|---:|']
    for g in r['compiledEditionGroups']:
        lines.append(f"| {g['compiledEditionLabel']} | {g['compiledRows']:,} | {g['exactAcceptedNamedFinancialTupleMatches']:,} | {g['uniqueAcceptedEntityPeriodMatches']:,} | {len(g['matchedAcceptedEntities'])} | {g['supplementalNameAndRemunerationMatches']:,} |")
    lines+=['','Exact named financial overlap, grouped by the official employer and source period:','',
            '| Compiled edition | Official calendar period | Official entity | Exact tuples |','|---|---|---|---:|']
    for g in r['compiledEditionGroups']:
        for v in g['exactAcceptedMatchesByEntityAndSourcePeriod']:
            lines.append(f"| {g['compiledEditionLabel']} | {v['sourcePeriod']} | `{v['employerSlug']}` | {v['compiledFinancialTuples']:,} |")
    lines+=['','The 2020/21 compiled label has exact financial tuples from **four** distinct 2020 official entity schedules; the 2023/24 label has exact tuples from **three** distinct 2023 official schedules. These are observed partial overlaps in differently labelled source groups, not an authorization to rename, redate or move the compiled groups. No match was found for the 2017/18 edition within the supplied official 2020–2025 comparison window; that does not establish its underlying source period or entity scope.','',
            'Supplemental name-plus-remuneration matching intentionally ignores expenses. Its totals include exact financial matches; the additional matches are weaker overlap evidence and do not count as exact financial equivalence. Expense differences for these supplemental-only matches are:','']
    for g in r['compiledEditionGroups']:
        lines.append(f"- {g['compiledEditionLabel']}: {json.dumps(g['expenseDifferencesAmongSupplementalOnlyMatches'],sort_keys=True)}")
    lines+=['','All official cohort row counts, fingerprints, accepted/held status and grouped match counts are retained in `compiled-entity-review.json`. Its hash-pinned `compiled-entity-observations.json.gzip` retains every one of the 12,464 baseline occurrences and its exact/partial source matches. Anonymous payments, position differences, unmatched rows and expense disagreements remain visible. No original person identity, publication provenance or employment continuity is inferred. The held CMBC 2024 schedule remains held.','',
            '**Decision:** retain all original compiled observations, employer labels and edition labels. No reassignment, deletion or blanket redating is performed. Complete source equivalence and each exception would need separate source-backed review before any such decision.','',
            'Reproduce with `python scripts/follow_through_translink_bridge.py`. The script reads the fingerprinted immutable baseline and current accepted/held row files, then writes only these bridge comparison artifacts. Its input pins are checked by the TransLink regression tests.']
    (OUT/'compiled-entity-review.md').write_text('\n'.join(lines)+'\n')
    print([(g['compiledEditionLabel'],g['exactAcceptedNamedFinancialTupleMatches'],g['supplementalNameAndRemunerationMatches']) for g in r['compiledEditionGroups']])


if __name__=='__main__':main()
