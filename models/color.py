# models/color.py

from __future__ import annotations  # Enables forward references
from typing import List
from models.lecture_hall import LectureHall
from models.course import Course
class Color:
    def __init__(self, day: int, slot: int):
        self.day = day
        self.slot = slot
        self.courses: List[Course] = []  # Forward reference
        self.available_halls: List[LectureHall] = []
    
    def __str__(self):
        return f"Day {self.day + 1}, Slot {self.slot + 1}"
    
    def __repr__(self):
        return self.__str__()
