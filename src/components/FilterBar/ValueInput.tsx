import Checkbox from '../ui/Checkbox';
import Select from '../ui/Select';
import { parse, useFormatter } from '../../dataformat';
import { CategoricalDataType, DataType } from '../../datatypes';
import { ChangeEvent, KeyboardEvent, useCallback } from 'react';
import 'twin.macro';

interface Props<T extends DataType = DataType> {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: any;
    type: T;
    placeholder: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onChange?: (value: any) => void;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onEnter?: (value: any) => void;
}

type FactoryProps = Omit<Props, 'type'> & {
    type?: DataType;
};

const CategoricalInput = ({
    value,
    type,
    onChange,
    placeholder,
}: Props<CategoricalDataType>): JSX.Element => {
    const keys = Object.values(type?.categories || {});
    const options = type.optional ? [...keys, null] : keys;
    const renderLabel = (val?: number) => type?.invertedCategories[val ?? NaN] ?? '';

    return (
        <div tw="min-w-[4rem]">
            <Select
                options={options}
                label={renderLabel}
                placeholder={placeholder}
                onChange={onChange}
                value={value}
                variant="inline"
            />
        </div>
    );
};

const DefaultInput = ({
    value,
    type,
    placeholder,
    onChange,
    onEnter,
}: Props): JSX.Element => {
    const onChangeInput = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            const value = parse(e.target.value, type);
            onChange?.(value);
        },
        [onChange, type]
    );

    const onKeyDown = useCallback(
        (e: KeyboardEvent<HTMLInputElement>) => {
            if (onEnter && e.key === 'Enter') {
                onEnter(parse(e.currentTarget.value, type));
            }
        },
        [onEnter, type]
    );

    const dataformat = useFormatter();
    const defaultValue =
        value === undefined ? undefined : dataformat.format(value, type);

    return (
        <input
            tw="
                p-0 px-1 w-auto
                text-sm
                bg-transparent shadow-none
                outline-none
                focus:bg-white focus:ring-1 ring-inset ring-blue-500
            "
            type="text"
            onKeyDown={onKeyDown}
            placeholder={placeholder}
            defaultValue={defaultValue}
            onChange={onChangeInput}
            readOnly={onChange === undefined}
        />
    );
};

const BoolInput = ({ value, onChange }: Props): JSX.Element => {
    return <Checkbox tw="mx-2 mt-0.5" checked={value ?? false} onChange={onChange} />;
};

const Placeholder = ({ value, placeholder }: FactoryProps): JSX.Element => {
    return (
        <input
            tw="
                p-0 px-1 w-auto
                text-sm
                bg-transparent shadow-none
                outline-none
                focus:bg-white focus:ring-1 ring-inset ring-blue-500
            "
            type="text"
            placeholder={value ?? placeholder}
            readOnly={true}
        />
    );
};

const ValueInput = (props: FactoryProps): JSX.Element => {
    if (!props.type) {
        return <Placeholder {...props} />;
    }

    switch (props.type.kind) {
        case 'Category':
            return <CategoricalInput {...props} type={props.type} />;
        case 'bool':
            return <BoolInput {...props} type={props.type} />;
        default:
            return <DefaultInput {...props} type={props.type} />;
    }
};

export default ValueInput;
