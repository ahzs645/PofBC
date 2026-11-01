"""Analytical registration fixtures; run with python -m unittest discover -s scripts -p test_rectify_health_maps.py."""
import unittest

from shapely.affinity import affine_transform
from shapely.geometry import Point

from rectify_health_maps import TO_METRES, fit_affine, read, RESEARCH


class RegistrationTests(unittest.TestCase):
    def test_affine_recovers_controls_and_preserves_an_independent_interior_point(self):
        # A source page constructed from projected coordinates has a known inverse.
        positions = [(-139, 60), (-120, 60), (-114, 49)]
        controls = []
        for lon, lat in positions:
            x, y = TO_METRES(lon, lat)
            controls.append({'pagePoint': [(x - 100000) / 4000, (2000000 - y) / 4000],
                             'longitudeLatitude': [lon, lat]})
        affine, residuals = fit_affine(controls)
        x, y = TO_METRES(-125, 53)
        point = affine_transform(Point((x - 100000) / 4000, (2000000 - y) / 4000), affine)
        self.assertAlmostEqual(point.x, x, places=5)
        self.assertAlmostEqual(point.y, y, places=5)
        self.assertLess(max(residuals), .01)

    def test_collinear_controls_are_rejected(self):
        controls = [{'pagePoint': [i, i], 'longitudeLatitude': [-130 + i, 50 + i]} for i in range(3)]
        with self.assertRaisesRegex(ValueError, 'collinear'):
            fit_affine(controls)

    def test_vancouver_richmond_membership_follows_both_printed_nines(self):
        page = read(RESEARCH / 'rectification-controls.json')['pages'][0]
        paths = {entry['areaId']: set(entry['drawingIndices']) for entry in page['areaDrawings']}
        self.assertEqual(paths['vancouver-richmond-health-board'], {76, 193})
        self.assertEqual(paths['south-fraser-health-region'], {198})
        self.assertTrue(paths['vancouver-richmond-health-board'].isdisjoint(paths['south-fraser-health-region']))


if __name__ == '__main__':
    unittest.main()
