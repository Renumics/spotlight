def get_append_column_fn_name(dtype_name: str) -> str:
    """
    Get name of the `append_column` dataset method for the given column type.
    """

    if dtype_name == "bool":
        return "append_bool_column"
    if dtype_name == "int":
        return "append_int_column"
    if dtype_name == "float":
        return "append_float_column"
    if dtype_name == "str":
        return "append_string_column"
    if dtype_name == "datetime":
        return "append_datetime_column"
    if dtype_name == "array":
        return "append_array_column"
    if dtype_name == "Embedding":
        return "append_embedding_column"
    if dtype_name == "Image":
        return "append_image_column"
    if dtype_name == "Sequence1D":
        return "append_sequence_1d_column"
    if dtype_name == "Mesh":
        return "append_mesh_column"
    if dtype_name == "Audio":
        return "append_audio_column"
    if dtype_name == "Category":
        return "append_categorical_column"
    if dtype_name == "Video":
        return "append_video_column"
    if dtype_name == "Window":
        return "append_window_column"
    raise TypeError(dtype_name)
