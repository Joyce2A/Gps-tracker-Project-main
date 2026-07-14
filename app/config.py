# from pydantic import BaseSettings


# class Settings(BaseSettings):
#     MONGO_URI: str = "mongodb://localhost:27017"
#     DB_NAME: str = "gps_tracker"
#     JWT_SECRET: str = "1khmsGIDTZD7CiH7NmbttVAv_b3Ry2zwsuc1XF8ugCM"
#     JWT_ALGORITHM: str = "HS256"
#     JWT_EXP_MINUTES: int = 60
#     # Email settings (loaded from .env)
#     EMAIL_HOST: str = "smtp.gmail.com"
#     EMAIL_PORT: int = 587
#     EMAIL_USERNAME: str | None = None
#     EMAIL_PASSWORD: str | None = None
#     EMAIL_FROM: str | None = None
#     EMAIL_FROM_NAME: str | None = None
#     MAIL_TLS: bool = True
#     MAIL_SSL: bool = False


#     class Config:
#         env_file = ".env"


# settings = Settings()


from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    MONGO_URI: str
    DB_NAME: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_MINUTES: int = 60

    # Email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str

    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # RESEND
    RESEND_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# 🔍 TEMP DEBUG – remove after testing
# print("EMAIL USER:", settings.EMAIL_USERNAME)
# print("EMAIL HOST:", settings.EMAIL_HOST)
