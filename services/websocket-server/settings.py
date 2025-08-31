import os
import pathlib
import hmac
import hashlib
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = pathlib.Path(__file__).parents[2] / ".env"
load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"

    websocket_secret: str = os.getenv("WEBSOCKET_SECRET", "dev-secret")

    def sign(self, user_id: str) -> str:
        return hmac.new(self.websocket_secret.encode(), user_id.encode(), hashlib.sha256).hexdigest()


settings = Settings()
