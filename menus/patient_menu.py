from datetime import datetime

from config import DATETIME_FORMAT
from menus.base_menu import Menu, choose_from_list, confirm
from services import patient_service
from services.patient_service import BookingError
from utils import session


def _fmt_range(start: datetime, end: datetime) -> str:
    return f"{start.strftime(DATETIME_FORMAT)} - {end.strftime('%H:%M')}"


class PatientMenu(Menu):
    def __init__(self):
        super().__init__(
            "Beteg menü",
            [
                ("Saját adataim", self._show_profile),
                ("Időpontjaim", self._show_appointments),
                ("Időpontfoglalás", self._book_appointment),
                ("Időpont lemondása", self._cancel_appointment),
            ],
            exit_label="Kijelentkezés",
        )

    @staticmethod
    def _show_profile() -> None:
        profile = patient_service.get_profile(session.current_user_id)
        if profile is None:
            print("A beteg adatlap nem található.")
            return
        print("\n--- Saját adataim ---")
        print(f"Név:         {profile['nev']}")
        print(f"TAJ:         {profile['TAJ']}")
        print(f"E-mail:      {profile['email'] or '-'}")
        print(f"Telefonszám: {profile['telefonszam'] or '-'}")

    @staticmethod
    def _show_appointments() -> None:
        appointments = patient_service.get_appointments(session.current_user_id)
        print("\n--- Időpontjaim ---")
        if not appointments:
            print("Nincs időpontod.")
        for a in appointments:
            print(f"{_fmt_range(a['kezdete'], a['vege'])} | "
                  f"{a['orvos_nev']} ({a['szakterulet']}) | {a['szoba']}. szoba, {a['reszleg']}")
            if a["diagnozis"]:
                print(f"    diagnózis: {a['diagnozis']} | eredmény: {a['eredmeny']}")

    @staticmethod
    def _book_appointment() -> None:

        specialties = patient_service.list_specialties()
        if not specialties:
            print("Jelenleg nincs elérhető szakterület.")
            return
        index = choose_from_list("Szakterületek", [s["megnevezes"] for s in specialties])
        if index is None:
            return
        specialty = specialties[index]

        doctors = patient_service.list_doctors_by_specialty(specialty["szakteruletId"])
        if not doctors:
            print(f"A(z) {specialty['megnevezes']} szakterülethez jelenleg nem tartozik orvos.")
            return
        index = choose_from_list(f"{specialty['megnevezes']} - orvosok", [d["nev"] for d in doctors])
        if index is None:
            return
        doctor = doctors[index]

        hours = patient_service.get_available_slots(doctor["orvosId"])
        if not hours:
            print(f"{doctor['nev']} rendelésein jelenleg nincs szabad időpont.")
            return
        labels = [
            f"{_fmt_range(h['kezdete'], h['vege'])} | {h['szoba']}. szoba ({h['reszleg']}) | "
            f"szabad helyek: {h['szabad']}/{h['max']}"
            for h in hours
        ]
        index = choose_from_list(f"{doctor['nev']} - rendelési idők", labels)
        if index is None:
            return
        consultation = hours[index]


        slot_labels = [_fmt_range(start, end) for start, end in consultation["slots"]]
        index = choose_from_list("Szabad időpontok", slot_labels)
        if index is None:
            return
        start, _ = consultation["slots"][index]


        try:
            booked = patient_service.book_appointment(
                session.current_user_id, consultation["rendelesIdoId"], start
            )
        except BookingError as error:
            print(f"\nA foglalás nem sikerült: {error}")
            return

        print("\nAz időpont rögzítve:")
        print(f"  {_fmt_range(booked['kezdete'], booked['vege'])}")
        print(f"  {booked['orvos_nev']} | {booked['szoba']}. szoba ({booked['reszleg']})")


    @staticmethod
    def _cancel_appointment() -> None:
        upcoming = patient_service.get_upcoming_appointments(session.current_user_id)
        if not upcoming:
            print("\nNincs lemondható (jövőbeli) időpontod.")
            return
        labels = [
            f"{_fmt_range(a['kezdete'], a['vege'])} | {a['orvos_nev']} ({a['szakterulet']}) | "
            f"{a['szoba']}. szoba"
            for a in upcoming
        ]

        index = choose_from_list("Lemondható időpontjaid", labels)
        if index is None:
            return
        
        if not confirm(f"Biztosan lemondod ezt az időpontot: {labels[index]}?"):
            print("A lemondás megszakítva.")
            return

        try:
            patient_service.cancel_appointment(session.current_user_id, upcoming[index]["idopontId"])
        except BookingError as error:
            print(f"\nA lemondás nem sikerült: {error}")
            return
        print("\nAz időpont lemondva, a hely újra szabad.")
