import numpy as np
import json
import operator
import csv
import networkx as nx
import pandas as pd

from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall
from constraint import Problem
from ortools.sat.python import cp_model
import csv

#MAX_SCHEDULE_DAYS = 5
#TIME_SLOTS = 3
GAMMA = 0.5  # Used in distance calculations for coloring scheme
import networkx as nx
import numpy as np
import csv

def compute_and_save_hoffman_bound(G, filename="hoffman_bound.csv"):
    A = nx.to_numpy_array(G)
    eigenvalues = np.linalg.eigvalsh(A)
    lambda_max = max(eigenvalues)
    lambda_min = min(eigenvalues)

    if lambda_min >= 0:
        bound = 1
    else:
        bound = 1 - (lambda_max / lambda_min)

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Lambda Max", "Lambda Min", "Hoffman Bound"])
        writer.writerow([round(lambda_max, 4), round(lambda_min, 4), round(bound, 4)])

    print(f"Hoffman bound saved to {filename}")


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

    # Sort courses by degree in descending order
    sorted_courses = sorted(courses, key=lambda c: c.degree, reverse=True)

    # Save sorted degrees to CSV
    with open("degree.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Course Code", "Degree"])  # CSV header
        for course in sorted_courses:
            writer.writerow([course.course_code, course.degree])

    # Build graph and find largest clique
    G = nx.Graph()
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            if matrix[i][j] != 0:
                G.add_edge(i, j)

    
    # Step 4: Find unique cliques (as sets of course codes)
    raw_cliques = list(nx.find_cliques(G))
    unique_cliques = set()

    for clique in raw_cliques:
        course_codes = frozenset(courses[i].course_code for i in clique)
        unique_cliques.add(course_codes)

    # Step 5: Sort cliques by size
    sorted_cliques = sorted(unique_cliques, key=len, reverse=True)

    # Step 6: Save to CSV
    with open("clique.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Clique Size", "Courses in Clique"])

        for clique in sorted_cliques:
            writer.writerow([len(clique), ", ".join(sorted(clique))])

    print("Degrees saved to 'course_degrees.csv' and all cliques saved to 'all_cliques.csv'.")
    compute_and_save_hoffman_bound(G)



def initialize_colors(max_days, max_slots):
    """
    Initialize the color matrix with Color objects for each day and time slot.
    """
    color_matrix = [[None for _ in range(max_slots)] for _ in range(max_days)]

    for day in range(max_days):
        for slot in range(max_slots):
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
        """"
        try:
            old_day, old_slot = exam_data[course_code][0], exam_data[course_code][1]
            crs = Course(counter, course_code, students, old_day, old_slot)
        except KeyError:
            err_courses.append(course_code)
            crs = Course(counter, course_code, students, 0, 0)
        """
        try:
            crs = Course(counter, course_code, students)
        except KeyError:
            err_courses.append(course_code)
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


def initialize_lecture_halls(color_matrix, max_days, max_slots):
    """
    Initialize lecture halls and assign them to each color (day-slot).
    """
    with open('data/lecture_halls.json', 'r') as data_file:
        data = json.load(data_file)

    lecture_halls = []

    for day in range(max_days):
        for slot in range(max_slots):
            color = color_matrix[day][slot]
            for number, capacity in data.items():
                lec_hall = LectureHall(number, capacity[0], capacity[1], capacity[2], color)
                lecture_halls.append(lec_hall)
                color.lecture_halls.append(lec_hall)
    return lecture_halls


def initialize_students(course_index, max_days, max_slots):
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

        
        #print(std.roll_no, [course.course_code for course in std.courses_enrolled])

    return student_list


def binary_search(alist, item):
    """
    Perform binary search to find the insertion index for a lecture hall based on capacity.
    """
    first = 0
    last = len(alist) - 1
    found = False
    """
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
    """
    return first


def get_lecture_hall(max_students, sorted_list, max_days, max_slots):
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
        """
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
        """
        seats = lecturehall_list[i][1]
        lecturehall_object = lecturehall_list[i][0][0]
        seating_type = lecturehall_list[i][0][1]
        if lecturehall_object not in selected_lecture_halls:
                selected_lecture_halls[lecturehall_object] = {}  # Initialize dictionary
        if(seats>max_students):
            selected_lecture_halls[lecturehall_object][seating_type] = max_students
            lecturehall_list[i] = [(lecturehall_object, seating_type), seats - max_students]
            max_students = 0
        else:
            selected_lecture_halls[lecturehall_object][seating_type] = seats
            del lecturehall_list[i]
            max_students -= seats

        lecturehall_list = [
            lh for lh in lecturehall_list 
            if (lh[0][0].number != lecturehall_object.number or 
                (lh[0][0].number == lecturehall_object.number and lh[0][1]=='s' and seating_type=='o') or
                (lh[0][0].number == lecturehall_object.number and lh[0][1]=='s' and seating_type=='e') or
                (lh[0][0].number == lecturehall_object.number and lh[0][1]=='o' and seating_type=='s') or
                (lh[0][0].number == lecturehall_object.number and lh[0][1]=='e' and seating_type=='s')
            )
        ]


    if max_students > 0:
        return {}

    return selected_lecture_halls
'''
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
'''
def output_to_csv(schedule_data, filename='exam_schedule.csv'):
    """
    Export the final exam schedule to a CSV file.
    
    Parameters:
    - time_slots: Number of time slots per day
    - max_schedule_days: Number of days in the schedule
    - color_matrix: 2D list with color objects containing courses in each time slot
    - csv_file_path: Path to the CSV file to be created (default is 'exam_schedule.csv')
    """
    if not schedule_data:
        raise ValueError("schedule_data cannot be empty")
    # Open the CSV file in write mode
    with open(filename, 'w', newline='') as csvfile:
        schedule = csv.writer(csvfile, delimiter=',')
        
        # Write the header
        schedule.writerow(['Course Code', 'No. of Students', 'Day', 'Slot'])
        
        # Iterate through each entry in the schedule
        for entry in schedule_data:
            course_code = entry.get('Course Code')
            students = entry.get('Students')
            day = entry.get("Day")
            slots = entry.get("Slot")
            
            # Write each entry to the CSV
            schedule.writerow([course_code, students, day, slots])
    
    print(f"Exam schedule has been written to '{filename}'.")

"""def convert_lecture_hall_to_csv(schedule_lecture_hall, filename='lecture_hall_schedule.csv'):
    
    Convert the lecture hall allocation to a CSV file.
    
    Parameters:
        schedule_lecture_hall (list): A list of dictionaries containing course, hall, position, and seat information.
        filename (str): The name of the CSV file to save the schedule to.
    
    if not schedule_lecture_hall:
        raise ValueError("schedule_lecture_hall cannot be empty")
    
    # Open the CSV file in write mode
    with open(filename, 'w', newline='') as csvfile:
        schedule = csv.writer(csvfile, delimiter=',')
        
        # Write the header
        schedule.writerow(['Course Code', 'Lecture Hall', 'Position', 'No. of seats'])
        
        # Iterate through each entry in the schedule
        for entry in schedule_lecture_hall:
            course_code = entry.get("Course Code")
            lecture_hall = entry.get("Lecture Hall")
            position = entry.get("Position")
            seats = entry.get("No. of seats")
            
            # Write each entry to the CSV
            schedule.writerow([course_code, lecture_hall, position, seats])
    
    print(f"Lecture hall schedule has been written to '{filename}'.")"""

def convert_lecture_hall_to_csv(max_days, max_slots, schedule_lecture_hall, filename='lecture_hall_schedule.csv'):
    """
    Convert the schedule_lecture_hall data into a CSV file with Day and Slot in the header.
    Arguments:
    - schedule_lecture_hall: The grouped and sorted schedule data (a defaultdict).
    - filename: The name of the output CSV file.
    if not schedule_data:
        raise ValueError("schedule_data cannot be empty")
    """
    if not schedule_lecture_hall:
        raise ValueError("schedule_lecture_hall cannot be empty")
    # Prepare the CSV file to write
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the schedule to CSV, grouping by Day and Slot
        for day in range(max_days):
            for slot in range(max_slots):
                courses_in_slot = schedule_lecture_hall[day][slot]
                # If there are courses in this day and slot, write them to the file
                if courses_in_slot:
                    # Write Day and Slot header
                    writer.writerow([f"Day {day + 1}", f"Slot {slot + 1}", ""])
                    # Write the column names (Course Code, No. of Students, Venue)
                    writer.writerow(["Course Code", "No. of Students", "Venue"])
                    
                    # Write course information for this day and slot
                    for course in courses_in_slot:
                        writer.writerow([course['Course Code'], course['No. of Students'], course['Venue']])

                    # Add an empty row for spacing
                    writer.writerow([])

        print(f"Lecture hall schedule has been written to '{filename}'.")

def convert_seating_plan_to_csv(max_days,max_slots,schedule_seating_plan,filename='seating_plan.csv'):
    # Prepare the CSV file to write
    if not schedule_seating_plan:
        raise ValueError("schedule_seating_plan cannot be empty")
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the schedule to CSV, grouping by Day and Slot
        for day in range(max_days):
            for slot in range(max_slots):
                courses_in_slot = schedule_seating_plan[day][slot]
                # If there are courses in this day and slot, write them to the file
                if courses_in_slot:
                    # Write Day and Slot header
                    writer.writerow([f"Day {day + 1}", f"Slot {slot + 1}", "", ""])
                    # Write the column names (Course Code, No. of Students, Venue)
                    writer.writerow(["Course Code", "Lecture Hall", "Position", "No. of seats"])
                    
                    # Write course information for this day and slot
                    for course in courses_in_slot:
                        writer.writerow([course['Course Code'], course['Lecture Hall'], course['Position'], course['No. of seats']])

                    # Add an empty row for spacing
                    writer.writerow([])


        print(f"Seating plan has been written to '{filename}'.")





