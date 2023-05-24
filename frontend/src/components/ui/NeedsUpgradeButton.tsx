import Button, { Props } from './Button';
import { forwardRef, ForwardRefRenderFunction } from 'react';
import 'twin.macro';

const NeedsUpgradeButton: ForwardRefRenderFunction<
    HTMLButtonElement,
    Omit<Props, 'onClick'>
> = ({ tooltip, children, ...buttonProps }, ref) => {
    const full_tooltip = (
        <div tw="flex flex-row items-center">
            <div>{tooltip ?? 'Only in Spotlight'}</div>
            <div tw="ml-1 px-0.5 rounded bg-blue-400/30 border-2 border-blue-400 text-xs font-bold">
                PRO
            </div>
        </div>
    );

    return (
        <Button
            disabled={true}
            tw="disabled:cursor-not-allowed text-gray-400 disabled:text-gray-400 disabled:hover:text-gray-400"
            tooltip={full_tooltip}
            {...buttonProps}
            ref={ref}
        >
            {children}
        </Button>
    );
};

export default forwardRef(NeedsUpgradeButton);
