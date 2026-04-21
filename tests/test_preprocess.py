import numpy as np

from vectorizer.preprocess import (
    binarize_image,
    convert_color_space,
    morphology_process,
    resize_if_needed,
    to_grayscale,
)


def test_to_grayscale_converts_bgr() -> None:
    image = np.zeros((8, 10, 3), dtype=np.uint8)
    image[:, :] = (0, 0, 255)

    gray = to_grayscale(image)

    assert gray.shape == (8, 10)
    assert gray.dtype == np.uint8


def test_binarize_fixed_and_invert() -> None:
    image = np.array([[0, 255]], dtype=np.uint8)

    normal = binarize_image(image, method="fixed", threshold=127, invert=False)
    inverted = binarize_image(image, method="fixed", threshold=127, invert=True)

    assert normal.tolist() == [[0, 255]]
    assert inverted.tolist() == [[255, 0]]


def test_morphology_open_removes_single_pixel_noise() -> None:
    image = np.zeros((12, 12), dtype=np.uint8)
    image[1, 1] = 255
    image[5:9, 5:9] = 255

    cleaned = morphology_process(image, op="open", kernel_size=3)

    assert cleaned[1, 1] == 0
    assert cleaned[6, 6] == 255


def test_resize_if_needed_preserves_aspect_ratio() -> None:
    image = np.zeros((50, 100, 3), dtype=np.uint8)

    resized = resize_if_needed(image, max_size=25)

    assert resized.shape[:2] == (12, 25)


def test_convert_color_space_to_rgb() -> None:
    image = np.zeros((1, 1, 3), dtype=np.uint8)
    image[0, 0] = (1, 2, 3)

    rgb = convert_color_space(image, target="rgb")

    assert rgb[0, 0].tolist() == [3, 2, 1]

