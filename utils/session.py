"""Az aktuálisan bejelentkezett felhasználó.

FONTOS: más modulokból így használd:   from utils import session
                                         session.current_user_id
(a `from utils.session import current_user_id` csak a belépés előtti értéket
másolná le, és sosem frissülne.)
"""
from typing import Optional

from config import ROLE_DOCTOR, ROLE_PATIENT

current_user_id: Optional[int] = None   # Felhasznalo.felhasznaloId
current_role: Optional[str] = None      # ROLE_DOCTOR ("orvos") vagy ROLE_PATIENT ("beteg")


def set_current_user(user_id: int, role: str) -> None:
    global current_user_id, current_role
    current_user_id = user_id
    current_role = role


def clear() -> None:
    global current_user_id, current_role
    current_user_id = None
    current_role = None


def is_logged_in() -> bool:
    return current_user_id is not None


def is_doctor() -> bool:
    return current_role == ROLE_DOCTOR


def is_patient() -> bool:
    return current_role == ROLE_PATIENT
