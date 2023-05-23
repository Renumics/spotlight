import { Configuration } from '../client/runtime';
import { TableApi } from '../client';
import application from '../application';

export default new TableApi(
    new Configuration({
        basePath: application.apiUrl,
    })
);
