import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from vectorizer.pipeline import VectorizeOptions, convert_bitmap_to_svg

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def write_png(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    encoded.tofile(str(path))


def test_binary_pipeline_writes_svg(tmp_path: Path) -> None:
    input_path = tmp_path / "logo.png"
    output_path = tmp_path / "logo.svg"
    image = np.zeros((50, 60, 3), dtype=np.uint8)
    cv2.rectangle(image, (10, 10), (45, 35), (255, 255, 255), thickness=-1)
    write_png(input_path, image)

    summary = convert_bitmap_to_svg(
        input_path,
        output_path,
        VectorizeOptions(mode="binary", min_area=20),
    )

    assert output_path.exists()
    assert summary.path_count >= 1
    assert summary.width == 60
    assert summary.height == 50
    assert "<path" in output_path.read_text(encoding="utf-8")


def test_color_pipeline_writes_multicolor_svg(tmp_path: Path) -> None:
    input_path = tmp_path / "icon.png"
    output_path = tmp_path / "icon.svg"
    image = np.zeros((40, 40, 3), dtype=np.uint8)
    image[:, :20] = (0, 0, 255)
    image[:, 20:] = (0, 255, 0)
    write_png(input_path, image)

    summary = convert_bitmap_to_svg(
        input_path,
        output_path,
        VectorizeOptions(mode="color", colors=2, min_area=10),
    )

    text = output_path.read_text(encoding="utf-8")
    assert summary.path_count >= 2
    assert summary.colors == 2
    assert "#ff0000" in text
    assert "#00ff00" in text


def test_cli_runs_end_to_end(tmp_path: Path) -> None:
    input_path = tmp_path / "logo.png"
    output_path = tmp_path / "logo.svg"
    image = np.zeros((30, 30, 3), dtype=np.uint8)
    cv2.circle(image, (15, 15), 8, (255, 255, 255), thickness=-1)
    write_png(input_path, image)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "main.py"),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--mode",
            "binary",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_path.exists()
    assert "Converted:" in result.stdout

