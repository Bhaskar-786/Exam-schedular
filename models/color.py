from typing import List
from models.lecture_hall import LectureHall


class Color:
    """
    Represents a timeslot in the exam schedule.

    """

    def __init__(self, day: int, slot: int):
        self.day = day
        self.slot = slot
        self.courses = []
        self.lecture_halls: List[LectureHall] = []

    def capacity_available(self) -> int:
        """Total capacity available in all lecture halls."""
        return sum(hall.total_capacity() for hall in self.lecture_halls)

    def lecture_hall_list(self) -> List[LectureHall]:
        """List of lecture halls with available capacity."""
        return [hall for hall in self.lecture_halls if hall.has_capacity()]

    def __str__(self):
        return f"Day {self.day}, Slot {self.slot}"
