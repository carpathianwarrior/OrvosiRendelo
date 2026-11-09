
from typing import Optional

from config import ROLE_DOCTOR, ROLE_PATIENT

current_user_id: Optional[int] = None
current_role: Optional[str] = None 


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
