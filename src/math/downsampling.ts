import _ from 'lodash';
import { Vec2 } from '../types';

export function largestTriangleThreeBuckets(
    data: Vec2[],
    numberOfPoints: number
): Vec2[] {
    if (data === undefined || data.length <= 0) return [];

    // calculate number of buckets with respect to start and end
    const bucketSize = (data.length - 2) / (numberOfPoints - 1);

    if (bucketSize <= 1) return data;

    const sampled: Vec2[] = [];
    // always add first point
    sampled.push(data[0]);

    for (let i = 0; i < numberOfPoints - 2; i++) {
        // start is minimum 1 because 0 is already in the sample
        const bucketStart = Math.max(1, Math.floor(i * bucketSize));
        const bucketEnd = Math.floor((i + 1) * bucketSize);
        const nextBucketEnd = Math.floor((i + 2) * bucketSize);

        // get average of next bucket and x from end of bucket
        const avgNextBucket: Vec2 = [
            _.meanBy(data.slice(bucketEnd, nextBucketEnd), ([, y]) => y),
            data[bucketEnd][0],
        ];
        // get last added bucket
        const bestLastBucket = sampled[i];

        // compute area between lastBestPoint, every point in this bucket and avgNextBucket
        const triangleAreas = data
            .slice(bucketStart, bucketEnd)
            .map(([x, y]) =>
                Math.abs(
                    (bestLastBucket[0] * (y - avgNextBucket[1]) +
                        x * (avgNextBucket[1] - bestLastBucket[1]) +
                        avgNextBucket[0] * (bestLastBucket[1] - y)) *
                        0.5
                )
            );

        // get index of point with last area
        const maxAreaIndex = triangleAreas.reduce(
            (prev, cur, index) => (prev.value < cur ? { index, value: cur } : prev),
            { index: -1, value: -Infinity }
        ).index;

        sampled.push(data[bucketStart + maxAreaIndex]);
    }
    sampled.push(data[data.length - 1]);
    return sampled;
}
