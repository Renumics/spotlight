export interface Message {
    type: string;
    data: unknown;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type MessageHandler = (data: any) => void;
