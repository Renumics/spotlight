import { TransferFunction } from '../../../../hooks/useColorTransferFunction';
import * as React from 'react';
import { memo } from 'react';
import tw, { css, styled } from 'twin.macro';
import { CategoricalTransferFunctionLegend } from './CategoricalLegend';
import { ContinuousTransferFunctionLegend } from './ContinuousLegend';

export type Alignment = 'left' | 'center' | 'right';
export type Arrangement = 'horizontal' | 'vertical';

export const DEFAULT_ALIGNMENT = 'left';
export const DEFAULT_ARRANGEMENT = 'horizontal';

interface BaseProps {
    transferFunction: TransferFunction;
    caption: string;
    arrange?: Arrangement;
    className?: string;
    align?: Alignment;
}

export interface ConstantProps {
    kind: 'constant';
}

const LegendWrapper = styled.div(({ align }: { align: Alignment }) => [
    css`
        max-width: '150px';
        min-width: '100px';
    `,
    tw`w-64 absolute top-0 flex flex-col space-y-1 mt-2 justify-end pointer-events-none`,
    align === 'left' && tw`pl-2`,
    align === 'right' && tw`right-4`,
    align === 'center' && tw`left-1/2 transform -translate-x-1/2`,
]);

const Legend: React.FunctionComponent<BaseProps> = ({
    align = DEFAULT_ALIGNMENT,
    arrange = DEFAULT_ARRANGEMENT,
    caption,
    transferFunction,
    className,
}) => {
    return (
        <LegendWrapper className={className} align={align}>
            <span tw="text-gray-900 text-xs font-bold" style={{ textAlign: align }}>
                {caption}
            </span>
            {transferFunction.kind === 'continuous' && (
                <ContinuousTransferFunctionLegend
                    transferFunction={transferFunction}
                    arrange={arrange}
                    align={align}
                />
            )}
            {transferFunction.kind === 'categorical' && (
                <CategoricalTransferFunctionLegend
                    transferFunction={transferFunction}
                    align={align}
                    arrange={arrange}
                />
            )}
        </LegendWrapper>
    );
};

export default memo(Legend);
