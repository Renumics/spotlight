import { useContext } from 'react';
import { SortingContext } from '../context/sortingContext';

function useRowCount(): number {
    const { sortedIndices } = useContext(SortingContext);
    return sortedIndices.length;
}

export default useRowCount;
