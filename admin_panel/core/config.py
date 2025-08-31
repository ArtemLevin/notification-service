from pathlib import Path
from typing_extensions import Self

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from admin_panel import PROJECT_DIR


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


class PostgresConfig(ConfigBase):
    """Конфигурация PostgreSQL."""
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    user: SecretStr = Field(env="POSTGRES_USER")
    password: SecretStr = Field(env="POSTGRES_PASSWORD")
    host: str = Field(default="localhost", env="POSTGRES_HOST")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    database: str = Field(default="message", env="POSTGRES_DB")
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False

    @computed_field 
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.user.get_secret_value()}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class AdminConfig(ConfigBase):
    """Конфигурация административной панели"""
    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    login: SecretStr = Field(env="ADMIN_LOGIN")
    password: SecretStr = Field(env="ADMIN_PASSWORD")


class CommonConfig(ConfigBase):
    """Конфигурация административной панели"""
    model_config = SettingsConfigDict(env_prefix="APP_")

    port: int = Field(default=8000, env="APP_PORT")
    name: str = Field(default="Административная панель", env="APP_NAME")
    description: str = Field(default="Административная панель", env="APP_DESCRIPTION")
    app_dir: Path = PROJECT_DIR


class Config(ConfigBase):
    common: CommonConfig = CommonConfig()
    postgres: PostgresConfig = PostgresConfig()
    admin: AdminConfig = AdminConfig()
    @classmethod
    def load(cls) -> Self:
        return cls()


settings = Config().load()