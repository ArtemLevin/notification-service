import pathlib
from typing import List, Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = pathlib.Path(__file__).parents[3] / ".env"
load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    environment: Literal["development", "test", "staging", "production"] = "development"

    debug: bool = False
    api_v1_str: str = "/api/v1"

    log_level: str = "INFO"
    log_json_format: bool = False

    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = ["*"]

    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_host}/{self.postgres_db}?user={self.postgres_user}&password={self.postgres_password}"  # noqa: E501


settings = Settings()
