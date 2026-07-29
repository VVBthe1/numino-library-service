from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "library-service"
    app_env: str = "development"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/neighborhood_library"
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051


@lru_cache
def get_settings() -> Settings:
    return Settings()
