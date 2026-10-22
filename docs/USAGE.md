# Usage

Run commands from the repository root with Python 3.10 or newer.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On servers without desktop libraries, use `opencv-python-headless` in place of `opencv-python`.

## Process images

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/demo \
  --workers 1
```

Use single-channel raw thermal frames, typically `uint16` TIFF or PNG files. The runner reads files directly inside the input folder in filename order. Use zero-padded names such as `000001.tiff` for ordered frames.

Each image dimension must be at least as large as the corresponding grid dimension (`8,8` by default). Color images are not supported.

The output folder contains 8-bit images with the original filenames, `manifest.csv`, and `summary.json`. Choose a separate output folder; rerunning replaces matching output files.

## Process a video sequence

```bash
python -m fieldscale2 \
  --input-dir /path/to/ordered_raw_frames \
  --output-dir outputs/video \
  --video \
  --ema-period 20 \
  --ema-alpha-override 0.047619047619047616 \
  --workers 1
```

Use one sequence per folder. Video processing is sequential, including when a higher worker count is requested. The example uses 20 frames of SMA initialization followed by EMA with `alpha = 1 / 21`; use at least 21 frames to reach the EMA stage.

## Save diagnostic images

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/debug \
  --combined-dir outputs/debug/previews \
  --save-debug-overlays \
  --workers 1 \
  --limit 5
```

Diagnostic images are saved under `outputs/debug/debug_overlays/` and `outputs/debug/previews/`.

Normal runs compute the rescaled frames without rendering diagnostic panels. Panels are generated only when an overlay, combined preview, or debug output is requested.

## Other options

The CLI uses three knots (`0,99,100`) by default. Additional knot and mapping options remain available for experiments.

- `--max-diff 500` sets one LES threshold for both high and low deviations of the upper knot from its neighborhood. It does not set a separate threshold for the lower knot.
- CLAHE is enabled by default; use `--no-clahe` to disable it.
- `--ema-alpha-override` selects the EMA coefficient explicitly. Without an override, the supplied implementation uses `2 / (N + 1)`.
- The legacy `--tail-activation-ratio` name refers to the compression offset in this implementation. Tail adjustment is activated at a fixed ratio of `0.3`.

```bash
python -m fieldscale2 --help
```

The direct script entry point is also available:

```bash
python fieldscale2/fieldscale_multiknot_batch.py --help
```
