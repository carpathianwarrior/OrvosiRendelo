"""Belépés / kilépés."""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select

from database.base import SessionLocal
from models import User
from utils import session
from utils.security import verify_password


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: int
    nev: str
    szerep: str


def normalize_taj(taj: str) -> str:
    """'123 456 789' és '123-456-789' is '123456789' lesz."""
    return "".join(ch for ch in taj if ch.isdigit())


def login(taj: str, password: str, expected_role: str) -> Optional[AuthenticatedUser]:
    """TAJ szám + jelszó alapján belépteti a felhasználót.

    Sikeres belépéskor beállítja az utils.session változóit
    (current_user_id, current_role) és visszaadja a felhasználót.
    Hibás adatoknál, vagy ha a felhasználó szerepe nem egyezik a kért
    szerepkörrel, None-t ad (és nem árulja el, melyik adat volt rossz).
    """
    taj = normalize_taj(taj)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.TAJ == taj, User.szerep == expected_role))
        if user is None or not verify_password(password, user.jelszo_hash):
            return None
        authenticated = AuthenticatedUser(user.felhasznaloId, user.nev, user.szerep)

    session.set_current_user(authenticated.user_id, authenticated.szerep)
    return authenticated


def logout() -> None:
    session.clear()
