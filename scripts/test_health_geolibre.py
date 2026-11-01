import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import rasterio

from import_health_gcps import import_gcps
from rectify_health_maps import PUBLIC, RESEARCH, TO_METRES


class GeoLibreWorkflowTests(unittest.TestCase):
    def test_csv_round_trip_preserves_pdf_page_coordinates_and_active_baseline(self):
        baseline_path = RESEARCH / 'rectification-controls.json'
        before = hashlib.sha256(baseline_path.read_bytes()).hexdigest()
        proposal = import_gcps('boards', PUBLIC / 'geolibre/boards-gcps.csv', PUBLIC / 'geolibre')
        self.assertTrue(proposal['candidateOnly'])
        self.assertFalse(proposal['proposal']['independentAccuracyEstablished'])
        original = json.loads(baseline_path.read_text())['pages'][0]['controls']
        imported = proposal['pages'][0]['controls']
        for a, b in zip(original, imported):
            self.assertEqual(a['pagePoint'], b['pagePoint'])
            self.assertEqual(a['longitudeLatitude'], b['longitudeLatitude'])
        self.assertEqual(before, hashlib.sha256(baseline_path.read_bytes()).hexdigest())

    def test_invalid_control_rows_are_rejected_instead_of_silently_skipped(self):
        for bad_row in [['nan', '1', '-126', '54'], ['999999', '1', '-126', '54'], ['1', '1', '-126', '91']]:
            with self.subTest(row=bad_row), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / 'bad.csv'
                with path.open('w', newline='') as output:
                    writer = csv.writer(output)
                    writer.writerow(['pixelX', 'pixelY', 'lng', 'lat'])
                    writer.writerow(bad_row)
                with self.assertRaises(ValueError):
                    import_gcps('boards', path, PUBLIC / 'geolibre')

    def test_geotiffs_have_real_crs_layout_and_input_provenance(self):
        manifest = json.loads((PUBLIC / 'geolibre/image-manifest.json').read_text())
        for image in manifest['images']:
            with self.subTest(map=image['mapId']), rasterio.open(PUBLIC / 'geolibre' / image['cog']) as dataset:
                self.assertEqual(dataset.crs.to_epsg(), 3857)
                self.assertEqual(dataset.tags(ns='IMAGE_STRUCTURE')['LAYOUT'], 'COG')
                self.assertEqual(dataset.count, 4)
                self.assertTrue(dataset.read(4).max() > 0)
                self.assertEqual(dataset.tags()['SOURCE_PDF_SHA256'], manifest['sourceSha256'])
                for point in image['controls']:
                    from pyproj import Transformer
                    x, y = Transformer.from_crs(4326, 3857, always_xy=True).transform(*point['longitudeLatitude'])
                    row, col = dataset.index(x, y)
                    self.assertTrue(0 <= row < dataset.height and 0 <= col < dataset.width)


if __name__ == '__main__':
    unittest.main()
