import { Color } from 'chroma-js';
import { DataType } from '../datatypes';
import _ from 'lodash';
import { useMemo } from 'react';
import { useColors } from '../stores/colors';
import { makeStats } from '../stores/dataset/statisticsFactory';
import { ColumnData } from '../types';

const MAX_VALUES_FOR_INT_CATEGORY = 100;

type BaseTransferFunction = {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (val: any): Color;
    paletteName: string;
    kind: 'continuous' | 'categorical' | 'constant';
    dType: DataType;
};

export interface CategoricalTransferFunction extends BaseTransferFunction {
    kind: 'categorical';
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    domain: any[];
}

export interface ContinuousTransferFunction extends BaseTransferFunction {
    kind: 'continuous';
    domain: [number, number];
    classBreaks?: number[];
}

export interface ConstantTransferFunction extends BaseTransferFunction {
    kind: 'constant';
}

export type TransferFunction =
    | CategoricalTransferFunction
    | ContinuousTransferFunction
    | ConstantTransferFunction;

export const createContinuousTransferFunction = (
    min: number,
    max: number,
    dType: DataType,
    /* when specified a continuous transfer function will be discreticed
     *   e.G. [0, 4, 5.5, 10] will return 3 different colors for values between 0 and 10
     */
    classBreaks?: number[]
): ContinuousTransferFunction => {
    const palette = useColors.getState().continuousPalette;
    const colorScale = palette.scale().domain([min, max]);

    if (classBreaks !== undefined) {
        colorScale.classes(classBreaks);
    }

    const tf = ((val: number) => colorScale(val)) as ContinuousTransferFunction;

    tf.kind = 'continuous';
    tf.domain = [min, max];
    tf.classBreaks = classBreaks;
    tf.paletteName = palette.name;
    tf.dType = dType;

    return tf;
};

export const createCategoricalTransferFunction = (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    values: any[],
    dType: DataType
): CategoricalTransferFunction => {
    const colorMap = new Map<unknown, Color>();
    const uniqueValues = _.uniq(values).sort();
    const palette = useColors.getState().categoricalPalette;
    const colorScale = palette.scale();

    // The provided types for chroma.scale.classes are incomplete
    // and don't allow calling scale.classes to aquire the configured classes
    const classCount = (colorScale.classes as unknown as () => number[])().length - 1;

    uniqueValues.forEach((val, index) => {
        colorMap.set(val, colorScale(index % classCount));
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const tf = ((val: any) => {
        return colorMap.get(val);
    }) as CategoricalTransferFunction;

    tf.kind = 'categorical';
    tf.domain = uniqueValues;
    tf.dType = dType;
    tf.paletteName = palette.name;

    return tf;
};

export const createConstantTransferFunction = (
    dType?: DataType
): ConstantTransferFunction => {
    const palette = useColors.getState().constantPalette;
    const colorScale = palette.scale();
    const tf = () => colorScale(0);
    tf.kind = 'constant';
    tf.paletteName = palette.name;
    tf.dType = dType || { kind: 'Unknown', optional: false };

    return tf as ConstantTransferFunction;
};

const createColorTransferFunction = (
    data: ColumnData | undefined,
    dType: DataType | undefined,
    classBreaks?: number[]
): TransferFunction => {
    const robustColoring = useColors.getState().useRobustColorScales;

    if (dType === undefined)
        return createConstantTransferFunction({ kind: 'Unknown', optional: false });
    if (data === undefined) return createConstantTransferFunction(dType);

    if (['int', 'bool', 'Category', 'str'].includes(dType.kind)) {
        const uniqValues = _.uniq(data);

        const tooManyInts =
            dType.kind === 'int' && uniqValues.length > MAX_VALUES_FOR_INT_CATEGORY;

        if (!tooManyInts) {
            const transferFunction = createCategoricalTransferFunction(
                uniqValues,
                dType
            );
            return transferFunction;
        }
    }

    if (['int', 'float'].includes(dType.kind)) {
        const stats = makeStats(dType, data);
        return createContinuousTransferFunction(
            (robustColoring ? stats?.p5 : stats?.min) ?? 0,
            (robustColoring ? stats?.p95 : stats?.max) ?? 1,
            dType,
            classBreaks
        );
    }

    return createConstantTransferFunction(dType);
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const useColorTransferFunction = (data: any[], dtype: DataType) =>
    useMemo(() => createColorTransferFunction(data, dtype), [dtype, data]);

export default useColorTransferFunction;
