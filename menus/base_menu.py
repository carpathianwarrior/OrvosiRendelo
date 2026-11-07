"""Újrahasznosítható szöveges menü."""
from typing import Callable, List, Optional, Tuple

MenuEntry = Tuple[str, Callable[[], Optional[bool]]]


class Menu:
    """Számozott menü. A 0. pont mindig a kilépés/visszalépés.

    Az akciók (callable-ök) visszatérhetnek True-val, ez bezárja a menüt;
    None/False esetén a menü újra megjelenik.
    """

    def __init__(self, title: str, entries: List[MenuEntry], exit_label: str = "Vissza"):
        self.title = title
        self.entries = entries
        self.exit_label = exit_label

    def show(self) -> None:
        print(f"\n=== {self.title} ===")
        for number, (label, _) in enumerate(self.entries, start=1):
            print(f"  {number}. {label}")
        print(f"  0. {self.exit_label}")

    def run(self) -> None:
        while True:
            self.show()
            choice = input("Választás: ").strip()
            if choice == "0":
                return
            try:
                index = int(choice) - 1
            except ValueError:
                index = -1
            if 0 <= index < len(self.entries):
                if self.entries[index][1]():
                    return
            else:
                print("Érvénytelen választás, próbáld újra.")


def choose_from_list(title: str, labels: List[str], cancel_label: str = "Mégse") -> Optional[int]:
    """Számozott listából választat. A választott elem 0-tól induló indexét adja,
    vagy None-t, ha a felhasználó a 0-t (mégse) választja."""
    print(f"\n--- {title} ---")
    for number, label in enumerate(labels, start=1):
        print(f"  {number}. {label}")
    print(f"  0. {cancel_label}")
    while True:
        choice = input("Választás: ").strip()
        if choice == "0":
            return None
        try:
            index = int(choice) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(labels):
            return index
        print("Érvénytelen választás, próbáld újra.")


def confirm(question: str) -> bool:
    """Igen/nem megerősítés ('i' / 'n')."""
    while True:
        answer = input(f"{question} (i/n): ").strip().lower()
        if answer in ("i", "igen"):
            return True
        if answer in ("n", "nem"):
            return False
        print("Kérlek, 'i' vagy 'n' választ adj.")
