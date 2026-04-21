from __future__ import annotations

from pathlib import Path
from typing import Any

import svgwrite

from vectorizer.exceptions import ParameterError, VectorizerError


def create_svg_document(width: int, height: int) -> svgwrite.Drawing:
    """Create an SVG document with width, height, and viewBox set."""
    if width < 1 or height < 1:
        raise ParameterError("SVG width and height must be >= 1")
    return svgwrite.Drawing(
        size=(f"{int(width)}px", f"{int(height)}px"),
        viewBox=f"0 0 {int(width)} {int(height)}",
        profile="full",
    )


def add_path(
    dwg: svgwrite.Drawing,
    path_data: str,
    fill: str = "#000000",
    stroke: str = "none",
    stroke_width: float = 1,
    fill_rule: str = "evenodd",
) -> None:
    """Add one SVG path to a drawing."""
    if not path_data:
        return
    dwg.add(
        dwg.path(
            d=path_data,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            fill_rule=fill_rule,
        )
    )


def add_paths(dwg: svgwrite.Drawing, paths: list[dict[str, Any]]) -> None:
    """Add many path dictionaries to a drawing."""
    for item in paths:
        add_path(
            dwg,
            item["path"],
            fill=item.get("fill", "#000000"),
            stroke=item.get("stroke", "none"),
            stroke_width=item.get("stroke_width", 1),
            fill_rule=item.get("fill_rule", "evenodd"),
        )


def save_svg(dwg: svgwrite.Drawing, output_path: str | Path) -> Path:
    """Save an SVG drawing, creating the output directory when necessary."""
    target = Path(output_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        dwg.saveas(str(target), pretty=True)
    except OSError as exc:
        raise VectorizerError(f"Failed to save SVG to {target}: {exc}") from exc
    return target


def write_svg(
    width: int,
    height: int,
    paths: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Create, populate, and save an SVG file."""
    dwg = create_svg_document(width, height)
    add_paths(dwg, paths)
    return save_svg(dwg, output_path)

