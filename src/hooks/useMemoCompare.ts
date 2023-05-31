import _ from 'lodash';
import { useRef } from 'react';

function useMemoCompare<T>(value: T, isEqual: (a: T, b: T) => boolean = _.isEqual): T {
    const prevRef = useRef<T>(value);
    if (!isEqual(prevRef.current, value)) prevRef.current = value;
    return prevRef.current;
}

export default useMemoCompare;
