from models import Course, Student, Color, LectureHall

from utils import (
    initialize_colors,
    get_lecture_hall,
    GAMMA,
    TIME_SLOTS,
    MAX_SCHEDULE_DAYS,
)
from utils import calculate_common_students, calculate_degree

def get_first_node_color(course, color_matrix):

    for j in range(MAX_SCHEDULE_DAYS):
        for k in range(TIME_SLOTS):
            hall_list = get_lecture_hall(course.no_of_students, color_matrix[j][k])
            if hall_list:
                return color_matrix[j][k], hall_list

    return None

def update_lecture_hall(hall_list, course, color):
    """
    Assign selected lecture halls to the course and update their availability.
    """
    course.assign_color(color)
    if course.no_of_students > 10:
        course.lecture_hall = hall_list

        for hall, position in course.lecture_hall.items():
            if position == 'o':
                hall.odd = 0
            elif position == 'e':
                hall.even = 0

def dis_1(color_1, color_2):
    """
    Calculate horizontal distance between two colors (same day).
    """
    if color_1.day == color_2.day:
        return abs(color_1.slot - color_2.slot)
    else:
        return "NA"


def dis_2(color_1, color_2):
    """
    Calculate vertical distance between two colors (different days).
    """
    return abs(color_1.day - color_2.day)


def dis_3(color_1, color_2):
    """
    Check if two colors are sufficiently spaced in the schedule.
    """
    num_1 = (color_1.day * TIME_SLOTS) + color_1.slot
    num_2 = (color_2.day * TIME_SLOTS) + color_2.slot

    if abs(num_1 - num_2) < 4:
        return False

    return True


def total_dis(color_1, color_2):
    """
    Calculate the total distance metric between two colors.
    """
    d2 = dis_2(color_1, color_2)
    d1 = dis_1(color_1, color_2)

    return GAMMA * d2 + d1


def check_three_exams_constraint(course, color_jk, day, color_matrix):
    """
    Ensure that no student has more than two exams on the same day.
    """
    students = course.student_list

    for student in students:
        counter = 0
        for slot in range(TIME_SLOTS):
            course_list = color_matrix[day][slot].courses
            for scheduled_course in course_list:
                if student in scheduled_course.student_list:
                    counter += 1
                    if counter == 2:
                        return False

    return True


def get_smallest_available_color(course, color_matrix, constraints):
    """
    Find the smallest available color for a course that satisfies all constraints.
    """
    adj_list = course.adjacency_list
    for day in range(MAX_SCHEDULE_DAYS):
      for slot in range(TIME_SLOTS):
        valid = True

        color = color_matrix[day][slot]
        
        # Construct sorted_list as per get_first_node_color
        sorted_list = []
        for lh in color.lecture_halls:
            if lh.odd > 0 and lh.odd_capacity > 0:
                sorted_list.append(((lh, 'o'), lh.odd_capacity))
            if lh.even > 0 and lh.even_capacity > 0:
                sorted_list.append(((lh, 'e'), lh.even_capacity))
        
        # Sort the list based on seats in descending order
        sorted_list.sort(key=lambda x: x[1], reverse=True)
        
        # Call get_lecture_hall with the correctly formatted sorted_list
        assigned_lh = get_lecture_hall(course.no_of_students, sorted_list)
        
        if not assigned_lh:
            valid = False
            continue

        for adj_course in adj_list:
            color_adj = adj_course.color
            if color_adj:
                if color_adj.day != day or color_adj.slot != slot:
                    if "check_dis_3" in constraints:
                        if not dis_3(color_adj, color_matrix[day][slot]):
                            valid = False
                            break

                    if "check_consecutive" in constraints:
                        if dis_2(color_adj, color_matrix[day][slot]) == 0:
                            if dis_1(color_adj, color_matrix[day][slot]) <= 1:
                                valid = False
                                break

                    if "check_three_exams" in constraints:
                        if not check_three_exams_constraint(course, color_matrix[day][slot], day, color_matrix):
                            valid = False
                            break
                else:
                    valid = False
                    break
            else:
                continue

        if valid:
            return color_matrix[day][slot], assigned_lh

    return None


def schedule_exam(sorted_courses, constraints, count, color_matrix):
    """
    Assign colors to courses based on sorted order and constraints.
    """
    num_colored_courses = 0

    for course in sorted_courses:
        if num_colored_courses == len(sorted_courses):
            break

        if not course.color and course.flag:
            if sorted_courses.index(course) == 0 and count == 0:
                res = get_first_node_color(course, color_matrix)
                if res:
                    color, hall_list = res
                else:
                    print("No schedule is possible")
                    break
            else:
                res = get_smallest_available_color(course, color_matrix, constraints)
                if res:
                    color, hall_list = res
                else:
                    color = None
                    course.flag = 0

            if color:
                num_colored_courses += 1
                if hall_list:
                    update_lecture_hall(hall_list, course, color)

        ordered_adj_list = course.ordered_adjacency_list()
        for adj_course in ordered_adj_list:
            if not adj_course.color and adj_course.flag:
                res = get_smallest_available_color(adj_course, color_matrix, constraints)
                if res:
                    color_cd, hall_list_cd = res
                else:
                    color_cd = None
                    adj_course.flag = 0

                if color_cd:
                    num_colored_courses += 1
                    if hall_list_cd:
                        update_lecture_hall(hall_list_cd, adj_course, color_cd)

    alloted_courses = []
    for day in range(MAX_SCHEDULE_DAYS):
        for slot in range(TIME_SLOTS):
            for course in color_matrix[day][slot].courses:
                alloted_courses.append(course)

    print(len(alloted_courses))
    unalloted_courses = list(set(sorted_courses) - set(alloted_courses))
    for c in unalloted_courses:
        c.flag = 1

    return sorted(
        unalloted_courses,
        key=lambda course: (course.degree, course.max_adjacency),
        reverse=True
    )


def hard_schedule(unalloted_courses, color_matrix):
    """
    Attempt to schedule remaining courses by progressively relaxing constraints.
    """
    constraints = ["check_consecutive", "check_three_exams", "check_dis_3"]
    unalloted_courses = schedule_exam(unalloted_courses, constraints, 0, color_matrix)

    constraints = ["check_three_exams"]
    unalloted_courses = schedule_exam(unalloted_courses, constraints, 1, color_matrix)

    constraints = ["check_dis_3"]
    unalloted_courses = schedule_exam(unalloted_courses, constraints, 1, color_matrix)

    constraints = ["check_consecutive"]
    unalloted_courses = schedule_exam(unalloted_courses, constraints, 2, color_matrix)

    constraints = [""]
    unalloted_courses = schedule_exam(unalloted_courses, constraints, 3, color_matrix)

    return len(unalloted_courses)


def get_first_node_color(course, color_matrix):
    """
    Assign the first available color to the first course.
    """
    for day in range(MAX_SCHEDULE_DAYS):
        for slot in range(TIME_SLOTS):
            color = color_matrix[day][slot]
            
            sorted_list = []
            for lh in color.lecture_halls:
                if lh.odd > 0:
                    sorted_list.append(((lh, 'o'), lh.odd_capacity))
                if lh.even > 0:
                    sorted_list.append(((lh, 'e'), lh.even_capacity))
            
            sorted_list.sort(key=lambda x: x[1], reverse=True)
            
            hall_list = get_lecture_hall(course.no_of_students, sorted_list)
            
            if hall_list:
                return color, hall_list

    return None