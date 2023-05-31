import type { StylesConfig } from 'react-select';
import tw from 'twin.macro';
import { OptionType, SelectVariant, Value } from './types';

export function makeStyles<T extends Value, M extends boolean = false>(
    variant: SelectVariant = 'normal'
): StylesConfig<OptionType<T>, M> {
    if (variant === 'compact') {
        return {
            control: (provided) => ({
                ...provided,
                ...tw`text-sm`,
                margin: '0px',
                padding: '1px',
                minHeight: '0px',
            }),
            valueContainer: (provided) => ({
                ...provided,
                margin: '0px',
                padding: '0px',
            }),
            singleValue: (provided) => ({
                ...provided,
                position: 'static',
                top: 'auto',
                left: 'auto',
                transform: 'none',
                maxWidth: 'none',
            }),
            indicatorsContainer: (provided) => ({
                ...provided,
                margin: '0px',
                padding: '0px',
            }),
            indicatorSeparator: (provided) => ({
                ...provided,
                marginTop: '0px',
                marginBottom: '0px',
            }),
            dropdownIndicator: (provided) => ({
                ...provided,
                margin: '0px',
                padding: '0px',
            }),
            input: (provided) => ({ ...provided, margin: '0px', padding: '0px' }),
            menuPortal: (provided) => ({
                ...provided,
                zIndex: 9999,
            }),
            menu: (provided) => ({ ...provided, zIndex: 9999 }),
        };
    }
    if (variant === 'inline') {
        return {
            container: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 text-sm`,
            }),
            control: (provided, state) => ({
                ...provided,

                ...tw`
                    min-h-0 min-w-0
                    m-0 p-0
                    border-none rounded-none hover:border-none focus:border-none
                    shadow-none hover:shadow-none focus:border-none
                    bg-transparent
                `,
                ...(state.isFocused && tw`bg-white ring-blue-500 ring-1 ring-inset`),
            }),
            valueContainer: (provided) => ({
                ...provided,
                ...tw`m-0 py-0 px-1 min-w-0 min-h-0`,
            }),
            singleValue: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            placeholder: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 text-gray-400`,
            }),
            indicatorsContainer: (provided) => ({
                ...provided,
                ...tw`hidden`,
            }),
            input: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            menuPortal: (provided) => ({
                ...provided,
                zIndex: 9999,
            }),
            menu: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 rounded-none w-auto min-w-full`,
            }),
            menuList: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            option: (provided, state) => ({
                ...provided,
                ...tw`m-0 px-1 py-0 w-auto h-5 truncate max-w-xs overflow-hidden text-sm`,
                ...(state.isFocused && tw`bg-gray-100`),
                ...(state.isSelected && tw`bg-blue-500`),
            }),
        };
    }
    if (variant === 'inset') {
        return {
            container: (provided, state) => ({
                ...provided,
                ...tw`relative w-full h-full m-0 p-0 text-sm text-midnight-600`,
                visibility: state.isDisabled ? 'hidden' : 'visible',
                textAlign: 'inherit',
            }),
            control: (provided, state) => ({
                ...provided,
                ...tw`
                    flex flex-row items-center
                    h-full w-full min-h-0
                    m-0 p-0
                    border-none rounded-none hover:border-none
                    shadow-none hover:shadow-none
                    bg-transparent
                `,
                ...(state.isFocused && tw`bg-white ring-blue-500 ring-1 ring-inset`),
            }),
            valueContainer: (provided) => ({
                ...provided,
                ...tw`p-0 flex-grow m-0 pl-1`,
            }),
            singleValue: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 top-auto left-auto transform-none`,
            }),
            placeholder: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 top-auto left-auto transform-none text-gray-400`,
            }),
            input: (provided) => ({
                ...provided,
                ...tw`m-0 p-0 outline-none bg-transparent`,
            }),
            menuPortal: (provided) => ({
                ...provided,
                zIndex: 9999,
            }),
            menu: (provided) => ({
                ...provided,
                ...tw`w-full p-0 m-0 rounded-none text-sm`,
            }),
            menuList: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            option: (provided, state) => ({
                ...provided,
                ...tw`m-0 px-1 py-0.5 h-6`,
                ...(state.isFocused && tw`bg-gray-100`),
                ...(state.isSelected && tw`bg-blue-500`),
            }),
            indicatorSeparator: (provided, state) => ({
                ...provided,
                ...tw`m-0 p-0 bg-gray-300`,
                ...(state.isFocused && tw`bg-blue-500`),
            }),
            indicatorsContainer: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            clearIndicator: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
            dropdownIndicator: (provided) => ({
                ...provided,
                ...tw`m-0 p-0`,
            }),
        };
    }

    return {
        container: (provided) => ({
            ...provided,
            ...tw`text-midnight-600 text-sm p-0 m-0`,
        }),
        control: (provided, state) => ({
            ...provided,
            ...tw`
                m-0 px-0 py-0 min-h-0
                shadow-none hover:shadow-none
                bg-white
            `,
            ...(state.isFocused && tw`border border-blue-500 hover:border-blue-500`),
        }),
        valueContainer: (provided) => ({
            ...provided,
            ...tw`m-0 py-1 px-1`,
        }),
        singleValue: (provided) => ({
            ...provided,
            ...tw`m-0 p-0 top-auto left-auto transform-none`,
        }),
        placeholder: (provided) => ({
            ...provided,
            ...tw`m-0 p-0 top-auto left-auto transform-none text-gray-400`,
        }),

        input: (provided) => ({
            ...provided,
            ...tw`m-0 p-0 outline-none bg-transparent`,
        }),
        indicatorSeparator: (provided, state) => ({
            ...provided,
            ...tw`m-0 p-0 bg-gray-300`,
            ...(state.isFocused && tw`bg-blue-500`),
        }),
        dropdownIndicator: (provided) => ({
            ...provided,
            ...tw`m-0 p-0.5`,
        }),
        menuPortal: (provided) => ({
            ...provided,
            zIndex: 9999,
        }),
        menu: (provided) => ({
            ...provided,
            ...tw`w-full p-0 mt-0.5 text-sm overflow-x-auto`,
        }),
        menuList: (provided) => ({
            ...provided,
            ...tw`w-max min-w-full m-0 p-0`,
        }),
        option: (provided, state) => ({
            ...provided,
            ...tw`m-0 px-1 py-1 w-auto`,
            ...(state.isFocused && tw`bg-gray-100`),
            ...(state.isSelected && tw`bg-blue-500`),
        }),
    };
}
