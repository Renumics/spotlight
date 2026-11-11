"""
global settings (read from env)
"""

from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_origin(value: str) -> str:
    """Validate an HTTP origin and normalize its hostname and default port."""
    if not value.isascii():
        raise ValueError(
            "Origins must be ASCII; use punycode for internationalized hostnames"
        )
    if any(char.isspace() for char in value) or any(char in value for char in "*\\%"):
        raise ValueError("Origins must be full HTTP(S) origins without wildcards")
    parsed = urlsplit(value)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or parsed.netloc.endswith(":")
    ):
        raise ValueError(
            "Origins must contain only a scheme, hostname and optional port"
        )
    hostname = parsed.hostname.lower()
    if ":" in hostname:
        hostname = f"[{hostname}]"
    port = parsed.port
    default_port = 443 if parsed.scheme == "https" else 80
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{parsed.scheme}://{hostname}{suffix}"


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
    allowed_origins: list[str] = []
    csp_report_only: bool = False
    csp_script_origins: list[str] = []
    csp_connect_origins: list[str] = []

    @field_validator("allowed_origins", "csp_script_origins", "csp_connect_origins")
    @classmethod
    def validate_allowed_origins(cls, values: list[str]) -> list[str]:
        """Reject ambiguous origins and fail early on invalid configuration."""
        return list(dict.fromkeys(normalize_origin(value) for value in values))

    model_config = SettingsConfigDict(env_prefix="spotlight_")


settings = Settings()
