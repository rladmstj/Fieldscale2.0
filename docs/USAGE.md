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

The output folder contains 8-bit images with the original filenames, `manifest.csv`, and `summary.json`. The manifest records each frame's contrast statistic and actual LES threshold. The summary records threshold counts, Python/NumPy/OpenCV versions, and source fingerprints. Choose a separate output folder; rerunning replaces matching output files.

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

## Parameters

The CLI and Python processor use the same spatial defaults in both modes. Temporal settings apply only with `--video`.

| Option / setting | Default | Meaning |
| --- | --- | --- |
| `--grid-shape` | `8,8` | Local grid dimensions |
| `--percentiles` | `0,99,100` | Lower, middle, and upper knots |
| `--max-diff` | unset | Use frame-adaptive LES; supplying a number overrides it with a fixed threshold |
| `--les-mode` | `single` | One LES pass per direction |
| `--iteration` | `7` | Message-passing iterations |
| `--mid-alpha` | `0.5` | Intermediate-knot message-passing coefficient |
| `--min-interval` | `1` | Minimum interval between adjacent knots |
| `--enforce-mode` | `top_down` | Restore knot ordering from the upper knot downward |
| `--anchor-mode` | `tail_adaptive_split` | Body/tail output allocation |
| `--tail-split-percentile` | `99` | Percentile separating body and tail |
| Tail activation threshold | `0.3` | Activate tail adjustment when the tail/body span ratio exceeds this value |
| `--tail-activation-ratio` | `0.05` | Legacy option name for the compression offset; distinct from the activation threshold |
| `--tail-suppression-gain` | `1` | Compression strength |
| `--tail-min-output` | `0` | Minimum output width assigned to the tail; independent of the LES threshold |
| `--body-linear-cap-ratio` | `2` | Maximum body output width relative to its linear allocation |
| `--body-tail-slope-ratio-cap` | disabled | Optional additional cap on the body/tail slope ratio |
| `--gamma` | `1.5` | Gamma correction |
| CLAHE | enabled | Disable with `--no-clahe` |
| LES / message passing | enabled | Disable with `--no-les` / `--no-mp` |
| `--video` | off | Enable SMA initialization followed by EMA |
| `--ema-period` | `20` | Video initialization window N; EMA alpha defaults to `1/(N+1)` |
| `--ema-alpha-override` | unset | Explicit video EMA coefficient |

With `--max-diff` omitted, LES uses the median of the local `P95−P5` spans across the grid to choose its threshold:

| Median local span | LES threshold |
| --- | ---: |
| Less than `100` | `400` |
| `100` to less than `1000` | `500` |
| `1000` through `2000` | `600` |
| Greater than `2000` | `800` |

Both LES directions share the selected threshold. To use a fixed threshold, add `--max-diff 100` or another nonnegative value; the supplied value is applied directly. There is no separate `--min-diff` option. `--no-les` disables LES.

Tail widths use the configured compression offset and body amplification limit, while the activation threshold remains fixed at `0.3`. The tail/body span ratio is computed from the refined knots. `--tail-min-output` controls the output width of the tail and is independent of the LES threshold.

Additional knot and mapping options remain available for experiments. `--span-lambda` and `--slope-cap-ratio` apply to the alternative `span` anchor mode.

## Image-output validation

The default image command reproduced the decoded 8-bit pixel arrays of all **1,366 archived FLIR ADAS v1 images** and **1,144 currently available FLIR ADAS v2 images** exactly, using Python 3.10.20, NumPy 1.26.4, and OpenCV 4.11.0. These runs selected LES thresholds of 400 or 500. The v2 archive records 1,145 frames; one input/output pair is currently unavailable and was excluded from verification.

A 30-image check with Python 3.13.13, NumPy 2.5.4, and OpenCV 5.0.0 also matched the reference environment exactly. These checks establish reproduction of the available stored image outputs. Video SMA/EMA behavior was checked separately.

## Python API

```python
from fieldscale2 import MultiKnotPercentileFieldscale

image_processor = MultiKnotPercentileFieldscale()
video_processor = MultiKnotPercentileFieldscale(video=True)
```

Pass an image path or a single-channel NumPy array to the processor. Create a new video processor or call `reset_temporal_state()` between sequences.

## All options

```bash
python -m fieldscale2 --help
```

The direct script entry point is also available:

```bash
python fieldscale2/fieldscale_multiknot_batch.py --help
```
