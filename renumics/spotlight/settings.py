"""
global settings (read from env)
"""

from ipaddress import ip_network

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Spotlight settings module
    settings will be loaded from env variables or .env file
    """

    dev: bool = False
    verbose: bool = False
    opt_out: bool = False
    opt_in: bool = False
    layout: str | None = None

    allowed_internal_networks: list[str] = []

    @field_validator("allowed_internal_networks")
    @classmethod
    def validate_allowed_internal_networks(cls, values: list[str]) -> list[str]:
        """Internal media servers must be explicitly allowed by IP or CIDR."""
        return list(dict.fromkeys(str(ip_network(value)) for value in values))

    model_config = SettingsConfigDict(env_prefix="spotlight_")


settings = Settings()
