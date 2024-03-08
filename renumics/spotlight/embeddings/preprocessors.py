"""
Data preprocessors available to embedders for conversion data batches from our
intern format to a common format.
"""

import io
from typing import List

import av
import numpy as np
import PIL.Image


def preprocess_batch(raw_values: list) -> list:
    """
    Preprocess a batch of any data, returns batch as is.
    """
    return raw_values


def preprocess_image_batch(raw_values: List[bytes]) -> List[PIL.Image.Image]:
    """
    Preprocess a batch of image data, converts images to pillow image format.
    """
    return [PIL.Image.open(io.BytesIO(value)) for value in raw_values]


def preprocess_audio_batch(
    raw_values: List[bytes], sampling_rate: int
) -> List[np.ndarray]:
    """
    Preprocess a batch of audio data, returns mono channel audio PCM resampled
    to the given sampling rate as an double array.
    """
    resampled_batch = []
    for raw_data in raw_values:
        with av.open(io.BytesIO(raw_data), "r") as container:
            resampler = av.AudioResampler(
                format="dbl", layout="mono", rate=sampling_rate
            )
            data = []
            for frame in container.decode(audio=0):
                resampled_frames = resampler.resample(frame)
                for resampled_frame in resampled_frames:
                    frame_array = resampled_frame.to_ndarray()[0]
                    data.append(frame_array)
            resampled_batch.append(np.concatenate(data, axis=0))
    return resampled_batch
