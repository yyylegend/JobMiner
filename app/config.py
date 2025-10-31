# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str  # 不要给默认值
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def db_url(self) -> str:
        return self.DB_URL

settings = Settings()
print("✅ Loaded DB_URL from .env:", settings.DB_URL)
