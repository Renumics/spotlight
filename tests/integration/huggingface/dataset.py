"""
Data for Hugging Face tests
"""

import datetime

import datasets


DATA = {
    "bool": [True, False, False],
    "int": [-1, 1, 100000],
    "uint": [1, 1, 30000],
    "float": [1.0, float("nan"), 1000],
    "string": ["foo", "barbaz", ""],
    "label": ["foo", "bar", "foo"],
    "binary": [b"foo", b"bar", b""],
    "duration": [-1, 2, 10],
    "decimal": [1.0, 3.0, 1000],
    "date": [datetime.date.min, datetime.date(2001, 2, 15), datetime.date.max],
    "time": [
        datetime.time.min,
        datetime.time(14, 24, 15, 2672),
        datetime.time.max,
    ],
    "timestamp": [
        datetime.datetime(1970, 2, 15, 14, 24, 15, 2672),
        datetime.datetime(2001, 2, 15, 14, 24, 15, 2672),
        datetime.datetime(2170, 2, 15, 14, 24, 15, 2672),
    ],
    "timestamp_ns": [
        datetime.datetime(1970, 2, 15, 14, 24, 15, 2672),
        datetime.datetime(2001, 2, 15, 14, 24, 15, 2672),
        datetime.datetime(2170, 2, 15, 14, 24, 15, 2672),
    ],
    "embedding": [[1, 2, 3, 4], [1, 6, 3, 7], [-1, -2, -3, -4]],
    "audio": [
        "data/audio/mono/gs-16b-1c-44100hz.mp3",
        "data/audio/1.wav",
        "data/audio/stereo/gs-16b-2c-44100hz.ogg",
    ],
    "image": [
        "data/images/nature-256p.ico",
        "data/images/sea-360p.gif",
        "data/images/nature-360p.jpg",
    ],
    # HF sequence as Spotlight sequence
    "sequence_1d": [[1, 2, 3, 4], [1, 6, 3], [-1, -2, float("nan"), -4, 10]],
    "sequence_2d": [
        [[1, 2, 3, 4], [-1, 3, 1, 6]],
        [[1, -3, 10], [1, 6, 3]],
        [[-10, 0, 10], [-1, -2, -3]],
    ],
    "sequence_2d_t": [[[5, 3], [2, 5], [10, 8]], [], [[-1, 1], [1, 10]]],
    # HF sequence as Spotlight array
    "sequence_2d_array": [
        [[1, 2, 3, 4], [-1, 3, 1, 6], [1, 2, 4, 4]],
        [[1, -3, 10], [1, 6, 3], [1, float("nan"), 4]],
        [[-10, 0, 10], [-1, -2, -3], [1, 2, 4]],
    ],
    "sequence_3d_array": [
        [[[1, 2, 3, 4], [-1, 3, 1, 6], [1, 2, 4, 4]]],
        [[[1, -3, 10], [1, 6, 3], [1, float("nan"), 4]]],
        [[[-10, 0, 10], [-1, -2, -3], [1, 2, 4]]],
    ],
    # HF 2D array as Spotlight sequence
    "array_2d_sequence": [
        [[1, 2, 3], [-1, 3, 1]],
        [[1, -3, 10], [1, 6, 3]],
        [[-10, 0, 10], [-1, -2, -3]],
    ],
    "array_2d_t_sequence": [
        [[5, 3], [2, 5], [10, 8]],
        [[float("nan"), 1], [1, 1], [2, 2]],
        [[-1, 1], [1, 10], [10, 1]],
    ],
    "array_2d_vlen_sequence": [
        [[5, 3], [2, 5], [10, 8]],
        [],
        [[-1, 1], [1, 10]],
    ],
    # HF 4D array as Spotlight array
    "array_4d": [
        [[[[1.0, 1.0, -10.0]]], [[[-1.0, 1.0, -1.0]]], [[[2.0, 1.0, 1.0]]]],
        [
            [[[2.0, -3.0, 0.0]]],
            [[[3.0, 6.0, -2.0]]],
            [[[4.0, float("nan"), 2.0]]],
            [[[4.0, float("nan"), 2.0]]],
        ],
        [[[[3.0, 10.0, 10.0]]], [[[6.0, 3.0, -3.0]]], [[[4.0, 4.0, 4.0]]]],
    ],
    # HF list as Spotlight embedding
    "list_sequence": [[1, 2, 3], [1, 6, 3, 7, 8], [-1, -2, -3, -4]],
}

FEATURES = {
    "bool": datasets.Value("bool"),
    "int": datasets.Value("int32"),
    "uint": datasets.Value("uint16"),
    "float": datasets.Value("float64"),
    "string": datasets.Value("string"),
    "label": datasets.ClassLabel(num_classes=4, names=["foo", "bar", "baz", "barbaz"]),
    "binary": datasets.Value("binary"),
    "duration": datasets.Value("duration[s]"),
    "decimal": datasets.Value("decimal128(10, 2)"),
    "date": datasets.Value("date32"),
    "time": datasets.Value("time64[us]"),
    "timestamp": datasets.Value("timestamp[us]"),
    "timestamp_ns": datasets.Value("timestamp[ns]"),
    "audio": datasets.Audio(),
    "image": datasets.Image(),
    "embedding": datasets.Sequence(feature=datasets.Value("float64"), length=4),
    "sequence_1d": datasets.Sequence(feature=datasets.Value("float64")),
    "sequence_2d": datasets.Sequence(
        feature=datasets.Sequence(feature=datasets.Value("float64")),
        length=2,
    ),
    "sequence_2d_t": datasets.Sequence(
        feature=datasets.Sequence(feature=datasets.Value("float64"), length=2),
    ),
    "sequence_2d_array": datasets.Sequence(
        feature=datasets.Sequence(feature=datasets.Value("float64")),
        length=3,
    ),
    "sequence_3d_array": datasets.Sequence(
        feature=datasets.Sequence(
            feature=datasets.Sequence(feature=datasets.Value("float64")),
            length=3,
        ),
        length=1,
    ),
    "array_2d_sequence": datasets.Array2D(shape=(2, 3), dtype="float64"),
    "array_2d_t_sequence": datasets.Array2D(shape=(3, 2), dtype="float64"),
    "array_2d_vlen_sequence": datasets.Array2D(shape=(None, 2), dtype="float64"),
    "array_4d": datasets.Array4D(shape=(None, 1, 1, 3), dtype="float64"),
    "list_sequence": [datasets.Value("float64")],
}


def create_hf_dataset() -> datasets.Dataset:
    ds = datasets.Dataset.from_dict(
        DATA,
        features=datasets.Features(FEATURES),
    )
    return ds
