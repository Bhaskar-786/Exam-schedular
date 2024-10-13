from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall
from typing import Set


class Constraints:
     
    def __init__(self, scheduler):
        self.scheduler = scheduler


    def is_suitable(self, course: Course, color: Color) -> bool:
        if not self.room_capacity(course, color):
            return False
        if not self.no_exam_clashes(course, color):
            return False
        if not self.no_consecutive_exams(course, color):
            return False
        if not self.maximum_exams_per_day(course, color):
            return False
        if not self.minimum_gap(course, color):
            return False
        return True
