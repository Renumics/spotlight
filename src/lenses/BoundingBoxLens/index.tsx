import { useColorTransferFunction } from '../../hooks';
import { useRef, useCallback, useState, useMemo } from 'react';
import { DataColumn, Lens } from '../../types';
import 'twin.macro';
import { CategoricalDataType } from '../../datatypes';
import BBox from './BBox';
import useResizeObserver from '@react-hook/resize-observer';

const BoundingBoxLens: Lens = ({ urls, values, columns }) => {
    const container = useRef<HTMLDivElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);
    const [imgSize, setImgSize] = useState({ width: 0, height: 0 });
    const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

    // In case of single bounding box with label
    const bboxColumnIndex = columns.findIndex((col) => col.type.kind === 'BoundingBox');
    const categoryColumnIndex = columns.findIndex(
        (col) => col.type.kind === 'Category'
    );

    // In case of multiple bounding boxes per image
    const bboxesColumnIndex = columns.findIndex(
        (col) => col.type.kind === 'Sequence' && col.type.dtype.kind === 'BoundingBox'
    );
    const categoriesColumnIndex = columns.findIndex(
        (col) => col.type.kind === 'Sequence' && col.type.dtype.kind === 'Category'
    );
    const imageColumnIndex = columns.findIndex((col) => col.type.kind === 'Image');
    const url = urls[imageColumnIndex];

    const boxes = useMemo(() => {
        if (bboxColumnIndex != -1) {
            return [values[bboxColumnIndex] as number[]];
        } else if (bboxesColumnIndex != -1) {
            return values[bboxesColumnIndex] as [number[]];
        } else {
            return [];
        }
    }, [values, bboxColumnIndex, bboxesColumnIndex]);

    const categories = useMemo(() => {
        if (categoryColumnIndex != -1) {
            return [values[categoryColumnIndex] as number];
        } else if (categoriesColumnIndex != -1) {
            return values[categoriesColumnIndex] as [number];
        } else {
            return [];
        }
    }, [values, categoryColumnIndex, categoriesColumnIndex]);

    // Natural dimensions of the image
    const naturalWidth = imgSize.width;
    const naturalHeight = imgSize.height;
    const imageAspectRatio = naturalWidth / Math.max(1, naturalHeight);

    //Dimensions of the parent element
    const parentWidth = containerSize.width;
    const parentHeight = containerSize.height;

    const parentAspectRatio = parentWidth / Math.max(1, parentHeight);

    let renderedWidth: number, renderedHeight: number;

    if (imageAspectRatio > parentAspectRatio) {
        renderedWidth = parentWidth;
        renderedHeight = parentWidth / imageAspectRatio;
    } else {
        renderedHeight = parentHeight;
        renderedWidth = parentHeight * imageAspectRatio;
    }
    const offsetWidth = (parentWidth - renderedWidth) / 2;
    const offsetHeight = (parentHeight - renderedHeight) / 2;

    const categoricalColumn =
        columns[categoryColumnIndex] ?? columns[categoriesColumnIndex];
    const categoricalDtype = (
        categoricalColumn?.type?.kind === 'Sequence'
            ? categoricalColumn?.type?.dtype
            : categoricalColumn?.type
    ) as CategoricalDataType | undefined;

    const colorTransferFunction = useColorTransferFunction(
        categories,
        categoricalDtype
    );

    useResizeObserver(container, () => {
        setContainerSize({
            width: container.current?.offsetWidth ?? 0,
            height: container.current?.offsetHeight ?? 0,
        });
    });

    const handleLoad = useCallback(() => {
        setImgSize({
            width: imgRef.current?.naturalWidth ?? 0,
            height: imgRef.current?.naturalHeight ?? 1,
        });
    }, []);

    return (
        <div tw="relative h-full w-full overflow-hidden" ref={container}>
            <img
                tw="absolute top-0 left-0 h-full w-full object-contain"
                ref={imgRef}
                src={url}
                alt="URL not found!"
                onLoad={handleLoad}
            />
            <svg tw="absolute top-0 left-0 h-full w-full" ref={svgRef}>
                <g />
                {boxes.map((box, index) => (
                    <BBox
                        key={index}
                        width={(box[2] - box[0]) * renderedWidth}
                        height={(box[3] - box[1]) * renderedHeight}
                        x={box[0] * renderedWidth + offsetWidth}
                        y={box[1] * renderedHeight + offsetHeight}
                        color={colorTransferFunction(categories[index])}
                        label={
                            categoricalDtype?.invertedCategories[categories[index]] ??
                            ''
                        }
                    />
                ))}
            </svg>
        </div>
    );
};

BoundingBoxLens.key = 'BoundingBoxView';
BoundingBoxLens.dataTypes = ['Image', 'BoundingBox', 'Sequence', 'Category', 'str'];
BoundingBoxLens.multi = true;
BoundingBoxLens.displayName = 'BoundingBox';
BoundingBoxLens.defaultHeight = 256;
BoundingBoxLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    const selectedTypes = selectedColumns.map((selectedCol) => selectedCol.type);
    const allowedColumns: DataColumn[] = [];

    // allow exactly one image column
    if (!selectedTypes.find((type) => type.kind === 'Image')) {
        allowedColumns.push(...allColumns.filter(({ type }) => type.kind === 'Image'));
    }

    // allow exactly one bbox or bbox[] column
    if (
        !selectedTypes.find(
            (type) =>
                type.kind === 'BoundingBox' ||
                (type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox')
        )
    ) {
        allowedColumns.push(
            ...allColumns.filter(
                ({ type }) =>
                    type.kind === 'BoundingBox' ||
                    (type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox')
            )
        );
    }

    // allow exactly one label or label[] column
    if (
        !selectedTypes.find(
            (type) =>
                type.kind === 'Category' ||
                type.kind === 'str' ||
                (type.kind === 'Sequence' &&
                    (type.dtype.kind === 'str' || type.dtype.kind === 'Category'))
        )
    ) {
        allowedColumns.push(
            ...allColumns.filter(
                ({ type }) =>
                    type.kind === 'Category' ||
                    type.kind === 'str' ||
                    (type.kind === 'Sequence' &&
                        (type.dtype.kind === 'str' || type.dtype.kind === 'Category'))
            )
        );
    }
    return allowedColumns;
};
BoundingBoxLens.isSatisfied = (columns) => {
    const types = columns.map((col) => col.type);
    const hasImage = !!types.find((type) => type.kind === 'Image');
    const hasBbox = !!types.find(
        (type) =>
            type.kind === 'BoundingBox' ||
            (type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox')
    );
    return hasImage && hasBbox;
};

export default BoundingBoxLens;
