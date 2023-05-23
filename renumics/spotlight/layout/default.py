"""
All-purpose default layout.
"""

from . import split, tab
from . import table, histogram, inspector, layout, scatterplot, similaritymap

DEFAULT_LAYOUT = layout(
    split(
        tab(table(), weight=60),
        tab(similaritymap(), scatterplot(), histogram(), weight=40),
        weight=60,
    ),
    tab(inspector(), weight=40),
)
