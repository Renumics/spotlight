#!/usr/bin/env python3
"""
generate the api spec
"""
import os
import json

import click

from renumics.spotlight.backend.app import create_app


@click.command()
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
    :param server_name: server name where api is reachable
    :param output_path: path to output json
    :return:
    """
    os.environ["SPOTLIGHT_DEV"] = "True"
    app = create_app()

    with open(output_path, "w", encoding="utf8") as out_f:
        json.dump(app.openapi(), out_f, indent=4)


if __name__ == "__main__":
    generate_api_spec()  # pylint: disable=no-value-for-parameter
