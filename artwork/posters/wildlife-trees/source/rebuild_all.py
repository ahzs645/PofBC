"""Rebuild the source-guided tree, portrait contexts, assembled poster and proofs.

The corrected animal SVGs and PofBC logo SVGs in assets/ are supplied inputs.
Their measured source and repair records are included for reference. Use
--assemble-only after changing copy or layout to reuse the existing artwork.
"""
from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble-only', action='store_true',
                        help='Reuse the tree and context SVGs; rebuild layout and exports.')
    args = parser.parse_args()
    if not shutil.which('inkscape'):
        parser.error('Inkscape must be installed and available on PATH.')
    import reconstruct_illustrations
    import finalise_tree
    import build_poster
    import export_outputs
    import build_proof
    import build_review

    if not args.assemble_only:
        print('Reconstructing the original tree penwork.', flush=True)
        reconstruct_illustrations.tree()
        for key in ('hawk', 'owl', 'squirrel', 'chickadee', 'bear', 'toad'):
            reconstruct_illustrations.panel_context(key)
        finalise_tree.run()
    build_poster.build(False)
    build_poster.build(True)
    export_outputs.run()
    build_proof.run()
    build_review.build(
        ROOT / 'Wildlife-Trees-outlined.svg',
        ROOT / 'reference/reference-native.jpg',
        ROOT / 'source/reference-regions.json',
        ROOT / 'Wildlife-Trees-overlay-review.html',
    )
    print('Rebuild complete.', flush=True)


if __name__ == '__main__':
    main()
