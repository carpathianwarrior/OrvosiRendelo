
import sys
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config import ROLE_DOCTOR, ROLE_PATIENT
from database.base import Base, SessionLocal, engine
from models import (
    Betegellatas, Doctor, Idopont, OrvosSzakterulet, Patient, Rendelesido,
    Reszleg, Szakterulet, SzakteruletReszleg, Szobak, User,
)
from utils.security import hash_password


def init_db(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(User)) == 0:
            seed(db)


def seed(db: Session) -> None:

    kardio = Szakterulet(megnevezes="Kardiológia")
    borgyogy = Szakterulet(megnevezes="Bőrgyógyászat")
    szemeszet = Szakterulet(megnevezes="Szemészet")

    belgyogy_r = Reszleg(megnevezes="Belgyógyászati osztály")
    sebeszet_r = Reszleg(megnevezes="Sebészeti osztály")
    borgyogy_r = Reszleg(megnevezes="Bőrgyógyászati osztály")
    szemeszet_r = Reszleg(megnevezes="Szemészeti osztály")

    db.add_all([kardio, borgyogy, szemeszet,
                belgyogy_r, sebeszet_r, borgyogy_r, szemeszet_r])

    db.add_all([
        SzakteruletReszleg(szakterulet=kardio, reszleg=belgyogy_r),
        SzakteruletReszleg(szakterulet=kardio, reszleg=sebeszet_r),
        SzakteruletReszleg(szakterulet=borgyogy, reszleg=borgyogy_r),
        SzakteruletReszleg(szakterulet=szemeszet, reszleg=szemeszet_r),
    ])


    sz101 = Szobak(Szobakszam="101", leiras="Kardiológiai rendelő, EKG-val", reszleg=belgyogy_r)
    sz102 = Szobak(Szobakszam="102", leiras="Kis műtő / beavatkozó", reszleg=sebeszet_r)
    sz201 = Szobak(Szobakszam="201", leiras="Bőrgyógyászati rendelő", reszleg=borgyogy_r)
    sz301 = Szobak(Szobakszam="301", leiras="Szemészeti vizsgáló, réslámpával", reszleg=szemeszet_r)
    db.add_all([sz101, sz102, sz201, sz301])

    u_kovacs = User(nev="Dr. Kovács István", TAJ="111222333", email="kovacs.istvan@korhaz.example",
                    jelszo_hash=hash_password("orvos123"), szerep=ROLE_DOCTOR)
    u_szabo = User(nev="Dr. Szabó Anna", TAJ="444555666", email="szabo.anna@korhaz.example",
                   jelszo_hash=hash_password("orvos456"), szerep=ROLE_DOCTOR)
    u_nagy = User(nev="Dr. Nagy Péter", TAJ="777888999", email="nagy.peter@korhaz.example",
                  jelszo_hash=hash_password("orvos789"), szerep=ROLE_DOCTOR)

    u_toth = User(nev="Tóth Gábor", TAJ="123456789", email="toth.gabor@example.com",
                  jelszo_hash=hash_password("beteg123"), szerep=ROLE_PATIENT)
    u_horvath = User(nev="Horváth Éva", TAJ="987654321", email="horvath.eva@example.com",
                     jelszo_hash=hash_password("beteg456"), szerep=ROLE_PATIENT)
    u_kiss = User(nev="Kiss Márta", TAJ="555666777", email="kiss.marta@example.com",
                  jelszo_hash=hash_password("beteg789"), szerep=ROLE_PATIENT)
    db.add_all([u_kovacs, u_szabo, u_nagy, u_toth, u_horvath, u_kiss])


    dr_kovacs = Doctor(user=u_kovacs, szakterulet="Kardiológia")
    dr_szabo = Doctor(user=u_szabo, szakterulet="Bőrgyógyászat")
    dr_nagy = Doctor(user=u_nagy, szakterulet="Szemészet")

    b1 = Patient(user=u_toth, telefonszam="+36301234567")
    b2 = Patient(user=u_horvath, telefonszam="+36209876543")
    b3 = Patient(user=u_kiss, telefonszam="+36705556667")
    db.add_all([dr_kovacs, dr_szabo, dr_nagy, b1, b2, b3])

    db.add_all([
        OrvosSzakterulet(orvos=dr_kovacs, szakterulet=kardio),
        OrvosSzakterulet(orvos=dr_szabo, szakterulet=borgyogy),
        OrvosSzakterulet(orvos=dr_szabo, szakterulet=szemeszet),
        OrvosSzakterulet(orvos=dr_nagy, szakterulet=szemeszet),
    ])

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def at(days: int, hour: int, minute: int = 0) -> datetime:
        return today + timedelta(days=days, hours=hour, minutes=minute)


    r1 = Rendelesido(kezdete=at(-4, 8), vege=at(-4, 12), maxPaciens=8, orvos=dr_kovacs, Szobak=sz101)
    r2 = Rendelesido(kezdete=at(-3, 13), vege=at(-3, 17), maxPaciens=8, orvos=dr_szabo, Szobak=sz201)
    
    r3 = Rendelesido(kezdete=at(3, 9), vege=at(3, 11), maxPaciens=4, orvos=dr_nagy, Szobak=sz301)
    r4 = Rendelesido(kezdete=at(2, 8), vege=at(2, 12), maxPaciens=8, orvos=dr_kovacs, Szobak=sz101)
    r5 = Rendelesido(kezdete=at(4, 13), vege=at(4, 17), maxPaciens=8, orvos=dr_szabo, Szobak=sz201)
    db.add_all([r1, r2, r3, r4, r5])

    i1 = Idopont(kezdete=at(-4, 8), vege=at(-4, 8, 30), beteg=b1, rendelesido=r1)
    i2 = Idopont(kezdete=at(-4, 8, 30), vege=at(-4, 9), beteg=b2, rendelesido=r1)
    i3 = Idopont(kezdete=at(-3, 13), vege=at(-3, 13, 30), beteg=b2, rendelesido=r2)
    i4 = Idopont(kezdete=at(3, 9), vege=at(3, 9, 30), beteg=b3, rendelesido=r3)
    i5 = Idopont(kezdete=at(3, 9, 30), vege=at(3, 10), beteg=b1, rendelesido=r3)
    i6 = Idopont(kezdete=at(2, 8), vege=at(2, 8, 30), beteg=b2, rendelesido=r4)
    i7 = Idopont(kezdete=at(4, 13), vege=at(4, 13, 30), beteg=b3, rendelesido=r5)
    db.add_all([i1, i2, i3, i4, i5, i6, i7])


    db.add_all([
        Betegellatas(betegellatasId="BE-2026-0001", panasz="Mellkasi szorítás terheléskor",
                     diagnozis="Szívritmuszavar gyanúja", eredmeny="24 órás Holter EKG elrendelve",
                     idopont=i1),
        Betegellatas(betegellatasId="BE-2026-0002", panasz="Viszkető kiütés a karokon",
                     diagnozis="Kontakt dermatitis", eredmeny="Kortikoszteroid krém felírva",
                     idopont=i3),
    ])

    db.commit()


if __name__ == "__main__":
    init_db(reset="--reset" in sys.argv)
    print("Adatbázis kész.")
