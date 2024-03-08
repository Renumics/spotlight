import { useRef, useCallback, useState, useMemo } from 'react';
import { DataColumn, Lens } from '../../types';
import 'twin.macro';
import BBox from './BBox';
import useResizeObserver from '@react-hook/resize-observer';
import chroma from 'chroma-js';
import _ from 'lodash';
import { useColorTransferFunction } from '../../hooks';
import { useDataformat } from '../../dataformat';
import { NO_DATA as NO_DATA_COLOR } from '../../palettes';
import { unknownDataType } from '../../datatypes';

type BBox = [number, number, number, number];
interface Label {
    text: string;
    color: chroma.Color;
}

const NO_VALUES: unknown[] = [];

function useLabels(column?: DataColumn, value?: unknown): Label[] {
    const colorFunc = useColorTransferFunction(
        NO_VALUES,
        column?.type ?? unknownDataType
    );
    const formatter = useDataformat();

    return useMemo(() => {
        if (!column) {
            return [{ text: '', color: NO_DATA_COLOR }];
        }

        if (column.type.kind === 'Sequence') {
            const innerType = column.type.dtype;
            const values = value as unknown[];
            return values.map((x) => ({
                text: formatter.format(x, innerType),
                color: colorFunc(x),
            }));
        } else {
            return [
                {
                    text: formatter.format(value, column.type),
                    color: colorFunc(value),
                },
            ];
        }
    }, [column, value, formatter, colorFunc]);
}

const BoundingBoxLens: Lens = ({ urls, values, columns }) => {
    const container = useRef<HTMLDivElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);
    const [imgSize, setImgSize] = useState({ width: 0, height: 0 });
    const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

    const imageColumnIndex = columns.findIndex((col) => col.type.kind === 'Image');
    const url = urls[imageColumnIndex];

    const bboxColumnIndex = columns.findIndex(
        (col) =>
            col.type.kind === 'BoundingBox' ||
            (col.type.kind === 'Sequence' && col.type.dtype.kind === 'BoundingBox')
    );
    const boxes: BBox[] = useMemo(() => {
        const boxValue = values[bboxColumnIndex] as number[] | number[][] | null;
        if (!boxValue) return [];
        return (
            boxValue.length && !_.isArray(boxValue[0]) ? [boxValue] : boxValue
        ) as BBox[];
    }, [values, bboxColumnIndex]);

    const labelsColumnIndex = columns.findIndex(
        (col) =>
            col.type.kind === 'Category' ||
            col.type.kind === 'str' ||
            (col.type.kind === 'Sequence' &&
                (col.type.dtype.kind === 'Category' || col.type.dtype.kind === 'str'))
    );
    const labels = useLabels(columns[labelsColumnIndex], values[labelsColumnIndex]);

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
                        color={labels[index]?.color ?? NO_DATA_COLOR}
                        label={labels[index]?.text ?? ''}
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
    const allowedColumns: DataColumn[] = [];

    // allow exactly one image column
    if (!selectedColumns.find(({ type }) => type.kind === 'Image')) {
        allowedColumns.push(...allColumns.filter(({ type }) => type.kind === 'Image'));
    }

    const allowSequences = !selectedColumns.find(
        ({ type }) => type.kind !== 'Image' && type.kind !== 'Sequence'
    );
    const allowNonSequences = !selectedColumns.find(
        ({ type }) => type.kind === 'Sequence'
    );

    // allow exactly one bbox or bbox[] column
    if (
        !selectedColumns.find(
            ({ type }) =>
                type.kind === 'BoundingBox' ||
                (type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox')
        )
    ) {
        if (allowNonSequences) {
            allowedColumns.push(
                ...allColumns.filter(({ type }) => type.kind === 'BoundingBox')
            );
        }
        if (allowSequences) {
            allowedColumns.push(
                ...allColumns.filter(
                    ({ type }) =>
                        type.kind === 'Sequence' && type.dtype.kind === 'BoundingBox'
                )
            );
        }
    }

    // allow exactly one label or label[] column
    if (
        !selectedColumns.find(
            ({ type }) =>
                type.kind === 'Category' ||
                type.kind === 'str' ||
                (type.kind === 'Sequence' &&
                    (type.dtype.kind === 'str' || type.dtype.kind === 'Category'))
        )
    ) {
        if (allowNonSequences) {
            allowedColumns.push(
                ...allColumns.filter(
                    ({ type }) => type.kind === 'Category' || type.kind === 'str'
                )
            );
        }
        if (allowSequences) {
            allowedColumns.push(
                ...allColumns.filter(
                    ({ type }) =>
                        type.kind === 'Sequence' &&
                        (type.dtype.kind === 'str' || type.dtype.kind === 'Category')
                )
            );
        }
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
