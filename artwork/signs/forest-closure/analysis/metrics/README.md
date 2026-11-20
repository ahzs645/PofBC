# Fixed-layout overlap diagnostics

These are in-sample fit diagnostics: the same two photographs informed the reconstruction. They do not identify a typeface and are not independent validation accuracy.

quantitative.json records all scores, exact method, thresholds, threshold sensitivity, SVG file hashes and fixed registration assumptions. No local letter or word alignment occurs in this analysis. Each artwork group keeps its published position; only the fixed measurement coordinate frame is inverted to make the sloping word readable.

Difference images: cyan is photographic ink only; magenta is vector ink only; dark is overlap; white is background. Each source and vector bitmap mask is also saved separately. The coloured *_ink.png files have transparency for interactive overlays.

The area measures (IoU and Dice) compare binary ink coverage. Boundary F1 compares both directions of the inner ink boundary within two canonical pixels, after 3x3 binary erosion defines the boundary. Values depend on the photograph threshold, soft print edges, the inferred equilateral layout and camera registration.

Re-run: python3 source/measure_overlap.py
Include revised CLOSED notice: python3 source/measure_overlap.py --include-closed-panel
