import { useRef, useCallback, useState, useEffect } from 'react';
import { Lens } from '../../types';
import tw, { styled, theme } from 'twin.macro';
import { CategoricalDataType, SequenceDataType } from '../../datatypes';
import { ColorsState, useColors } from '../../stores/colors';
import { Dataset, useDataset } from '../../stores/dataset';
import chroma from 'chroma-js';

const Container = styled.div`
    ${tw`relative h-full w-full overflow-hidden`}
    img {
        ${tw`absolute top-0 left-0 h-full w-full object-contain`}
    }
    svg {
        ${tw`absolute top-0 left-0 h-full w-full`}
    }
`;

const BoundingBoxLens: Lens = ({ urls, values, columns }) => {
    const container = useRef<HTMLDivElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);
    const [imgSize, setImgSize] = useState({ width: 0, height: 1 });

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

    let boxes: [number[]] | [];
    let categories: number[] | [];
    let invertedCategories = (index: number) => index.toString();

    // Check if single bounding box or multiple
    if (bboxColumnIndex != -1) {
        boxes = [values[bboxColumnIndex] as number[]];
    } else if (bboxesColumnIndex != -1) {
        boxes = values[bboxesColumnIndex] as [number[]];
    } else {
        boxes = [];
    }

    if (categoryColumnIndex != -1) {
        categories = [values[categoryColumnIndex] as number];

        invertedCategories = (index) =>
            (columns[categoryColumnIndex].type as CategoricalDataType)
                .invertedCategories[index];
    } else if (categoriesColumnIndex != -1) {
        categories = values[categoriesColumnIndex] as [number];

        invertedCategories = (index) =>
            (
                (columns[categoriesColumnIndex].type as SequenceDataType)
                    .dtype as CategoricalDataType
            ).invertedCategories[index];
    } else {
        categories = [];
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
    const colorTransferFunctionSelector = useCallback(
        (d: Dataset) => {
            if (categoryColumnIndex != -1) {
                return d.colorTransferFunctions[columns[categoryColumnIndex].key]?.[
                    'full'
                ];
            }
            return undefined;
        },
        [columns, categoryColumnIndex]
    );

    const colorPaletteSelector = (c: ColorsState) => c.continuousPalette;
    const colorPalette = useColors(colorPaletteSelector);
    const colorTransferFunction = useDataset(colorTransferFunctionSelector);

    let colorFunc: (i: number) => string;

    if (categories.length === 0) {
        colorFunc = (i: number) => colorPalette.scale().colors(boxes.length)[i];
    } else {
        if (colorTransferFunction !== undefined) {
            colorFunc = (i: number) => colorTransferFunction(categories[i]).hex();
        } else {
            colorFunc = (i: number) => {
                const dtype = (columns[categoriesColumnIndex].type as SequenceDataType)
                    .dtype as CategoricalDataType;
                const index = dtype.categories[invertedCategories(categories[i])];
                return colorPalette
                    .scale()
                    .colors(Object.keys(dtype.categories).length)[index];
            };
        }
    }

    useEffect(() => {
        const handleLoad = () => {
            setImgSize({
                width: imgRef.current?.naturalWidth ?? 0,
                height: imgRef.current?.naturalHeight ?? 1,
            });
        };

        const image = imgRef.current;

        if (image) {
            image.addEventListener('load', handleLoad);
        }

        return () => {
            if (image) {
                image.removeEventListener('load', handleLoad);
            }
        };
    }, []);
    //}, [boxes, categories, colorFunc]);

    return (
        <Container ref={container}>
            <img ref={imgRef} src={url} alt="URL not found!" />
            <svg ref={svgRef}>
                {boxes.map((box, index) => {
                    if (!svgRef.current) return;
                    if (!container.current) return;
                    if (!boxes) return;

                    console.log('draw a box');
                    //const image = imgRef.current;

                    // Natural dimensions of the image
                    //const naturalWidth = image?.naturalWidth ?? 1;
                    //const naturalHeight = image?.naturalHeight ?? 1;
                    const naturalWidth = imgSize.width;
                    const naturalHeight = imgSize.height;
                    const imageAspectRatio = naturalWidth / naturalHeight;

                    // Dimensions of the parent element
                    const parentWidth = container.current.offsetWidth;
                    const parentHeight = container.current.offsetHeight;

                    const parentAspectRatio = parentWidth / parentHeight;

                    let renderedWidth, renderedHeight;

                    if (imageAspectRatio > parentAspectRatio) {
                        renderedWidth = parentWidth;
                        renderedHeight = parentWidth / imageAspectRatio;
                    } else {
                        renderedHeight = parentHeight;
                        renderedWidth = parentHeight * imageAspectRatio;
                    }
                    const offsetWidth = (parentWidth - renderedWidth) / 2;
                    const offsetHeight = (parentHeight - renderedHeight) / 2;

                    // Box format [x, y, w, h] normalized.
                    const x = box[0] * renderedWidth + offsetWidth;
                    const y = box[1] * renderedHeight + offsetHeight;
                    const width = (box[2] - box[0]) * renderedWidth;
                    const height = (box[3] - box[1]) * renderedHeight;
                    const boxColor = colorFunc(index);
                    const text = invertedCategories(categories[index]);
                    const white = chroma(theme`colors.white`);
                    const black = chroma(theme`colors.black`);

                    const textColor =
                        chroma.contrast(boxColor, white) >
                        chroma.contrast(boxColor, black)
                            ? white
                            : black;

                    return (
                        <g key={index}>
                            <rect
                                key={index + 'bbox'}
                                x={x}
                                y={y}
                                width={width}
                                height={height}
                                fill="none"
                                stroke={boxColor}
                                strokeWidth={2}
                            ></rect>
                            <rect
                                key={index + 'background'}
                                x={x}
                                y={y - 11}
                                width={width}
                                height={12}
                                fill={boxColor}
                                stroke={boxColor}
                                strokeWidth={2}
                            ></rect>
                            <text
                                key={index + 'text'}
                                x={x}
                                y={y}
                                fontSize={12}
                                stroke={textColor.hex()}
                            >
                                {text}
                            </text>
                        </g>
                    );
                })}
            </svg>
        </Container>
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
