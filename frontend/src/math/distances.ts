function bhattacharyya(a: number[], b: number[]): number {
    const len = a.length;
    let total = 0;
    for (let i = 0; i < len; i++) {
        total += Math.sqrt(a[i] * b[i]);
    }
    return -Math.log(total);
}

const exports = { bhattacharyya };
export default exports;
