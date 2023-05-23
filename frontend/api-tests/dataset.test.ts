import fetch from 'node-fetch';
import { TableApi } from '../src/client';
import { Configuration } from '../src/client/runtime';

const apiConfig = new Configuration({
    basePath: process.env.BACKEND_BASE_URL || 'http://localhost:5000',
    fetchApi: fetch as unknown as WindowOrWorkerGlobalScope['fetch'],
});

export const tableApi = new TableApi(apiConfig);

const waitForApp = async () => {
    const maxTries = 20;
    for (let tries = 0; tries < maxTries; tries++) {
        try {
            let table = await tableApi.getTable();
            console.log('Server online, starting test suite...');
            return;
        } catch (error) {
            console.log(error);
            await new Promise((resolve) => setTimeout(resolve, 2000));
        }
    }
    throw new Error('Server not responding');
};

beforeAll(async () => {
    await waitForApp();
});

test('can get table slices', async () => {
    let table = await tableApi.getTable();
});
