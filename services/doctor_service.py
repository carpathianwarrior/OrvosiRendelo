"""Orvosi funkciók üzleti logikája.

A függvények egyszerű dict-eket adnak vissza; üzleti szabály megsértésekor
ConsultationError-t dobnak, aminek az üzenete közvetlenül megjeleníthető.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config import APPOINTMENT_MINUTES, DATETIME_FORMAT
from database.base import SessionLocal
from models import Doctor, Rendelesido, Reszleg, Szakterulet, Szobak
from utils.scheduling import generate_slots, overlaps


class ConsultationError(Exception):
    """Rendelési idő meghirdetésének üzleti szabálysértése."""


# ------------------------------------------------------------------ segédek
def _get_doctor(db: Session, user_id: int) -> Optional[Doctor]:
    return db.scalar(select(Doctor).where(Doctor.felhasznaloId == user_id))


def _find_conflict(rendelesidok, kezdete: datetime, vege: datetime):
    """Az első olyan rendelési idő, ami átfed a megadott időtartammal (vagy None)."""
    return next((r for r in rendelesidok if overlaps(kezdete, vege, r.kezdete, r.vege)), None)


def _fmt(r) -> str:
    return f"{r.kezdete.strftime(DATETIME_FORMAT)} - {r.vege.strftime('%H:%M')}"


def _validate_window(doctor: Doctor, kezdete: datetime, vege: datetime,
                     max_paciens: int, now: datetime) -> None:
    """Az időtartam, a létszám és az orvos saját ütközéseinek ellenőrzése."""
    if kezdete <= now:
        raise ConsultationError("A rendelési idő kezdete nem lehet a múltban.")
    if vege <= kezdete:
        raise ConsultationError("A rendelés végének a kezdete után kell lennie.")

    slot_count = len(generate_slots(kezdete, vege, APPOINTMENT_MINUTES))
    if slot_count == 0:
        raise ConsultationError(f"A rendelési időnek legalább {APPOINTMENT_MINUTES} percesnek kell lennie.")
    if max_paciens < 1:
        raise ConsultationError("A maximális páciensszámnak legalább 1-nek kell lennie.")
    if max_paciens > slot_count:
        raise ConsultationError(
            f"Ennyi idő alatt legfeljebb {slot_count} páciens fér el "
            f"({APPOINTMENT_MINUTES} perces időpontokkal)."
        )

    conflict = _find_conflict(doctor.rendelesidok, kezdete, vege)
    if conflict is not None:
        raise ConsultationError(f"Már van rendelési időd ekkor: {_fmt(conflict)}.")


# ------------------------------------------------------------------ megtekintés
def get_profile(user_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            return None
        return {
            "orvosId": doctor.orvosId,
            "nev": doctor.user.nev,
            "TAJ": doctor.user.TAJ,
            "email": doctor.user.email,
            "szakterulet": doctor.szakterulet,
            "szakteruletek": [os.szakterulet.megnevezes for os in doctor.orvos_szakteruletek],
        }


def get_consultation_hours(user_id: int) -> List[dict]:
    """Az orvos rendelési idejei, időrendben."""
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            return []
        return [
            {
                "rendelesIdoId": r.rendelesIdoId,
                "kezdete": r.kezdete,
                "vege": r.vege,
                "szoba": r.szoba.szobaszam,
                "reszleg": r.szoba.reszleg.megnevezes,
                "foglalt": len(r.idopontok),
                "max": r.maxPaciens,
            }
            for r in sorted(doctor.rendelesidok, key=lambda r: r.kezdete)
        ]


def get_appointments(user_id: int) -> List[dict]:
    """Az orvos rendelési időiben lefoglalt időpontok, időrendben."""
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            return []
        rows = [
            {
                "kezdete": i.kezdete,
                "vege": i.vege,
                "beteg_nev": i.beteg.user.nev,
                "beteg_taj": i.beteg.user.TAJ,
                "szoba": r.szoba.szobaszam,
                "diagnozis": i.betegellatas.diagnozis if i.betegellatas else None,
            }
            for r in doctor.rendelesidok
            for i in r.idopontok
        ]
        return sorted(rows, key=lambda row: row["kezdete"])


def get_patient_list(user_id: int, rendelesido_id: int) -> List[dict]:
    """Egy rendelési időhöz foglalt időpontok és a hozzájuk tartozó betegek, időrendben.

    Csak az orvos saját rendelési idejére kérdezhető le; idegen vagy nem létező
    rendelési időre ConsultationError-t dob.
    """
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            raise ConsultationError("Az orvosi adatlap nem található.")
        rendelesido = db.get(Rendelesido, rendelesido_id)
        if rendelesido is None or rendelesido.orvosId != doctor.orvosId:
            raise ConsultationError("A rendelési idő nem található.")
        rows = [
            {
                "idopontId": i.idopontId,
                "kezdete": i.kezdete,
                "vege": i.vege,
                "beteg_nev": i.beteg.user.nev,
                "beteg_taj": i.beteg.user.TAJ,
                "beteg_telefon": i.beteg.telefonszam,
                "beteg_email": i.beteg.user.email,
                "diagnozis": i.betegellatas.diagnozis if i.betegellatas else None,
            }
            for i in rendelesido.idopontok
        ]
        return sorted(rows, key=lambda row: row["kezdete"])


# ------------------------------------------------------------------ rendelési idő meghirdetése
def get_my_specialties(user_id: int) -> List[dict]:
    """Az orvos saját szakterületei (OrvosSzakterulet alapján)."""
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            return []
        rows = [
            {"szakteruletId": os.szakterulet.szakteruletId, "megnevezes": os.szakterulet.megnevezes}
            for os in doctor.orvos_szakteruletek
        ]
        return sorted(rows, key=lambda row: row["megnevezes"])


def get_departments_for_specialty(szakterulet_id: int) -> List[dict]:
    """A szakterülethez besorolt részlegek (SzakteruletReszleg alapján)."""
    with SessionLocal() as db:
        szakterulet = db.get(Szakterulet, szakterulet_id)
        if szakterulet is None:
            return []
        rows = [
            {"reszlegId": sr.reszleg.reszlegId, "megnevezes": sr.reszleg.megnevezes}
            for sr in szakterulet.szakterulet_reszlegek
        ]
        return sorted(rows, key=lambda row: row["megnevezes"])


def check_consultation_window(user_id: int, kezdete: datetime, vege: datetime,
                              max_paciens: int, now: Optional[datetime] = None) -> None:
    """Korai ellenőrzés (még szoba nélkül): időtartam, létszám, orvos-ütközés."""
    now = now or datetime.now()
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            raise ConsultationError("Az orvosi adatlap nem található.")
        _validate_window(doctor, kezdete, vege, max_paciens, now)


def get_free_rooms(reszleg_id: int, kezdete: datetime, vege: datetime) -> List[dict]:
    """A részleg azon szobái, amelyekben a megadott időszakban nincs más rendelés."""
    with SessionLocal() as db:
        reszleg = db.get(Reszleg, reszleg_id)
        if reszleg is None:
            return []
        rows = [
            {"szobaId": s.szobaId, "szobaszam": s.szobaszam, "leiras": s.leiras}
            for s in reszleg.szobak
            if _find_conflict(s.rendelesidok, kezdete, vege) is None
        ]
        return sorted(rows, key=lambda row: row["szobaszam"])


def create_consultation_hour(user_id: int, szoba_id: int, kezdete: datetime, vege: datetime,
                             max_paciens: int, now: Optional[datetime] = None) -> dict:
    """Teljes (újra)ellenőrzés és rögzítés.

    Szabályok: az időtartam/létszám érvényes, az orvosnak nincs ütköző rendelése,
    a szoba az orvos valamelyik szakterületéhez besorolt részlegen van, és a
    szobában nincs ütköző rendelés.
    """
    now = now or datetime.now()
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            raise ConsultationError("Az orvosi adatlap nem található.")
        _validate_window(doctor, kezdete, vege, max_paciens, now)

        szoba = db.get(Szobak, szoba_id)
        if szoba is None:
            raise ConsultationError("A kiválasztott szoba nem létezik.")

        # A részleg tartozzon az orvos valamelyik szakterületéhez
        my_specialties = {os.szakteruletId for os in doctor.orvos_szakteruletek}
        department_specialties = {sr.szakteruletId for sr in szoba.reszleg.szakterulet_reszlegek}
        if not my_specialties & department_specialties:
            raise ConsultationError(
                "Ebben a szobában nem hirdethetsz rendelést: a részleg egyik szakterületedhez sem tartozik."
            )

        # Szobaütközés
        conflict = _find_conflict(szoba.rendelesidok, kezdete, vege)
        if conflict is not None:
            raise ConsultationError(f"A(z) {szoba.szobaszam}. szoba ekkor már foglalt: {_fmt(conflict)}.")

        rendelesido = Rendelesido(kezdete=kezdete, vege=vege, maxPaciens=max_paciens,
                                  orvosId=doctor.orvosId, szobaId=szoba.szobaId)
        db.add(rendelesido)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ConsultationError("A rendelési időt nem sikerült rögzíteni (érvénytelen adatok).")

        return {
            "rendelesIdoId": rendelesido.rendelesIdoId,
            "kezdete": rendelesido.kezdete,
            "vege": rendelesido.vege,
            "maxPaciens": rendelesido.maxPaciens,
            "szoba": szoba.szobaszam,
            "reszleg": szoba.reszleg.megnevezes,
        }