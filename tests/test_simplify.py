import cv2
import numpy as np

from vectorizer.simplify import build_bezier_path, simplify_contour, smooth_points


def test_simplify_contour_reduces_circle_points() -> None:
    image = np.zeros((80, 80), dtype=np.uint8)
    cv2.circle(image, (40, 40), 25, 255, thickness=1)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = contours[0]

    simplified = simplify_contour(contour, epsilon_ratio=0.02)

    assert len(simplified) < len(contour)
    assert len(simplified) >= 3


def test_smooth_points_chaikin_adds_points() -> None:
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]

    smoothed = smooth_points(square, method="chaikin")

    assert len(smoothed) > len(square)
    assert smoothed[0] == smoothed[-1]


def test_build_bezier_path_uses_cubic_commands() -> None:
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]

    path = build_bezier_path(square)

    assert path.startswith("M 0 0")
    assert "C " in path
    assert path.endswith("Z")

