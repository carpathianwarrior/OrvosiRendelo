
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.base import SessionLocal
from models import Doctor


def _get_doctor(db: Session, user_id: int) -> Optional[Doctor]:
    return db.scalar(select(Doctor).where(Doctor.felhasznaloId == user_id))


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
    with SessionLocal() as db:
        doctor = _get_doctor(db, user_id)
        if doctor is None:
            return []
        return [
            {
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
