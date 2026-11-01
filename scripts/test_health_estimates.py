"""Check coverage, independent tracing and substantive historical constraints."""
import unittest
from collections import Counter

from shapely.geometry import shape
from shapely.ops import unary_union

from rectify_health_maps import PUBLIC, RESEARCH, read, score, TO_METRES, transform


class HealthEstimatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = read(PUBLIC / 'estimates-index.json')
        cls.best = read(PUBLIC / 'best-estimates.geojson')['features']
        cls.drawn = read(PUBLIC / 'source-drawn-estimates.geojson')['features']
        cls.statistics = read(PUBLIC / 'statistical-region-estimates.geojson')['features']

    def test_every_label_has_valid_source_and_chosen_geometry(self):
        ids = {area['id'] for area in read(PUBLIC / 'catalogue.json')['areas']}
        for features in [self.best, self.drawn]:
            self.assertEqual(len(features), 52)
            self.assertEqual({f['properties']['code'] for f in features}, ids)
            for feature in features:
                geometry = shape(feature['geometry'])
                self.assertTrue(geometry.is_valid, feature['properties']['code'])
                self.assertGreater(geometry.area, 0)
                west, south, east, north = geometry.bounds
                self.assertTrue(-140 < west < east < -113)
                self.assertTrue(48 < south < north < 61)
                self.assertFalse(feature['properties']['boundaryIdentityVerified'])

    def test_council_source_cells_are_not_shared_between_labels(self):
        councils = [row for row in self.report['assessments'] if row['mapId'] == 'councils']
        self.assertEqual(len(councils), 34)
        ownership = {}
        for council in councils:
            self.assertTrue(council['trace']['sourceCellIds'])
            for cell in council['trace']['sourceCellIds']:
                self.assertNotIn(cell, ownership, (council['areaId'], ownership.get(cell)))
                ownership[cell] = council['areaId']

    def test_screening_uses_independent_drawing_not_chosen_proxy(self):
        lhas = {f['properties']['code']: transform(TO_METRES, shape(f['geometry'])) for f in read(PUBLIC / 'display-lha.geojson')['features']}
        source = {f['properties']['code']: transform(TO_METRES, shape(f['geometry'])) for f in self.drawn}
        for area in self.report['assessments']:
            proxy = unary_union([lhas[code] for code in area['modernLhaCodes']])
            self.assertEqual(score(source[area['areaId']], proxy), area['sourceDrawingVsModernCandidate'])
            self.assertLess(area['sourceDrawingVsModernCandidate']['iou'], .999)
            for key in ['regionalDistricts', 'municipalities', 'schoolDistricts']:
                self.assertIn(key, area['currentBoundaryScreening'])

    def test_snow_country_uses_historical_extent_and_explicit_parallel(self):
        snow = next(f for f in self.best if f['properties']['code'] == 'snow-country-health-council')
        self.assertEqual(snow['properties']['method'], 'source-drawn')
        self.assertLessEqual(shape(snow['geometry']).bounds[3], 57.000001)
        # The approximate drawing can fall short of the legal line; the cap
        # excludes north-of-57 geometry without inventing an exact survey edge.
        self.assertGreater(shape(snow['geometry']).bounds[3], 56.8)
        self.assertEqual(snow['properties']['modernLhaCodes'], [])

    def test_statistical_illustration_covers_lhas_once_and_retains_distinct_regions(self):
        self.assertEqual(len(self.statistics), 20)
        assigned = [code for f in self.statistics for code in f['properties']['modernLhaCodes']]
        lhas = [f['properties']['code'] for f in read(PUBLIC / 'display-lha.geojson')['features']]
        self.assertEqual(Counter(assigned), Counter(lhas))
        by_code = {f['properties']['code']: f for f in self.statistics}
        self.assertEqual(by_code['5917']['properties']['modernLhaCodes'], ['221'])  # Burnaby
        self.assertNotIn('221', by_code['5908']['properties']['modernLhaCodes'])  # Simon Fraser
        self.assertIn('518', by_code['5913']['properties']['modernLhaCodes'])  # Nisga'a in NW statistics
        for feature in self.statistics:
            self.assertTrue(shape(feature['geometry']).is_valid)

    def test_written_definitions_do_not_collapse_related_nisgaa_identity(self):
        definitions = read(RESEARCH / 'boundary-definition-evidence.json')['records']
        direct = [row for row in definitions if not row['relatedEntityOnly']]
        related = [row for row in definitions if row['relatedEntityOnly']]
        self.assertEqual(len(direct), 44)
        self.assertEqual(len(related), 1)
        self.assertIn('nisgaa', related[0]['areaId'])
        self.assertTrue(all(not row['boundaryVerified'] for row in definitions))
        self.assertEqual(self.report['summary']['verifiedHistoricalBoundaries'], 0)

    def test_coastal_comparison_preserves_displacement_and_records_local_review(self):
        area = next(row for row in self.report['assessments'] if row['areaId'] == 'vancouver-richmond-health-board')
        self.assertFalse(area['trace']['clippedToModernCoverage'])
        self.assertLess(area['sourceDrawingVsModernCandidate']['sourceCovered'], .9)
        self.assertGreater(area['sourceDrawingVsModernCandidate']['iou'], .4)
        review = self.report['alignmentReviews'][area['areaId']]
        self.assertFalse(review['activeRegistrationChanged'])
        self.assertEqual(round(review['supersededComparison']['metrics']['iou'] * 100), 29)
        original = next(step for step in review['steps'] if step['northShiftMetres'] == 0)
        north = next(step for step in review['steps'] if step['northShiftMetres'] == 5000)
        self.assertGreater(north['metricsByLayer']['lha']['iou'], original['metricsByLayer']['lha']['iou'])
        a = transform(TO_METRES, shape(original['geometry'])).centroid
        b = transform(TO_METRES, shape(north['geometry'])).centroid
        self.assertAlmostEqual(b.y - a.y, 5000, delta=.2)
        self.assertAlmostEqual(b.x, a.x, delta=.2)
        check = review['physicalCheck']
        self.assertFalse(check['usedForFitting'])
        self.assertTrue(check['independentOfVancouverRichmondCandidate'])
        self.assertAlmostEqual(check['targetAreaKm2'], 50.51, delta=.1)
        self.assertGreater(check['targetMinusSourceCentroidMetres']['north'], 5000)
        self.assertLess(check['scenarios'][1]['p95Metres'], check['scenarios'][0]['p95Metres'])

    def test_working_local_alignment_exports_reference_and_both_traces(self):
        review = self.report['alignmentReviews']['vancouver-richmond-health-board']
        self.assertTrue(review['workingAlignment']['enabled'])
        self.assertTrue(review['localDisplayAlignmentApplied'])
        self.assertFalse(review['activeRegistrationChanged'])
        adjusted = read(PUBLIC / 'adjusted-source-traces.geojson')['features']
        self.assertEqual(len(adjusted), 1)
        self.assertEqual(adjusted[0]['properties']['code'], 'vancouver-richmond-health-board')
        original = next(f for f in self.drawn if f['properties']['code'] == 'vancouver-richmond-health-board')
        from shapely.affinity import translate
        expected = translate(transform(TO_METRES, shape(original['geometry'])), yoff=5000)
        actual = transform(TO_METRES, shape(adjusted[0]['geometry']))
        self.assertLess(expected.hausdorff_distance(actual), .2)
        self.assertFalse(adjusted[0]['properties']['boundaryIdentityVerified'])
        bundle = read(PUBLIC / review['workingAlignment']['downloadFile'])
        self.assertEqual(Counter(f['properties']['layerRole'] for f in bundle['features']),
                         {'original-trace': 1, 'adjusted-trace': 1, 'current-reference': 7})
        self.assertEqual(len({f['id'] for f in bundle['features']}), 9)
        reference = {f['properties']['code']: f['geometry'] for f in read(PUBLIC / 'display-lha.geojson')['features']}
        for f in bundle['features']:
            if f['properties']['layerRole'] == 'current-reference':
                self.assertEqual(f['geometry'], reference[f['properties']['code']])


if __name__ == '__main__':
    unittest.main()
