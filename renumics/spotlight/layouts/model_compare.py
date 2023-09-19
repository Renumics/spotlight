from renumics.spotlight import layout
from renumics.spotlight.layout import (
    Layout,
    lenses,
    table,
    similaritymap,
    inspector,
    split,
    tab,
    metric,
    issues,
    confusion_matrix,
)
from typing import Optional
from renumics.spotlight import Audio, Image


def model_compare_classification(
    label: str = "label",
    model1_prediction: str = "m1_prediction",
    model1_embedding: str = "",
    model1_correct: str = "",
    model2_prediction: str = "m2_prediction",
    model2_embedding: str = "",
    model2_correct: str = "",
    inspect: Optional[dict] = None
) -> Layout:
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

    column2 = tab(
        confusion_matrix(
            name="Model 1 confusion matrix", x_column=label, y_column=model1_prediction
        ),
        confusion_matrix(
            name="Model 2 confusion matrix", x_column=label, y_column=model2_prediction
        ),
        weight=40,
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
            column2 = split([column2, row2], weight=80, orientation="horizontal")

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
            column2 = split([column2, row3], orientation="horizontal")

    # fourth column: inspector
    inspector_fields = []
    if inspect:
        for item, _type in inspect.items():
            if _type == Audio:
                inspector_fields.append(lenses.audio(item))
            elif _type == Image:
                inspector_fields.append(lenses.image(item))
            else:
                print("Type {} not supported by this layout.".format(_type))

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
