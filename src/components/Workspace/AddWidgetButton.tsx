import Button from '../ui/Button';
import Tag from '../ui/Tag';
import type { IconType } from 'react-icons';
import 'twin.macro';

interface Props {
    name: string;
    icon: IconType;
    experimental?: boolean;
    onClick: () => void;
}

const AddWidgetButton = ({
    name,
    icon,
    experimental = false,
    onClick,
}: Props): JSX.Element => {
    const Icon = icon;

    return (
        <Button onClick={onClick}>
            <div tw="overflow-hidden flex flex-row space-x-1 items-center w-full">
                <div tw="w-8 h-8 bg-midnight-600 hover:bg-blue-600 text-gray-100 rounded p-0.5">
                    <Icon style={{ width: '100%', height: '100%' }} />
                </div>
                <div tw="font-normal text-sm">{name}</div>
                {experimental && <Tag tw="text-xxs" tag="experimental" />}
            </div>
        </Button>
    );
};

export default AddWidgetButton;
