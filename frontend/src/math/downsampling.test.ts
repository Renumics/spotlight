import { Vec2 } from '../types';
import { largestTriangleThreeBuckets } from './downsampling';

it('get mean for x=y', () => {
    const data: Vec2[] = Array.from(Array(100).keys()).map((x) => [x, x]);
    const reduced: Vec2[] = [
        [0, 0],
        [9, 9],
        [20, 20],
        [31, 31],
        [42, 42],
        [53, 53],
        [64, 64],
        [75, 75],
        [86, 86],
        [99, 99],
    ];
    expect(largestTriangleThreeBuckets(data, 10)).toEqual(reduced);
});

it('test more points than in chart', () => {
    const data: Vec2[] = [
        [1, 2],
        [5, 2],
        [6, 6],
    ];
    expect(largestTriangleThreeBuckets(data, 10)).toEqual(data);
});

it('select 0 points', () => {
    const data: Vec2[] = [
        [1, 2],
        [5, 2],
        [6, 6],
    ];
    expect(largestTriangleThreeBuckets(data, 0)).toEqual(data);
});
