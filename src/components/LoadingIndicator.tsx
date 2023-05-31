import useTimeout from '../hooks/useTimeout';
import { useCallback, useState } from 'react';
import tw from 'twin.macro';
import Spinner from './ui/Spinner';

const layoutStyle = tw`relative flex items-center justify-center h-full w-full`;

interface Props {
    delay?: number;
}

const LoadingIndicator = ({ delay = 0 }: Props): JSX.Element => {
    const [visible, setVisible] = useState(!delay);
    const show = useCallback(() => setVisible(true), []);
    useTimeout(show, delay);

    return (
        <div css={[layoutStyle, !visible && tw`invisible`]}>
            <Spinner tw="w-16 h-16 transition" />
        </div>
    );
};

export default LoadingIndicator;
