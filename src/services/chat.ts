import { Problem } from '../types';
import websocketService, { WebsocketService } from './websocket';

export interface Message {
    content: string;
    role: string;
    content_type?: string;
    done?: boolean;
}

interface ChatResponse {
    chat_id: string;
    message?: Message;
    done?: boolean;
}

interface ChatError {
    chat_id: string;
    error: Problem;
}

interface ChatHandler {
    resolve: (message: ChatResponse) => void;
    reject: (error: Problem) => void;
}

// service handling the execution of remote tasks
class ChatService {
    // dispatch table for chat responses/errors
    dispatchTable: Map<string, ChatHandler>;
    websocketService: WebsocketService;

    constructor(websocketService: WebsocketService) {
        this.dispatchTable = new Map();
        this.websocketService = websocketService;
        this.websocketService.registerMessageHandler(
            'chat.response',
            (data: ChatResponse) => {
                this.dispatchTable.get(data.chat_id)?.resolve(data);
            }
        );
        this.websocketService.registerMessageHandler(
            'chat.error',
            (data: ChatError) => {
                this.dispatchTable.get(data.chat_id)?.reject(data.error);
            }
        );
    }

    async *stream(message: string) {
        const chat_id = crypto.randomUUID();
        websocketService.send({
            type: 'chat',
            data: {
                chat_id: chat_id,
                message,
            },
        });

        let response: ChatResponse;
        do {
            const promise = new Promise<ChatResponse>((resolve, reject) => {
                this.dispatchTable.set(chat_id, { resolve, reject });
            });
            response = await promise;
            if (response.message) {
                yield response.message;
            }
        } while (!response.done);
    }
}

const chatService = new ChatService(websocketService);
export default chatService;
