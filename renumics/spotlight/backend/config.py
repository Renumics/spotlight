"""
Spotlight Frontend Configuration
"""
import json
from typing import Dict, Union, cast, Optional

from databases import Database

from renumics.spotlight import appdirs

ConfigValue = Union[Dict, str, int, float, bool]


class Config:
    """
    Configuration object that stores key value pairs in an sqlite db on disk.
    """

    def __init__(self) -> None:
        appdirs.config_dir.mkdir(parents=True, exist_ok=True)
        db_path = appdirs.config_dir / "config.db"
        db_url = f"sqlite:///{db_path}"
        self.database = Database(db_url)
        self.connected = False

    async def _lazy_init(self) -> None:
        """
        lazy initialization function
        """
        if not self.connected:
            await self.database.connect()
            query = """
            CREATE TABLE IF NOT EXISTS entries (
                name TEXT NOT NULL,
                value JSON NOT NULL,
                user TEXT,
                dataset TEXT,
                PRIMARY KEY (name, user, dataset)
            )
            """
            await self.database.execute(query)
            self.connected = True

    async def get(self, name: str, *, dataset: str = "") -> Optional[ConfigValue]:
        """
        get a stored value by name
        """
        await self._lazy_init()

        query = """
        SELECT value FROM entries
        WHERE name = :name AND user = :user AND dataset = :dataset
        """

        row = await self.database.fetch_one(
            query, {"name": name, "user": "", "dataset": dataset}
        )
        if not row:
            return None
        value = json.loads(row[0])
        return cast(ConfigValue, value)

    async def set(self, name: str, value: ConfigValue, *, dataset: str = "") -> None:
        """
        set a config value by name
        """
        await self._lazy_init()
        values = {
            "name": name,
            "user": "",
            "dataset": dataset,
            "value": json.dumps(value),
        }
        query = """
        REPLACE INTO entries (name, value, user, dataset)
        VALUES (:name, :value, :user, :dataset)
        """
        await self.database.execute(query, values)

    async def remove(self, name: str, *, dataset: str = "") -> None:
        """
        remove a config value by name
        """
        await self._lazy_init()
        query = """
        DELETE FROM entries
        WHERE name = :name AND user = :user AND dataset = :dataset
        """
        await self.database.execute(
            query, values={"name": name, "user": "", "dataset": dataset}
        )
