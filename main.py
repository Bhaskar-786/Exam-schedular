from utils import (
    build_weight_matrix,
    calculate_degree,
    initialize_colors,
    initialize_students,
    initialize_lecture_halls,
    output_to_csv,
    convert_lecture_hall_to_csv,
    MAX_SCHEDULE_DAYS,
    TIME_SLOTS
)
from scheduler import hard_schedule

def main():
    graph, course_list, course_index = build_weight_matrix()

    # Calculate degrees for prioritizing course scheduling
    calculate_degree(graph, course_list)

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
        print(f"Unable to schedule {no_of_unscheduled_courses} courses. Consider increasing the number of days or slots.")

    # Prepare schedule data for output
    schedule_data = []
    for day in range(MAX_SCHEDULE_DAYS):
        for slot in range(TIME_SLOTS):
            courses_in_slot = color_matrix[day][slot].courses
            if courses_in_slot:
                for course in courses_in_slot:
                    schedule_data.append({
                        'Day': day + 1,
                        'Slot': slot + 1,
                        'Course Code': course.course_code,
                        'Students': course.no_of_students
                    })

    schedule_lecture_hall = []
    for course in course_list:
        for hall, seating_info in course.lecture_hall.items():
            for position, seat_taken in seating_info.items():  # Iterate through seat allocations
                schedule_lecture_hall.append({
                    "Course Code": course.course_code,
                    "Lecture Hall": hall.number,
                    "Position": "Left" if position == 'o' else "Right",
                    "No. of seats": seat_taken
                })


    # Sort schedule data by Day and Slot
    schedule_data.sort(key=lambda x: (x['Day'], x['Slot']))

    # Sort schedule lecture hall by Course and Lecture Hall
    schedule_lecture_hall.sort(key=lambda x: (x['Course Code']))

    # Print schedule in a table format
    print("\nExam Schedule:")
    print(f"{'Day':<5} {'Slot':<5} {'Course Code':<10} {'Students':<10}")
    print("-" * 40)
    for item in schedule_data:
        print(f"{item['Day']:<5} {item['Slot']:<5} {item['Course Code']:<10} {item['Students']:<10}")

    # Print Lecture Hall in a table format
    print("\nLecture Hall Schedule:")
    print(f"{'Course Code':<10} {'Lecture Hall':<10} {'Position':<10} {'No. of seats':<10}")
    print("-" * 40)
    for item in schedule_lecture_hall:
        print(f"{item['Course Code']:<10} {item['Lecture Hall']:<10} {item['Position']:<10} {item['No. of seats']:<10}")

    """"
    # Print schedule for the first three students
    print("\nSchedules for the first three students:")
    student_ids = ['S1', 'S2', 'S3']
    for student_id in student_ids:
        student_courses = []
        for course in course_list:
            if student_id in course.student_list:
                student_courses.append({
                    'Course Code': course.course_code,
                    'Day': course.color.day + 1 if course.color else None,
                    'Slot': course.color.slot + 1 if course.color else None
                })
        print(f"\nStudent {student_id}:")
        if student_courses:
            for sc in student_courses:
                if sc['Day'] and sc['Slot']:
                    print(f"  {sc['Course Code']}: Day {sc['Day']}, Slot {sc['Slot']}")
                else:
                    print(f"  {sc['Course Code']}: Not scheduled")
        else:
            print("  No courses found for this student.")"
        """

    # Export the schedule to CSV
    output_to_csv(TIME_SLOTS, MAX_SCHEDULE_DAYS, color_matrix)
    convert_lecture_hall_to_csv(schedule_lecture_hall,'lecture_hall_schedule.csv')

    # Optionally, print total number of scheduled courses
    total_scheduled_courses = len(schedule_data)
    total_courses = len(course_list)
    unscheduled_courses = total_courses - total_scheduled_courses
    print(f"\nTotal Scheduled Courses: {total_scheduled_courses}")
    if unscheduled_courses > 0:
        print(f"Total Unscheduled Courses: {unscheduled_courses}")
    else:
        print("All courses have been scheduled successfully.")

if __name__ == "__main__":
    main()
