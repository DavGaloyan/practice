from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Restaurant Booking System"
    VERSION: str = "1.0.0"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_ADMIN: str

    class Config:
        env_file = ".env"

settings = Settings()
