"""Alkalmazás-szintű beállítások és konstansok."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "korhaz.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Szerepkörök (a Felhasznalo.szerep oszlop és az utils.session is ezt használja)
ROLE_DOCTOR = "orvos"
ROLE_PATIENT = "beteg"

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# Egy időpont hossza percben: a rendelési időt ennyi perces sávokra osztjuk
APPOINTMENT_MINUTES = 30
