import FilterIcon from '../../icons/Filter';
import Tooltip from '../ui/Tooltip';
import { FunctionComponent, useCallback, useState } from 'react';
import { useDataset } from '../../stores/dataset';
import 'twin.macro';
import { Filter } from '../../types';
import Button from './Button';
import FilterEditor from './FilterEditor';

const FilterCreator: FunctionComponent = () => {
    const [inEditMode, setInEditMode] = useState(false);
    const addFilter = useDataset((d) => d.addFilter);

    const onEdit = useCallback(() => {
        if (!inEditMode) setInEditMode(true);
    }, [inEditMode]);
    const onCancel = () => {
        setInEditMode(false);
    };
    const onAccept = (filter: Filter) => {
        addFilter(filter);
        setInEditMode(false);
    };

    return (
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events,jsx-a11y/no-static-element-interactions
        <div onClick={onEdit}>
            {inEditMode ? (
                <FilterEditor onAccept={onAccept} onCancel={onCancel} />
            ) : (
                <Tooltip content="Create filter from column">
                    <Button onClick={onEdit}>
                        +<FilterIcon />
                    </Button>
                </Tooltip>
            )}
        </div>
    );
};

export default FilterCreator;
