"""
Test `renumics.spotlight.descriptors` module.
"""

from renumics.spotlight import Dataset
from renumics.spotlight.dataset.descriptors import pca
from renumics.spotlight.dataset.descriptors import catch22


class TestPCA:
    """
    Test PCA descriptor.
    """

    min_seq_length = 2
    min_img_length = 2
    min_audio_length = 2

    def test_embedding_shape(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on embeddings.
        """
        components = 2
        # Embedding should generate warning
        _output_embedding = pca(
            descriptors_dataset, "embedding", n_components=components
        )

    def test_embedding_none(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on sequences 1D and `None`s.
        """
        components = 2
        # Embedding should generate warning
        _output_embedding = pca(
            descriptors_dataset, "embedding_none", n_components=components
        )

    def test_sequence_shape(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on sequences 1D.
        """
        components = 2
        # Sequence compressed
        _sequence = descriptors_dataset["sequence_1d"]
        _output_sequence = pca(
            descriptors_dataset, "sequence_1d", n_components=components, inplace=True
        )
        assert "sequence_1d-pca" in descriptors_dataset.keys()
        # assert correct shape for each embedding
        for embedding in descriptors_dataset["sequence_1d-pca"]:
            if TestPCA.min_seq_length < components:
                assert embedding.shape[0] == TestPCA.min_seq_length
            else:
                assert embedding.shape[0] == components

    def test_sequence_nan(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on sequences 1D with NaN.
        """
        components = 2
        # Sequence compressed
        _sequence = descriptors_dataset["sequence_1d_nan"]
        _output_sequence = pca(
            descriptors_dataset, "sequence_1d_nan", n_components=components
        )

    def test_image_shape(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image", n_components=components, inplace=True
        )
        assert "image-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_different_shapes(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with different shapes.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image_shapes", n_components=components, inplace=True
        )
        assert "image_shapes-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_shapes-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_different_dtypes(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with different dtypes.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image_dtypes", n_components=components, inplace=True
        )
        assert "image_dtypes-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_dtypes-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_nan(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with NaN.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image_nan", n_components=components, inplace=True
        )
        assert "image_nan-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_nan-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_rgba_gray(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with different channels.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset,
            "image_rgba_gray",
            n_components=components,
            inplace=True,
        )
        assert "image_rgba_gray-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_rgba_gray-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_rgba_rgb(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with different channels.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image_rgba_rgb", n_components=components, inplace=True
        )
        assert "image_rgba_rgb-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_rgba_rgb-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_image_gray_rgb(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on images with different channels.
        """
        components = 2
        # Image compressed
        _output_image = pca(
            descriptors_dataset, "image_gray_rgb", n_components=components, inplace=True
        )
        assert "image_gray_rgb-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["image_gray_rgb-pca"]:
            if TestPCA.min_img_length < components:
                assert embedding.shape[0] == TestPCA.min_img_length
            else:
                assert embedding.shape[0] == components

    def test_audio_shape(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio with different shapes.
        """
        components = 2
        _output_audio = pca(
            descriptors_dataset, "audio", n_components=components, inplace=True
        )
        assert "audio-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["audio-pca"]:
            if TestPCA.min_audio_length < components:
                assert embedding.shape[0] == TestPCA.min_audio_length
            else:
                assert embedding.shape[0] == components

    def test_audio_dtypes(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio with different dtypes.
        """
        components = 2
        _output_audio = pca(
            descriptors_dataset, "audio_dtypes", n_components=components, inplace=True
        )
        assert "audio_dtypes-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["audio_dtypes-pca"]:
            if TestPCA.min_audio_length < components:
                assert embedding.shape[0] == TestPCA.min_audio_length
            else:
                assert embedding.shape[0] == components

    def test_audio_channels(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio with different channels.
        """
        components = 2
        _output_audio = pca(
            descriptors_dataset, "audio_channels", n_components=components, inplace=True
        )
        assert "audio_channels-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["audio_channels-pca"]:
            if TestPCA.min_audio_length < components:
                assert embedding.shape[0] == TestPCA.min_audio_length
            else:
                assert embedding.shape[0] == components

    def test_audio_shapes_2(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio with different shapes.
        """
        components = 2
        _output_audio = pca(
            descriptors_dataset, "audio_shapes", n_components=components, inplace=True
        )
        assert "audio_shapes-pca" in descriptors_dataset.keys()
        for embedding in descriptors_dataset["audio_shapes-pca"]:
            if TestPCA.min_audio_length < components:
                assert embedding.shape[0] == TestPCA.min_audio_length
            else:
                assert embedding.shape[0] == components

    def test_audio_nan(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio with NaN.
        """
        components = 2
        _output_embeddings = pca(
            descriptors_dataset, "audio_nan", n_components=components, inplace=True
        )

    def test_audio_none(self, descriptors_dataset: Dataset) -> None:
        """
        Test PCA descriptor on audio.
        """
        components = 2
        _output_embedding = pca(
            descriptors_dataset, "audio_none", n_components=components, inplace=True
        )


class TestCatch22:
    """
    Test Catch22 descriptor.
    """

    def test_sequence_shape(self, descriptors_dataset: Dataset) -> None:
        """
        Test Catch22 descriptor on sequences 1D.
        """
        _output_sequence = catch22(
            descriptors_dataset, "sequence_1d_extended", inplace=True
        )
        assert "sequence_1d_extended-catch22" in descriptors_dataset.keys()
        # assert correct shape for each embedding
        for embedding in descriptors_dataset["sequence_1d_extended-catch22"]:
            assert embedding.shape[0] == 22

    def test_sequence_two_samples(self, descriptors_dataset: Dataset) -> None:
        """
        Test Catch22 descriptor on sequences 1D.
        """
        _output_sequence = catch22(descriptors_dataset, "sequence_1d", inplace=True)
        assert "sequence_1d-catch22" in descriptors_dataset.keys()

    def test_sequence_float_columns(self, descriptors_dataset: Dataset) -> None:
        """
        Test Catch22 descriptor on float data.
        """
        _output_sequence = catch22(
            descriptors_dataset,
            "sequence_1d_extended",
            as_float_columns=True,
            inplace=True,
        )

    def test_sequence_nan(self, descriptors_dataset: Dataset) -> None:
        """
        Test Catch22 descriptor on NaN data.
        """
        _output_sequence = catch22(
            descriptors_dataset, "sequence_1d_nan_extended", inplace=True
        )
        assert "sequence_1d_nan_extended-catch22" in descriptors_dataset.keys()
        # assert correct shape for each embedding
        for counter, embedding in enumerate(
            descriptors_dataset["sequence_1d_nan_extended-catch22"]
        ):
            if counter == 0:
                assert embedding is None
            else:
                assert embedding.shape[0] == 22
