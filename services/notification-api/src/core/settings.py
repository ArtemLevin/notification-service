import os
from typing import List, Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    environment: Literal["development", "test", "staging", "production"] = "development"

    app_name: str = "Auth Service"
    debug: bool = False
    api_v1_str: str = "/api/v1"

    log_level: str = "INFO"
    log_json_format: bool = False

    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = ["*"]


settings = Settings()

if __name__ == "__main__":
    print(settings.model_dump(exclude={"jwt_secret_key", "jwt_refresh_secret_key"}))
