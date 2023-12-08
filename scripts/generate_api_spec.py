#!/usr/bin/env python3
"""
generate the api spec
"""
import json

import click

from renumics.spotlight.app import SpotlightApp


@click.command()  # type: ignore
@click.option(
    "--output-path",
    "-o",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="path to write spec to",
    required=True,
)
def generate_api_spec(output_path: str) -> None:
    """
    generate swagger api spec as json
    :param output_path: path to output json
    :return:
    """
    app = SpotlightApp()
    app.openapi_version = "3.0.2"

    with open(output_path, "w", encoding="utf8") as out_f:
        json.dump(app.openapi(), out_f, indent=4)


if __name__ == "__main__":
    generate_api_spec()
