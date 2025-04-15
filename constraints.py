from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall
from typing import Set


class Constraints:
     
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def no_exam_clashes(self, course: Course, color: Color) -> bool:
        for scheduled_course in color.courses:
             
            if course.student_list & scheduled_course.student_list:
                
                return False
        return True

    def minimum_gap(self, course: Course, color: Color, min_gap: int = 1) -> bool:
        day = color.day
        slot = color.slot
        total_slots = self.scheduler.time_slots
        max_days = self.scheduler.max_days

        for student in course.student_list:
            
            for offset in range(-min_gap, min_gap + 1):
                if offset == 0:
                    continue   
                check_slot_index = day * total_slots + slot + offset
                check_day = check_slot_index // total_slots
                check_slot = check_slot_index % total_slots

                if 0 <= check_day < max_days and 0 <= check_slot < total_slots:
                    other_color = self.scheduler.color_matrix[check_day][check_slot]
                    for scheduled_course in other_color.courses:
                        if student in scheduled_course.student_list:
                            # Found a student with exams too close together
                            return False
        return True

    def maximum_exams_per_day(self, course: Course, color: Color, max_exams: int = 2) -> bool:
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
                            return False
        return True

    def no_consecutive_exams(self, course: Course, color: Color) -> bool:
        day = color.day
        slot = color.slot

        adjacent_slots = []
        if slot > 0:
            adjacent_slots.append(slot - 1)
        if slot < self.scheduler.time_slots - 1:
            adjacent_slots.append(slot + 1)

        for adj_slot in adjacent_slots:
            adj_color = self.scheduler.color_matrix[day][adj_slot]
            for scheduled_course in adj_color.courses:
                if course.student_list & scheduled_course.student_list:
                    # Found a student with consecutive exams
                    return False
        return True

    def room_capacity(self, course: Course, color: Color) -> bool:
        capacity_available = color.capacity_available()
        if course.no_of_students > capacity_available:
            return False
        return True

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





