"""Relocated-checkout regressions using the untouched frozen peer guard."""
import copy
from importlib import import_module, util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import gap_fill_repository_paths as adapter


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATHS = {
    'gap_health_other_history': ('ROOT', 'AREA', 'OLD'),
    'gap_health_other_history_export': ('ROOT', 'AREA', 'COLLECTION'),
}


class RelocatedFrozenRepositoryPaths(unittest.TestCase):
    def setUp(self):
        self.original_modules = {name: sys.modules.get(name) for name in MODULE_PATHS}
        self.original_values = {
            name: {field: getattr(module, field) for field in MODULE_PATHS[name]}
            for name, module in self.original_modules.items() if module is not None
        }
        self.addCleanup(self.restore_modules)
        self.core = import_module('gap_health_other_history')
        self.export = import_module('gap_health_other_history_export')
        self.cache = self.core.CACHE
        self.peer_constants = {
            name: value for name, value in vars(self.export).items()
            if name.startswith('PEER_') or name.startswith('CONTEXT')
        }
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.checkout = Path(self.directory.name) / 'a-different-checkout'
        self.checkout.mkdir()
        for field in ('PEER_FIRST', 'PEER_ADDITIVE', 'PEER_FINAL', 'PEER_ACCEPT'):
            relative = getattr(self.export, field)
            target = self.checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def tearDown(self):
        self.assertEqual(self.core.CACHE, self.cache)
        for name, value in self.peer_constants.items():
            self.assertEqual(getattr(self.export, name), value)

    def restore_modules(self):
        # Run even if setup or an assertion fails. Other tests retain references
        # to these exact objects, so restore globals and cache entries/absence.
        for name, module in self.original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                for field, value in self.original_values[name].items():
                    setattr(module, field, value)
                sys.modules[name] = module

    def assert_paths(self, root, export=None):
        self.assertEqual(self.core.ROOT, root)
        self.assertEqual(self.core.AREA, root / 'research/salaries/gap-fill-2026-11-02/health_other_history')
        self.assertEqual(self.core.OLD, root / 'research/salaries/gap-fill-2026-11-02/health_employees')
        if export is not None:
            self.assertEqual(export.ROOT, root)
            self.assertEqual(export.AREA, self.core.AREA)
            self.assertEqual(export.COLLECTION, root / 'research/salaries/gap-fill-health-other-history')

    def test_loaded_export_reads_all_pinned_peer_receipts_from_relocated_checkout(self):
        self.assertEqual(adapter.bind_frozen_checkout(self.checkout), self.checkout.resolve())
        self.assert_paths(self.checkout.resolve(), self.export)
        rows, changes = self.export.peer_selection()
        self.assertEqual(len(rows), 247)
        self.assertEqual(len(changes), 3)

    def test_future_export_import_inherits_the_bound_core(self):
        sys.modules.pop('gap_health_other_history_export')
        adapter.bind_frozen_checkout(self.checkout)
        loaded = import_module('gap_health_other_history_export')
        self.assert_paths(self.checkout.resolve(), loaded)
        self.assertEqual(len(loaded.peer_selection()[0]), 247)

    def test_default_root_follows_adapter_file_in_a_different_checkout(self):
        scripts = self.checkout / 'scripts'
        scripts.mkdir()
        copied = scripts / 'gap_fill_repository_paths.py'
        shutil.copyfile(Path(adapter.__file__), copied)
        spec = util.spec_from_file_location('relocated_path_adapter_fixture', copied)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.bind_frozen_checkout(), self.checkout.resolve())
        self.assert_paths(self.checkout.resolve(), self.export)
        self.assertEqual(len(self.export.peer_selection()[0]), 247)

    def test_changed_evidence_bytes_still_fail_the_original_hash_assertion(self):
        adapter.bind_frozen_checkout(self.checkout)
        self.export.peer_selection()
        final = self.checkout / self.export.PEER_FINAL
        value = json.loads(final.read_text())
        value['rows'][0]['remuneration'] = '0'
        final.write_text(json.dumps(value) + '\n')
        with self.assertRaisesRegex(AssertionError, 'pin changed'):
            self.export.peer_selection()

    def test_unapproved_in_memory_amount_change_still_fails_after_pin_verification(self):
        adapter.bind_frozen_checkout(self.checkout)
        real = self.export.pinned

        def changed(path, digest):
            value = real(path, digest)
            if path == self.export.PEER_FINAL:
                value = copy.deepcopy(value)
                value['rows'][0]['remuneration'] = '0'
            return value

        with mock.patch.object(self.export, 'pinned', changed):
            with self.assertRaises(AssertionError):
                self.export.peer_selection()

    def test_invalid_checkout_rejected_before_any_module_path_changes(self):
        prior = {field: getattr(self.core, field) for field in MODULE_PATHS['gap_health_other_history']}
        with self.assertRaises(ValueError):
            adapter.bind_frozen_checkout(self.checkout / 'missing')
        self.assertEqual({field: getattr(self.core, field) for field in prior}, prior)


if __name__ == '__main__':
    unittest.main()
