import os
from pathlib import Path
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).resolve().parent.parent

def load_dotenv_file(filepath: Path):
    if not filepath.exists():
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k not in os.environ:
                os.environ[k] = v

load_dotenv_file(BASE_DIR / ".env")

@dataclass
class Settings:
    PORT: int = int(os.getenv("PORT", "8081"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "15"))
    TIMEZONE: str = os.getenv("TIMEZONE", "America/New_York")
    MOCK_WRITE_MODE: bool = os.getenv("MOCK_WRITE_MODE", "true").lower() in ("1", "true", "yes")

    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / "data" / "cache"
    SAMPLES_DIR: Path = BASE_DIR / "data" / "samples"
    LOCAL_STORE_DIR: Path = BASE_DIR / "data" / "local_store"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"

    def ensure_directories(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        self.LOCAL_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()

