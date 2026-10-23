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

This is the default mode. Each image is rescaled independently; SMA and EMA are disabled, and the output does not depend on previously processed images. EMA options apply only with `--video`.

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/demo \
  --workers 1
```

Use single-channel raw thermal frames, typically `uint16` TIFF or PNG files. The runner reads files directly inside the input folder in filename order.

Each image dimension must be at least as large as the corresponding grid dimension (`8,8` by default). Color images are not supported.

The output folder contains 8-bit images with the original filenames, `manifest.csv`, and `summary.json`. Choose a separate output folder; rerunning replaces matching output files.

## Process a video sequence

Enable `--video` for temporally ordered raw frames from one sequence. It adds temporal smoothing to the spatial and tail-adaptive rescaling used in image mode.

```bash
python -m fieldscale2 \
  --input-dir /path/to/ordered_raw_frames \
  --output-dir outputs/video \
  --video \
  --workers 1
```

Use one sequence per folder and zero-padded filenames such as `000001.tiff` to preserve temporal order. Video processing is sequential, including when a higher worker count is requested.

By default, the first 20 frames use SMA initialization. From frame 21 onward, the knot grids are updated with EMA using `alpha = 1 / 21`. Set `--ema-period N` to change the initialization window; the default EMA coefficient becomes `1 / (N + 1)`. An explicit `--ema-alpha-override` replaces this coefficient in video mode.

Start a new command for each sequence. In the Python API, create a new processor or call `reset_temporal_state()` before a new sequence.

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
- `--video` enables SMA initialization and EMA for ordered video frames. Without it, every image is processed independently.
- `--ema-period` defaults to `20` and applies only in video mode. The default EMA coefficient is `1 / (N + 1)`; `--ema-alpha-override` sets it explicitly.
- The legacy `--tail-activation-ratio` name refers to the compression offset in this implementation. Tail adjustment is activated at a fixed ratio of `0.3`.

```bash
python -m fieldscale2 --help
```

The direct script entry point is also available:

```bash
python fieldscale2/fieldscale_multiknot_batch.py --help
```
