from typing import List
from models.lecture_hall import LectureHall


class Color:
    def __init__(self, day: int, slot: int):
        self.day = day
        self.slot = slot
        self.courses = []
        self.lecture_halls: List[LectureHall] = []

    def capacity_available(self) -> int:
        """Returns maximum number of students that can be accommodated."""
        capacity = 0
        for hall in self.lecture_halls:
            capacity += hall.availability()['total']
        return capacity

    def lecture_hall_list(self) -> List[LectureHall]:
        """List of lecture halls with available capacity."""
        available_halls = []
        for hall in self.lecture_halls:
            if hall.availability()['total'] > 0:
                available_halls.append(hall)
        return available_halls

    def __unicode__(self):
        return 'color %s %s' % (self.day, self.slot)
