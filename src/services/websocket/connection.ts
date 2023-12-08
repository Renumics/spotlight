// the maximum number of outgoing messages that are queued,
import { Message } from './types';

// while the connection is down
const MAX_QUEUED_MESSAGES = 16;

// a websocket connection to the spotlight backend
// automatically reconnects when necessary
class Connection {
    url: string;
    socket?: WebSocket;
    messageQueue: string[];
    onmessage?: (data: unknown) => void;

    constructor(host: string, port: string, basePath: string) {
        this.messageQueue = [];
        const protocol = globalThis.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.url = `${protocol}//${host}:${port}${basePath}api/ws`;
        this.#connect();
    }

    send(message: Message): void {
        const data = JSON.stringify(message);
        if (this.socket) {
            this.socket.send(data);
        } else {
            if (this.messageQueue.length > MAX_QUEUED_MESSAGES) {
                this.messageQueue.shift();
            }
            this.messageQueue.push(data);
        }
    }

    #connect() {
        const webSocket = new WebSocket(this.url);

        webSocket.onopen = () => {
            this.socket = webSocket;
            this.messageQueue.forEach((message) => this.socket?.send(message));
            this.messageQueue.length = 0;
        };
        webSocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.onmessage?.(message);
        };
        webSocket.onerror = () => {
            webSocket.close();
        };
        webSocket.onclose = () => {
            this.socket = undefined;
            setTimeout(() => {
                this.#connect();
            }, 500);
        };
    }
}

export default Connection;
