<div align="center">
<h1>Fieldscale 2.0</h1>
<p><strong>Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images</strong></p>

**Eunseo Kim** · Hyeonjae Gil · Tai Hyoung Rhee · Ayoung Kim · Dongjae Lee<sup>*</sup>

Department of Mechanical Engineering, Seoul National University<br/>
**ICCAS 2026** · <sup>*</sup>Corresponding author

[Method](#method) · [Results](#results) · [Quick start](#quick-start) · [Citation](#citation)
</div>

**Fieldscale 2.0** converts raw thermal images and video frames into 8-bit images, addressing saturation, residual darkening, and temporal flickering.

## Method

<div align="center">
<a href="assets/pdf/overview.pdf"><img src="assets/overview.png" alt="Method overview: spatial field construction, optional temporal stabilization, and tail-adaptive 8-bit rescaling" width="720"/></a>
</div>

1. **Spatial adaptation** constructs local intensity fields from the raw thermal input.
2. **Temporal stabilization (video)** smooths the fields across frames.
3. **Tail-adaptive mapping** produces the final 8-bit image.

## Results

<div align="center">
<a href="assets/pdf/saturation.pdf"><img src="assets/saturation.png" alt="Saturation comparison on FLIR ADAS v1: Fieldscale above, Fieldscale 2.0 below" width="360" align="top"/></a>
<a href="assets/pdf/darkening.pdf"><img src="assets/teaser.png" alt="Residual darkening comparison on FLIR ADAS v2: Fieldscale above, Fieldscale 2.0 below" width="360" align="top"/></a>
</div>

- **Saturation · FLIR ADAS v1:** More building structure remains visible in the highlighted region.
- **Residual darkening · FLIR ADAS v2:** The surrounding scene remains more visible around hot objects.

These are original examples from the paper. Click any figure to open its full-resolution PDF. The paper also evaluates temporal consistency and downstream feature matching.

## Quick start

Requires **Python 3.10+**, NumPy, and OpenCV.

```bash
git clone https://github.com/rladmstj/fieldscale2.git
cd fieldscale2
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Rescale single-channel raw thermal frames, typically `uint16` TIFF or PNG files:

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/demo \
  --workers 1
```

Outputs include the rescaled images, `manifest.csv`, and `summary.json`. See the [usage guide](docs/USAGE.md) for video processing and diagnostic outputs, or run `python -m fieldscale2 --help` for all options.

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
