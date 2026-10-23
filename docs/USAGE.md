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

Specify only the input and output folders to use the paper defaults. Each image is processed independently, with temporal smoothing disabled.

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/images
```

Use single-channel raw thermal images, typically `uint16` TIFF or PNG files. Each image dimension must be at least the corresponding grid dimension (`8,8` by default).

The runner reads files directly inside the input folder in filename order. The output folder contains 8-bit images with the original filenames, `manifest.csv`, and `summary.json`. The manifest records the actual LES threshold for each image; the summary records settings, runtime versions, and source fingerprints. Choose a separate output folder; rerunning replaces matching output files.

## Process a video sequence

Add `--video` for ordered raw frames from one sequence:

```bash
python -m fieldscale2 \
  --input-dir /path/to/ordered_raw_frames \
  --output-dir outputs/video \
  --video
```

The first 20 frames use SMA initialization. From frame 21 onward, the knot grids use EMA with `alpha = 1/21`. Changing `--ema-period N` changes both the initialization window and the derived coefficient `alpha = 1/(N+1)`.

Use one sequence per folder and zero-padded filenames such as `000001.tiff`. Video processing is sequential. Start a new command for each sequence; in the Python API, create a new processor or call `reset_temporal_state()`.

## Parameters

The following options are optional. Omitting them uses the paper settings in both the CLI and Python API.

| Paper setting | CLI option | Default |
| --- | --- | --- |
| LES threshold, τ | `--max-diff` | `500` |
| Local grid | `--grid-shape` | `8,8` |
| Lower, intermediate, upper knot percentiles | `--percentiles` | `0,99,100` |
| Message-passing iterations | `--iteration` | `7` |
| Tail activation threshold, ρ_act | `--tail-activation-threshold` | `0.3` |
| Video smoothing window, N | `--ema-period` | `20` |

For example, to experiment with a different LES threshold and tail activation threshold:

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/custom \
  --max-diff 300 \
  --tail-activation-threshold 0.4
```

`--max-diff` applies the supplied fixed threshold to both LES directions. `--percentiles` accepts exactly three increasing values in `[0,100]`; the middle value defines the body/tail boundary. For example, `--percentiles 0,95,100` changes the intermediate knot to P95. EMA settings apply only with `--video`.

The tail/body span ratio `r` is computed from the refined knots. When `r` exceeds the activation threshold, the tail output width is `w_T,lin / (1+r)`; otherwise, the linear width is retained. The remaining output width is assigned to the body.

Other implementation settings are kept internally: a one-unit minimum knot interval, averaging the intermediate knot with its neighborhood mean, the P95 upper-knot floor, P98-based ordering repair, and bilinear field interpolation.

## Optional postprocessing

The paper allows gamma correction and CLAHE after rescaling. This implementation enables gamma `1.5` and CLAHE by default; these numerical postprocessing choices are implementation defaults.

- `--gamma VALUE` changes gamma; `--gamma 0` disables gamma correction.
- `--no-clahe` disables CLAHE.

## Save diagnostic images

```bash
python -m fieldscale2 \
  --input-dir /path/to/raw_frames \
  --output-dir outputs/debug \
  --combined-dir outputs/debug/previews \
  --save-debug-overlays \
  --limit 5
```

Diagnostic panels are rendered only when requested. They are saved under `outputs/debug/debug_overlays/` and `outputs/debug/previews/`. Use `--workers N` to process independent images in parallel; the default is one worker.

## Python API

```python
from fieldscale2 import MultiKnotPercentileFieldscale

image_processor = MultiKnotPercentileFieldscale()
video_processor = MultiKnotPercentileFieldscale(video=True)
custom_processor = MultiKnotPercentileFieldscale(
    max_diff=300,
    tail_activation_threshold=0.4,
)
```

Pass an image path or a single-channel NumPy array to the processor. The same paper parameters are available as keyword arguments, with `grid_shape`, `percentiles`, `iteration`, and `ema_period` matching their CLI names.

## All options

```bash
python -m fieldscale2 --help
```

The direct script entry point is also available as `python fieldscale2/fieldscale_multiknot_batch.py`.
