import Button, { Props } from './Button';
import { forwardRef, ForwardRefRenderFunction } from 'react';
import 'twin.macro';

const NeedsUpgradeButton: ForwardRefRenderFunction<
    HTMLButtonElement,
    Omit<Props, 'onClick'>
> = ({ tooltip, children, ...buttonProps }, ref) => {
    return (
        <Button
            disabled={true}
            tw="disabled:cursor-not-allowed text-gray-400 disabled:text-gray-400 disabled:hover:text-gray-400"
            tooltip={tooltip ?? 'This feature is only available in the pro version.'}
            {...buttonProps}
            ref={ref}
        >
            {children}
        </Button>
    );
};

export default forwardRef(NeedsUpgradeButton);
