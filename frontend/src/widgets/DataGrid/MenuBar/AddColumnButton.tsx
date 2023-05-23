import AddColumnIcon from '../../../icons/AddBox';
import { FunctionComponent } from 'react';
import 'twin.macro';
import NeedsUpgradeButton from '../../../components/ui/NeedsUpgradeButton';

const AddColumnButton: FunctionComponent = () => {
    return (
        <div data-test-tag="datagrid-add-column-button">
            <NeedsUpgradeButton>
                <AddColumnIcon />
            </NeedsUpgradeButton>
        </div>
    );
};

export default AddColumnButton;
