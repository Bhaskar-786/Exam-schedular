from typing import Set
from models.course import Course


class Student:
    
    def __init__(self, roll_no: str, courses: Set[Course]):
        self.roll_no = roll_no
        self.courses_enrolled = courses
        self.count = {}  # e.g., {day: number_of_exams_on_that_day}

    def fairness_quotient(self):
        # Implement method if needed
        pass

    def __str__(self):
        return f"Student {self.roll_no}"