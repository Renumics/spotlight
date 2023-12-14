import { useColorTransferFunction } from '../../hooks';
import { useRef, useCallback, useState, useMemo } from 'react';
import { Lens } from '../../types';
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
                        color={colorTransferFunction(categories[index]).hex()}
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
BoundingBoxLens.dataTypes = ['Image', 'BoundingBox', 'Sequence', 'Category'];
BoundingBoxLens.multi = true;
BoundingBoxLens.displayName = 'BoundingBox';
BoundingBoxLens.defaultHeight = 256;
BoundingBoxLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 3) return [];

    const selectedTypes = selectedColumns.map((selectedCol) => selectedCol.type);
    if (selectedColumns.length === 0)
        return allColumns.filter(({ type }) =>
            BoundingBoxLens.dataTypes.includes(type.kind)
        );

    if (selectedTypes.find((type) => type.kind === 'Sequence')) {
        return allColumns.filter(({ type }) => {
            return type.kind === 'Sequence' || type.kind === 'Image';
        });
    } else if (
        selectedTypes.find((type) => ['BoundingBox', 'Category'].includes(type.kind))
    ) {
        return allColumns.filter(({ type }) => {
            return (
                type.kind === 'BoundingBox' ||
                type.kind === 'Category' ||
                type.kind === 'Image'
            );
        });
    } else {
        return allColumns.filter(({ type }) =>
            BoundingBoxLens.dataTypes.includes(type.kind)
        );
    }
};
BoundingBoxLens.isSatisfied = (columns) => {
    if (columns.length < 2) return false;

    const types = columns.map((col) => col.type);

    if (!types.find((type) => type.kind === 'Image')) return false;

    if (!types.find((type) => ['BoundingBox', 'Sequence'].includes(type.kind)))
        return false;

    if (
        types.find(
            (type) => type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox'
        )
    ) {
        return true;
    } else {
        if (types.find((type) => type.kind === 'BoundingBox')) return true;
        else return false;
    }
};

export default BoundingBoxLens;
