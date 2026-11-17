"""Orvosi menü."""
from datetime import datetime

from config import APPOINTMENT_MINUTES, DATETIME_FORMAT
from menus.base_menu import Menu, choose_from_list, confirm, prompt_datetime, prompt_int
from services import doctor_service
from services.doctor_service import ConsultationError
from utils import session


def _fmt_range(start: datetime, end: datetime) -> str:
    return f"{start.strftime(DATETIME_FORMAT)} - {end.strftime('%H:%M')}"


class DoctorMenu(Menu):
    def __init__(self):
        super().__init__(
            "Orvosi menü",
            [
                ("Saját adataim", self._show_profile),
                ("Rendelési időim", self._show_consultation_hours),
                ("Foglalt időpontjaim", self._show_appointments),
                ("Rendelési idő meghirdetése", self._announce_consultation_hour),
            ],
            exit_label="Kijelentkezés",
        )

    # ------------------------------------------------------------ megtekintés
    @staticmethod
    def _show_profile() -> None:
        profile = doctor_service.get_profile(session.current_user_id)
        if profile is None:
            print("Az orvosi adatlap nem található.")
            return
        print("\n--- Saját adataim ---")
        print(f"Név:            {profile['nev']}")
        print(f"TAJ:            {profile['TAJ']}")
        print(f"E-mail:         {profile['email'] or '-'}")
        print(f"Fő szakterület: {profile['szakterulet'] or '-'}")
        print(f"Szakterületek:  {', '.join(profile['szakteruletek']) or '-'}")

    @staticmethod
    def _show_consultation_hours() -> None:
        hours = doctor_service.get_consultation_hours(session.current_user_id)
        print("\n--- Rendelési időim ---")
        if not hours:
            print("Nincs rendelési idő.")
        for h in hours:
            print(f"{_fmt_range(h['kezdete'], h['vege'])} | "
                  f"{h['szoba']}. szoba ({h['reszleg']}) | foglalt: {h['foglalt']}/{h['max']}")

    @staticmethod
    def _show_appointments() -> None:
        appointments = doctor_service.get_appointments(session.current_user_id)
        print("\n--- Foglalt időpontjaim ---")
        if not appointments:
            print("Nincs foglalt időpont.")
        for a in appointments:
            print(f"{_fmt_range(a['kezdete'], a['vege'])} | "
                  f"{a['beteg_nev']} (TAJ: {a['beteg_taj']}) | {a['szoba']}. szoba | "
                  f"diagnózis: {a['diagnozis'] or '-'}")

    # ------------------------------------------------------------ rendelési idő meghirdetése
    @staticmethod
    def _announce_consultation_hour() -> None:
        user_id = session.current_user_id

        # 1. Saját szakterületek listázása és kiválasztása
        specialties = doctor_service.get_my_specialties(user_id)
        if not specialties:
            print("\nA profilodhoz nincs szakterület rendelve.")
            return
        index = choose_from_list("Saját szakterületeim", [s["megnevezes"] for s in specialties])
        if index is None:
            return
        specialty = specialties[index]

        # 2. Részleg kiválasztása
        departments = doctor_service.get_departments_for_specialty(specialty["szakteruletId"])
        if not departments:
            print(f"\nA(z) {specialty['megnevezes']} szakterülethez nincs részleg rendelve.")
            return
        index = choose_from_list(f"{specialty['megnevezes']} - részlegek",
                                 [d["megnevezes"] for d in departments])
        if index is None:
            return
        department = departments[index]

        # 3. Kezdet, vég és maximális páciensszám
        print(f"\nA rendelési idő {APPOINTMENT_MINUTES} perces időpontokra lesz osztva.")
        kezdete = prompt_datetime("Rendelés kezdete")
        if kezdete is None:
            return
        vege = prompt_datetime("Rendelés vége")
        if vege is None:
            return
        max_paciens = prompt_int("Maximális páciensszám")
        if max_paciens is None:
            return

        # 4. Orvosütközés és érvényesség ellenőrzése, majd a szabad szobák lekérése
        try:
            doctor_service.check_consultation_window(user_id, kezdete, vege, max_paciens)
        except ConsultationError as error:
            print(f"\nNem hirdethető meg: {error}")
            return
        rooms = doctor_service.get_free_rooms(department["reszlegId"], kezdete, vege)
        if not rooms:
            print(f"\nEbben az időszakban nincs szabad szoba a(z) {department['megnevezes']} részlegen.")
            return

        # 5. Szabad szoba kiválasztása
        labels = [f"{r['szobaszam']}. szoba" + (f" - {r['leiras']}" if r["leiras"] else "") for r in rooms]
        index = choose_from_list(f"Szabad szobák ({department['megnevezes']})", labels)
        if index is None:
            return
        room = rooms[index]

        # Összegzés és megerősítés
        print("\nMeghirdetendő rendelési idő:")
        print(f"  Szakterület:  {specialty['megnevezes']}")
        print(f"  Részleg/szoba: {department['megnevezes']}, {room['szobaszam']}. szoba")
        print(f"  Időtartam:    {_fmt_range(kezdete, vege)}")
        print(f"  Max. páciens: {max_paciens}")
        if not confirm("Meghirdeted a rendelési időt?"):
            print("A meghirdetés megszakítva.")
            return

        # 6. Rögzítés (a service a szobaütközést is újraellenőrzi)
        try:
            created = doctor_service.create_consultation_hour(
                user_id, room["szobaId"], kezdete, vege, max_paciens
            )
        except ConsultationError as error:
            print(f"\nA meghirdetés nem sikerült: {error}")
            return
        print(f"\nA rendelési idő meghirdetve: {_fmt_range(created['kezdete'], created['vege'])}, "
              f"{created['szoba']}. szoba ({created['reszleg']}), max. {created['maxPaciens']} páciens.")