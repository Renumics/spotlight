import { Problem } from '../types';
import websocketService, { WebsocketService } from './websocket';

interface ChatResponse {
    chat_id: string;
    message: string;
}

interface ChatError {
    chat_id: string;
    type: string;
    title: string;
    detail: string;
}

interface ChatHandler {
    resolve: (message: string) => void;
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
                this.dispatchTable.get(data.chat_id)?.resolve(data.message);
            }
        );
        this.websocketService.registerMessageHandler(
            'chat.error',
            (data: ChatError) => {
                this.dispatchTable.get(data.chat_id)?.reject(data);
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

        let msg = '';
        do {
            const promise = new Promise<string>((resolve, reject) => {
                this.dispatchTable.set(chat_id, { resolve, reject });
            });
            msg = await promise;
            yield msg;
        } while (msg !== '');
    }
}

const chatService = new ChatService(websocketService);
export default chatService;
