"""
api settings
"""
from pydantic import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """
    Spotlight settings module
    settings will be loaded from env variables or .env file
    """

    dev: bool = False
    verbose: bool = False
    opt_out: bool = False
    opt_in: bool = False

    class Config:
        """
        settings config
        set env prefix to spotlight_
        """

        env_prefix = "spotlight_"


settings = Settings()
