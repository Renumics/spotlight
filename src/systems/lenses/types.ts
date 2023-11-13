export interface Setting<T = unknown> {
    value: T;
}
export type Settings = Record<string, Setting>;
