import sys
from utils import (
    build_weight_matrix,
    calculate_degree,
    initialize_colors,
    initialize_students,
    initialize_lecture_halls,
    output_to_csv,
    convert_lecture_hall_to_csv,
)
from scheduler import hard_schedule

def main(max_days, max_slots):
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
    color_matrix = initialize_colors(max_days, max_slots)
    initialize_students(course_index, max_days, max_slots)
    initialize_lecture_halls(color_matrix,max_days, max_slots)

    # Perform scheduling
    no_of_unscheduled_courses = hard_schedule(sorted_courses, color_matrix, max_days, max_slots)

    if no_of_unscheduled_courses != 0:
        print(f"Unable to schedule {no_of_unscheduled_courses} courses. Consider increasing the number of days or slots.")

    # Prepare schedule data for output
    schedule_data = []
    for day in range(max_days):
        for slot in range(max_slots):
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
                    "Position": "Left" if position == 'o' else "Right" if position == 'e' else "Single",
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

    # Export the schedule to CSV
    output_to_csv(max_slots, max_days, color_matrix)
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
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    slots = int(sys.argv[2]) if len(sys.argv) > 1 else 2
    main(days, slots)
