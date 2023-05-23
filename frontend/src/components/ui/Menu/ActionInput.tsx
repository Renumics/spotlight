import React, { forwardRef } from 'react';
import tw from 'twin.macro';
import Button from '../Button';
import { default as InputBase } from './Input';

export interface Props extends React.ComponentProps<typeof InputBase> {
    onClickAction?: () => void;
    actionIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, Props>(
    ({ onClickAction, actionIcon, ...props }, ref): JSX.Element => {
        return (
            <div
                css={[
                    onClickAction &&
                        tw`rounded m-1 focus:outline-none focus:ring-1 focus:border-blue-400 text-xs placeholder-gray-500`,
                    tw`flex`,
                ]}
            >
                <InputBase
                    {...props}
                    ref={ref}
                    css={[onClickAction && tw`rounded-r-none m-0`, tw`flex-grow`]}
                />
                {onClickAction && (
                    <Button
                        disabled={onClickAction === undefined}
                        onClick={onClickAction}
                        tw="inline-flex rounded-r-md border border-l-0"
                    >
                        {actionIcon}
                    </Button>
                )}
            </div>
        );
    }
);
Input.displayName = 'Input';
export default Input;
