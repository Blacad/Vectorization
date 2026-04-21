from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from vectorizer.exceptions import ImageDecodeError, ImageValidationError, ParameterError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
READ_MODES = {
    "unchanged": cv2.IMREAD_UNCHANGED,
    "color": cv2.IMREAD_COLOR,
    "grayscale": cv2.IMREAD_GRAYSCALE,
}


def validate_image_file(path: str | Path) -> None:
    """Validate that a path points to a supported bitmap image file."""
    image_path = Path(path)
    if not image_path.exists():
        raise ImageValidationError(f"Input path does not exist: {image_path}")
    if not image_path.is_file():
        raise ImageValidationError(f"Input path is not a file: {image_path}")
    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ImageValidationError(
            f"Unsupported file format '{image_path.suffix}'. Expected one of: {allowed}"
        )


def _decode_image(path: Path, flag: int) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, flag)
    if image is None:
        raise ImageDecodeError(f"Failed to decode image: {path}")
    return image


def _composite_alpha_on_white(image: np.ndarray) -> np.ndarray:
    if image.ndim != 3 or image.shape[2] != 4:
        return image
    bgr = image[:, :, :3].astype(np.float32)
    alpha = image[:, :, 3:4].astype(np.float32) / 255.0
    white = np.full_like(bgr, 255.0)
    return np.round((bgr * alpha) + (white * (1.0 - alpha))).astype(np.uint8)


def load_image(path: str | Path, mode: str = "unchanged") -> np.ndarray:
    """Read a jpg/jpeg/png image as a NumPy array.

    Color images are returned in OpenCV BGR channel order. PNG alpha channels are
    composited onto a white background so downstream contour extraction receives
    a normal 3-channel image.
    """
    if mode not in READ_MODES:
        raise ParameterError(f"Unsupported read mode '{mode}'. Expected: {', '.join(READ_MODES)}")

    image_path = Path(path)
    validate_image_file(image_path)
    image = _decode_image(image_path, READ_MODES[mode])
    if mode != "grayscale":
        image = _composite_alpha_on_white(image)
    return image


def get_image_info(image: np.ndarray) -> dict[str, Any]:
    """Return width, height, channel count, dtype, and shape for an image."""
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ImageValidationError("Image must be a non-empty NumPy array.")

    height, width = image.shape[:2]
    channels = 1 if image.ndim == 2 else image.shape[2]
    return {
        "width": int(width),
        "height": int(height),
        "channels": int(channels),
        "dtype": str(image.dtype),
        "shape": tuple(int(v) for v in image.shape),
    }

