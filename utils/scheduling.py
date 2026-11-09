
from datetime import datetime, timedelta
from typing import List, Tuple

Slot = Tuple[datetime, datetime]


def generate_slots(start: datetime, end: datetime, minutes: int) -> List[Slot]:

    step = timedelta(minutes=minutes)
    slots: List[Slot] = []
    current = start
    while current + step <= end:
        slots.append((current, current + step))
        current += step
    return slots


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end
