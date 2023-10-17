"""
global settings (read from env)
"""
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Spotlight settings module
    settings will be loaded from env variables or .env file
    """

    dev: bool = False
    verbose: bool = False
    opt_out: bool = False
    opt_in: bool = False
    layout: Optional[str] = None

    class Config:
        """
        settings config
        set env prefix to spotlight_
        """

        env_prefix = "spotlight_"


settings = Settings()
