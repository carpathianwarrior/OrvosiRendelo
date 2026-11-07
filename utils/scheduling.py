"""Időpont-számítási segédfüggvények (adatbázis nélkül)."""
from datetime import datetime, timedelta
from typing import List, Tuple

Slot = Tuple[datetime, datetime]


def generate_slots(start: datetime, end: datetime, minutes: int) -> List[Slot]:
    """A [start, end) tartományt egyenlő hosszú sávokra osztja.

    Csak a teljesen beleférő sávokat adja vissza: 8:00-12:00 és 30 perc esetén
    8 sáv lesz (8:00-8:30 ... 11:30-12:00).
    """
    step = timedelta(minutes=minutes)
    slots: List[Slot] = []
    current = start
    while current + step <= end:
        slots.append((current, current + step))
        current += step
    return slots


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Igaz, ha a két időtartam átfedi egymást (a szomszédos, érintkező nem ütközik)."""
    return a_start < b_end and b_start < a_end
