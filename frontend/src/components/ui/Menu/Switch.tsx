import { ChangeEvent, ReactNode, useCallback } from 'react';
import 'twin.macro';

export interface Props {
    value?: boolean;
    onChange?: (value: boolean) => void;
    children?: ReactNode;
}

const Switch = ({ value, onChange, children }: Props): JSX.Element => {
    const handleChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            onChange?.(e.target.checked);
        },
        [onChange]
    );

    return (
        <label tw="flex items-center">
            <input type="checkbox" checked={value} onChange={handleChange} />
            <span tw="pl-1 flex-grow">{children}</span>
        </label>
    );
};

export default Switch;
