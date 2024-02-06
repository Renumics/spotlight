#!/usr/bin/env python3
"""
    Command line entrypoint for the renumics-spotlight python package
"""
import os
import platform
import signal
import sys
from typing import Dict, Optional, Tuple, Union

import click

from renumics import spotlight
from renumics.spotlight import logging


def cli_dtype_callback(
    _ctx: click.Context, _param: click.Option, value: Tuple[str, ...]
) -> Optional[Dict[str, str]]:
    """
    Parse column types from multiple strings in format
    `COLUMN_NAME=DTYPE` to a dict.
    """
    if not value:
        return None
    dtypes: Dict[str, str] = {}
    for mapping in value:
        try:
            column_name, dtype = mapping.split("=")
        except ValueError as e:
            raise click.BadParameter(
                "Column type setting separator '=' not specified or specified "
                "more than once."
            ) from e
        dtypes[column_name] = dtype
    return dtypes


@click.command()  # type: ignore
@click.argument(
    "dataset",
    required=False,
    default=os.environ.get("SPOTLIGHT_TABLE_FILE"),
)
@click.option(
    "--folder",
    help="Root folder for filebrowser and file lookup.",
    required=False,
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
    help="Custom column types setting (use COLUMN_NAME=DTYPE notation). Multiple settings allowed.",
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
    "--analyze-all",
    is_flag=True,
    default=False,
    help="Automatically analyze issues for all columns.",
)
@click.option(
    "--analyze",
    default=(),
    multiple=True,
    help="Columns to analyze (if no --analyze-all).",
)
@click.option(
    "--embed-all",
    is_flag=True,
    default=False,
    help="Automatically embed all columns.",
)
@click.option(
    "--embed",
    default=(),
    multiple=True,
    help="Columns to embed (if no --embed-all).",
)
@click.option("-v", "--verbose", is_flag=True)
@click.version_option(spotlight.__version__)
def main(
    dataset: Optional[str],
    folder: Optional[str],
    host: str,
    port: Union[int, str],
    layout: Optional[str],
    dtype: Optional[Dict[str, str]],
    no_browser: bool,
    filebrowsing: bool,
    analyze: Tuple[str],
    analyze_all: bool,
    embed: Tuple[str],
    embed_all: bool,
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
        dataset,
        folder=folder,
        dtype=dtype,
        host=host,
        port="auto" if port == "auto" else int(port),
        layout=layout,
        no_browser=no_browser,
        allow_filebrowsing=filebrowsing,
        wait="forever",
        analyze=True if analyze_all else list(analyze),
        embed=True if embed_all else list(embed),
    )
