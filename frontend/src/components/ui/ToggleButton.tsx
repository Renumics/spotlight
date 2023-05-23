import { FunctionComponent, useState } from 'react';
import Button, { Props as ButtonProps } from './Button';

type Props = {
    checked?: boolean;
    onChange?: ({ checked }: { checked: boolean }) => void;
    tooltip?: string;
} & ButtonProps;

const ToggleButton: FunctionComponent<Props> = ({
    checked,
    onChange,
    tooltip,
    children,
    ...buttonProps
}) => {
    const [state, setState] = useState<boolean>(checked ?? false);

    const handleClick = () => {
        const newState = !(checked ?? state);
        onChange?.({ checked: newState });
        setState(newState);
    };

    return (
        <Button
            onClick={handleClick}
            checked={checked ?? state}
            tooltip={tooltip}
            {...buttonProps}
        >
            {children}
        </Button>
    );
};

export default ToggleButton;
