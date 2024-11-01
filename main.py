# main.py
from models.course import Course
from models.student import Student
from models.lecture_hall import LectureHall
from scheduler import initialize_colors, build_weight_matrix, calculate_degree, schedule_exams
from constraints import Constraints
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Sample Data
students = [
    Student("S1", set()),
    Student("S2", set()),
    Student("S3", set()),
]

courses = [
    Course(1, "C1", {"S1", "S2"}),
    Course(2, "C2", {"S2", "S3"}),
    Course(3, "C3", {"S1", "S3"}),
    Course(4, "C4", {"S1"}),
]

# Associate students with courses
for student in students:
    for course in courses:
        if student.roll_no in course.student_list:
            student.courses_enrolled.add(course)

# Lecture Halls
lecture_halls = [
    LectureHall("L1", 30, 30),
    LectureHall("L2", 40, 40),
]

# Scheduler Logic
MAX_SCHEDULE_DAYS = 3
TIME_SLOTS = 3

color_matrix = initialize_colors(MAX_SCHEDULE_DAYS, TIME_SLOTS)
course_index = build_weight_matrix(courses)
calculate_degree(courses)

# Initialize lecture halls for each color
def initialize_lecture_halls_for_colors(color_matrix, lecture_halls):
    for color in color_matrix:
        color.lecture_halls = lecture_halls.copy()

initialize_lecture_halls_for_colors(color_matrix, lecture_halls)

# Constraints
class Scheduler:
    def __init__(self, max_days, time_slots, color_matrix, logger):
        self.max_days = max_days
        self.time_slots = time_slots
        self.color_matrix = color_matrix
        self.logger = logger

scheduler = Scheduler(MAX_SCHEDULE_DAYS, TIME_SLOTS, color_matrix, logger)
constraints = Constraints(scheduler)

def schedule_exams_with_constraints(courses, color_matrix, constraints):
    sorted_courses = sorted(courses, key=lambda course: course.degree, reverse=True)
    for course in sorted_courses:
        for color in color_matrix:
            if constraints.is_suitable(course, color):
                course.assign_color(color)
                assign_lecture_halls(course, color)
                break

def assign_lecture_halls(course, color):
    required_capacity = course.no_of_students
    for hall in color.lecture_halls:
        if required_capacity <= 0:
            break
        if hall.has_capacity():
            seat_type = 'o' if hall.odd_available else 'e'
            hall.assign_seats(seat_type)
            course.lecture_halls[hall] = seat_type
            required_capacity -= hall.total_capacity()

# Schedule exams with constraints
schedule_exams_with_constraints(courses, color_matrix, constraints)

# Print schedule
for course in courses:
    if course.color:
        lecture_halls_assigned = ", ".join([str(hall) for hall in course.lecture_halls.keys()])
        print(f"{course.course_code} scheduled on {course.color}, Lecture Halls: {lecture_halls_assigned}")
    else:
        print(f"{course.course_code} could not be scheduled")
