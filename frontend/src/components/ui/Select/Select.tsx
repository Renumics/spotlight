import { PropsWithChildren, ReactElement, useCallback, useMemo } from 'react';
import ReactSelect, { components as reactSelectComponents } from 'react-select';
import type { SingleValue, SingleValueProps } from 'react-select';
import Creatable from 'react-select/creatable';
import { makeStyles } from './styles';
import { OptionType, SelectVariant, Value } from './types';

interface SelectProps<T extends Value> {
    options: readonly T[];
    value?: T;
    defaultValue?: T;
    placeholder?: string;
    variant?: SelectVariant;
    onChange?: (value?: T) => void;
    autoFocus?: boolean;
    openMenuOnFocus?: boolean;
    isDisabled?: boolean;
    label?: (value?: T) => string;
    isSearchable?: boolean;
    isClearable?: boolean;
    canCreate?: boolean;
    singleValueTemplate?: (value: React.ReactNode) => React.ReactNode;
}

function defaultLabel<T extends Value>(v?: T) {
    return v?.toString() || 'None';
}

function Select<T extends Value>({
    options,
    value,
    defaultValue,
    placeholder,
    variant,
    onChange,
    autoFocus,
    openMenuOnFocus,
    isDisabled,
    label = defaultLabel,
    singleValueTemplate,
    canCreate = false,
    isSearchable = true,
    isClearable = false,
}: PropsWithChildren<SelectProps<T>>): ReactElement {
    const wrappedOptions = useMemo(
        () =>
            options.map((option) => ({
                value: option,
            })),
        [options]
    );

    const components = useMemo(
        () => ({
            SingleValue:
                singleValueTemplate !== undefined
                    ? ({
                          children,
                          ...props
                      }: SingleValueProps<OptionType<T>, false>) => (
                          <reactSelectComponents.SingleValue {...props}>
                              {singleValueTemplate(children)}
                          </reactSelectComponents.SingleValue>
                      )
                    : reactSelectComponents.SingleValue,
        }),
        [singleValueTemplate]
    );

    const wrappedValue = useMemo(
        () => (value === undefined ? undefined : { value }),
        [value]
    );

    const getOptionLabel = useCallback((o: OptionType<T>) => label(o.value), [label]);

    const wrappedDefaultValue = useMemo(
        () =>
            defaultValue === undefined
                ? undefined
                : {
                      value: defaultValue,
                  },
        [defaultValue]
    );

    const handleChange = useCallback(
        (option: SingleValue<OptionType<T>>) => {
            if (option) {
                onChange?.((option as OptionType<T>).value);
            } else {
                onChange?.();
            }
        },
        [onChange]
    );

    const styles = useMemo(() => makeStyles<T>(variant), [variant]);

    const SelectType = canCreate ? Creatable : ReactSelect;

    const menuPortalTarget = document.getElementById('selectMenuRoot');
    if (menuPortalTarget === null) return <></>;

    return (
        <SelectType<OptionType<T>, false>
            options={wrappedOptions}
            value={wrappedValue ?? null}
            defaultValue={wrappedDefaultValue}
            placeholder={placeholder}
            onChange={handleChange}
            styles={styles}
            // eslint-disable-next-line jsx-a11y/no-autofocus
            autoFocus={autoFocus}
            isDisabled={isDisabled}
            openMenuOnFocus={openMenuOnFocus}
            getOptionLabel={getOptionLabel}
            menuPortalTarget={menuPortalTarget}
            menuPlacement="auto"
            components={components}
            isSearchable={isSearchable}
            isClearable={isClearable}
        />
    );
}

export default Select;
