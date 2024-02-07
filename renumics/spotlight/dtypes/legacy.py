from renumics.spotlight.media import (
    Audio,  # noqa: F401
    Embedding,  # noqa: F401
    Image,  # noqa: F401
    Mesh,  # noqa: F401
    Sequence1D,  # noqa: F401
    Video,  # noqa: F401
)


class Category:
    """
    A string value that takes only a limited number of possible values (categories).

    The corresponding categories can be got and set with get/set_column_attributes['categories'].

    Dummy class for window column creation, should not be explicitly used as
    input data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_categorical_column("my_new_cat",
        ...         categories=["red", "green", "blue"],)
        ...     dataset.append_row(my_new_cat="blue")
        ...     dataset.append_row(my_new_cat="green")
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["my_new_cat", 1])
        green

    Example:
        >>> import numpy as np
        >>> import datetime
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_categorical_column("my_new_cat",
        ...         categories=["red", "green", "blue"],)
        ...     current_categories = dataset.get_column_attributes("my_new_cat")["categories"]
        ...     dataset.set_column_attributes("my_new_cat", categories={**current_categories,
        ...         "black":100})
        ...     dataset.append_row(my_new_cat="black")
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["my_new_cat", 0])
        black
    """


class Window:
    """
    A pair of two timestamps in seconds which can be later projected onto
    continuous data (only `renumics.spotlight.dtypes.Audio`
    is currently supported).

    Dummy class for window column creation
    (see `renumics.spotlight.dataset.Dataset.append_column`),
    should not be explicitly used as input data.

    To create a window column, use
    `renumics.spotlight.dataset.Dataset.append_window_column`
    method.

    Examples:

        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_window_column("window", [[1, 2]] * 4)
        ...     dataset.append_row(window=(0, 1))
        ...     dataset.append_row(window=np.array([-1, 0]))
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["window"])
        [[ 1.  2.]
         [ 1.  2.]
         [ 1.  2.]
         [ 1.  2.]
         [ 0.  1.]
         [-1.  0.]]


        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_int_column("start", range(5))
        ...     dataset.append_float_column("end", dataset["start"] + 2)
        ...     print(dataset["start"])
        ...     print(dataset["end"])
        [0 1 2 3 4]
        [2. 3. 4. 5. 6.]
        >>> with Dataset("docs/example.h5", "a") as dataset:
        ...     dataset.append_window_column("window", zip(dataset["start"], dataset["end"]))
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["window"])
        [[0. 2.]
         [1. 3.]
         [2. 4.]
         [3. 5.]
         [4. 6.]]
    """
