# CLOSED strip boundary correction

## What was wrong

The legacy registration took the lower corners of the CLOSED photograph (near y1051 and y1058) as corners of the dark status strip. Fresh examination shows a physical lower edge around y1022, with trees, post and background texture below it. The left plate edge also starts around x36 rather than the photograph's x10 border. Therefore the legacy 1000x158 apparent ratio was not a valid board observation.

## Revised interpretation

Use one shared 1000x130 rectangular design convention for both OPEN and CLOSED. The OPEN coordinates are unchanged. Revised CLOSED ideal edge corners are TL(36,885.5), TR(1044,893), BR(1043,1020.5), BL(30,1023.5), approximately +/-3 pixels and +/-5 at the less distinct right edge. No engineering drawing establishes the exact ratio or physical dimensions. The source bulletin describes changing the signs between open and closed but does not specify the mechanism or dimensions.

The revised geometry removes background; it does not require a hinge angle or a deliberately circular O to explain the discrepancy. The prior 150-height suggestion based on O circularity should not be used as design evidence.

## Files

- registration.json: complete revised registration, preserving the legacy CLOSED panel fields under panel_revision.
- closed_panel_rectified.png and open_panel_rectified.png: both 1000x130.
- notice_layout.json: existing individual character boxes transformed through one old-to-new homography, with both projected quadrilaterals and enclosing axis-aligned boxes. This is no new glyph fitting.
- mapping_diagnostics.json: exact old-to-new projective matrix and the error of a whole-notice affine approximation.
- closed_panel_edge_correction.png: cyan physical strip boundary versus magenta legacy photographic frame boundary.
- shared_panel_rectification.png: two states in the same rectangular convention.

## Fair overlap evaluation

Freeze these revised corners before assessing any lettering changes. Render the vector and source in the same revised panel coordinates. Recompute Otsu/sensitivity and overlap rather than comparing newly normalized values directly to the earlier score. Keep identical masks/ROIs and no independent per-letter fitting. The old scores can remain an audit record but should be marked superseded because the old panel frame included background.

The exact old-to-new homography is inv(H_revised_to_photo) @ H_legacy_to_photo. SVG affine matrix transforms cannot represent that full projective map. Enclosing boxes and a whole-notice affine approximation are conveniences, and the revised artwork should be rechecked visually and numerically afterward. Differing letter width/height settings can be designed with shared masters; that is separate from proving the original historical font family.
