import { notifyProblem } from '../../notify';
import Connection from './connection';
import { Message, MessageHandler } from './types';

// this service provides a websocket connection to the service
// and handles incoming and outgoing messages
export class WebsocketService {
    connection: Connection;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    messageHandlers: Map<string, MessageHandler>;

    constructor(host: string, port: string) {
        this.messageHandlers = new Map();
        this.connection = new Connection(host, port);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.connection.onmessage = (message: any) => {
            const messageHandler = this.messageHandlers.get(message.type);
            if (messageHandler) {
                messageHandler(message);
            } else {
                console.error(`Unknown websocket message: ${message.type}`);
            }
        };
    }

    registerMessageHandler(messageType: string, handler: MessageHandler): void {
        this.messageHandlers.set(messageType, handler);
    }

    send(message: Message): void {
        this.connection.send(message);
    }
}

const websocketService = new WebsocketService(
    globalThis.location.hostname,
    globalThis.location.port
);

websocketService.registerMessageHandler('error', (message: Message) => {
    notifyProblem(message.data);
});

export default websocketService;
