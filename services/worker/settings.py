import pathlib
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = pathlib.Path(__file__).parents[2] / ".env"
load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    # DB
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"

    # Scheduler
    scheduler_poll_seconds: int = 10

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_host}/{self.postgres_db}"
            f"?user={self.postgres_user}&password={self.postgres_password}"
        )


settings = Settings()
