import CheckedIcon from '../../icons/Checked';
import UncheckedIcon from '../../icons/Unchecked';
import { ChangeEvent, FunctionComponent, KeyboardEvent, useCallback } from 'react';
import tw, { styled } from 'twin.macro';

interface Props {
    onChange?: (checked: boolean) => void;
    checked: boolean;
    className?: string;
}

const StyledLabel = styled.label`
    input {
        border: 0;
        clip: rect(0 0 0 0);
        clippath: inset(50%);
        height: 1px;
        margin: -1px;
        overflow: hidden;
        padding: 0;
        position: absolute;
        white-space: nowrap;
        width: 1px;
    }
    svg {
        ${tw`block! hover:text-blue-600`}
    }
    input:focus + svg {
        ${tw`text-blue-600`}
    }
`;

const Checkbox: FunctionComponent<Props> = ({ checked, onChange, className }) => {
    const onCheckboxChange = useCallback(
        (event: ChangeEvent<HTMLInputElement>) => {
            onChange?.(event.target.checked);
        },
        [onChange]
    );

    const onKeyDown = useCallback(
        (event: KeyboardEvent<HTMLInputElement>) => {
            if (event.key === 'Enter') {
                onChange?.(!checked);
            }
        },
        [checked, onChange]
    );

    return (
        <div className={className}>
            <StyledLabel tw="cursor-pointer block">
                <input
                    type="checkbox"
                    onKeyDown={onKeyDown}
                    className="hiddenCheckbox"
                    checked={checked}
                    onChange={onCheckboxChange}
                />
                {checked ? (
                    <CheckedIcon tw="text-blue-500" />
                ) : (
                    <UncheckedIcon tw="text-gray-700" />
                )}
            </StyledLabel>
        </div>
    );
};

export default Checkbox;
