from models.user import User
from models.doctor import Doctor
from models.patient import Patient
from models.betegellatas import Betegellatas
from models.idopont import Idopont
from models.rendelesiido import Rendelesido
from models.reszleg import Reszleg
from models.szakterulet_reszleg import SzakteruletReszleg
from models.szoba import Szobak
from models.szakterulet import Szakterulet
from models.orvos_szakterulet import OrvosSzakterulet


__all__ = [
    "User", "Doctor", "Szakterulet", "OrvosSzakterulet", "Patient",
    "Reszleg", "SzakteruletReszleg", "Szobak", "Rendelesido", "Idopont", "Betegellatas",
]
