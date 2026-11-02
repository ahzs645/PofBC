"""Bind two frozen Other-history modules to this checkout, in memory only.

Call ``bind_frozen_checkout()`` in the same Python process before
unittest loads the frozen exporter. Original source files, evidence pins and
external PDF/cache locations remain unchanged.
"""
from importlib import import_module
from pathlib import Path
import sys


def bind_frozen_checkout(repository_root=None):
    """Return the resolved checkout and bind only its six repository paths.

    The core module is imported before binding. If the exporter is already
    loaded, update its copied ROOT/AREA values and derived COLLECTION as well.
    A future exporter import instead inherits the bound core paths normally.
    """
    root = (Path(__file__).resolve().parents[1] if repository_root is None
            else Path(repository_root).resolve())
    if not root.is_dir():
        raise ValueError('Repository checkout must be an existing directory')
    area = root / 'research/salaries/gap-fill-2026-11-02/health_other_history'
    core = import_module('gap_health_other_history')
    core.ROOT = root
    core.AREA = area
    core.OLD = root / 'research/salaries/gap-fill-2026-11-02/health_employees'
    export = sys.modules.get('gap_health_other_history_export')
    if export is not None:
        export.ROOT = root
        export.AREA = area
        export.COLLECTION = root / 'research/salaries/gap-fill-health-other-history'
    return root
