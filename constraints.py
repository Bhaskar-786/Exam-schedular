# constraints.py

from __future__ import annotations  # Enables forward references
from typing import Set
from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall
from scheduler import Scheduler 
import logging


class Constraints:
     
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
        self.logger = scheduler.logger  # Access logger directly
    
    def no_exam_clashes(self, course: Course, color: Color) -> bool:
        """
        Ensures that the course does not clash with any already scheduled courses in the same color (day and slot).
        A clash occurs if there is at least one common student between the two courses.
        """
        for scheduled_course in color.courses:
            # Assuming student_list is a set for efficient intersection
            if course.student_list.intersection(scheduled_course.student_list):
                # Found a clash
                self.logger.debug(
                    f"No Exam Clashes: {course.course_code} clashes with {scheduled_course.course_code}"
                )
                return False
        return True

    def maximum_exams_per_day(self, course: Course, color: Color, max_exams: int = 2) -> bool:
        """
        Ensures that no student has more than `max_exams` on the same day.
        """
        day = color.day
        for student in course.student_list:
            exam_count = 0
            for slot in range(self.scheduler.time_slots):
                other_color = self.scheduler.color_matrix[day][slot]
                for scheduled_course in other_color.courses:
                    if student in scheduled_course.student_list:
                        exam_count += 1
                        if exam_count >= max_exams:
                            # Student has reached or exceeded the maximum exams per day
                            self.logger.debug(
                                f"Maximum Exams Per Day: {student} has {exam_count} exams on Day {day + 1}"
                            )
                            return False
        return True

    def room_capacity(self, course: Course, color: Color) -> bool:
        """
        Ensures that the lecture hall(s) allocated to the course can accommodate all enrolled students.
        Assumes that the color (day and slot) has an attribute `available_halls` which is a list of LectureHall objects.
        """
        total_capacity = sum(hall.capacity for hall in color.available_halls)
        if course.no_of_students > total_capacity:
            self.logger.debug(
                f"Room Capacity: {course.course_code} requires {course.no_of_students} but only {total_capacity} available on Day {color.day + 1}, Slot {color.slot + 1}"
            )
            return False
        return True

    def is_suitable(self, course: Course, color: Color) -> bool:
        """
        Checks if a color (day and slot) is suitable for scheduling the given course based on hard constraints.
        """
        if not self.room_capacity(course, color):
            return False
        if not self.no_exam_clashes(course, color):
            return False
        if not self.maximum_exams_per_day(course, color):
            return False
        return True
