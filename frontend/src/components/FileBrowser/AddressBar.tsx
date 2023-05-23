import UpIcon from '../../icons/Up';
import Button from '../ui/Button';
import { Fragment, MouseEvent, useCallback } from 'react';
import 'twin.macro';

interface Props {
    path: string;
    parent?: string;
    setPath: (path: string) => void;
}

const AddressBar = ({ path, parent, setPath }: Props): JSX.Element => {
    const formattedPath = path === '.' ? '' : path;
    const pathSegments = formattedPath.split('/');
    const subPaths = pathSegments.map((_, i) => pathSegments.slice(0, i + 1).join('/'));

    const handleSubPathClick = useCallback(
        (event: MouseEvent<HTMLDivElement>) => {
            const path = event.currentTarget.getAttribute('data-path');
            if (path) setPath(path);
        },
        [setPath]
    );

    const gotoParent = () => parent && setPath(parent);

    return (
        <div tw="flex flex-row items-center p-1 border-b border-gray-400">
            <Button onClick={gotoParent} disabled={!parent}>
                <UpIcon />
            </Button>
            <div tw="px-1 flex-grow rounded outline-none mr-1">
                {pathSegments.map((s, i) => (
                    <Fragment key={subPaths[i]}>
                        <span tw="px-px text-gray-700">/</span>
                        {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events,jsx-a11y/no-static-element-interactions */}
                        <span
                            tw="last:font-bold cursor-pointer hover:text-blue-600"
                            onClick={handleSubPathClick}
                            data-path={subPaths[i]}
                        >
                            {s}
                        </span>
                    </Fragment>
                ))}
            </div>
        </div>
    );
};

export default AddressBar;
