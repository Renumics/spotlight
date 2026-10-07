/**
 * The indices without repeats, in the order of their first occurrence.
 */
export const uniqueIndices = (indices: ArrayLike<number>): Int32Array => {
    const seen = new Set<number>();
    const unique: number[] = [];
    for (let position = 0; position < indices.length; position++) {
        const index = indices[position];
        if (!seen.has(index)) {
            seen.add(index);
            unique.push(index);
        }
    }
    return Int32Array.from(unique);
};
