from __future__ import annotations

import argparse
import sys

from vectorizer.exceptions import VectorizerError
from vectorizer.pipeline import VectorizeOptions, convert_bitmap_to_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bitmap-to-vector",
        description="Convert jpg/jpeg/png bitmap images into SVG vector paths.",
    )
    parser.add_argument("--input", required=True, help="Input jpg/jpeg/png image path.")
    parser.add_argument("--output", required=True, help="Output SVG path.")
    parser.add_argument("--mode", choices=["binary", "color"], default="binary")
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        help="Fixed binary threshold, 0-255.",
    )
    parser.add_argument("--min-area", type=float, default=10.0, help="Small contour filter area.")
    parser.add_argument("--colors", type=int, default=8, help="Color count for color mode.")
    parser.add_argument(
        "--epsilon-ratio",
        type=float,
        default=0.002,
        help="Douglas-Peucker simplification strength.",
    )
    parser.add_argument("--invert", action="store_true", help="Invert binary threshold polarity.")
    parser.add_argument(
        "--max-size",
        type=int,
        default=None,
        help="Resize longest side before tracing.",
    )
    parser.add_argument("--smooth", choices=["none", "chaikin", "bezier"], default="none")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = VectorizeOptions(
        mode=args.mode,
        threshold=args.threshold,
        min_area=args.min_area,
        colors=args.colors,
        epsilon_ratio=args.epsilon_ratio,
        invert=args.invert,
        max_size=args.max_size,
        smooth=args.smooth,
    )

    try:
        summary = convert_bitmap_to_svg(args.input, args.output, options)
    except VectorizerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Converted: {summary.input_path} -> {summary.output_path}")
    print(
        "Summary: "
        f"mode={summary.mode}, size={summary.width}x{summary.height}, paths={summary.path_count}"
    )
    if summary.colors is not None:
        print(f"Colors: {summary.colors}")
    return 0
