"""Itt importáljuk az összes modellt, hogy a Base.metadata mindet ismerje."""
from models.user import User
from models.doctor import Doctor, OrvosSzakterulet, Szakterulet
from models.patient import Patient
from models.appointment import (
    Betegellatas, Idopont, Rendelesido, Reszleg, SzakteruletReszleg, Szobak,
)

__all__ = [
    "User", "Doctor", "Szakterulet", "OrvosSzakterulet", "Patient",
    "Reszleg", "SzakteruletReszleg", "Szobak", "Rendelesido", "Idopont", "Betegellatas",
]
