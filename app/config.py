from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


class AuthJWTSettings(BaseSettings):
    JWT_PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.key"
    JWT_PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.key"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1500

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


class InitialAdminSettings(BaseSettings):
    CREATE_INITIAL_ADMIN: bool = False
    INITIAL_ADMIN_PHONE: Optional[str] = None
    INITIAL_ADMIN_PASSWORD: Optional[str] = None
    INITIAL_ADMIN_NAME: Optional[str] = None

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    jwt: AuthJWTSettings = AuthJWTSettings()
    admin: InitialAdminSettings = InitialAdminSettings()

settings = Settings()