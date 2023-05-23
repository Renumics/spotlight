import { useContext } from 'react';
import { SortingContext } from '../context/sortingContext';

function useSort() {
    const { sortedIndices, getOriginalIndex, getSortedIndex } =
        useContext(SortingContext);
    return { sortedIndices, getOriginalIndex, getSortedIndex };
}

export default useSort;
