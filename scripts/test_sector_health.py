"""Include the historical health-source regressions in the standard test suite."""
import importlib.util
from pathlib import Path
import sys


def load_tests(loader, tests, pattern):
    collection = Path(__file__).resolve().parents[1] / "research/salaries/sector-health"
    spec = importlib.util.spec_from_file_location(
        "sector_health_regression_tests", collection / "test_sector_health_fraser.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(collection))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return loader.loadTestsFromModule(module)
