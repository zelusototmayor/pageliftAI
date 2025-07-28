from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    OPENAI_MODEL: str = "gpt-4.1"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/pagelift"
    REDIS_URL: str = "redis://redis:6379/0"
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "pagelift-assets"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 