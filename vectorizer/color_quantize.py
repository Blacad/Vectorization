from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from vectorizer.contour import ContourRegion, build_polygon_path, contour_to_points, find_contours
from vectorizer.exceptions import ParameterError
from vectorizer.simplify import (
    build_bezier_path,
    filter_short_segments,
    simplify_contour,
    smooth_points,
)


def _color_to_hex(color: tuple[int, int, int] | np.ndarray) -> str:
    r, g, b = [int(v) for v in color]
    return f"#{r:02x}{g:02x}{b:02x}"


def _sort_centers_by_frequency(
    labels: np.ndarray,
    centers: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.bincount(labels.reshape(-1), minlength=len(centers))
    order = np.argsort(-counts)
    remap = np.zeros(len(order), dtype=np.int32)
    for new_index, old_index in enumerate(order):
        remap[old_index] = new_index
    return remap[labels.reshape(-1)], centers[order]


def _quantize_with_sklearn(
    pixels: np.ndarray,
    k: int,
    random_state: int,
    sample_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    from sklearn.cluster import KMeans

    rng = np.random.default_rng(random_state)
    fit_pixels = pixels
    if len(pixels) > sample_size:
        sample_indices = rng.choice(len(pixels), size=sample_size, replace=False)
        fit_pixels = pixels[sample_indices]

    model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    model.fit(fit_pixels)
    labels = model.predict(pixels).astype(np.int32)
    centers = np.clip(np.round(model.cluster_centers_), 0, 255).astype(np.uint8)
    return labels, centers


def _quantize_with_opencv(
    pixels: np.ndarray,
    k: int,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    cv2.setRNGSeed(int(random_state))
    compactness, labels, centers = cv2.kmeans(
        pixels.astype(np.float32),
        k,
        None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.2),
        5,
        cv2.KMEANS_PP_CENTERS,
    )
    _ = compactness
    return labels.reshape(-1).astype(np.int32), np.clip(np.round(centers), 0, 255).astype(np.uint8)


def quantize_colors(
    image: np.ndarray,
    k: int = 8,
    random_state: int = 0,
    sample_size: int = 10_000,
) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    """Quantize an RGB image to k colors."""
    if k < 1:
        raise ParameterError("k must be >= 1")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ParameterError("quantize_colors expects a 3-channel RGB image.")

    height, width = image.shape[:2]
    pixels = image.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    cluster_count = min(k, len(unique_colors))

    if cluster_count == len(unique_colors):
        centers = unique_colors.astype(np.uint8)
        label_lookup = {tuple(color): index for index, color in enumerate(centers)}
        labels = np.array([label_lookup[tuple(color)] for color in pixels], dtype=np.int32)
    else:
        try:
            labels, centers = _quantize_with_sklearn(
                pixels,
                cluster_count,
                random_state,
                sample_size,
            )
        except Exception:
            labels, centers = _quantize_with_opencv(pixels, cluster_count, random_state)

    sorted_labels, sorted_centers = _sort_centers_by_frequency(labels, centers)
    quantized = sorted_centers[sorted_labels].reshape(height, width, 3).astype(np.uint8)
    colors = [tuple(int(value) for value in color) for color in sorted_centers]
    return quantized, colors


def _scale_points(
    points: list[tuple[float, float]],
    scale_x: float,
    scale_y: float,
) -> list[tuple[float, float]]:
    return [(x * scale_x, y * scale_y) for x, y in points]


def _path_from_region(
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


def extract_color_regions(
    quantized_image: np.ndarray,
    colors: list[tuple[int, int, int]],
    min_area: float = 10,
    epsilon_ratio: float = 0.002,
    smooth: str = "none",
    scale_x: float = 1.0,
    scale_y: float = 1.0,
) -> list[dict[str, Any]]:
    """Extract SVG-ready regions for each representative RGB color."""
    if min_area < 0:
        raise ParameterError("min_area must be >= 0")
    if smooth not in {"none", "chaikin", "bezier"}:
        raise ParameterError("smooth must be one of: none, chaikin, bezier")

    regions: list[dict[str, Any]] = []
    for color in colors:
        color_array = np.array(color, dtype=np.uint8)
        mask = np.all(quantized_image == color_array, axis=2).astype(np.uint8) * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2, 2), dtype=np.uint8))
        contour_regions = find_contours(mask, min_area=min_area, retrieve_holes=True)
        for region in contour_regions:
            path = _path_from_region(region, epsilon_ratio, smooth, scale_x, scale_y)
            if path:
                regions.append(
                    {
                        "path": path,
                        "fill": _color_to_hex(color),
                        "stroke": "none",
                        "area": float(region.area * scale_x * scale_y),
                    }
                )
    return regions


def build_colored_paths(regions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort colored paths so larger regions are painted first."""
    return sorted(regions, key=lambda item: float(item.get("area", 0.0)), reverse=True)
