import { useDataset } from '../stores/dataset';
import { useLayout } from '../stores/layout';
import { IndexArray } from '../types';
import { v4 as uuidv4 } from 'uuid';

export const umapMetricNames = [
    'euclidean',
    'standardized euclidean',
    'robust euclidean',
    'cosine',
    'mahalanobis',
] as const;

export type UmapMetric = typeof umapMetricNames[number];

export const pcaNormalizations = ['none', 'standardize', 'robust standardize'] as const;

export type PCANormalization = typeof pcaNormalizations[number];

interface ReductionResult {
    points: [number, number][];
    indices: IndexArray;
}

const MAX_QUEUED_MESSAGES = 16;

class Connection {
    url: string;
    socket?: WebSocket;
    messageQueue: string[];
    onmessage?: (data: unknown) => void;

    constructor(host: string, port: string) {
        this.messageQueue = [];
        if (globalThis.location.protocol === 'https:') {
            this.url = `wss://${host}:${port}/api/ws`;
        } else {
            this.url = `ws://${host}:${port}/api/ws`;
        }
        this.#connect();
    }

    send(message: unknown): void {
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

export class DataService {
    connection: Connection;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dispatchTable: Map<string, (message: any) => void>;

    constructor(host: string, port: string) {
        this.connection = new Connection(host, port);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.connection.onmessage = (message: any) => {
            if (message.uid) {
                this.dispatchTable.get(message.uid)?.(message);
                return;
            }
            if (message.type === 'refresh') {
                useDataset.getState().refresh();
            } else if (message.type === 'resetLayout') {
                useLayout.getState().reset();
            }
        };
        this.dispatchTable = new Map();
    }

    async computeUmap(
        widgetId: string,
        columnNames: string[],
        indices: IndexArray,
        n_neighbors: number,
        metric: UmapMetric,
        min_dist: number
    ): Promise<ReductionResult> {
        const messageId = uuidv4();

        const promise = new Promise<ReductionResult>((resolve) => {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            this.dispatchTable.set(messageId, (message: any) => {
                const result = {
                    points: message.data.points,
                    indices: message.data.indices,
                };
                resolve(result);
            });
        });

        this.connection.send({
            type: 'umap',
            widget_id: widgetId,
            uid: messageId,
            generation_id: useDataset.getState().generationID,
            data: {
                indices: Array.from(indices),
                columns: columnNames,
                n_neighbors: n_neighbors,
                metric: metric,
                min_dist: min_dist,
            },
        });

        return promise;
    }

    async computePCA(
        widgetId: string,
        columnNames: string[],
        indices: IndexArray,
        pcaNormalization: PCANormalization
    ): Promise<ReductionResult> {
        const messageId = uuidv4();

        const promise = new Promise<ReductionResult>((resolve) => {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            this.dispatchTable.set(messageId, (message: any) => {
                const result = {
                    points: message.data.points,
                    indices: message.data.indices,
                };
                resolve(result);
            });
        });

        this.connection.send({
            type: 'pca',
            widget_id: widgetId,
            uid: messageId,
            generation_id: useDataset.getState().generationID,
            data: {
                indices: Array.from(indices),
                columns: columnNames,
                normalization: pcaNormalization,
            },
        });

        return promise;
    }
}

const dataService = new DataService(
    globalThis.location.hostname,
    globalThis.location.port
);

export default dataService;
