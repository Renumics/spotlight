from pathlib import Path

import click
import numpy as np
import pandas as pd

from renumics import spotlight

COLUMNS_IN_NEED_OF_FIXING = [
    "distance_to_driver_ahead",
    "distance",
    "relative_distance",
    "r_p_m",
    "speed",
    "n_gear",
    "throttle",
    "brake",
    "d_r_s",
    "x",
    "y",
    "z",
]


@click.command()
@click.option(
    "--input-path",
    "-i",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    help="input file",
)
def main(input_path: Path) -> None:
    df = pd.read_parquet(input_path)

    for col in COLUMNS_IN_NEED_OF_FIXING:
        df[col] = df[col].apply(lambda x: np.array(x.tolist(), np.float32))  # type: ignore

    spotlight.show(df)


if __name__ == "__main__":
    main()
