import AddWidgetIcon from '../../icons/Add';
import Dropdown, { DropdownContext } from '../ui/Dropdown';
import { Widget } from '../../widgets/types';
import { widgets } from '../../widgets/WidgetFactory';
import { useContext } from 'react';
import 'twin.macro';
import AddWidgetButton from './AddWidgetButton';

interface Props {
    addWidget: (widget: Widget) => void;
}

const Content = ({ addWidget }: Props) => {
    const dropdown = useContext(DropdownContext);

    return (
        <div tw="flex flex-col space-y-2 p-1">
            {widgets.map((widget) => (
                <AddWidgetButton
                    name={widget.defaultName}
                    key={widget.key}
                    icon={widget.icon}
                    onClick={() => {
                        dropdown.hide();
                        addWidget(widget);
                    }}
                    experimental={widget.key.startsWith('experimental/')}
                />
            ))}
        </div>
    );
};

const AddWidgetDropdown = ({ addWidget }: Props): JSX.Element => {
    return (
        <Dropdown
            key="add"
            tooltip="Add Widget"
            content={<Content addWidget={addWidget} />}
        >
            <AddWidgetIcon tw="w-4 h-4" data-tour="addWidget" />
        </Dropdown>
    );
};

export default AddWidgetDropdown;
