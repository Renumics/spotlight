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
        <Button tw="w-32" onClick={onClick}>
            <div tw="flex flex-col text-xs items-center w-full">
                <div tw="w-8 h-8">
                    <Icon style={{ width: '100%', height: '100%' }} />
                </div>
                <div>{name}</div>
                {experimental && <Tag tw="text-xxs" tag="experimental" />}
            </div>
        </Button>
    );
};

export default AddWidgetButton;
