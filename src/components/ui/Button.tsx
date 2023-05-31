import Tooltip from './Tooltip';
import * as React from 'react';
import { forwardRef, ForwardRefRenderFunction, ReactNode } from 'react';
import tw, { styled } from 'twin.macro';

type Size = 'small' | 'medium';

type ExtraProps = {
    outlined?: boolean;
    checked?: boolean;
    size?: Size;
    tooltip?: ReactNode;
};

const StyledHTMLButton = styled.button(
    ({ outlined = false, checked = false, size = 'medium' }: ExtraProps) => [
        tw`
            flex flex-row items-center justify-center
            px-0.5
            font-semibold
            text-navy-600
            hover:text-blue-600
            active:hover:text-blue-200
            disabled:shadow-none
            disabled:text-gray-600
            disabled:active:text-gray-400
            focus:outline-none
            focus:text-blue-600
            bg-transparent
            transition-colors
            ease-in-out
            cursor-pointer`,
        outlined && tw`hover:(shadow bg-gray-200) border border-gray-400 rounded`,
        checked && tw`bg-gray-200 shadow-inner rounded`,
        size === 'small' && tw`px-0`,
    ]
);

export type Props = ExtraProps &
    Omit<React.ComponentProps<typeof StyledHTMLButton>, 'as' | 'title'>;

const Button: ForwardRefRenderFunction<HTMLButtonElement, Props> = (
    { tooltip, children, ...buttonProps },
    ref
) => {
    const button = (
        <StyledHTMLButton ref={ref} {...buttonProps}>
            {children}
        </StyledHTMLButton>
    );
    if (tooltip) {
        return <Tooltip content={tooltip}>{button}</Tooltip>;
    } else {
        return button;
    }
};

export default forwardRef(Button);
