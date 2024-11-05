import numpy as np
import json
import operator
import csv

from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall

MAX_SCHEDULE_DAYS = 1
TIME_SLOTS = 3
GAMMA = 0.5  # Used in distance calculations for coloring scheme


def calculate_common_students(c1, c2):
    """
    Calculate the number of common students between two courses.
    """
    return len(set(c1.student_list).intersection(c2.student_list))


def calculate_degree(matrix, courses):
    """
    Calculate the degree (number of conflicts) for each course based on the adjacency matrix.
    """
    for i in range(len(courses)):
        courses[i].degree = np.sum(matrix[i] != 0)


def initialize_colors(max_schedule_days=MAX_SCHEDULE_DAYS, time_slots=TIME_SLOTS):
    """
    Initialize the color matrix with Color objects for each day and time slot.
    """
    color_matrix = [[None for _ in range(time_slots)] for _ in range(max_schedule_days)]

    for day in range(max_schedule_days):
        for slot in range(time_slots):
            new_color = Color(day, slot)
            color_matrix[day][slot] = new_color

    return color_matrix


def build_weight_matrix():
    """
    Build the weight matrix representing course conflicts and initialize courses.
    """
    with open('data/data_course.json', 'r') as data_file:
        course_data = json.load(data_file)

    with open('data/mid_sem_exam_schedule.json', 'r') as data_file:
        exam_data = json.load(data_file)

    course_index = {}
    courses = []
    counter = 1
    err_courses = []

    for course_code, students in course_data.items():
        if not students:
            continue
        try:
            old_day, old_slot = exam_data[course_code][0], exam_data[course_code][1]
            crs = Course(counter, course_code, students, old_day, old_slot)
        except KeyError:
            err_courses.append(course_code)
            crs = Course(counter, course_code, students, 0, 0)
        courses.append(crs)
        course_index[course_code] = crs
        counter += 1

    with open('err_courses.txt', 'w') as out:
        out.write(str(err_courses))

    total = len(courses)
    graph = np.zeros((total, total), dtype=int)

    # Assigning weights to matrix
    for i in range(total):
        for j in range(i + 1, total):
            graph[i, j] = calculate_common_students(courses[i], courses[j])
            graph[j, i] = graph[i, j]

    # Adding adjacent courses to adjacency lists
    for i in range(total):
        courses[i].max_adjacency = np.max(graph[i])
        for j in range(total):
            if graph[i, j] > 0:
                courses[i].adjacency_list.append(courses[j])

    return graph, courses, course_index


def initialize_lecture_halls(color_matrix):
    """
    Initialize lecture halls and assign them to each color (day-slot).
    """
    with open('data/lecture_halls.json', 'r') as data_file:
        data = json.load(data_file)

    lecture_halls = []

    for day in range(MAX_SCHEDULE_DAYS):
        for slot in range(TIME_SLOTS):
            color = color_matrix[day][slot]
            for number, capacity in data.items():
                lec_hall = LectureHall(number, capacity[0], capacity[1], color)
                lecture_halls.append(lec_hall)
                color.lecture_halls.append(lec_hall)
    return lecture_halls


def initialize_students(course_index):
    """
    Initialize students with their enrolled courses.
    """
    with open('data/data_student.json', 'r') as data_file:
        data = json.load(data_file)

    student_list = []

    for roll, courses in data.items():
        course_objects = []
        for course_code in courses:
            if course_code in course_index:
                course_objects.append(course_index[course_code])
            else:
                print(f"No object for {course_code}")

        std = Student(roll, course_objects)
        student_list.append(std)

        # Assuming you want to print the last student's details
        print(std.roll_no, [course.course_code for course in std.courses_enrolled])

    return student_list


def binary_search(alist, item):
    """
    Perform binary search to find the insertion index for a lecture hall based on capacity.
    """
    first = 0
    last = len(alist) - 1
    found = False

    while first <= last and not found:
        midpoint = (first + last) // 2
        if alist[midpoint][1] == item:
            found = True
            last = midpoint - 1
        else:
            if item < alist[midpoint][1]:
                last = midpoint - 1
            else:
                first = midpoint + 1
    return last + 1


def get_lecture_hall(max_students, sorted_list):
    """
    Select a combination of lecture halls to accommodate the maximum number of students.
    """
    lecturehall_list = list(sorted_list)  # Make a mutable copy
    selected_lecture_halls = {}

    while max_students > 0 and lecturehall_list:
        i = binary_search(lecturehall_list, max_students)
        if i < 0:
            i = 0
        elif i >= len(lecturehall_list):
            i = len(lecturehall_list) - 1

        if i < 0:
            selected_lecture_halls = {}
            break

        seats = lecturehall_list[i][1]
        max_students -= seats

        lecturehall_object = lecturehall_list[i][0][0]
        seating_type = lecturehall_list[i][0][1]

        del lecturehall_list[i]

        selected_lecture_halls[lecturehall_object] = seating_type

        lecturehall_list = [
            lh for lh in lecturehall_list 
            if lh[0][0].number != lecturehall_object.number
        ]

    if max_students > 0:
        return {}

    return selected_lecture_halls
def output_to_csv(time_slots, max_schedule_days, color_matrix):
    """
    Export the final exam schedule to a CSV file.
    """
    if color_matrix is None:
        raise ValueError("color_matrix cannot be None")

    with open('exam_schedule.csv', 'w', newline='') as csvfile:
        schedule = csv.writer(csvfile, delimiter=',')
        schedule.writerow(['Exam Schedule'])
        for day in range(max_schedule_days):
            for slot in range(time_slots):
                color = color_matrix[day][slot]
                color_str = ", ".join([course.course_code for course in color.courses])
                day_str = f"Day {day + 1} Slot {slot + 1}"
                schedule.writerow([day_str, color_str])
            schedule.writerow([])



