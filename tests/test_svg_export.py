from pathlib import Path

from vectorizer.svg_export import add_path, create_svg_document, save_svg, write_svg


def test_svg_document_can_write_path(tmp_path: Path) -> None:
    output_path = tmp_path / "shape.svg"
    dwg = create_svg_document(20, 10)
    add_path(dwg, "M 1 1 L 10 1 L 10 8 Z", fill="#123456")

    save_svg(dwg, output_path)
    text = output_path.read_text(encoding="utf-8")

    assert 'viewBox="0 0 20 10"' in text
    assert "<path" in text
    assert 'fill="#123456"' in text


def test_write_svg_creates_parent_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "shape.svg"

    write_svg(5, 5, [{"path": "M 0 0 L 4 0 L 4 4 Z", "fill": "#000000"}], output_path)

    assert output_path.exists()

