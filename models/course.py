from __future__ import annotations  # Enables forward references
from typing import Set, Optional, List
from models.lecture_hall import LectureHall
from models.color import Color

class Course:
    def __init__(self, course_code: str, student_list: Set[str], no_of_students: int):
        self.course_code = course_code
        self.student_list = set(student_list)  # Set of student IDs
        self.no_of_students = no_of_students
        self.conflicts: Set[Course] = set()
        self.degree: int = 0
        self.assigned_color: Optional[Color] = None  # Forward reference
        self.lecture_halls: List[LectureHall] = []
    
    def __str__(self):
        return f"Course({self.course_code})"
    
    def __repr__(self):
        return self.__str__()