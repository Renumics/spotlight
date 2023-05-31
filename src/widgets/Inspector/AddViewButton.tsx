import AddIcon from '../../icons/AddCell';
import Dropdown from '../../components/ui/Dropdown';
import ViewConfigurator from './ViewConfigurator';

const AddViewButton = (): JSX.Element => {
    return (
        <Dropdown tooltip="Add View" content={<ViewConfigurator />}>
            <AddIcon data-tour="detailViewAddView" />
        </Dropdown>
    );
};

export default AddViewButton;
