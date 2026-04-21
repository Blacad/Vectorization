from __future__ import annotations

import cv2
import numpy as np

from vectorizer.exceptions import ParameterError


def _odd_kernel_size(kernel_size: int) -> int:
    if kernel_size < 1:
        raise ParameterError("kernel_size must be >= 1")
    return kernel_size if kernel_size % 2 == 1 else kernel_size + 1


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale."""
    if image.ndim == 2:
        return image.copy()
    if image.ndim != 3:
        raise ParameterError("Expected a 2D grayscale or 3D color image.")
    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    raise ParameterError(f"Unsupported channel count: {image.shape[2]}")


def denoise_image(
    image: np.ndarray,
    method: str = "gaussian",
    kernel_size: int = 5,
) -> np.ndarray:
    """Denoise an image with gaussian, median, bilateral, or no filtering."""
    method = method.lower()
    if method == "none":
        return image.copy()

    if method == "gaussian":
        k = _odd_kernel_size(kernel_size)
        return cv2.GaussianBlur(image, (k, k), 0)
    if method == "median":
        return cv2.medianBlur(image, _odd_kernel_size(kernel_size))
    if method == "bilateral":
        k = max(1, int(kernel_size))
        return cv2.bilateralFilter(image, k, sigmaColor=75, sigmaSpace=75)
    raise ParameterError("method must be one of: none, gaussian, median, bilateral")


def binarize_image(
    image: np.ndarray,
    method: str = "otsu",
    threshold: int | None = None,
    invert: bool = False,
) -> np.ndarray:
    """Convert an image to a binary uint8 mask with values 0 or 255."""
    gray = to_grayscale(image)
    method = method.lower()
    threshold_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY

    if method == "otsu":
        _, binary = cv2.threshold(gray, 0, 255, threshold_type | cv2.THRESH_OTSU)
        return binary

    if method == "fixed":
        value = 127 if threshold is None else int(threshold)
        if not 0 <= value <= 255:
            raise ParameterError("threshold must be between 0 and 255")
        _, binary = cv2.threshold(gray, value, 255, threshold_type)
        return binary

    raise ParameterError("method must be one of: otsu, fixed")


def morphology_process(
    image: np.ndarray,
    op: str = "open",
    kernel_size: int = 3,
    iterations: int = 1,
) -> np.ndarray:
    """Apply a basic morphology operation to a binary image."""
    op = op.lower()
    if op == "none":
        return image.copy()
    if kernel_size < 1:
        raise ParameterError("kernel_size must be >= 1")
    if iterations < 1:
        raise ParameterError("iterations must be >= 1")

    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    if op == "erode":
        return cv2.erode(image, kernel, iterations=iterations)
    if op == "dilate":
        return cv2.dilate(image, kernel, iterations=iterations)
    if op == "open":
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
    if op == "close":
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    raise ParameterError("op must be one of: none, erode, dilate, open, close")


def convert_color_space(image: np.ndarray, target: str = "rgb") -> np.ndarray:
    """Convert from OpenCV BGR input to BGR, RGB, HSV, or grayscale."""
    target = target.lower()
    if target == "bgr":
        return image.copy()
    if target == "gray":
        return to_grayscale(image)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ParameterError("Color-space conversion expects a 3-channel BGR image.")
    if target == "rgb":
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if target == "hsv":
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    raise ParameterError("target must be one of: bgr, rgb, hsv, gray")


def resize_if_needed(image: np.ndarray, max_size: int | None = None) -> np.ndarray:
    """Resize an image so its longest side is no larger than max_size."""
    if max_size is None:
        return image.copy()
    if max_size < 1:
        raise ParameterError("max_size must be >= 1")

    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_size:
        return image.copy()

    scale = max_size / float(longest)
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

