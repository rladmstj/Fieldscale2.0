from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import csv
import hashlib
import json
import platform

import cv2
import numpy as np

if __package__:
    from .fieldscale_multiknot import MultiKnotPercentileFieldscale, parse_percentiles
else:
    from fieldscale_multiknot import MultiKnotPercentileFieldscale, parse_percentiles


SUPPORTED_SUFFIXES = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp"}


@dataclass(frozen=True)
class BatchConfig:
    output_dir: str
    overlay_dir: str | None
    combined_dir: str | None
    debug_dir: str | None
    max_diff: float
    iteration: int
    gamma: float
    clahe: bool
    video: bool
    ema_period: int
    grid_shape: tuple[int, int]
    percentiles: tuple[float, ...]
    tail_activation_threshold: float


def parse_pair(text: str) -> tuple[int, int]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Expected two positive integers in rows,cols format.")
    try:
        values = (int(parts[0]), int(parts[1]))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Grid values must be integers in rows,cols format.") from error
    if values[0] <= 0 or values[1] <= 0:
        raise argparse.ArgumentTypeError("Grid values must be positive.")
    return values


def parse_percentile_text(text: str) -> tuple[float, ...]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Expected exactly three comma-separated percentiles.")
    try:
        values = tuple(float(part) for part in parts)
        if not all(np.isfinite(value) for value in values):
            raise ValueError("Percentiles must be finite.")
        return parse_percentiles(values)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rescale thermal frames with FIELDSCALE 2.0 using the paper's default parameters. "
            "Image mode is the default, with no temporal smoothing. Use --video for SMA/EMA smoothing."
        )
    )
    processing = parser.add_argument_group("Processing")
    processing.add_argument("--input-dir", type=Path, required=True, help="Folder of raw grayscale thermal frames.")
    processing.add_argument("--output-dir", type=Path, required=True, help="Separate folder for 8-bit frames and run metadata.")
    processing.add_argument("--overlay-dir", type=Path, default=None)
    processing.add_argument("--combined-dir", type=Path, default=None)
    processing.add_argument("--save-debug-overlays", action="store_true")
    processing.add_argument("--workers", type=int, default=1, help="Image-processing workers (default: 1); video is sequential.")
    processing.add_argument("--limit", type=int, default=None, help="Process at most this many frames.")

    paper = parser.add_argument_group("Paper parameters")
    paper.add_argument(
        "--max-diff", type=float, default=500.0,
        help="Fixed shared LES threshold for both upper-knot directions (default: 500).",
    )
    paper.add_argument("--iteration", type=int, default=7, help="Message-passing iterations (default: 7).")
    paper.add_argument("--grid-shape", type=parse_pair, default=(8, 8), metavar="ROWS,COLS", help="Local grid dimensions (default: 8,8).")
    paper.add_argument("--percentiles", type=parse_percentile_text, default=(0.0, 99.0, 100.0), metavar="LOW,MID,HIGH", help="Three strictly increasing percentiles; MID is the body/tail boundary (default: 0,99,100).")
    paper.add_argument(
        "--tail-activation-threshold", type=float, default=0.3,
        help="Activate tail rescaling when the tail/body span ratio exceeds this value (default: 0.3).",
    )
    paper.add_argument(
        "--video", action="store_true",
        help="Enable temporal smoothing: SMA warmup followed by EMA (default N=20, alpha=1/21).",
    )
    paper.add_argument(
        "--ema-period", type=int, default=20,
        help="SMA warmup length N for --video (default: 20); EMA alpha defaults to 1/(N+1).",
    )

    post = parser.add_argument_group("Optional post-processing")
    post.add_argument("--gamma", type=float, default=1.5, help="Gamma correction exponent; 0 disables it (default: 1.5).")
    post.add_argument("--no-clahe", action="store_true", help="Disable CLAHE (enabled by default).")
    args = parser.parse_args()
    if not args.input_dir.is_dir():
        parser.error("--input-dir must be an existing directory")
    input_root = args.input_dir.resolve()
    for name in ("output_dir", "overlay_dir", "combined_dir"):
        destination = getattr(args, name)
        if destination is not None and destination.resolve() == input_root:
            parser.error(f"--{name.replace('_', '-')} must differ from --input-dir")
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if not np.isfinite(args.max_diff) or args.max_diff < 0:
        parser.error("--max-diff must be finite and at least 0")
    if args.iteration < 0:
        parser.error("--iteration must be at least 0")
    if not np.isfinite(args.tail_activation_threshold) or args.tail_activation_threshold < 0:
        parser.error("--tail-activation-threshold must be finite and at least 0")
    if not np.isfinite(args.gamma) or args.gamma < 0:
        parser.error("--gamma must be finite and at least 0")
    if args.ema_period < 1:
        parser.error("--ema-period must be at least 1")
    return args


def iter_frame_files(input_dir: Path, limit: int | None = None) -> list[Path]:
    frame_files = sorted(
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if limit is not None:
        return frame_files[:max(0, int(limit))]
    return frame_files


def build_processor(config: BatchConfig) -> MultiKnotPercentileFieldscale:
    return MultiKnotPercentileFieldscale(
        max_diff=config.max_diff,
        iteration=config.iteration,
        gamma=config.gamma,
        clahe=config.clahe,
        video=config.video,
        ema_period=config.ema_period,
        grid_shape=config.grid_shape,
        percentiles=config.percentiles,
        tail_activation_threshold=config.tail_activation_threshold,
    )


def process_frame(
    frame_path: Path,
    config: BatchConfig,
    processor: MultiKnotPercentileFieldscale,
) -> dict[str, object]:
    if config.overlay_dir is None and config.combined_dir is None and config.debug_dir is None:
        output = processor(str(frame_path))
        debug = {}
    else:
        debug = processor.process_debug(str(frame_path))
        output = debug["rescaled"]
    frame_les_diff = processor.last_frame_les_diff
    frame_grid_span_median = processor.last_frame_grid_span_median
    output_path = Path(config.output_dir) / frame_path.name
    ok = cv2.imwrite(str(output_path), output)
    if not ok:
        raise IOError(f"Failed to write output image: {output_path}")

    overlay_path = None
    if config.overlay_dir is not None:
        overlay_path = Path(config.overlay_dir) / frame_path.name
        ok = cv2.imwrite(str(overlay_path), debug["curve_overlay"])
        if not ok:
            raise IOError(f"Failed to write overlay image: {overlay_path}")

    combined_path = None
    if config.combined_dir is not None:
        combined_path = Path(config.combined_dir) / frame_path.name
        ok = cv2.imwrite(str(combined_path), debug["combined_preview"])
        if not ok:
            raise IOError(f"Failed to write combined image: {combined_path}")

    curve_debug_path = None
    distribution_debug_path = None
    tail_ratio_debug_path = None
    body_slope_gain_debug_path = None
    p99_choice_debug_path = None
    board_debug_path = None
    preview_debug_path = None
    if config.debug_dir is not None:
        debug_dir = Path(config.debug_dir)
        curve_debug_path = debug_dir / f"{frame_path.stem}__curve.png"
        distribution_debug_path = debug_dir / f"{frame_path.stem}__distribution.png"
        tail_ratio_debug_path = debug_dir / f"{frame_path.stem}__tail_ratio.png"
        body_slope_gain_debug_path = debug_dir / f"{frame_path.stem}__body_slope_gain.png"
        p99_choice_debug_path = debug_dir / f"{frame_path.stem}__p99_choice.png"
        board_debug_path = debug_dir / f"{frame_path.stem}__board.png"
        preview_debug_path = debug_dir / f"{frame_path.stem}__debug.png"

        debug_outputs = [
            (curve_debug_path, debug["curve_overlay"]),
            (distribution_debug_path, debug["distribution_overlay"]),
            (tail_ratio_debug_path, debug["tail_ratio_overlay"]),
            (body_slope_gain_debug_path, debug["body_slope_gain_overlay"]),
            (p99_choice_debug_path, debug["p99_choice_overlay"]),
            (board_debug_path, debug["debug_board"]),
            (preview_debug_path, debug["debug_preview"]),
        ]
        for save_path, image_data in debug_outputs:
            ok = cv2.imwrite(str(save_path), image_data)
            if not ok:
                raise IOError(f"Failed to write debug image: {save_path}")

    return {
        "frame_name": frame_path.name,
        "frame_path": str(frame_path),
        "output_path": str(output_path),
        "overlay_path": None if overlay_path is None else str(overlay_path),
        "combined_path": None if combined_path is None else str(combined_path),
        "curve_debug_path": None if curve_debug_path is None else str(curve_debug_path),
        "distribution_debug_path": None if distribution_debug_path is None else str(distribution_debug_path),
        "tail_ratio_debug_path": None if tail_ratio_debug_path is None else str(tail_ratio_debug_path),
        "body_slope_gain_debug_path": None if body_slope_gain_debug_path is None else str(body_slope_gain_debug_path),
        "p99_choice_debug_path": None if p99_choice_debug_path is None else str(p99_choice_debug_path),
        "board_debug_path": None if board_debug_path is None else str(board_debug_path),
        "preview_debug_path": None if preview_debug_path is None else str(preview_debug_path),
        "frame_les_diff": frame_les_diff,
        "frame_grid_span_median": frame_grid_span_median,
        "output_mean": float(output.mean()),
        "output_min": int(output.min()),
        "output_max": int(output.max()),
    }


def analyze_one(frame_path: Path, config: BatchConfig) -> dict[str, object]:
    processor = build_processor(config)
    return process_frame(frame_path, config, processor)


def infer_sequence_key(frame_path: Path) -> str:
    stem = frame_path.stem
    if "-frame-" in stem:
        return stem.split("-frame-", maxsplit=1)[0]
    if "_frame" in stem:
        return stem.split("_frame", maxsplit=1)[0]
    return "__single_sequence__"


def save_manifest(rows: list[dict[str, object]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_run_metadata(config: BatchConfig) -> dict[str, object]:
    """Capture source provenance and settings derived from config before processing."""
    runner_path = Path(__file__)
    source_files = (runner_path.with_name("fieldscale_multiknot.py"), runner_path)
    return {
        "runtime_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "opencv": cv2.__version__,
        },
        "source_sha256": {
            f"fieldscale2/{source_path.name}": hashlib.sha256(source_path.read_bytes()).hexdigest()
            for source_path in source_files
        },
        "configured_effective_settings": {
            "les": {
                "threshold_policy": "fixed",
                "fixed_value": config.max_diff,
            },
            "tail": {
                "activation_threshold": config.tail_activation_threshold,
                "active_tail_width_formula": "wT_lin / (1 + r)",
            },
            "temporal": {
                "mode": "sma_then_ema" if config.video else "disabled",
                "warmup_frames": config.ema_period if config.video else None,
                "ema_alpha": 1.0 / (config.ema_period + 1.0) if config.video else None,
            },
        },
    }


def build_summary(
    rows: list[dict[str, object]],
    args: argparse.Namespace,
    config: BatchConfig,
    run_metadata: dict[str, object],
) -> dict[str, object]:
    total_frames = len(rows)
    observed_les_threshold_counts = {}
    for row in rows:
        if row["frame_les_diff"] is not None:
            threshold = float(row["frame_les_diff"])
            key = str(int(threshold)) if threshold.is_integer() else str(threshold)
            observed_les_threshold_counts[key] = observed_les_threshold_counts.get(key, 0) + 1
    return {
        "input_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "total_frames": total_frames,
        "params": {
            **asdict(config),
            "grid_shape": list(config.grid_shape),
            "percentiles": list(config.percentiles),
        },
        "run_metadata": {
            **run_metadata,
            "observed_les_threshold_counts": observed_les_threshold_counts,
        },
        "mean_output_mean": sum(float(row["output_mean"]) for row in rows) / total_frames,
    }


def main() -> None:
    args = parse_args()
    frame_files = iter_frame_files(args.input_dir, args.limit)
    if not frame_files:
        raise FileNotFoundError(f"No supported image files found in {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    overlay_dir = None if args.overlay_dir is None else args.overlay_dir
    if overlay_dir is not None:
        overlay_dir.mkdir(parents=True, exist_ok=True)
    combined_dir = None if args.combined_dir is None else args.combined_dir
    if combined_dir is not None:
        combined_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = args.output_dir / "debug_overlays" if args.save_debug_overlays else None
    if debug_dir is not None:
        debug_dir.mkdir(parents=True, exist_ok=True)
    config = BatchConfig(
        output_dir=str(args.output_dir),
        overlay_dir=None if overlay_dir is None else str(overlay_dir),
        combined_dir=None if combined_dir is None else str(combined_dir),
        debug_dir=None if debug_dir is None else str(debug_dir),
        max_diff=float(args.max_diff),
        iteration=int(args.iteration),
        gamma=float(args.gamma),
        clahe=not args.no_clahe,
        video=bool(args.video),
        ema_period=int(args.ema_period),
        grid_shape=args.grid_shape,
        percentiles=args.percentiles,
        tail_activation_threshold=float(args.tail_activation_threshold),
    )
    run_metadata = build_run_metadata(config)

    if config.video and args.workers > 1:
        print("video=True detected; forcing sequential processing to preserve EMA state.", flush=True)

    if args.workers <= 1 or config.video:
        rows = []
        processor = build_processor(config)
        current_sequence_key = None
        for index, frame_path in enumerate(frame_files, start=1):
            sequence_key = infer_sequence_key(frame_path)
            if sequence_key != current_sequence_key:
                processor.reset_temporal_state()
                current_sequence_key = sequence_key
            row = process_frame(frame_path, config, processor)
            rows.append(row)
            if index == 1 or index % 100 == 0 or index == len(frame_files):
                print(f"[{index}/{len(frame_files)}] saved {Path(row['output_path']).name}", flush=True)
    else:
        rows = []
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            for index, row in enumerate(executor.map(analyze_one, frame_files, [config] * len(frame_files)), start=1):
                rows.append(row)
                if index == 1 or index % 100 == 0 or index == len(frame_files):
                    print(f"[{index}/{len(frame_files)}] saved {Path(row['output_path']).name}", flush=True)

    manifest_path = args.output_dir / "manifest.csv"
    summary_path = args.output_dir / "summary.json"
    save_manifest(rows, manifest_path)
    summary = build_summary(rows, args, config, run_metadata)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_path),
        "total_frames": len(rows),
        "params": summary["params"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
