import application from '../application';
import { ConfigApi, Configuration } from '../client';

type ConfigValue = number | string | boolean | Record<string, unknown>;

export class ConfigService {
    api: ConfigApi;

    constructor() {
        let apiBasePath = application.apiUrl;
        apiBasePath = apiBasePath ?? application.publicUrl;
        const apiConfig = new Configuration({ basePath: apiBasePath });

        this.api = new ConfigApi(apiConfig);
    }

    async get<T>(name: string): Promise<T> {
        return (await this.api.getValue({ name })) as T;
    }
    async getItem<T>(name: string): Promise<T> {
        return this.get<T>(name);
    }

    async set<T>(name: string, value: T) {
        await this.api.setValue({
            name,
            setConfigRequest: { value: value as ConfigValue | undefined },
        });
    }
    async setItem<T>(name: string, value: T) {
        this.set<T>(name, value);
    }

    async remove(name: string) {
        await this.api.remove({ name });
    }
    async removeItem(name: string) {
        this.remove(name);
    }
}

const configService = new ConfigService();

export default configService;
