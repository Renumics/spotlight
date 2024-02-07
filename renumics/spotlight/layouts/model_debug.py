from typing import Any, Dict, List, Optional, Union

from renumics.spotlight import layout
from renumics.spotlight.dtypes import create_dtype, is_audio_dtype, is_image_dtype
from renumics.spotlight.layout import (
    Layout,
    Split,
    Tab,
    confusion_matrix,
    histogram,
    inspector,
    issues,
    lenses,
    metric,
    similaritymap,
    split,
    tab,
    table,
)


def debug_classification(
    label: str = "label",
    prediction: str = "prediction",
    embedding: str = "",
    inspect: Optional[Dict[str, Any]] = None,
    features: Optional[List[str]] = None,
) -> Layout:
    """This function generates a Spotlight layout for debugging a machine learning classification model.

    Args:
        label: Name of the column that contains the label.
        prediction: Name of the column that contains the prediction.
        embedding: Name of the column that contains the embedding.
        inspect: Name and type of the columns that are displayed in the inspector, e.g. {'audio': spotlight.dtypes.audio_dtype}.
        features: Names of the columns that contain useful metadata and features.

    Returns:
        The configured layout for `spotlight.show`.
    """

    # first column: table + issues
    metrics = tab(
        metric(name="Accuracy", metric="accuracy", columns=[label, prediction]),
        weight=15,
    )
    column1 = split(
        [metrics, tab(table(), weight=65)], weight=80, orientation="horizontal"
    )
    column1 = split(
        [column1, tab(issues(), weight=40)], weight=80, orientation="horizontal"
    )

    column2_list = []
    column2_list.append(
        tab(
            confusion_matrix(
                name="Confusion matrix", x_column=label, y_column=prediction
            ),
            weight=40,
        )
    )

    # second column: confusion matric, feature histograms (optional), embedding (optional)
    if features is not None:
        histogram_list = []
        for idx, feature in enumerate(features):
            if idx > 2:
                break
            h = histogram(
                name="Histogram {}".format(feature),
                column=feature,
                stack_by_column=label,
            )
            histogram_list.append(h)

        row2 = tab(*histogram_list, weight=40)
        column2_list.append(row2)

    if embedding != "":
        row3 = tab(
            similaritymap(name="Embedding", columns=[embedding], color_by_column=label),
            weight=40,
        )
        column2_list.append(row3)

    column2: Union[Tab, Split]

    if len(column2_list) == 1:
        column2 = column2_list[0]
    elif len(column2_list) == 2:
        column2 = split(column2_list, orientation="horizontal")
    else:
        column2 = split(
            [column2_list[0], column2_list[1]], weight=80, orientation="horizontal"
        )
        column2 = split([column2, column2_list[2]], orientation="horizontal")

    # fourth column: inspector
    inspector_fields = []
    if inspect:
        for item, dtype_like in inspect.items():
            dtype = create_dtype(dtype_like)
            if is_audio_dtype(dtype):
                inspector_fields.append(lenses.audio(item))
            elif is_image_dtype(dtype):
                inspector_fields.append(lenses.image(item))
            else:
                print("Type {} not supported by this layout.".format(dtype))

        inspector_fields.append(lenses.scalar(label))
        inspector_fields.append(lenses.scalar(prediction))

        inspector_view = inspector("Inspector", lenses=inspector_fields, num_columns=4)

    else:
        inspector_view = inspector("Inspector", num_columns=4)

    # build everything together
    column2.weight = 40
    half1 = split([column1, column2], weight=80, orientation="vertical")
    half2 = tab(inspector_view, weight=40)

    nodes = [half1, half2]

    the_layout = layout.layout(nodes)

    return the_layout
