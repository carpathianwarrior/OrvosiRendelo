"""Általános felhasználói funkciók: regisztráció és saját adatok módosítása."""
import re
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import ROLE_DOCTOR, ROLE_PATIENT
from database.base import SessionLocal
from models import Doctor, OrvosSzakterulet, Patient, Szakterulet, User
from services.auth_service import normalize_taj
from utils.security import hash_password, verify_password

MIN_PASSWORD_LENGTH = 6
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?[0-9 /()-]{6,20}$")


class UserError(Exception):
    """Regisztráció / adatmódosítás üzleti szabálysértése (az üzenet megjeleníthető)."""


# ------------------------------------------------------------------ validáció
def _clean_name(nev: str) -> str:
    nev = " ".join((nev or "").split())
    if len(nev) < 2:
        raise UserError("A név megadása kötelező (legalább 2 karakter).")
    return nev


def _clean_taj(taj: str) -> str:
    taj = normalize_taj(taj or "")
    if len(taj) != 9:
        raise UserError("A TAJ számnak pontosan 9 számjegyből kell állnia.")
    return taj


def _clean_email(email: Optional[str]) -> Optional[str]:
    email = (email or "").strip().lower()
    if not email:
        return None
    if not _EMAIL_RE.match(email):
        raise UserError("Érvénytelen e-mail cím.")
    return email


def _clean_phone(telefon: Optional[str]) -> Optional[str]:
    telefon = (telefon or "").strip()
    if not telefon:
        return None
    if not _PHONE_RE.match(telefon):
        raise UserError("Érvénytelen telefonszám.")
    return telefon


def _check_password(password: str) -> None:
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise UserError(f"A jelszónak legalább {MIN_PASSWORD_LENGTH} karakter hosszúnak kell lennie.")


def _email_taken(db, email: Optional[str], exclude_user_id: Optional[int] = None) -> bool:
    if email is None:
        return False
    other = db.scalar(select(User).where(User.email == email))
    return other is not None and other.felhasznaloId != exclude_user_id


# ------------------------------------------------------------------ regisztráció
def register_user(role: str, nev: str, taj: str, password: str, email: Optional[str] = None,
                  telefon: Optional[str] = None,
                  szakterulet_ids: Optional[List[int]] = None) -> dict:
    """Új felhasználó (beteg vagy orvos) felvétele. Orvosnál legalább egy szakterület kell."""
    if role not in (ROLE_DOCTOR, ROLE_PATIENT):
        raise UserError("Ismeretlen szerepkör.")
    nev, taj, email = _clean_name(nev), _clean_taj(taj), _clean_email(email)
    telefon = _clean_phone(telefon)
    _check_password(password)
    szakterulet_ids = list(dict.fromkeys(szakterulet_ids or []))
    if role == ROLE_DOCTOR and not szakterulet_ids:
        raise UserError("Orvosként legalább egy szakterületet meg kell adni.")

    with SessionLocal() as db:
        if db.scalar(select(User).where(User.TAJ == taj)) is not None:
            raise UserError("Ezzel a TAJ számmal már van regisztrált felhasználó.")
        if _email_taken(db, email):
            raise UserError("Ez az e-mail cím már foglalt.")

        user = User(nev=nev, TAJ=taj, email=email,
                    jelszo_hash=hash_password(password), szerep=role)
        if role == ROLE_PATIENT:
            user.patient = Patient(telefonszam=telefon)
        else:
            specialties = [db.get(Szakterulet, sid) for sid in szakterulet_ids]
            if any(s is None for s in specialties):
                raise UserError("A kiválasztott szakterület nem létezik.")
            doctor = Doctor(szakterulet=specialties[0].megnevezes)
            doctor.orvos_szakteruletek = [OrvosSzakterulet(szakterulet=s) for s in specialties]
            user.doctor = doctor
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise UserError("A regisztráció nem sikerült (a TAJ vagy az e-mail már foglalt).")
        return {"felhasznaloId": user.felhasznaloId, "nev": user.nev, "szerep": user.szerep}


# ------------------------------------------------------------------ saját adatok
def get_account(user_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            return None
        return {
            "nev": user.nev,
            "TAJ": user.TAJ,
            "email": user.email,
            "szerep": user.szerep,
            "telefonszam": user.patient.telefonszam if user.patient else None,
        }


def update_profile(user_id: int, nev: str, email: Optional[str],
                   telefon: Optional[str] = None) -> None:
    """Név, e-mail (és betegnél telefonszám) módosítása. A TAJ szám nem módosítható."""
    nev, email = _clean_name(nev), _clean_email(email)
    telefon = _clean_phone(telefon)
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise UserError("A felhasználó nem található.")
        if _email_taken(db, email, exclude_user_id=user_id):
            raise UserError("Ez az e-mail cím már foglalt.")
        user.nev, user.email = nev, email
        if user.patient is not None:
            user.patient.telefonszam = telefon
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise UserError("A módosítás nem sikerült (az e-mail cím már foglalt).")


def change_password(user_id: int, old_password: str, new_password: str) -> None:
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise UserError("A felhasználó nem található.")
        if not verify_password(old_password, user.jelszo_hash):
            raise UserError("A jelenlegi jelszó hibás.")
        _check_password(new_password)
        user.jelszo_hash = hash_password(new_password)
        db.commit()
