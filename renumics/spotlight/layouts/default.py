from renumics.spotlight.layout import (
    histogram,
    inspector,
    layout,
    scatterplot,
    similaritymap,
    split,
    tab,
    table,
)
from renumics.spotlight.layout.nodes import Layout


def default() -> Layout:
    """
    Default layout for spotlight.
    """

    return layout(
        split(
            tab(table(), weight=60),
            tab(similaritymap(), scatterplot(), histogram(), weight=40),
            weight=60,
        ),
        tab(inspector(), weight=40),
    )
