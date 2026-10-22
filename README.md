<div align="center">
<h2>Fieldscale 2.0: Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images</h2>

**Eunseo Kim** · Hyeonjae Gil · Tai Hyoung Rhee · Ayoung Kim · Dongjae Lee<sup>*</sup>

Department of Mechanical Engineering, Seoul National University

**ICCAS 2026**

<sup>*</sup>Corresponding author

[Overview](#overview) · [Visual comparisons](#visual-comparisons) · [Installation](#installation) · [Citation](#citation)
</div>

<div align="center">
<img src="assets/teaser.png" alt="Fieldscale and Fieldscale 2.0 on a FLIR ADAS v2 street scene, with enlarged regions showing residual darkening and recovered scene details" width="960"/>
<p><em>Preserving scene details around hot objects. Original Fieldscale (top) and Fieldscale 2.0 (bottom), from the paper's FLIR ADAS v2 example.</em></p>
</div>

## Overview

**Fieldscale 2.0** converts high-bit-depth thermal infrared images and video frames into 8-bit images for visualization and downstream vision tasks. It builds on Fieldscale to address saturation, residual darkening, and frame-to-frame flickering during thermal image rescaling.

- **Preserve local details:** retain visible structures in regions affected by saturation.
- **Improve scene visibility:** alleviate residual darkening around local hot regions.
- **Stabilize thermal video:** reduce frame-to-frame flickering through temporal field smoothing.

The paper evaluates rescaling quality, temporal consistency, and downstream feature matching on thermal image and video datasets.

<details>
<summary>Pipeline overview</summary>

<img src="assets/overview.png" alt="Paper pipeline overview: raw thermal input, spatial field construction, optional temporal stabilization, and 8-bit output" width="1200"/>

Spatial field estimation, optional temporal stabilization, and adaptive rescaling produce the final 8-bit frame. See the [original vector figure](assets/pdf/overview.pdf) for a larger view.

</details>

## Visual comparisons

<div align="center">
<img src="assets/saturation.png" alt="FLIR ADAS v1 comparison showing saturated building details in Fieldscale and preserved structures in Fieldscale 2.0" width="960"/>
</div>

**Reducing saturation and detail loss.** In this FLIR ADAS v1 example, Fieldscale 2.0 preserves more structural details in the highlighted region. The accompanying histograms illustrate how raw thermal intensities are mapped into the 8-bit range.

Both comparisons are original qualitative examples from the paper. The full-resolution [darkening](assets/pdf/darkening.pdf) and [saturation](assets/pdf/saturation.pdf) figures are included.

## Installation

Requires **Python 3.10 or newer**.

```bash
git clone https://github.com/rladmstj/fieldscale2.git
cd fieldscale2
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Only NumPy and OpenCV are required.

## Usage

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/demo \
  --workers 1
```

Use single-channel raw thermal frames, typically `uint16` TIFF or PNG files. Outputs include the rescaled images, `manifest.csv`, and `summary.json`.

See the [usage guide](docs/USAGE.md) for video processing and diagnostic outputs. Run `python -m fieldscale2 --help` to list all options.

## Citation

```bibtex
@misc{kim2026fieldscale2,
  title={Fieldscale 2.0: Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images},
  author={Kim, Eunseo and Gil, Hyeonjae and Rhee, Tai Hyoung and Kim, Ayoung and Lee, Dongjae},
  year={2026},
  note={ICCAS 2026},
  url={https://github.com/rladmstj/fieldscale2}
}
```

## Acknowledgments and License

This work builds on [Fieldscale](https://github.com/HyeonJaeGil/fieldscale). The original attribution is retained under the [MIT License](LICENSE). See [source provenance](docs/PROVENANCE.md).
