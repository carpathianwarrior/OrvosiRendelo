
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "korhaz.db"
DB_URL = f"sqlite:///{DB_PATH}"


ROLE_DOCTOR = "orvos"
ROLE_PATIENT = "beteg"

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

APPOINTMENT_MINUTES = 30
