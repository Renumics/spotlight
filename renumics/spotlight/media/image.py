import io
from typing import Optional, Union

import imageio.v3 as iio
import numpy as np
from loguru import logger

from renumics.spotlight.media.base import FileMediaType, ImageLike
from renumics.spotlight.typing import FileType

from ..io import file as file_io
from . import exceptions


class Image(FileMediaType):
    """
    An RGB(A) or grayscale image that will be saved in encoded form.

    Attributes:
        data: Array-like with shape `(num_rows, num_columns)` or
            `(num_rows, num_columns, num_channels)` with `num_channels` equal to
            3, or 4; with dtype "uint8".

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Image
        >>> data = np.full([100,100,3], 255, dtype=np.uint8)  # white uint8 image
        >>> image = Image(data)
        >>> float_data = np.random.uniform(0, 1, (100, 100))  # random grayscale float image
        >>> float_image = Image(float_data)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_image_column("images", [image, float_image, data, float_data])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["images", 0].data[50][50])
        ...     print(dataset["images", 3].data.dtype)
        [255 255 255]
        uint8
    """

    data: np.ndarray

    def __init__(self, data: ImageLike) -> None:
        data_array = np.asarray(data)
        if (
            data_array.size == 0
            or data_array.ndim != 2
            and (data_array.ndim != 3 or data_array.shape[-1] not in (1, 3, 4))
        ):
            raise ValueError(
                f"`data` argument should be a numpy array with shape "
                f"`(num_rows, num_columns, num_channels)` or "
                f"`(num_rows, num_columns)` or with `num_rows > 0`, "
                f"`num_cols > 0` and `num_channels` equal to 1, 3, or 4, but "
                f"shape {data_array.shape} received."
            )
        if data_array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"`data` argument should be a numpy array with integer or "
                f"float dtypes, but dtype {data_array.dtype.name} received."
            )
        if data_array.ndim == 3 and data_array.shape[2] == 1:
            data_array = data_array.squeeze(axis=2)
        if data_array.dtype.str[1] == "f":
            logger.info(
                'Image data converted to "uint8" dtype by multiplication with '
                "255 and rounding."
            )
            data_array = (255 * data_array).round()
        self.data = data_array.astype("uint8")

    @classmethod
    def from_file(cls, filepath: FileType) -> "Image":
        """
        Read image from a filepath, an URL, or a file-like object.

        `imageio` is used inside, so only supported formats are allowed.
        """
        with file_io.as_file(filepath) as file:
            try:
                image_array = iio.imread(file, index=False)  # type: ignore
            except Exception as e:
                raise exceptions.InvalidFile(
                    f"Image {filepath} does not exist or could not be read."
                ) from e
        return cls(image_array)

    @classmethod
    def from_bytes(cls, blob: bytes) -> "Image":
        """
        Read image from raw bytes.

        `imageio` is used inside, so only supported formats are allowed.
        """
        try:
            image_array = iio.imread(blob, index=False)  # type: ignore
        except Exception as e:
            raise exceptions.InvalidFile(
                "Image could not be read from the given bytes."
            ) from e
        return cls(image_array)

    @classmethod
    def empty(cls) -> "Image":
        """
        Create a transparent 1 x 1 image.
        """
        return cls(np.zeros((1, 1, 4), np.uint8))

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Image":
        if isinstance(value, np.void):
            buffer = io.BytesIO(value.tolist())
            return cls(iio.imread(buffer, extension=".png", index=False))
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, _target: Optional[str] = None) -> np.void:
        buf = io.BytesIO()
        iio.imwrite(buf, self.data, extension=".png")
        return np.void(buf.getvalue())
