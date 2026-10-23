import { uniqueIndices } from './uniqueIndices';

describe('uniqueIndices', () => {
    it('keeps indices that are all different as they are', () => {
        expect(Array.from(uniqueIndices([4, 1, 3]))).toEqual([4, 1, 3]);
        expect(Array.from(uniqueIndices(Int32Array.of(2, 0, 1)))).toEqual([2, 0, 1]);
    });
    it('removes repeats and keeps the order of the first occurrences', () => {
        expect(Array.from(uniqueIndices([2, 6, 4, 5, 6, 7, 8]))).toEqual([
            2, 6, 4, 5, 7, 8,
        ]);
        expect(Array.from(uniqueIndices([1, 1, 1]))).toEqual([1]);
    });
    it('gives no indices for none', () => {
        expect(uniqueIndices([])).toHaveLength(0);
        expect(uniqueIndices(new Int32Array())).toBeInstanceOf(Int32Array);
    });
});
