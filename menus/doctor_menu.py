from datetime import datetime

from config import APPOINTMENT_MINUTES, DATETIME_FORMAT
from menus.account_menu import EditAccountMenu
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
                ("Beteglista rendelési időhöz", self._show_patient_list),
                ("Saját adatok módosítása", lambda: EditAccountMenu().run()),
                ("Rendelési idő meghirdetése", self._announce_consultation_hour),
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

    @staticmethod
    def _show_patient_list() -> None:
        user_id = session.current_user_id
        hours = doctor_service.get_consultation_hours(user_id)
        if not hours:
            print("\nNincs rendelési idő.")
            return
        labels = [f"{_fmt_range(h['kezdete'], h['vege'])} | {h['szoba']}. szoba ({h['reszleg']}) | "
                  f"foglalt: {h['foglalt']}/{h['max']}" for h in hours]
        index = choose_from_list("Rendelési idő kiválasztása", labels)
        if index is None:
            return
        chosen = hours[index]
        try:
            patients = doctor_service.get_patient_list(user_id, chosen["rendelesIdoId"])
        except ConsultationError as error:
            print(f"\n{error}")
            return
        print(f"\n--- Beteglista: {_fmt_range(chosen['kezdete'], chosen['vege'])}, "
              f"{chosen['szoba']}. szoba ---")
        if not patients:
            print("Ehhez a rendelési időhöz még nincs foglalt időpont.")
            return
        for p in patients:
            print(f"{p['kezdete'].strftime('%H:%M')} - {p['vege'].strftime('%H:%M')} | "
                  f"{p['beteg_nev']} (TAJ: {p['beteg_taj']}) | tel.: {p['beteg_telefon'] or '-'} | "
                  f"diagnózis: {p['diagnozis'] or '-'}")
        print(f"Összesen: {len(patients)} beteg ({chosen['max']} férőhelyből).")

    @staticmethod
    def _show_patient_list() -> None:
        user_id = session.current_user_id
        hours = doctor_service.get_consultation_hours(user_id)
        if not hours:
            print("\nNincs rendelési idő.")
            return
        labels = [f"{_fmt_range(h['kezdete'], h['vege'])} | {h['szoba']}. szoba ({h['reszleg']}) | "
                  f"foglalt: {h['foglalt']}/{h['max']}" for h in hours]
        index = choose_from_list("Rendelési idő kiválasztása", labels)
        if index is None:
            return
        chosen = hours[index]
        try:
            patients = doctor_service.get_patient_list(user_id, chosen["rendelesIdoId"])
        except ConsultationError as error:
            print(f"\n{error}")
            return
        print(f"\n--- Beteglista: {_fmt_range(chosen['kezdete'], chosen['vege'])}, "
              f"{chosen['szoba']}. szoba ---")
        if not patients:
            print("Ehhez a rendelési időhöz még nincs foglalt időpont.")
            return
        for p in patients:
            print(f"{p['kezdete'].strftime('%H:%M')} - {p['vege'].strftime('%H:%M')} | "
                  f"{p['beteg_nev']} (TAJ: {p['beteg_taj']}) | tel.: {p['beteg_telefon'] or '-'} | "
                  f"diagnózis: {p['diagnozis'] or '-'}")
        print(f"Összesen: {len(patients)} beteg ({chosen['max']} férőhelyből).")

    @staticmethod
    def _announce_consultation_hour() -> None:
        user_id = session.current_user_id

        specialties = doctor_service.get_my_specialties(user_id)
        if not specialties:
            print("\nA profilodhoz nincs szakterület rendelve.")
            return
        index = choose_from_list("Saját szakterületeim", [s["megnevezes"] for s in specialties])
        if index is None:
            return
        specialty = specialties[index]

        departments = doctor_service.get_departments_for_specialty(specialty["szakteruletId"])
        if not departments:
            print(f"\nA(z) {specialty['megnevezes']} szakterülethez nincs részleg rendelve.")
            return
        index = choose_from_list(f"{specialty['megnevezes']} - részlegek",
                                 [d["megnevezes"] for d in departments])
        if index is None:
            return
        department = departments[index]

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

        try:
            doctor_service.check_consultation_window(user_id, kezdete, vege, max_paciens)
        except ConsultationError as error:
            print(f"\nNem hirdethető meg: {error}")
            return
        rooms = doctor_service.get_free_rooms(department["reszlegId"], kezdete, vege)
        if not rooms:
            print(f"\nEbben az időszakban nincs szabad szoba a(z) {department['megnevezes']} részlegen.")
            return

        labels = [f"{r['szobaszam']}. szoba" + (f" - {r['leiras']}" if r["leiras"] else "") for r in rooms]
        index = choose_from_list(f"Szabad szobák ({department['megnevezes']})", labels)
        if index is None:
            return
        room = rooms[index]

        print("\nMeghirdetendő rendelési idő:")
        print(f"  Szakterület:  {specialty['megnevezes']}")
        print(f"  Részleg/szoba: {department['megnevezes']}, {room['szobaszam']}. szoba")
        print(f"  Időtartam:    {_fmt_range(kezdete, vege)}")
        print(f"  Max. páciens: {max_paciens}")
        if not confirm("Meghirdeted a rendelési időt?"):
            print("A meghirdetés megszakítva.")
            return

        try:
            created = doctor_service.create_consultation_hour(
                user_id, room["szobaId"], kezdete, vege, max_paciens
            )
        except ConsultationError as error:
            print(f"\nA meghirdetés nem sikerült: {error}")
            return
        print(f"\nA rendelési idő meghirdetve: {_fmt_range(created['kezdete'], created['vege'])}, "
              f"{created['szoba']}. szoba ({created['reszleg']}), max. {created['maxPaciens']} páciens.")