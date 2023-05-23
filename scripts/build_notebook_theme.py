#!/usr/bin/env python3

"""
Build Notebook theme for Spotlight-Notebook CLI.
"""

import tempfile
from pathlib import Path

import lesscpy


def main() -> None:
    """Build Notebook theme"""

    theme_folder = Path("data") / "notebook-theme"

    layout = theme_folder / "layout"

    # if there is more than one theme switch over themes
    variables_less = theme_folder / "styles" / "renumics-light.less"

    style_less = ""

    with open(variables_less, "r", encoding="utf-8") as f:
        style_less += f.read() + "\n"

    for less_path in layout.glob("*.less"):
        with open(less_path, "r", encoding="utf-8") as less_file:
            style_less += less_file.read() + "\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_css_file = Path(tmp_dir) / "tmp.less"

        with open(tmp_css_file, "w", encoding="utf-8") as f:
            f.write(style_less)
        with open(tmp_css_file, "r", encoding="utf-8") as f:
            compiled = lesscpy.compile(f, minify=True)

    destination_path = (
        Path("renumics") / "spotlight" / "notebook" / "theme" / "custom.css"
    )
    with open(destination_path, "w", encoding="utf-8") as f:
        f.write(compiled)


if __name__ == "__main__":
    main()
