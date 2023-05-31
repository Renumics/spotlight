import { useEffect, useRef } from 'react';

function useWhyDidYouUpdate<T>(name: string, props: Record<string, T>): void {
    const previousProps = useRef<Record<string, T>>({});

    useEffect(() => {
        if (previousProps.current) {
            const allKeys = Object.keys({ ...previousProps.current, ...props });
            const changesObj: Record<string, { from: T; to: T }> = {};
            allKeys.forEach((key) => {
                if (previousProps.current[key] !== props[key]) {
                    changesObj[key] = {
                        from: previousProps.current[key],
                        to: props[key],
                    };
                }
            });

            if (Object.keys(changesObj).length) {
                // eslint-disable-next-line no-console
                console.log('[why-did-you-update]', name, changesObj);
            }
        }

        previousProps.current = props;
    });
}

export default useWhyDidYouUpdate;
