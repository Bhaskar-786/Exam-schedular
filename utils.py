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
     


def initialize_lecture_halls(color_matrix):
    """
    Initialize lecture halls and assign them to each color (day-slot).
    """
     


def initialize_students(course_index):
    """
    Initialize students with their enrolled courses.
    """
     

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


