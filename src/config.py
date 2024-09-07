from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    # essentially telling pydantic to import .env file (with all class config settings)
    class Config:
        env_file = ".env"

# instance of settings class above, performs validation
settings = Settings()

