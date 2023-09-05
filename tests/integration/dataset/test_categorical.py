"""
Test Spotlight dataset with categorical columns.
"""

import pytest
from renumics.spotlight.dataset import exceptions
from renumics.spotlight import Dataset


@pytest.mark.parametrize(
    "categorical_color_dataset", ["red", "green", None], indirect=True
)
def test_categorical_unknown_category(categorical_color_dataset: Dataset) -> None:
    """adding not existing category value should add `None`"""
    categorical_color_dataset.append_row(my_new_cat="invalid_color")
    assert categorical_color_dataset["my_new_cat", -1] is None


@pytest.mark.parametrize(
    "categorical_color_dataset", ["red", "green", None], indirect=True
)
def test_categorical_new_category(categorical_color_dataset: Dataset) -> None:
    """adding new category with existing int value should raise"""
    old_categories = categorical_color_dataset.get_column_attributes("my_new_cat")[
        "categories"
    ]
    categorical_color_dataset.set_column_attributes(
        "my_new_cat",
        categories={**old_categories, "black": max(old_categories.values()) + 1},
    )
    with pytest.raises(exceptions.InvalidAttributeError):
        categorical_color_dataset.set_column_attributes(
            "my_new_cat", categories={**old_categories, "black": 0}
        )


@pytest.mark.parametrize(
    "categorical_color_dataset", ["red", "green", None], indirect=True
)
def test_categorical_remvove_used_raises(categorical_color_dataset: Dataset) -> None:
    """removing used categories should raise"""
    with pytest.raises(exceptions.InvalidAttributeError):
        categorical_color_dataset.set_column_attributes(
            "my_new_cat", categories={"black": 999}
        )


@pytest.mark.parametrize(
    "categorical_color_dataset", ["red", "green", None], indirect=True
)
def test_categorical_remvove_unused(categorical_color_dataset: Dataset) -> None:
    """removing unused categories should work"""
    old_categories = categorical_color_dataset.get_column_attributes("my_new_cat")[
        "categories"
    ]
    for i in range(len(categorical_color_dataset)):
        if categorical_color_dataset["my_new_cat", i] == "green":
            categorical_color_dataset["my_new_cat", i] = "red"
    del old_categories["green"]
    if (
        categorical_color_dataset.get_column_attributes("my_new_cat")["default"]
        == "green"
    ):
        categorical_color_dataset.set_column_attributes("my_new_cat", default="red")

    categorical_color_dataset.set_column_attributes(
        "my_new_cat", categories={**old_categories}
    )

    assert (
        len(categorical_color_dataset.get_column_attributes("my_new_cat")["categories"])
        == 2
    )
