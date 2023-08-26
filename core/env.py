from dataclasses import dataclass
from os import getenv
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

ROOT_DIR = Path(__name__).resolve().parent

load_dotenv(dotenv_path=ROOT_DIR / ".env")


@dataclass
class Env:
    DEBUG: Final[bool] = bool(getenv("DEBUG", None))
    SECRET_KEY: Final[str] = getenv("SECRET_KEY", "")
    BASE_URI: Final[str] = getenv("BASE_URI", "http://localhost:8000")
    # email configs
    EMAIL_ACTIVE: Final[bool] = bool(getenv('EMAIL_ACTIVE'))
    EMAIL_HOST: Final[str] = getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: Final[int] = int(getenv("EMAIL_PORT", 587))
    EMAIL_USER: Final[str] = getenv("EMAIL_USER", "")
    EMAIL_PASSD: Final[str] = getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_TLS: Final[bool] = bool(getenv("EMAIL_USE_TLS"))
