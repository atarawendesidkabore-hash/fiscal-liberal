from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Fiscal Liberal - Suite 2058"
    DATABASE_URL: str = "sqlite:///./fiscal.db"
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 heures

    class Config:
        env_file = ".env"


settings = Settings()
