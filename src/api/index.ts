import application from '../application';
import {
    FilebrowserApi,
    LayoutApi,
    PluginsApi,
    TableApi,
    ProblemsApi,
} from '../client';
import { Configuration } from '../client/runtime';

const config = new Configuration({ basePath: application.apiUrl });

export default {
    table: new TableApi(config),
    filebrowser: new FilebrowserApi(config),
    layout: new LayoutApi(config),
    plugin: new PluginsApi(config),
    problems: new ProblemsApi(config),
};
