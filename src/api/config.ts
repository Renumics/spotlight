import application from '../application';
import { Configuration } from '../client/runtime';

export const config = new Configuration({ basePath: application.apiUrl });
