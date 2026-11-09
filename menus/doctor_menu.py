from config import DATETIME_FORMAT
from menus.base_menu import Menu
from services import doctor_service
from utils import session


class DoctorMenu(Menu):
    def __init__(self):
        super().__init__(
            "Orvosi menü",
            [
                ("Saját adataim", self._show_profile),
                ("Rendelési időim", self._show_consultation_hours),
                ("Foglalt időpontjaim", self._show_appointments),
            ],
            exit_label="Kijelentkezés",
        )

    @staticmethod
    def _show_profile() -> None:
        profile = doctor_service.get_profile(session.current_user_id)
        if profile is None:
            print("Az orvosi adatlap nem található.")
            return
        print("\n--- Saját adataim ---")
        print(f"Név:           {profile['nev']}")
        print(f"TAJ:           {profile['TAJ']}")
        print(f"E-mail:        {profile['email'] or '-'}")
        print(f"Fő szakterület: {profile['szakterulet'] or '-'}")
        print(f"Szakterületek: {', '.join(profile['szakteruletek']) or '-'}")

    @staticmethod
    def _show_consultation_hours() -> None:
        hours = doctor_service.get_consultation_hours(session.current_user_id)
        print("\n--- Rendelési időim ---")
        if not hours:
            print("Nincs rendelési idő.")
        for h in hours:
            print(f"{h['kezdete'].strftime(DATETIME_FORMAT)} - {h['vege'].strftime('%H:%M')} | "
                  f"{h['szoba']}. szoba ({h['reszleg']}) | foglalt: {h['foglalt']}/{h['max']}")

    @staticmethod
    def _show_appointments() -> None:
        appointments = doctor_service.get_appointments(session.current_user_id)
        print("\n--- Foglalt időpontjaim ---")
        if not appointments:
            print("Nincs foglalt időpont.")
        for a in appointments:
            print(f"{a['kezdete'].strftime(DATETIME_FORMAT)} - {a['vege'].strftime('%H:%M')} | "
                  f"{a['beteg_nev']} (TAJ: {a['beteg_taj']}) | {a['szoba']}. szoba | "
                  f"diagnózis: {a['diagnozis'] or '-'}")
