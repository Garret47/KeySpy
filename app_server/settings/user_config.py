from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='key_spy.conf', env_file_encoding='utf-8', extra='ignore')


class ServerSettings(BaseEnvSettings):
    LISTEN_HOST: str
    LISTEN_PORT: str


class PrivateSettings(BaseSettings):
    EMAIL_USERNAME: Optional[SecretStr] = ''
    EMAIL_PASSWORD: Optional[SecretStr] = ''

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


class EmailSettings(BaseEnvSettings):
    EMAIL_SMTP: str
    EMAIL_PORT: int


class ClientSettings(BaseEnvSettings):
    SERVER_IP: str
    SERVER_PORT: str


class Credentials(BaseSettings):
    email_settings: EmailSettings = Field(default_factory=EmailSettings)
    email_private_settings: PrivateSettings = Field(default_factory=PrivateSettings)
    client_settings: ClientSettings = Field(default_factory=ClientSettings)


class UserSettings(BaseEnvSettings):
    server: ServerSettings = Field(default_factory=ServerSettings)
    credentials: Credentials = Field(default_factory=Credentials)

    DEBUG: Optional[bool] = False


user_config = UserSettings()
