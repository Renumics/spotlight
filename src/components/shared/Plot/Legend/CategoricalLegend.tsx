import { Color } from 'chroma-js';
import Dot from '../../../ui/Dot';
import { isCategorical } from '../../../../datatypes';
import { CategoricalTransferFunction } from '../../../../hooks/useColorTransferFunction';
import * as React from 'react';
import tw, { styled } from 'twin.macro';
import { Alignment, Arrangement, DEFAULT_ALIGNMENT, DEFAULT_ARRANGEMENT } from '.';

export interface CategoricalProps {
    colorMap: { label: string; color: Color }[];
    align?: Alignment;
    arrange?: Arrangement;
}

const CategoryList = styled.ul(
    ({ arrange, align }: { arrange?: Arrangement; align?: Alignment }) => [
        tw`leading-3 mt-0`,
        arrange === 'horizontal' && tw`flex flex-row flex-wrap`,
        align === 'right' && tw`justify-end`,
        align === 'center' && tw`justify-center`,
    ]
);

const CategoryListItem = styled.li(({ align = 'left' }: { align?: Alignment }) => [
    tw`flex items-center`,
    align === 'right' && tw`flex-row-reverse`,
    align === 'center' && tw`place-content-center`,
]);

const TooMuchCategoriesText = styled.span(({ align }: { align: Alignment }) => [
    tw`text-gray-900 text-xs mt-0`,
    align === 'right' && tw`text-right`,
    align === 'center' && tw`text-center`,
]);

export const CategoricalLegend: React.FunctionComponent<CategoricalProps> = ({
    colorMap,
    align = DEFAULT_ALIGNMENT,
    arrange = DEFAULT_ARRANGEMENT,
}) => {
    if (colorMap.length > 10)
        return (
            <TooMuchCategoriesText
                align={align}
                tw="ml-1"
            >{`${colorMap.length} categories`}</TooMuchCategoriesText>
        );
    return (
        <CategoryList arrange={arrange} align={align}>
            {colorMap.map(({ label, color }) => (
                <CategoryListItem key={label} align={align}>
                    <Dot color={color.hex()} />
                    <span tw="ml-2 mr-1 text-gray-900 text-xs">{label}</span>
                </CategoryListItem>
            ))}
        </CategoryList>
    );
};

interface CategoricalTransferFunctionLegendProps
    extends Omit<CategoricalProps, 'colorMap'> {
    transferFunction: CategoricalTransferFunction;
}

export const CategoricalTransferFunctionLegend: React.FunctionComponent<
    CategoricalTransferFunctionLegendProps
> = ({ transferFunction, ...props }) => {
    const colorMap = React.useMemo((): { label: string; color: Color }[] => {
        const map = transferFunction.domain.map((v) => {
            const label = isCategorical(transferFunction.dType)
                ? transferFunction.dType.invertedCategories[v] ?? 'None'
                : v === null
                  ? 'null'
                  : v.toString();
            return { label, color: transferFunction(v) };
        });
        return map;
    }, [transferFunction]);

    return <CategoricalLegend colorMap={colorMap} {...props} />;
};
