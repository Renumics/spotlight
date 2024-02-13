import application from '../application';
import { FilebrowserApi, LayoutApi, PluginsApi, TableApi, IssuesApi } from '../client';
import { Configuration } from '../client/runtime';
import { parseError } from './errors';

const config = new Configuration({ basePath: application.apiUrl });

export default {
    table: new TableApi(config),
    filebrowser: new FilebrowserApi(config),
    layout: new LayoutApi(config),
    plugin: new PluginsApi(config),
    issues: new IssuesApi(config),
    parseError,
};
