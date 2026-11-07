from getpass import getpass
from typing import Type

from config import ROLE_DOCTOR, ROLE_PATIENT
from menus.base_menu import Menu
from menus.doctor_menu import DoctorMenu
from menus.patient_menu import PatientMenu
from services import auth_service


class MainMenu(Menu):
    def __init__(self):
        super().__init__(
            "Rendelő időpontfoglaló rendszer",
            [
                ("Orvos belépés", lambda: self._login(ROLE_DOCTOR, DoctorMenu)),
                ("Beteg belépés", lambda: self._login(ROLE_PATIENT, PatientMenu)),
            ],
            exit_label="Kilépés",
        )

    @staticmethod
    def _login(role: str, menu_class: Type[Menu]) -> None:
        taj = input("TAJ szám: ")
        password = getpass("Jelszó: ")

        user = auth_service.login(taj, password, role)
        if user is None:
            print("Hibás TAJ szám vagy jelszó.")
            return

        print(f"\nSikeres belépés. Üdvözöljük, {user.nev}!")
        try:
            menu_class().run()
        finally:
            auth_service.logout()
