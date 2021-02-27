"""Application Settings"""
import typing
from functools import cache
from pydantic import BaseSettings

ENV_PREFIX = "MAPA_"


class Settings(BaseSettings):
    """
    Application Settings
    """

    database_url: str = "sqlite:///db.sqlite"
    listen_host: str = "127.0.0.1"
    listen_port: int = 8000
    verbose: bool = True
    serve_static: typing.Optional[str] = None
    media_base: str = "media/"

    class Config:
        """
        Settings config -- read environment variables
        """
        env_prefix = ENV_PREFIX


# create settings instance
settings = Settings()


@cache
def get(name, fb=None):
    """Get settings or return fallback value."""
    return settings.__dict__.get(name, fb)
