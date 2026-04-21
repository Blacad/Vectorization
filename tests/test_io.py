from pathlib import Path

import cv2
import numpy as np
import pytest

from vectorizer.exceptions import ImageDecodeError, ImageValidationError
from vectorizer.io import get_image_info, load_image, validate_image_file


def write_image(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(path.suffix, image)
    assert ok
    encoded.tofile(str(path))


def test_load_png_and_image_info(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.zeros((12, 20, 3), dtype=np.uint8)
    image[:, :] = (10, 20, 30)
    write_image(image_path, image)

    loaded = load_image(image_path)
    info = get_image_info(loaded)

    assert loaded.shape == (12, 20, 3)
    assert info["width"] == 20
    assert info["height"] == 12
    assert info["channels"] == 3


def test_validate_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(ImageValidationError, match="does not exist"):
        validate_image_file(tmp_path / "missing.png")


def test_validate_rejects_unsupported_extension(tmp_path: Path) -> None:
    bad_path = tmp_path / "sample.gif"
    bad_path.write_bytes(b"not an image")

    with pytest.raises(ImageValidationError, match="Unsupported file format"):
        validate_image_file(bad_path)


def test_load_rejects_corrupt_image(tmp_path: Path) -> None:
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"not a real png")

    with pytest.raises(ImageDecodeError, match="Failed to decode"):
        load_image(corrupt_path)

