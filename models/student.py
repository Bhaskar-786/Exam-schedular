from typing import Set

class Student:
    def __init__(self, student_id: str, enrolled_courses: Set[str]):
        self.student_id = student_id
        self.enrolled_courses = set(enrolled_courses)

    def __str__(self):
        return f"Student({self.student_id})"

    def __repr__(self):
        return self.__str__()