from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from vectorizer.exceptions import ParameterError


@dataclass(frozen=True)
class ContourRegion:
    """An outer contour and optional inner hole contours."""

    outer: np.ndarray
    holes: tuple[np.ndarray, ...]
    area: float


def _normalize_binary(binary_image: np.ndarray) -> np.ndarray:
    if binary_image.ndim != 2:
        raise ParameterError("find_contours expects a 2D binary image.")
    if binary_image.dtype != np.uint8:
        binary_image = binary_image.astype(np.uint8)
    _, normalized = cv2.threshold(binary_image, 0, 255, cv2.THRESH_BINARY)
    return normalized


def _child_indices(hierarchy: np.ndarray, first_child: int) -> list[int]:
    children: list[int] = []
    current = first_child
    while current != -1:
        children.append(current)
        current = int(hierarchy[current][0])
    return children


def find_contours(
    binary_image: np.ndarray,
    min_area: float = 10,
    retrieve_holes: bool = True,
    retrieval_mode: int | None = None,
) -> list[ContourRegion]:
    """Find contour regions in a binary image, optionally preserving holes."""
    if min_area < 0:
        raise ParameterError("min_area must be >= 0")

    mode = retrieval_mode
    if mode is None:
        mode = cv2.RETR_CCOMP if retrieve_holes else cv2.RETR_EXTERNAL

    contours, hierarchy = cv2.findContours(
        _normalize_binary(binary_image),
        mode,
        cv2.CHAIN_APPROX_NONE,
    )
    if hierarchy is None:
        return []

    hierarchy_rows = hierarchy[0]
    regions: list[ContourRegion] = []

    if not retrieve_holes:
        for contour in contours:
            area = abs(float(cv2.contourArea(contour)))
            if area >= min_area:
                regions.append(ContourRegion(contour, (), area))
        return sorted(regions, key=lambda item: item.area, reverse=True)

    for index, contour in enumerate(contours):
        parent = int(hierarchy_rows[index][3])
        if parent != -1:
            continue

        area = abs(float(cv2.contourArea(contour)))
        if area < min_area:
            continue

        first_child = int(hierarchy_rows[index][2])
        holes: list[np.ndarray] = []
        if first_child != -1:
            for child_index in _child_indices(hierarchy_rows, first_child):
                child = contours[child_index]
                if abs(float(cv2.contourArea(child))) >= min_area:
                    holes.append(child)

        regions.append(ContourRegion(contour, tuple(holes), area))

    return sorted(regions, key=lambda item: item.area, reverse=True)


def contour_to_points(contour: np.ndarray) -> list[tuple[float, float]]:
    """Convert an OpenCV contour to a deduplicated, closed point list."""
    points: list[tuple[float, float]] = []
    for raw_point in contour.reshape(-1, 2):
        point = (float(raw_point[0]), float(raw_point[1]))
        if not points or points[-1] != point:
            points.append(point)

    if len(points) > 1 and points[0] != points[-1]:
        points.append(points[0])
    return points


def signed_area(points: list[tuple[float, float]]) -> float:
    """Return signed polygon area using the shoelace formula."""
    if len(points) < 3:
        return 0.0
    total = 0.0
    for index in range(len(points) - 1):
        x1, y1 = points[index]
        x2, y2 = points[index + 1]
        total += (x1 * y2) - (x2 * y1)
    return total / 2.0


def ensure_orientation(
    points: list[tuple[float, float]],
    clockwise: bool = True,
) -> list[tuple[float, float]]:
    """Return points in a consistent winding direction."""
    if len(points) < 3:
        return points
    is_clockwise = signed_area(points) < 0
    if is_clockwise == clockwise:
        return points
    body = list(reversed(points[:-1]))
    if body and body[0] != body[-1]:
        body.append(body[0])
    return body


def format_number(value: float) -> str:
    """Format SVG coordinates compactly without losing useful precision."""
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def build_polygon_path(points: list[tuple[float, float]]) -> str:
    """Build an SVG M/L/Z path from a closed or open point list."""
    if len(points) < 2:
        return ""

    clean_points = points[:-1] if points[0] == points[-1] else points
    if not clean_points:
        return ""

    first_x, first_y = clean_points[0]
    commands = [f"M {format_number(first_x)} {format_number(first_y)}"]
    for x, y in clean_points[1:]:
        commands.append(f"L {format_number(x)} {format_number(y)}")
    commands.append("Z")
    return " ".join(commands)
