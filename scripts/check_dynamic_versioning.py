#!/usr/bin/env python3
"""
Check if dynamic versioning is enabled
Exit with code 1 otherwise
"""

import sys

import toml

if __name__ == "__main__":
    with open("pyproject.toml", encoding="utf-8") as pyproject_file:
        pyproject = toml.load(pyproject_file)

    errors = []

    if pyproject["tool"]["poetry"]["version"] != "0.0.0":
        errors.append("Error: tool.poetry.version != 0.0.0")
    if not pyproject["tool"]["poetry-dynamic-versioning"]["enable"]:
        errors.append("Error: tool.poetry-dymamic-versioning.enable != true")

    for error in errors:
        print(error)
    if errors:
        sys.exit(1)
