"""Beteg funkciók üzleti logikája (input/print nélkül).

A függvények egyszerű dict-eket adnak vissza; üzleti szabály megsértésekor
BookingError-t dobnak, aminek az üzenete közvetlenül megjeleníthető.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config import APPOINTMENT_MINUTES, DATETIME_FORMAT
from database.base import SessionLocal
from models import Doctor, Idopont, OrvosSzakterulet, Patient, Rendelesiido, Szakterulet
from utils.scheduling import generate_slots, overlaps


class BookingError(Exception):
    """Foglalás vagy lemondás üzleti szabályának megsértése."""


# ------------------------------------------------------------------ segédek
def _get_patient(db: Session, user_id: int) -> Optional[Patient]:
    return db.scalar(select(Patient).where(Patient.felhasznaloId == user_id))


def _free_slots(r: Rendelesiido, now: datetime) -> list:
    """A rendelési idő még szabad, jövőbeli sávjai.

    Üres lista, ha a rendelési idő betelt (maxPaciens). Egy sáv foglalt, ha
    átfed egy már rögzített időponttal.
    """
    if len(r.idopontok) >= r.maxPaciens:
        return []
    return [
        (start, end)
        for start, end in generate_slots(r.kezdete, r.vege, APPOINTMENT_MINUTES)
        if start > now and not any(overlaps(start, end, i.kezdete, i.vege) for i in r.idopontok)
    ]


def _appointment_to_dict(i: Idopont) -> dict:
    r = i.rendelesido
    return {
        "idopontId": i.idopontId,
        "kezdete": i.kezdete,
        "vege": i.vege,
        "orvos_nev": r.orvos.user.nev,
        "szakterulet": r.orvos.szakterulet,
        "szoba": r.szoba.szobaszam,
        "reszleg": r.szoba.reszleg.megnevezes,
        "diagnozis": i.betegellatas.diagnozis if i.betegellatas else None,
        "eredmeny": i.betegellatas.eredmeny if i.betegellatas else None,
    }


# ------------------------------------------------------------------ adatlap, időpontok
def get_profile(user_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        patient = _get_patient(db, user_id)
        if patient is None:
            return None
        return {
            "betegId": patient.betegId,
            "nev": patient.user.nev,
            "TAJ": patient.user.TAJ,
            "email": patient.user.email,
            "telefonszam": patient.telefonszam,
        }


def get_appointments(user_id: int) -> List[dict]:
    """A beteg összes időpontja (múltbeli és jövőbeli), időrendben."""
    with SessionLocal() as db:
        patient = _get_patient(db, user_id)
        if patient is None:
            return []
        rows = [_appointment_to_dict(i) for i in patient.idopontok]
        return sorted(rows, key=lambda row: row["kezdete"])


# ------------------------------------------------------------------ időpontfoglalás
def list_specialties() -> List[dict]:
    with SessionLocal() as db:
        rows = db.scalars(select(Szakterulet).order_by(Szakterulet.megnevezes)).all()
        return [{"szakteruletId": s.szakteruletId, "megnevezes": s.megnevezes} for s in rows]


def list_doctors_by_specialty(szakterulet_id: int) -> List[dict]:
    """A szakterülethez tartozó orvosok az OrvosSzakterulet kapcsolótábla alapján."""
    with SessionLocal() as db:
        stmt = (
            select(Doctor)
            .join(OrvosSzakterulet, OrvosSzakterulet.orvosId == Doctor.orvosId)
            .where(OrvosSzakterulet.szakteruletId == szakterulet_id)
        )
        doctors = db.scalars(stmt).all()
        rows = [{"orvosId": d.orvosId, "nev": d.user.nev} for d in doctors]
        return sorted(rows, key=lambda row: row["nev"])


def get_available_slots(orvos_id: int, now: Optional[datetime] = None) -> List[dict]:
    """Az orvos jövőbeli rendelési idői, amelyekben van még szabad időpont.

    Minden elem tartalmazza a szabad sávokat ("slots": [(kezdete, vege), ...]).
    """
    now = now or datetime.now()
    with SessionLocal() as db:
        stmt = (
            select(Rendelesiido)
            .where(Rendelesiido.orvosId == orvos_id, Rendelesiido.vege > now)
            .order_by(Rendelesiido.kezdete)
        )
        result = []
        for r in db.scalars(stmt).all():
            free = _free_slots(r, now)
            if not free:
                continue
            foglalt = len(r.idopontok)
            result.append({
                "rendelesIdoId": r.rendelesIdoId,
                "kezdete": r.kezdete,
                "vege": r.vege,
                "szoba": r.szoba.szobaszam,
                "reszleg": r.szoba.reszleg.megnevezes,
                "foglalt": foglalt,
                "max": r.maxPaciens,
                "szabad": min(r.maxPaciens - foglalt, len(free)),
                "slots": free,
            })
        return result


def book_appointment(user_id: int, rendelesido_id: int, kezdete: datetime,
                     now: Optional[datetime] = None) -> dict:
    """Ellenőrzi (érvényesség, kapacitás, ütközések) és rögzíti az időpontot."""
    now = now or datetime.now()
    vege = kezdete + timedelta(minutes=APPOINTMENT_MINUTES)

    with SessionLocal() as db:
        patient = _get_patient(db, user_id)
        if patient is None:
            raise BookingError("A beteg adatlap nem található.")
        r = db.get(Rendelesiido, rendelesido_id)
        if r is None:
            raise BookingError("A rendelési idő nem létezik.")

        # Érvényes sáv-e, és jövőbeli-e
        if (kezdete, vege) not in generate_slots(r.kezdete, r.vege, APPOINTMENT_MINUTES):
            raise BookingError("Ez az időpont nem tartozik a rendelési időhöz.")
        if kezdete <= now:
            raise BookingError("Múltbeli időpontra nem lehet foglalni.")

        # Kapacitásellenőrzés
        if len(r.idopontok) >= r.maxPaciens:
            raise BookingError("A rendelési idő betelt (elérte a maximális páciensszámot).")

        # Ütközés az orvos már foglalt időpontjaival
        if any(overlaps(kezdete, vege, i.kezdete, i.vege) for i in r.idopontok):
            raise BookingError("Ezt az időpontot már lefoglalták.")

        # Ütközés a beteg saját időpontjaival (egyszerre csak egy helyen lehet)
        for i in patient.idopontok:
            if overlaps(kezdete, vege, i.kezdete, i.vege):
                raise BookingError(
                    f"Már van másik időpontod ekkor: {i.kezdete.strftime(DATETIME_FORMAT)}."
                )

        # Rögzítés
        idopont = Idopont(kezdete=kezdete, vege=vege,
                          betegId=patient.betegId, rendelesIdoId=r.rendelesIdoId)
        db.add(idopont)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise BookingError("Az időpontot közben valaki más lefoglalta.")

        return {
            "idopontId": idopont.idopontId,
            "kezdete": idopont.kezdete,
            "vege": idopont.vege,
            "orvos_nev": r.orvos.user.nev,
            "szoba": r.szoba.szobaszam,
            "reszleg": r.szoba.reszleg.megnevezes,
        }


# ------------------------------------------------------------------ lemondás
def get_upcoming_appointments(user_id: int, now: Optional[datetime] = None) -> List[dict]:
    """A beteg jövőbeli időpontjai, időrendben."""
    now = now or datetime.now()
    with SessionLocal() as db:
        patient = _get_patient(db, user_id)
        if patient is None:
            return []
        rows = [_appointment_to_dict(i) for i in patient.idopontok if i.kezdete > now]
        return sorted(rows, key=lambda row: row["kezdete"])


def cancel_appointment(user_id: int, idopont_id: int, now: Optional[datetime] = None) -> None:
    """Törli a beteg saját, jövőbeli időpontját. A hely ezzel újra szabaddá válik,
    mert a szabad helyeket mindig a ténylegesen rögzített időpontokból számoljuk."""
    now = now or datetime.now()
    with SessionLocal() as db:
        patient = _get_patient(db, user_id)
        if patient is None:
            raise BookingError("A beteg adatlap nem található.")
        idopont = db.get(Idopont, idopont_id)
        if idopont is None or idopont.betegId != patient.betegId:
            raise BookingError("Ez az időpont nem található az időpontjaid között.")
        if idopont.kezdete <= now:
            raise BookingError("Már elmúlt időpontot nem lehet lemondani.")
        if idopont.betegellatas is not None:
            raise BookingError("Ehhez az időponthoz már tartozik betegellátás.")
        db.delete(idopont)
        db.commit()
