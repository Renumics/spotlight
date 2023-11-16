export type Vec2 = [number, number];

export type IndexArray = number[] | Int32Array;

export type TypedArray =
    | Int8Array
    | Uint8Array
    | Int16Array
    | Uint16Array
    | Int32Array
    | Uint32Array
    | Uint8ClampedArray
    | Float32Array
    | Float64Array;

export type Setter<T> = (value: T | ((previous: T) => T)) => void;
