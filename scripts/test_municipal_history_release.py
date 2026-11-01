"""The historical municipal gate must reject drift without absorbing later imports."""
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('municipal_history_review', Path(__file__).with_name('build-municipal-history-review.py'))
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class FrozenMunicipalReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.research = self.root / 'research/salaries'
        self.out = self.research / 'municipal-history-pass'
        self.index_path = self.root / 'public/salaries/employers/index.json'
        self.collections = ['municipal-history-' + area for area in REVIEW.AREAS]
        imports, aggregates, sources, municipalities, tasks, fingerprints = [], [], {}, [], [], {}
        for at, (area, collection) in enumerate(zip(REVIEW.AREAS, self.collections)):
            slug = f'city-of-example-{at}'
            identifier = f'employee-{at}'
            rows = [[slug, f'Employee {at}', None, 100000, None, 1]]
            raw = gzip.compress(json.dumps(rows).encode(), mtime=0)
            folder = self.research / collection
            folder.mkdir(parents=True)
            (folder / '2024.json.gzip').write_bytes(raw)
            source = dict(id=identifier, employerSlug=slug, year='2024', periodType='calendar',
                          periodStart='2024-01-01', periodEnd='2024-12-31', category='employee-remuneration',
                          sourceUrl=f'https://example.test/{at}.pdf', sha256=hashlib.sha256(f'original {at}'.encode()).hexdigest(),
                          file='2024.json.gzip', dataSha256=hashlib.sha256(raw).hexdigest(), rowCount=1,
                          status='accepted', threshold=75000, thresholdComparison='>', notes=['Original qualification.'],
                          publicWarning='Retain source qualification.', validation={'completeEmployeeSchedule': False},
                          completeEmployeeSchedule=False)
            sources[identifier] = {**source, 'url': source['sourceUrl'], 'scope': source['category'], 'sourceKind': 'official'}
            imports.append(dict(collection=collection, sourceId=identifier, employerSlug=slug, year='2024',
                                category='employee-remuneration', rows=1, unnamedRows=0, sourceUrl=source['sourceUrl'],
                                sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source['publicWarning']))
            manifest = {'sources': [source]}
            if at == 0:
                aggregate = dict(id='aggregate-only', employerSlug=slug, year='2023', periodType='calendar',
                                 periodStart='2023-01-01', periodEnd='2023-12-31', rowCount=0,
                                 sourceUrl='https://example.test/aggregate.pdf', sha256=hashlib.sha256(b'original aggregate').hexdigest(),
                                 status='verified-aggregate-only', threshold=75000, thresholdComparison='>',
                                 validation={'explicitNoNamedEmployeeTextVerified': True}, notes=['No named schedule.'])
                manifest['aggregateOnlySources'] = [aggregate]
                sources[aggregate['id']] = {**aggregate, 'url': aggregate['sourceUrl'], 'scope': 'aggregate-only', 'sourceKind': 'official'}
                aggregates.append(dict(collection=collection, sourceId=aggregate['id'], employerSlug=slug, year='2023',
                                       sourceUrl=aggregate['sourceUrl'], sourceSha256=aggregate['sha256'], rows=0))
            self.write(folder / 'sources.json', manifest)
            municipalities.append({'employerSlug': slug, 'status': 'current'})
            task = {key: None for key in REVIEW.FIELDS}
            task.update(id=f'task-{at}', employerSlug=slug, employerName=f'City {at}', reportingPeriods=['2022'],
                        sector='Municipalities', route='processing', status='requires-ocr',
                        nextAction='Review original.', reason='Requires source review.')
            queue_path = self.out / area / 'work-queue.json'
            self.write(queue_path, [task])
            fingerprints[area] = hashlib.sha256(queue_path.read_bytes()).hexdigest()
            tasks.append({**task, 'area': area, 'requestStatus': 'not-sent'})
        baseline = dict(repositoryCommit='a' * 40, overall=dict(records=1, officialRecords=0, compiledRecords=1,
                        employerEntries=1, acceptedSourceFiles=0), municipalities=municipalities, municipalSummary={'currentJurisdictions': 6})
        release = dict(baseline=baseline['overall'], baselineCommit=baseline['repositoryCommit'],
                       proposed=dict(records=7, officialRecords=6, compiledRecords=1, employerEntries=7, acceptedSourceFiles=6),
                       municipalCoverageBefore=baseline['municipalSummary'], imports=imports, aggregateOnlySources=aggregates,
                       officialRowsAdded=6, compiledRowsReplaced=0, netRowsAdded=6, employeeRowsAdded=6,
                       councilRowsAdded=0, unnamedRowsAdded=0, originalReports=7, municipalityYears=7,
                       taskInputSha256=fingerprints, tasks=6, requestCandidates=0, taskCountsByRoute={'processing': 6})
        self.write(self.research / 'collections.json', {'collections': self.collections})
        self.write(self.index_path, {'sources': sources, 'employers': [{'counts': [7]}]})
        self.write(self.out / 'baseline.json', baseline)
        self.write(self.out / 'release.json', release)
        self.write(self.out / 'work-queue.json', {'tasks': tasks})
        self.write(self.out / 'acquisition-list.json', {'candidates': []})

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + '\n')

    def update(self, path, change):
        value = json.loads(path.read_text())
        change(value)
        self.write(path, value)

    def test_later_unrelated_salary_growth_does_not_rewrite_historical_release(self):
        self.update(self.index_path, lambda value: value['employers'].append({'counts': [10000]}))
        self.update(self.research / 'collections.json', lambda value: value['collections'].append('north-island-history'))
        before = {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        result = REVIEW.validate_frozen_release(self.root)
        self.assertEqual(result['records'], 7)
        self.assertEqual(result['officialRowsAdded'], 6)
        self.assertEqual(result['aggregateOnlySourcesVerified'], 1)
        after = {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(before, after)

    def test_changed_normalized_rows_fail_hash_validation(self):
        path = self.research / self.collections[0] / '2024.json.gzip'
        rows = json.loads(gzip.decompress(path.read_bytes()))
        rows[0][3] += 1
        path.write_bytes(gzip.compress(json.dumps(rows).encode(), mtime=0))
        with self.assertRaisesRegex(AssertionError, 'normalized hash differs'):
            REVIEW.validate_frozen_release(self.root)

    def test_dropped_published_warning_fails(self):
        self.update(self.index_path, lambda value: value['sources']['employee-0'].pop('publicWarning'))
        with self.assertRaisesRegex(AssertionError, 'published warning differs'):
            REVIEW.validate_frozen_release(self.root)

    def test_aggregate_scope_cannot_become_employee_records(self):
        self.update(self.index_path, lambda value: value['sources']['aggregate-only'].update(scope='employee-remuneration'))
        with self.assertRaises(AssertionError):
            REVIEW.validate_frozen_release(self.root)

    def test_historical_total_cannot_absorb_later_additions(self):
        self.update(self.out / 'release.json', lambda value: value['proposed'].update(records=8, officialRecords=7))
        with self.assertRaises(AssertionError):
            REVIEW.validate_frozen_release(self.root)

    def test_queue_input_changes_are_detected_before_accepting_new_tasks(self):
        self.update(self.out / REVIEW.AREAS[0] / 'work-queue.json', lambda value: value[0].update(nextAction='Changed action.'))
        with self.assertRaisesRegex(AssertionError, 'historical queue input changed'):
            REVIEW.validate_frozen_release(self.root)

    def test_released_source_list_cannot_drop_a_cohort(self):
        self.update(self.out / 'release.json', lambda value: value['imports'].pop())
        with self.assertRaisesRegex(AssertionError, 'Released regional collection list changed'):
            REVIEW.validate_frozen_release(self.root)


if __name__ == '__main__':
    unittest.main()
