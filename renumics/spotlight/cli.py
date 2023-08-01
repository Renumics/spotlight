#!/usr/bin/env python3
"""
    Command line entrypoint for the renumics-spotlight python package
"""
import os
import platform
import signal
import sys
from typing import Optional, Tuple, Union
from pathlib import Path

import click

from renumics import spotlight
from renumics.spotlight.dtypes.typing import COLUMN_TYPES_BY_NAME, ColumnTypeMapping

from renumics.spotlight import logging


def cli_dtype_callback(
    _ctx: click.Context, _param: click.Option, value: Tuple[str, ...]
) -> Optional[ColumnTypeMapping]:
    """
    Parse column types from multiple strings in format
    `COLUMN_NAME=DTYPE` to a dict.
    """
    if not value:
        return None
    dtype = {}
    for mapping in value:
        try:
            column_name, dtype_name = mapping.split("=")
        except ValueError as e:
            raise click.BadParameter(
                "Column type setting separator '=' not specified or specified "
                "more than once."
            ) from e
        try:
            column_type = COLUMN_TYPES_BY_NAME[dtype_name]
        except KeyError as e:
            raise click.BadParameter(
                f"Column types from {list(COLUMN_TYPES_BY_NAME.keys())} "
                f"expected, but value '{dtype_name}' recived."
            ) from e
        dtype[column_name] = column_type
    return dtype


@click.command()  # type: ignore
@click.argument(
    "table-or-folder",
    type=str,
    required=False,
    default=os.environ.get("SPOTLIGHT_TABLE_FILE", str(Path.cwd())),
)
@click.option(
    "--host",
    "-h",
    default="localhost",
    help="The host that Spotlight should listen on.",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    type=str,
    default="auto",
    help="The port that Spotlight should listen on (use 'auto' to use a random free port)",
    show_default=True,
)
@click.option(
    "--layout",
    default=None,
    help="Preconfigured layout to use as default.",
)
@click.option(
    "--dtype",
    type=click.UNPROCESSED,
    callback=cli_dtype_callback,
    multiple=True,
    help="Custom column types setting (use COLUMN_NAME={"
    + "|".join(sorted(COLUMN_TYPES_BY_NAME.keys()))
    + "} notation). Multiple settings allowed.",
)
@click.option(
    "--no-browser",
    is_flag=True,
    default=False,
    help="Do not automatically show Spotlight in browser.",
)
@click.option(
    "--filebrowsing/--no-filebrowsing",
    is_flag=True,
    default=True,
    help="Whether to allow users to browse and open datasets.",
)
@click.option(
    "--analyze",
    is_flag=True,
    default=False,
    help="Automatically analyze common dataset errors.",
)
@click.option("-v", "--verbose", is_flag=True)
@click.version_option(spotlight.__version__)
def main(
    table_or_folder: str,
    host: str,
    port: Union[int, str],
    layout: Optional[str],
    dtype: Optional[ColumnTypeMapping],
    no_browser: bool,
    filebrowsing: bool,
    analyze: bool,
    verbose: bool,
) -> None:
    """
    Parse CLI arguments and launch Renumics Spotlight.
    """

    if verbose:
        logging.enable()

    signal.signal(signal.SIGINT, lambda *_: sys.exit())
    signal.signal(signal.SIGTERM, lambda *_: sys.exit())
    if platform.system() != "Windows":
        signal.signal(signal.SIGHUP, lambda *_: sys.exit())

    spotlight.show(
        table_or_folder,
        dtype=dtype,
        host=host,
        port="auto" if port == "auto" else int(port),
        layout=layout,
        no_browser=no_browser,
        allow_filebrowsing=filebrowsing,
        wait="forever",
        analyze=analyze,
    )
