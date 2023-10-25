export interface Message {
    type: string;
    data: any;
}

export type MessageHandler = (message: Message) => void;
