import ToggleButton from '../ui/ToggleButton';
import _ from 'lodash';
import {
    FunctionComponent,
    MouseEvent,
    useCallback,
    useEffect,
    useMemo,
    useState,
} from 'react';
import { IoInvertMode, IoInvertModeOutline } from 'react-icons/io5';
import tw from 'twin.macro';
import { getApplicablePredicates, hasApplicablePredicates } from '../../filters';
import { useDataset } from '../../stores/dataset';
import { Filter, Predicate, PredicateFilter, SetFilter } from '../../types';
import CheckIcon from '../../icons/Check';
import CancelIcon from '../../icons/X';
import Select from '../ui/Select';
import Button from './Button';
import ValueInput from './ValueInput';

const HorizontalDivider = tw.div`h-auto border-r border-gray-400 box-border`;

interface Props {
    filter?: Filter;
    onAccept: (filter: Filter) => void;
    onCancel: () => void;
}

interface EditorDefaultControlsProps extends Props {
    onAccept: () => void;
    canAccept?: boolean;
    isInverted?: boolean;
    setIsInverted?: (isInverted: boolean) => void;
}

const EditorDefaultControls: FunctionComponent<EditorDefaultControlsProps> = ({
    onAccept,
    onCancel,
    canAccept = true,
    isInverted,
    setIsInverted,
}) => {
    const onClickCancel = (e: MouseEvent) => {
        e.stopPropagation();
        onCancel();
    };

    const onChangeIsInverted = useCallback(
        ({ checked }: { checked: boolean }) => {
            setIsInverted?.(checked);
        },
        [setIsInverted]
    );

    return (
        <div tw="flex flex-row items-stretch">
            {setIsInverted !== undefined && (
                <>
                    <HorizontalDivider />
                    <ToggleButton
                        tooltip="Invert filter"
                        tw="max-h-full rounded-none py-0"
                        checked={isInverted}
                        onChange={onChangeIsInverted}
                    >
                        {isInverted ? <IoInvertMode /> : <IoInvertModeOutline />}
                    </ToggleButton>
                </>
            )}
            <HorizontalDivider />
            <Button
                tw="flex items-center h-full"
                onClick={onAccept}
                disabled={!canAccept}
                tooltip="Save filter"
            >
                <CheckIcon />
            </Button>
            <HorizontalDivider />
            <Button
                tw="flex items-center h-full"
                onClick={onClickCancel}
                tooltip="Cancel editing"
            >
                <CancelIcon />
            </Button>
        </div>
    );
};

interface PredicateFilterEditorProps {
    filter?: Partial<PredicateFilter>;
    onAccept: (filter: PredicateFilter) => void;
    onCancel: () => void;
}

const PredicateFilterEditor: FunctionComponent<PredicateFilterEditorProps> = ({
    filter = { kind: 'PredicateFilter' },
    onAccept,
    onCancel,
}) => {
    const [column, setColumn] = useState(filter.column);
    const [predicate, setPredicate] = useState(filter.predicate);
    const [_referenceValue, setReferenceValue] = useState<unknown>(
        filter?.referenceValue
    );

    const nullValue = column?.type.kind === 'bool' ? false : null;
    const referenceValue = _referenceValue ?? nullValue;

    const columns = useDataset((d) => d.columns);

    const filterableColumns = useMemo(
        () => columns.filter((col) => hasApplicablePredicates(col.type.kind)),
        [columns]
    );

    const applicablePredicates = useMemo(
        () => (column?.type.kind ? getApplicablePredicates(column.type.kind) : {}),
        [column?.type.kind]
    );

    useEffect(() => {
        if (!predicate && _.size(applicablePredicates) === 1) {
            setPredicate(Object.values(applicablePredicates)[0]);
        }
        if (!predicate) return;
        if (!Object.values(applicablePredicates).includes(predicate)) {
            setPredicate(undefined);
        }
    }, [applicablePredicates, predicate]);

    const handleSelectColumnName = (name?: string) => {
        const newColumn = columns.find((c) => c.name === name);
        if (newColumn?.type.kind !== column?.type.kind) {
            setReferenceValue(null);
        }
        setColumn(newColumn);
    };
    const handleSelectPredicate = (pred?: Predicate) => setPredicate(pred);

    // only allow accepting when the user selected a predicate and a column
    // also deny accepting when column is numbercolumn and referenceValue cannot be parsed to Number
    const canAccept =
        !!predicate &&
        !!column &&
        referenceValue !== undefined &&
        (column.optional || referenceValue !== null);

    // when the accept button is clicked build the current filter and call onAccept
    const onClickAccept = useCallback(() => {
        // don't do anything when predicate or column is undefined (the button should be disabled anyway)
        if (canAccept) {
            onAccept(new PredicateFilter(column, predicate, referenceValue));
        }
    }, [predicate, column, referenceValue, onAccept, canAccept]);

    const onEnter = useCallback(
        (value: unknown) => {
            if (canAccept) {
                if (!predicate || !column) return;
                onAccept(new PredicateFilter(column, predicate, value));
            }
        },
        [canAccept, column, onAccept, predicate]
    );

    const makePredicateLabel = (pred?: Predicate) => pred?.shorthand ?? 'None';
    return (
        <div tw="flex flex-row items-stretch h-auto">
            <Select
                options={filterableColumns.map((col) => col.name)}
                value={column?.name}
                // eslint-disable-next-line jsx-a11y/no-autofocus
                autoFocus={true}
                openMenuOnFocus={true}
                placeholder="column"
                onChange={handleSelectColumnName}
                variant="inline"
            />
            <HorizontalDivider />
            <Select
                options={Object.values(applicablePredicates)}
                value={predicate}
                label={makePredicateLabel}
                openMenuOnFocus={true}
                placeholder="op"
                onChange={handleSelectPredicate}
                variant="inline"
                isDisabled={_.size(applicablePredicates) === 1}
            />
            <HorizontalDivider />
            <ValueInput
                value={referenceValue}
                type={column?.type}
                placeholder="reference"
                onChange={setReferenceValue}
                onEnter={onEnter}
            />
            <EditorDefaultControls
                canAccept={canAccept}
                onAccept={onClickAccept}
                onCancel={onCancel}
            />
        </div>
    );
};

interface NamedFilterEditorProps {
    filter: SetFilter;
    onAccept: (filter: SetFilter) => void;
    onCancel: () => void;
}

const NamedFilterEditor: FunctionComponent<NamedFilterEditorProps> = ({
    filter,
    onAccept,
    onCancel,
}) => {
    const [name, setName] = useState(filter.name);
    const [isInverted, setIsInverted] = useState(filter.isInverted);
    // only allow accepting when the user selected a column
    const canAccept = !!name;

    // when the accept button is clicked build the current filter and call onAccept
    const onClickAccept = useCallback(() => {
        // don't do anything when name is undefined (the button should be disabled anyway)
        if (!name) return;

        onAccept(Object.assign(new SetFilter([], ''), filter, { name, isInverted }));
    }, [name, onAccept, filter, isInverted]);

    const onEnter = useCallback(
        (name: unknown) => {
            if (!name) return;
            onAccept(
                Object.assign(new SetFilter([], ''), filter, { name, isInverted })
            );
        },
        [filter, isInverted, onAccept]
    );

    return (
        <div tw="flex flex-row items-stretch">
            <ValueInput
                value={name}
                type={{ kind: 'str', optional: true, binary: false, lazy: true }}
                placeholder="name"
                onChange={setName}
                onEnter={onEnter}
            />
            <EditorDefaultControls
                canAccept={canAccept}
                onAccept={onClickAccept}
                onCancel={onCancel}
                isInverted={isInverted}
                setIsInverted={setIsInverted}
            />
        </div>
    );
};

const FilterEditor: FunctionComponent<Props> = ({ filter, onAccept, onCancel }) => {
    return (
        <>
            {filter === undefined || filter.kind === 'PredicateFilter' ? (
                <PredicateFilterEditor
                    filter={filter as undefined | PredicateFilter}
                    onAccept={onAccept}
                    onCancel={onCancel}
                />
            ) : (
                filter.kind === 'SetFilter' && (
                    <NamedFilterEditor
                        filter={filter as SetFilter}
                        onAccept={onAccept}
                        onCancel={onCancel}
                    />
                )
            )}
        </>
    );
};

export default FilterEditor;
