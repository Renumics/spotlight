import { useCallback, useEffect, useState } from 'react';

const useKeyPressed = (key: string): boolean => {
    const [isKeyPressed, setIsKeyPressed] = useState(false);

    const onKeyEvent = useCallback(
        (e: KeyboardEvent) => {
            if (e.key === key) setIsKeyPressed(e.type === 'keydown');
        },
        [key]
    );

    useEffect(() => {
        document.addEventListener('keydown', onKeyEvent);
        document.addEventListener('keyup', onKeyEvent);

        return () => {
            document.removeEventListener('keydown', onKeyEvent);
            document.removeEventListener('keyup', onKeyEvent);
        };
    }, [onKeyEvent]);

    return isKeyPressed;
};

export default useKeyPressed;
