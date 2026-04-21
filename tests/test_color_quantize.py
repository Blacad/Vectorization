import numpy as np

from vectorizer.color_quantize import build_colored_paths, extract_color_regions, quantize_colors


def test_quantize_colors_returns_limited_palette() -> None:
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    image[:, :10] = (255, 0, 0)
    image[:, 10:] = (0, 255, 0)

    quantized, colors = quantize_colors(image, k=2)

    assert quantized.shape == image.shape
    assert len(colors) == 2
    assert len(np.unique(quantized.reshape(-1, 3), axis=0)) == 2


def test_extract_color_regions_builds_colored_paths() -> None:
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    image[:, :10] = (255, 0, 0)
    image[:, 10:] = (0, 255, 0)
    quantized, colors = quantize_colors(image, k=2)

    regions = extract_color_regions(quantized, colors, min_area=5)
    paths = build_colored_paths(regions)

    assert len(paths) >= 2
    assert {item["fill"] for item in paths} == {"#ff0000", "#00ff00"}
    assert all(item["path"].startswith("M ") for item in paths)

