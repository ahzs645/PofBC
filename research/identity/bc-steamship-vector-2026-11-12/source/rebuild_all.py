#!/usr/bin/env python3
"""Regenerate outlined SVG masters. FontTools and the named local fonts are
required only to rebuild the lettering, not to use the finished SVG/PDF files.
"""
from pathlib import Path
import runpy
import shutil

HERE=Path(__file__).resolve().parent
OUT=HERE.parent
runpy.run_path(str(HERE/'rebuild_emblem.py'),run_name='__main__')
runpy.run_path(str(HERE/'rebuild_lettering.py'),run_name='__main__')
shutil.move(str(HERE/'bc-steamship-wordmark-outlined.svg'),OUT/'bc-steamship-wordmark.svg')
(OUT/'studies').mkdir(exist_ok=True)
shutil.move(str(HERE/'bc-steamship-token-inscription-provisional.svg'),OUT/'studies'/'token-inscription-provisional.svg')
runpy.run_path(str(HERE/'assemble_study.py'),run_name='__main__')
runpy.run_path(str(HERE/'rebuild_round_inscription.py'),run_name='__main__')
runpy.run_path(str(HERE/'assemble_round.py'),run_name='__main__')
print('SVG files regenerated. Render exports with Inkscape as described in README.md.')
