from utils import (
    build_weight_matrix,
    calculate_degree,
    initialize_colors,
    initialize_students,
    initialize_lecture_halls,
    output_to_csv,
    MAX_SCHEDULE_DAYS,
    TIME_SLOTS
)
from scheduler import hard_schedule

def main():
    
    graph, course_list, course_index = build_weight_matrix()

    # Calculate degrees for prioritizing course scheduling
    calculate_degree(graph, course_list)
    print("Total Courses:", len(course_list))

    # Sort courses based on degree and maximum adjacency
    sorted_courses = sorted(
        course_list,
        key=lambda course: (course.degree, course.max_adjacency),
        reverse=True
    )

    # Initialize colors (time slots) and lecture halls
    color_matrix = initialize_colors()
    initialize_students(course_index)
    initialize_lecture_halls(color_matrix)

    # Perform scheduling
    no_of_unscheduled_courses = hard_schedule(sorted_courses, color_matrix)

    if no_of_unscheduled_courses != 0:
        print("Increase days or slots.", no_of_unscheduled_courses, "courses remain unscheduled")

    # Print and output schedule
    for course in course_list:
        if course.lecture_halls:
            res = f"{course.course_code} :: Day {course.color.day + 1} Slot {course.color.slot + 1}, Rooms :"
            for hall, position in course.lecture_hall.items():
                res += f" L{hall.number} {position}"
            res += f" Strength: {course.no_of_students}"
            print(res)
    print("\n")

    # Export the schedule to CSV
    output_to_csv(TIME_SLOTS, MAX_SCHEDULE_DAYS, color_matrix)

    # Additional printing and testing
    alloted_courses = []
    count = 0
    for day in range(MAX_SCHEDULE_DAYS):
        for slot in range(TIME_SLOTS):
            courses_in_slot = color_matrix[day][slot].courses
            students_in_slot = sum([course.no_of_students for course in courses_in_slot])
            alloted_courses.extend(courses_in_slot)
            course_codes = [course.course_code for course in courses_in_slot]
            print(f"Day {day + 1} Slot {slot + 1} : Courses : {course_codes}, Students : {students_in_slot}")
            count += len(courses_in_slot)
    print("Total Courses:", count)

    #test_for_clash(student_list, TIME_SLOTS)
    #test_constraints(student_list, TIME_SLOTS)


if __name__ == "__main__":
    main()