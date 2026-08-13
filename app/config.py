from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = (
        "postgresql+psycopg2://finance_user:finance_password@localhost:5432/finance_db"
    )
    app_name: str = "Personal Finance Manager"
    debug: bool = True


settings = Settings()
