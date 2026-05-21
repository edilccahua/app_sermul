from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql://sermul_user:sermul_password@localhost:5432/sermul_db"
    )
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost,http://localhost:5173"
    algorithm: str = "HS256"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
