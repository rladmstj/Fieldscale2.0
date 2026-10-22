<div align="center">
<h2>Fieldscale 2.0: Spatiotemporal Tail-adaptive Rescaling for Thermal Infrared Images</h2>

**Eunseo Kim** · Hyeonjae Gil · Tai Hyoung Rhee · Ayoung Kim · Dongjae Lee<sup>*</sup>

Department of Mechanical Engineering, Seoul National University

**ICCAS 2026**

<sup>*</sup>Corresponding author
</div>

Python code for **Fieldscale 2.0**, which rescales high-bit-depth thermal infrared images and video frames to 8-bit images.

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
