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

    return "".join(ch for ch in taj if ch.isdigit())


def login(taj: str, password: str, expected_role: str) -> Optional[AuthenticatedUser]:

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
