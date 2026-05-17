from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    REDIS_PASSWORD: str

    class Config:
        env_file = "../.env"

settings = Settings()
