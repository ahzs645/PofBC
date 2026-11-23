# Current pale-tree construction

This file supersedes the separate pass07 pale-tree refinement. The current pale tree uses the authored dark-tree branch vocabulary under the affine correspondence recorded in shared-tree-landmarks.json. The pale_construction field in tree-geometry.json records that transform and the dark voids deliberately excluded from the pale instance.

The completion_* components rebuild the fuller pale right canopy and visible brush windows. They are not part of the common master. instance_loose_fleck is a small independently authored basal mark. Shared components are stored explicitly so the portable build has no scientific-library dependencies.

To regenerate shared components after editing the dark master, run regenerate_shared_pale.py and then assemble_logo.py --export. Regeneration preserves completion_* and instance_* components. NumPy and svgpathtools are required only for that optional geometry transformation.

The common pattern is strongly supported by eleven visually paired source features, but it is a reconstruction hypothesis. The source does not prove that the two complete historical trees were identical paths at different sizes. Hidden pale geometry is deliberately simple and remains interpretive.
