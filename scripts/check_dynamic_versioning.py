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

    if not pyproject["tool"]["poetry-dynamic-versioning"]["enable"]:
        sys.exit(1)
