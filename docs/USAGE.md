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

Use one sequence per folder. Video processing is sequential, including when a higher worker count is requested.

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

## Other options

```bash
python -m fieldscale2 --help
```

The direct script entry point is also available:

```bash
python fieldscale2/fieldscale_multiknot_batch.py --help
```
