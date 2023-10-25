import { useDataset } from '../lib';
import websocketService, { WebsocketService } from './websocket';

interface ResponseHandler {
    resolve: (result: unknown) => void;
    reject: (error: unknown) => void;
}

// service handling the execution of remote tasks
class TaskService {
    // dispatch table for task responses/errors
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dispatchTable: Map<string, ResponseHandler>;
    websocketService: WebsocketService;

    constructor(websocketService: WebsocketService) {
        this.dispatchTable = new Map();
        this.websocketService = websocketService;
        this.websocketService.registerMessageHandler('task.result', (message: any) => {
            this.dispatchTable.get(message.data.task_id)?.resolve(message.data.result);
        });
        this.websocketService.registerMessageHandler('task.error', (message: any) => {
            this.dispatchTable.get(message.data.task_id)?.reject(message.data.error);
        });
    }

    async run(task: string, name: string, args: unknown) {
        return new Promise<any>((resolve, reject) => {
            const task_id = crypto.randomUUID();
            this.dispatchTable.set(task_id, { resolve, reject });
            websocketService.send({
                type: 'task',
                data: {
                    task: task,
                    widget_id: name,
                    task_id,
                    generation_id: useDataset.getState().generationID,
                    args,
                },
            });
        });
    }
}

const taskService = new TaskService(websocketService);
export default taskService;
