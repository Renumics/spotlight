from typing import Any, Dict, Optional, Union

from renumics.spotlight import dtypes, layout
from renumics.spotlight.layout import (
    Layout,
    Split,
    Tab,
    confusion_matrix,
    inspector,
    issues,
    lenses,
    metric,
    similaritymap,
    split,
    tab,
    table,
)


def compare_classification(
    label: str = "label",
    model1_prediction: str = "m1_prediction",
    model1_embedding: str = "",
    model1_correct: str = "",
    model2_prediction: str = "m2_prediction",
    model2_embedding: str = "",
    model2_correct: str = "",
    inspect: Optional[Dict[str, Any]] = None,
) -> Layout:
    """This function generates a Spotlight layout for comparing two different machine learning classification models.

    Args:
        label: Name of the column that contains the label.
        model1_prediction: Name of the column that contains the prediction for model 1.
        model1_embedding: Name of the column that contains thee embedding for model 1.
        model1_correct: Name of the column that contains a flag if the data sample is predicted correctly by model 1.
        model2_prediction: Name of the column that contains the prediction for model 2.
        model2_embedding: Name of the column that contains thee embedding for model 2.
        model2_correct: Name of the column that contains a flag if the data sample is predicted correctly by model 2.
        inspect: Name and type of the columns that are displayed in the inspector, e.g. {'audio': spotlight.dtypes.audio_dtype}.

    Returns:
        The configured layout for `spotlight.show`.
    """

    # first column: table + issues
    metrics = split(
        [
            tab(
                metric(
                    name="Accuracy model 1",
                    metric="accuracy",
                    columns=[label, model1_prediction],
                )
            ),
            tab(
                metric(
                    name="Accuracy model 2",
                    metric="accuracy",
                    columns=[label, model2_prediction],
                )
            ),
        ],
        orientation="vertical",
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
                name="Model 1 confusion matrix",
                x_column=label,
                y_column=model1_prediction,
            ),
            confusion_matrix(
                name="Model 2 confusion matrix",
                x_column=label,
                y_column=model2_prediction,
            ),
            weight=40,
        )
    )

    # third column: similarity maps
    if model1_correct != "":
        if model2_correct != "":
            row2 = tab(
                confusion_matrix(
                    name="Model1 vs. Model2 - binned scatterplot",
                    x_column=model1_correct,
                    y_column=model2_correct,
                ),
                weight=40,
            )
            column2_list.append(row2)

    if model1_embedding != "":
        if model2_embedding != "":
            row3 = tab(
                similaritymap(
                    name="Model 1 embedding",
                    columns=[model1_embedding],
                    color_by_column=label,
                ),
                similaritymap(
                    name="Model 2 embedding",
                    columns=[model2_embedding],
                    color_by_column=label,
                ),
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
            dtype = dtypes.create_dtype(dtype_like)
            if dtypes.is_audio_dtype(dtype):
                inspector_fields.append(lenses.audio(item))
            elif dtypes.is_image_dtype(dtype):
                inspector_fields.append(lenses.image(item))
            else:
                print(f"Type {dtype} not supported by this layout.")

        inspector_fields.append(lenses.scalar(label))
        inspector_fields.append(lenses.scalar(model1_prediction))
        inspector_fields.append(lenses.scalar(model2_prediction))

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
