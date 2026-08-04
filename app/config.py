# ------- IMPORTS -------
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ------- CLASSES -------
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = False
    )

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

# ------- SETUP -------
settings = Settings()