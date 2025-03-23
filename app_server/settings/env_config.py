from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    HOST: str
    PORT: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


env_config = EnvSettings()
