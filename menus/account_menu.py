
from getpass import getpass
from typing import Optional

from config import ROLE_DOCTOR, ROLE_PATIENT
from menus.base_menu import Menu, choose_from_list
from services import patient_service, user_service
from services.user_service import UserError
from utils import session


def _ask(label: str, current: Optional[str] = None) -> str:
    if current is None:
        return input(f"{label}: ").strip()
    shown = current or "-"
    raw = input(f"{label} [{shown}] (üresen hagyva: nem változik; '-': törlés): ").strip()
    if raw == "-":
        return ""
    return raw or current


def _ask_password(label: str) -> Optional[str]:
    first = getpass(f"{label}: ")
    if getpass(f"{label} újra: ") != first:
        print("A két jelszó nem egyezik.")
        return None
    return first


def register() -> None:
    print("\n--- Regisztráció ---")
    index = choose_from_list("Szerepkör", ["Beteg", "Orvos"])
    if index is None:
        return
    role = ROLE_PATIENT if index == 0 else ROLE_DOCTOR

    nev = _ask("Név")
    taj = _ask("TAJ szám (9 számjegy)")
    email = _ask("E-mail (nem kötelező)")
    telefon = _ask("Telefonszám (nem kötelező)") if role == ROLE_PATIENT else None
    password = _ask_password("Jelszó")
    if password is None:
        return

    szakterulet_ids = []
    if role == ROLE_DOCTOR:
        specialties = patient_service.list_specialties()
        while specialties:
            labels = [s["megnevezes"] for s in specialties]
            chosen = ", ".join(s["megnevezes"] for s in specialties if s["szakteruletId"] in szakterulet_ids)
            index = choose_from_list(
                f"Szakterület hozzáadása (kiválasztva: {chosen or '-'}; 0: kész)", labels, cancel_label="Kész")
            if index is None:
                break
            sid = specialties[index]["szakteruletId"]
            if sid not in szakterulet_ids:
                szakterulet_ids.append(sid)

    try:
        user = user_service.register_user(role, nev, taj, password, email, telefon, szakterulet_ids)
    except UserError as error:
        print(f"\nA regisztráció nem sikerült: {error}")
        return
    print(f"\nSikeres regisztráció, {user['nev']}! Most már beléphetsz a TAJ számoddal.")


def _edit_profile() -> None:
    account = user_service.get_account(session.current_user_id)
    if account is None:
        print("A felhasználó nem található.")
        return
    print(f"\n--- Adataim módosítása --- (TAJ: {account['TAJ']}, nem módosítható)")
    nev = _ask("Név", account["nev"])
    email = _ask("E-mail", account["email"] or "")
    telefon = None
    if account["szerep"] == ROLE_PATIENT:
        telefon = _ask("Telefonszám", account["telefonszam"] or "")
    try:
        user_service.update_profile(session.current_user_id, nev, email, telefon)
    except UserError as error:
        print(f"\nA módosítás nem sikerült: {error}")
        return
    print("\nAz adatok módosítva.")


def _change_password() -> None:
    old = getpass("Jelenlegi jelszó: ")
    new = _ask_password("Új jelszó")
    if new is None:
        return
    try:
        user_service.change_password(session.current_user_id, old, new)
    except UserError as error:
        print(f"\nA jelszócsere nem sikerült: {error}")
        return
    print("\nA jelszó megváltozott.")


class EditAccountMenu(Menu):
    def __init__(self):
        super().__init__("Saját adatok módosítása", [
            ("Név, e-mail, telefonszám", _edit_profile),
            ("Jelszó módosítása", _change_password),
        ])
