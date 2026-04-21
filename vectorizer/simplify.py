from __future__ import annotations

import math

import cv2
import numpy as np

from vectorizer.contour import build_polygon_path, format_number
from vectorizer.exceptions import ParameterError


def simplify_contour(
    contour: np.ndarray,
    epsilon_ratio: float = 0.002,
    max_points: int | None = None,
) -> np.ndarray:
    """Simplify an OpenCV contour with Douglas-Peucker approximation."""
    if epsilon_ratio < 0:
        raise ParameterError("epsilon_ratio must be >= 0")
    if max_points is not None and max_points < 3:
        raise ParameterError("max_points must be >= 3")

    perimeter = cv2.arcLength(contour, closed=True)
    epsilon = max(0.0, perimeter * epsilon_ratio)
    simplified = cv2.approxPolyDP(contour, epsilon, closed=True)

    if max_points is None or len(simplified) <= max_points:
        return simplified

    growing_epsilon = max(epsilon, 1.0)
    for _ in range(24):
        growing_epsilon *= 1.35
        simplified = cv2.approxPolyDP(contour, growing_epsilon, closed=True)
        if len(simplified) <= max_points:
            break
    return simplified


def filter_short_segments(
    points: list[tuple[float, float]],
    min_length: float = 1.0,
) -> list[tuple[float, float]]:
    """Remove points that create tiny consecutive line segments."""
    if min_length <= 0 or len(points) < 3:
        return points

    closed = points[0] == points[-1]
    body = points[:-1] if closed else points
    filtered = [body[0]]
    for point in body[1:]:
        last = filtered[-1]
        if math.hypot(point[0] - last[0], point[1] - last[1]) >= min_length:
            filtered.append(point)

    if closed and filtered and filtered[0] != filtered[-1]:
        filtered.append(filtered[0])
    return filtered


def _chaikin_once(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    closed = points[0] == points[-1]
    body = points[:-1] if closed else points
    if len(body) < 3:
        return points

    smoothed: list[tuple[float, float]] = []
    count = len(body)
    for index, current in enumerate(body):
        nxt = body[(index + 1) % count]
        q = ((0.75 * current[0]) + (0.25 * nxt[0]), (0.75 * current[1]) + (0.25 * nxt[1]))
        r = ((0.25 * current[0]) + (0.75 * nxt[0]), (0.25 * current[1]) + (0.75 * nxt[1]))
        smoothed.extend([q, r])

    if closed:
        smoothed.append(smoothed[0])
    return smoothed


def smooth_points(
    points: list[tuple[float, float]],
    method: str = "none",
    iterations: int = 1,
) -> list[tuple[float, float]]:
    """Smooth a closed point list. 'bezier' is handled during path building."""
    method = method.lower()
    if method in {"none", "bezier"}:
        return points
    if method != "chaikin":
        raise ParameterError("smooth method must be one of: none, chaikin, bezier")
    if iterations < 1:
        raise ParameterError("iterations must be >= 1")

    smoothed = points
    for _ in range(iterations):
        smoothed = _chaikin_once(smoothed)
    return smoothed


def build_bezier_path(points: list[tuple[float, float]]) -> str:
    """Build a closed Catmull-Rom-to-Bezier path from points."""
    if len(points) < 3:
        return build_polygon_path(points)

    body = points[:-1] if points[0] == points[-1] else points
    if len(body) < 3:
        return build_polygon_path(points)

    commands = [f"M {format_number(body[0][0])} {format_number(body[0][1])}"]
    count = len(body)
    for index, current in enumerate(body):
        previous = body[(index - 1) % count]
        nxt = body[(index + 1) % count]
        after_next = body[(index + 2) % count]

        c1 = (
            current[0] + ((nxt[0] - previous[0]) / 6.0),
            current[1] + ((nxt[1] - previous[1]) / 6.0),
        )
        c2 = (
            nxt[0] - ((after_next[0] - current[0]) / 6.0),
            nxt[1] - ((after_next[1] - current[1]) / 6.0),
        )
        commands.append(
            "C "
            f"{format_number(c1[0])} {format_number(c1[1])} "
            f"{format_number(c2[0])} {format_number(c2[1])} "
            f"{format_number(nxt[0])} {format_number(nxt[1])}"
        )
    commands.append("Z")
    return " ".join(commands)

