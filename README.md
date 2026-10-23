<div align="center">
<h1>Fieldscale 2.0</h1>
<p><strong>Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images</strong></p>

**Eunseo Kim** · Hyeonjae Gil · Tai Hyoung Rhee · Ayoung Kim · Dongjae Lee<sup>*</sup>

Department of Mechanical Engineering, Seoul National University<br/>
**ICCAS 2026** · <sup>*</sup>Corresponding author

[Quick start](#quick-start) · [Usage guide](docs/USAGE.md) · [Citation](#citation)
</div>

**Fieldscale 2.0** turns high-bit-depth thermal images into 8-bit images while preserving scene details. Spatial adaptation and tail-adaptive rescaling address saturation and residual darkening. For video sequences, temporal smoothing with SMA initialization followed by EMA additionally reduces flickering. **Image mode processes each image independently, without temporal smoothing.**

<div align="center">
<a href="assets/pdf/overview.pdf"><img src="assets/overview.png" alt="Method overview: spatial field construction, optional temporal stabilization, and tail-adaptive 8-bit rescaling" width="720"/></a>
</div>

The examples below show two improvements over the [original Fieldscale](https://github.com/HyeonJaeGil/fieldscale): **building details remain visible in saturated regions**, and **backgrounds stay clearer around hot objects**. For video, smoothing the spatial fields helps reduce frame-to-frame flickering.

<div align="center">
<a href="assets/pdf/saturation.pdf"><img src="assets/saturation.png" alt="Saturation comparison on FLIR ADAS v1: Fieldscale above, Fieldscale 2.0 below" width="360" align="top"/></a>
<a href="assets/pdf/darkening.pdf"><img src="assets/teaser.png" alt="Residual darkening comparison on FLIR ADAS v2: Fieldscale above, Fieldscale 2.0 below" width="360" align="top"/></a>
</div>

## Quick start

Requires **Python 3.10+**, NumPy, and OpenCV.

```bash
git clone https://github.com/rladmstj/Fieldscale2.0.git
cd Fieldscale2.0
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Use single-channel raw thermal frames, typically `uint16` TIFF or PNG files.

### Images

The default mode processes each image independently. SMA and EMA are disabled.

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/demo
```

### Video sequences

Add `--video` to process ordered frames from one sequence. The first 20 frames initialize the knot grids with SMA; subsequent frames use EMA with `alpha = 1 / 21`. Frames are processed sequentially.

```bash
python -m fieldscale2 \
  --input-dir /path/to/ordered_raw_frames \
  --output-dir outputs/video \
  --video
```

Outputs in both modes include the rescaled images, `manifest.csv`, and `summary.json`.

### Default parameters

The paper settings are used automatically. Only the input and output folders are required:

| Setting | Default |
| --- | --- |
| Grid / percentile knots | `8×8` / `0, 99, 100` |
| LES threshold | `500`, shared by both directions |
| Message passing | `7` iterations |
| Tail activation threshold | `0.3` |
| Video smoothing window | `N=20`; EMA `alpha=1/(N+1)` |

These parameters can be changed for experiments; see the [parameter list](docs/USAGE.md#parameters). Optional postprocessing uses gamma `1.5` and CLAHE by default. The [usage guide](docs/USAGE.md) explains overrides, video processing, and diagnostic outputs.

## Citation

```bibtex
@misc{kim2026fieldscale2,
  title={Fieldscale 2.0: Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images},
  author={Kim, Eunseo and Gil, Hyeonjae and Rhee, Tai Hyoung and Kim, Ayoung and Lee, Dongjae},
  year={2026},
  note={ICCAS 2026},
  url={https://github.com/rladmstj/Fieldscale2.0}
}
```

## Acknowledgments and License

This work builds on [**Fieldscale**](https://github.com/HyeonJaeGil/fieldscale), the locality-aware thermal image rescaling method by Hyeonjae Gil, Myung-Hwan Jeon, and Ayoung Kim (RA-L 2024 / ICRA 2025). Fieldscale 2.0 extends its field-based approach with tail-adaptive rescaling and updated temporal smoothing.

The linked repository provides the original paper, supplementary video, and Python/C++ implementations.

This code is released under the [MIT License](LICENSE), with the original copyright notice retained.
