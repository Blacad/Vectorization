from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from vectorizer.color_quantize import build_colored_paths, extract_color_regions, quantize_colors
from vectorizer.contour import ContourRegion, build_polygon_path, contour_to_points, find_contours
from vectorizer.exceptions import ParameterError
from vectorizer.io import get_image_info, load_image
from vectorizer.preprocess import (
    binarize_image,
    convert_color_space,
    denoise_image,
    morphology_process,
    resize_if_needed,
    to_grayscale,
)
from vectorizer.simplify import (
    build_bezier_path,
    filter_short_segments,
    simplify_contour,
    smooth_points,
)
from vectorizer.svg_export import write_svg


@dataclass(frozen=True)
class VectorizeOptions:
    mode: str = "binary"
    threshold: int | None = None
    min_area: float = 10.0
    colors: int = 8
    epsilon_ratio: float = 0.002
    invert: bool = False
    max_size: int | None = None
    smooth: str = "none"


@dataclass(frozen=True)
class ConversionSummary:
    input_path: str
    output_path: str
    mode: str
    width: int
    height: int
    path_count: int
    colors: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_options(options: VectorizeOptions) -> None:
    if options.mode not in {"binary", "color"}:
        raise ParameterError("mode must be one of: binary, color")
    if options.threshold is not None and not 0 <= options.threshold <= 255:
        raise ParameterError("threshold must be between 0 and 255")
    if options.min_area < 0:
        raise ParameterError("min_area must be >= 0")
    if options.colors < 1:
        raise ParameterError("colors must be >= 1")
    if options.epsilon_ratio < 0:
        raise ParameterError("epsilon_ratio must be >= 0")
    if options.max_size is not None and options.max_size < 1:
        raise ParameterError("max_size must be >= 1")
    if options.smooth not in {"none", "chaikin", "bezier"}:
        raise ParameterError("smooth must be one of: none, chaikin, bezier")


def _resize_with_scale(image: np.ndarray, max_size: int | None) -> tuple[np.ndarray, float, float]:
    original_height, original_width = image.shape[:2]
    resized = resize_if_needed(image, max_size=max_size)
    resized_height, resized_width = resized.shape[:2]
    scale_x = original_width / float(resized_width)
    scale_y = original_height / float(resized_height)
    return resized, scale_x, scale_y


def _scale_points(
    points: list[tuple[float, float]],
    scale_x: float,
    scale_y: float,
) -> list[tuple[float, float]]:
    return [(x * scale_x, y * scale_y) for x, y in points]


def _region_to_path(
    region: ContourRegion,
    epsilon_ratio: float,
    smooth: str,
    scale_x: float,
    scale_y: float,
) -> str:
    path_parts: list[str] = []
    for contour in (region.outer, *region.holes):
        simplified = simplify_contour(contour, epsilon_ratio=epsilon_ratio, max_points=1500)
        points = contour_to_points(simplified)
        points = filter_short_segments(points, min_length=0.5)
        points = _scale_points(points, scale_x, scale_y)
        points = smooth_points(points, method=smooth, iterations=1)
        path = build_bezier_path(points) if smooth == "bezier" else build_polygon_path(points)
        if path:
            path_parts.append(path)
    return " ".join(path_parts)


def vectorize_binary(
    image: np.ndarray,
    options: VectorizeOptions,
) -> tuple[list[dict[str, Any]], int, int]:
    """Vectorize a high-contrast image into black SVG paths."""
    _validate_options(options)
    source_info = get_image_info(image)
    processed, scale_x, scale_y = _resize_with_scale(image, options.max_size)
    gray = to_grayscale(processed)
    denoised = denoise_image(gray, method="gaussian", kernel_size=3)
    binary = binarize_image(
        denoised,
        method="fixed" if options.threshold is not None else "otsu",
        threshold=options.threshold,
        invert=options.invert,
    )
    cleaned = morphology_process(binary, op="open", kernel_size=3, iterations=1)
    regions = find_contours(cleaned, min_area=options.min_area, retrieve_holes=True)

    paths: list[dict[str, Any]] = []
    for region in regions:
        path = _region_to_path(region, options.epsilon_ratio, options.smooth, scale_x, scale_y)
        if path:
            paths.append(
                {
                    "path": path,
                    "fill": "#000000",
                    "stroke": "none",
                    "area": float(region.area * scale_x * scale_y),
                }
            )

    paths.sort(key=lambda item: float(item["area"]), reverse=True)
    return paths, int(source_info["width"]), int(source_info["height"])


def vectorize_color(
    image: np.ndarray,
    options: VectorizeOptions,
) -> tuple[list[dict[str, Any]], int, int]:
    """Vectorize an image into color-filled SVG paths."""
    _validate_options(options)
    source_info = get_image_info(image)
    processed, scale_x, scale_y = _resize_with_scale(image, options.max_size)
    rgb = convert_color_space(processed, target="rgb")
    quantized, colors = quantize_colors(rgb, k=options.colors)
    regions = extract_color_regions(
        quantized,
        colors,
        min_area=options.min_area,
        epsilon_ratio=options.epsilon_ratio,
        smooth=options.smooth,
        scale_x=scale_x,
        scale_y=scale_y,
    )
    paths = build_colored_paths(regions)
    return paths, int(source_info["width"]), int(source_info["height"])


def convert_bitmap_to_svg(
    input_path: str | Path,
    output_path: str | Path,
    options: VectorizeOptions | None = None,
) -> ConversionSummary:
    """Run the selected vectorization pipeline and write an SVG file."""
    options = options or VectorizeOptions()
    _validate_options(options)
    image = load_image(input_path)

    if options.mode == "binary":
        paths, width, height = vectorize_binary(image, options)
        color_count: int | None = None
    else:
        paths, width, height = vectorize_color(image, options)
        color_count = len({item["fill"] for item in paths})

    write_svg(width, height, paths, output_path)
    return ConversionSummary(
        input_path=str(input_path),
        output_path=str(output_path),
        mode=options.mode,
        width=width,
        height=height,
        path_count=len(paths),
        colors=color_count,
    )
