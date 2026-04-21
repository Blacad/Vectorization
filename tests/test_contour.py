import cv2
import numpy as np

from vectorizer.contour import build_polygon_path, contour_to_points, find_contours


def test_find_contours_preserves_hole() -> None:
    image = np.zeros((40, 40), dtype=np.uint8)
    cv2.rectangle(image, (5, 5), (34, 34), 255, thickness=-1)
    cv2.rectangle(image, (15, 15), (24, 24), 0, thickness=-1)

    regions = find_contours(image, min_area=5, retrieve_holes=True)

    assert len(regions) == 1
    assert len(regions[0].holes) == 1


def test_build_polygon_path_outputs_closed_svg_path() -> None:
    contour = np.array([[[1, 1]], [[8, 1]], [[8, 8]], [[1, 8]]], dtype=np.int32)

    points = contour_to_points(contour)
    path = build_polygon_path(points)

    assert path.startswith("M 1 1")
    assert "L 8 8" in path
    assert path.endswith("Z")


def test_find_contours_filters_small_regions() -> None:
    image = np.zeros((30, 30), dtype=np.uint8)
    cv2.rectangle(image, (2, 2), (3, 3), 255, thickness=-1)
    cv2.rectangle(image, (10, 10), (20, 20), 255, thickness=-1)

    regions = find_contours(image, min_area=20, retrieve_holes=False)

    assert len(regions) == 1
    assert regions[0].area >= 20

