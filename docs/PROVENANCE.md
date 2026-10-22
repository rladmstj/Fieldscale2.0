# Source provenance

The Python implementation is adapted from `rladmstj/Fieldscale2.0`, commit
`c55cabc2a4ebcbf32c3e1ed75e4d84d028ce0899`.

- `fieldscale2/fieldscale_multiknot.py` preserves the committed implementation; trailing whitespace was removed from one blank line.
- `fieldscale2/fieldscale_multiknot_batch.py` adds portable input/output paths, the paper's default configuration, package imports, and basic argument checks.
- `fieldscale2/__init__.py` and `fieldscale2/__main__.py` expose the package and command-line entry point.

The code retains the original [Fieldscale](https://github.com/HyeonJaeGil/fieldscale)
MIT copyright notice. Uncommitted local experiments, datasets, paper source files,
and generated experiment outputs are not included.

## README figures

The README uses the manuscript's original figures, exported from the author's Overleaf project:

| Original vector figure | README preview | Manuscript figure |
| --- | --- | --- |
| `assets/pdf/saturation.pdf` | `assets/saturation.png` | Figure 1: saturation and detail loss, FLIR ADAS v1 |
| `assets/pdf/darkening.pdf` | `assets/teaser.png` | Figure 2: residual darkening, FLIR ADAS v2 |
| `assets/pdf/overview.pdf` | `assets/overview.png` | Figure 3: pipeline overview |

The PNG previews are rendered from these PDFs with Poppler. The original figure contents are preserved; no synthetic results or image enhancements are added.
