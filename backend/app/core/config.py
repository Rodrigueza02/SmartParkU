
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "8883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "Juliana")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "1138524566Juli*")

    class Config:
        env_file = ".env"


settings = Settings()

