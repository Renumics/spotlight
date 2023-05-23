"""
This module provides common utilities for handling meshes.
"""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np


def reindex(point_ids: np.ndarray, *elements: np.ndarray) -> Tuple[np.ndarray, ...]:
    """
    Reindex elements which refer to the non-negative unique point ids so that
    they refer to the indices of point ids (`np.arange(len(point_ids))`) in the
    same way.
    """
    if elements:
        inverse_point_ids = np.full(
            max((x.max(initial=0) for x in (point_ids, *elements))) + 1,
            -1,
            np.int64,
        )
        inverse_point_ids[point_ids] = np.arange(len(point_ids))
        return tuple(inverse_point_ids[x].astype(x.dtype) for x in elements)
    return ()


def attribute_to_array(attribute: Union[np.ndarray, List[np.ndarray]]) -> np.ndarray:
    """
    Encode a single attribute or a list of attribute steps as array with shape
    `(num_steps, n, ...)` and squeeze all dimensions except for 0 and 1.
    """
    if not isinstance(attribute, list):
        attribute = [attribute]
    attribute = np.asarray(attribute)
    attribute = attribute.reshape(
        (*attribute.shape[:2], *(x for x in attribute.shape[2:] if x != 1))
    )
    return attribute


def triangulate(
    triangles: Optional[np.ndarray] = None,
    triangle_attributes: Optional[
        Dict[str, Union[np.ndarray, List[np.ndarray]]]
    ] = None,
    quadrangles: Optional[np.ndarray] = None,
    quadrangle_attributes: Optional[
        Dict[str, Union[np.ndarray, List[np.ndarray]]]
    ] = None,
) -> Tuple[np.ndarray, Dict[str, Union[np.ndarray, List[np.ndarray]]]]:
    """
    Triangulate quadrangles and respective attributes and append them to the
    given triangles/attributes.
    """
    # pylint: disable=too-many-branches
    attrs = {}
    if triangles is None:
        trias = np.empty((0, 3), np.uint32)
        if triangle_attributes:
            raise ValueError(
                f"`triangles` not given, but `triangle_attributes` have "
                f"{len(triangle_attributes)} items."
            )
    else:
        trias = triangles
        if triangle_attributes is not None:
            for attr_name, triangle_attr in triangle_attributes.items():
                attrs[attr_name] = attribute_to_array(triangle_attr)

    if quadrangles is None:
        if quadrangle_attributes is not None and len(quadrangle_attributes) != 0:
            raise ValueError(
                f"`quadrangles` not given, but `quadrangle_attributes` have "
                f"{len(quadrangle_attributes)} items."
            )
    else:
        trias = np.concatenate(
            (trias, quadrangles[:, [0, 1, 2]], quadrangles[:, [0, 2, 3]])
        )
        for attr_name, quadrangle_attr in (quadrangle_attributes or {}).items():
            quadrangle_attr = attribute_to_array(quadrangle_attr)
            try:
                attr = attrs[attr_name]
            except KeyError:
                attrs[attr_name] = np.concatenate(
                    (quadrangle_attr, quadrangle_attr), axis=1
                )
            else:
                attrs[attr_name] = np.concatenate(
                    (attr, quadrangle_attr, quadrangle_attr), axis=1
                )

    for attr_name, attr in attrs.items():
        if attr.shape[1] != len(trias):
            raise ValueError(
                f"Values of attributes should have the same length as "
                f"triangles ({len(trias)}), but length {attr.shape[1]} "
                f"received."
            )
    return (
        trias,
        {
            attr_name: attr[0] if len(attr) == 1 else list(attr)
            for attr_name, attr in attrs.items()
        },
    )


def clean(
    points: np.ndarray,
    triangles: np.ndarray,
    point_attributes: Optional[Dict[str, np.ndarray]] = None,
    triangle_attributes: Optional[Dict[str, np.ndarray]] = None,
    point_displacements: Optional[List[np.ndarray]] = None,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    Dict[str, np.ndarray],
    Dict[str, np.ndarray],
    List[np.ndarray],
]:
    """
    Remove:
        degenerated triangles and respective attributes;
        invalid triangles and respective attributes;
        invalid points and respective attributes;
        empty attributes and point displacements.
    """
    point_ids = np.arange(len(points))
    valid_triangles_mask = (
        (triangles[:, 0] != triangles[:, 1])
        & (triangles[:, 0] != triangles[:, 2])
        & (triangles[:, 1] != triangles[:, 2])
        & np.isin(triangles, point_ids).all(axis=1)
    )
    triangles = triangles[valid_triangles_mask]
    triangle_attributes = {
        k: [x[valid_triangles_mask] for x in v]
        if isinstance(v, list)
        else v[valid_triangles_mask]
        for k, v in (triangle_attributes or {}).items()
    }

    valid_points_mask = np.isin(point_ids, triangles)
    points = points[valid_points_mask]
    point_attributes = {
        k: [x[valid_points_mask] for x in v]
        if isinstance(v, list)
        else v[valid_points_mask]
        for k, v in (point_attributes or {}).items()
    }
    point_displacements = [x[valid_points_mask] for x in point_displacements or []]
    point_ids = point_ids[valid_points_mask]
    triangles, *_ = reindex(point_ids, triangles)

    return (
        points,
        triangles,
        {k: v for k, v in point_attributes.items() if len(v) > 0},
        {k: v for k, v in triangle_attributes.items() if len(v) > 0},
        [x for x in point_displacements if len(x) > 0],
    )
