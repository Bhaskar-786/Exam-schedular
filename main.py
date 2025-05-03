import sys
from collections import defaultdict
from utils import (
    build_weight_matrix,
    calculate_degree,
    initialize_colors,
    initialize_students,
    initialize_lecture_halls,
    output_to_csv,
    convert_lecture_hall_to_csv,
    convert_seating_plan_to_csv
)
from scheduler import hard_schedule
import os

def main(max_days, max_slots):
    os.makedirs("bounds", exist_ok=True)
    summary_file = "bounds/scheduling_summary.txt"

    with open(summary_file, "w") as f:
        f.write("Scheduling Summary\n")
        f.write("===================\n")

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
        raise ValueError(
            f"{no_of_unscheduled_courses} course(s) could not be scheduled. "
            "Consider increasing the number of days or time slots."
        )
        


    """# Prepare schedule data for output
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
                    })"""
    
    schedule_data = []
    total_no_of_slots = 0
    for day in range(max_days):
        for slot in range(max_slots):
            courses_in_slot = color_matrix[day][slot].courses
            if courses_in_slot:
                total_no_of_slots += 1
                for course in courses_in_slot:
                    schedule_data.append({
                        'Course Code': course.course_code,
                        'Students': course.no_of_students,
                        'Day': day + 1,
                        'Slot': slot + 1
                    })

    with open("bounds/scheduling_summary.txt", mode='a') as f:
        f.write(f"Total no. of slots: {total_no_of_slots}\n")

    """schedule_lecture_hall = []
    for course in course_list:
        for hall, seating_info in course.lecture_hall.items():
            for position, seat_taken in seating_info.items():  # Iterate through seat allocations
                schedule_lecture_hall.append({
                    "Course Code": course.course_code,
                    "Lecture Hall": hall.number,
                    "Position": "Left" if position == 'o' else "Right" if position == 'e' else "Single",
                    "No. of seats": seat_taken
                })"""
    
    # Grouping schedule by day and slot, sorted by course code
    schedule_lecture_hall = defaultdict(lambda: defaultdict(list))
    max_LH = 0
    for day in range(max_days):
        for slot in range(max_slots):
            courses_in_slot = color_matrix[day][slot].courses
            if courses_in_slot:
                LH_list = set()
                for course in courses_in_slot:
                    # Create a list to store lecture hall details for each course
                    hall_numbers = []
                    for hall, seating_info in course.lecture_hall.items():
                        LH_list.add(f"{hall.number}")
                        for position, seat_taken in seating_info.items():
                            if f"{hall.number}" not in hall_numbers:
                                hall_numbers.append(f"{hall.number}")

                    # Join the hall numbers into a string
                    venue = ", ".join(hall_numbers)
                
                    # Sort by course code before appending
                    schedule_lecture_hall[day][slot].append({
                        "Course Code": course.course_code,
                        "No. of Students": course.no_of_students,
                        "Venue": venue
                    })
                max_LH = max(max_LH, len(LH_list))
            schedule_lecture_hall[day][slot].sort(key=lambda x: x["Course Code"])

    with open("bounds/scheduling_summary.txt", mode='a') as f:
        f.write(f"Max lecture halls used at any slot: {max_LH}\n")
    
    # Grouping schedule by day and slot, sorted by course code
    schedule_seating_plan = defaultdict(lambda: defaultdict(list))

    for day in range(max_days):
        for slot in range(max_slots):
            courses_in_slot = color_matrix[day][slot].courses
            if courses_in_slot:
                for course in courses_in_slot:
                    for hall, seating_info in course.lecture_hall.items():
                        for position, seat_taken in seating_info.items():  # Iterate through seat allocations
                            schedule_seating_plan[day][slot].append({
                                "Course Code": course.course_code,
                                "Lecture Hall": hall.number,
                                "Position": "Left" if position == 'o' else "Right" if position == 'e' else "Single",
                                "No. of seats": seat_taken
                            })
            schedule_seating_plan[day][slot].sort(key=lambda x: x["Course Code"])


    # Sort schedule data by Day and Slot
    #schedule_data.sort(key=lambda x: (x['Day'], x['Slot']))
    schedule_data.sort(key=lambda x: (x['Course Code']))

    # Sort schedule lecture hall by Course and Lecture Hall
    #schedule_lecture_hall.sort(key=lambda x: (x['Course Code']))

    # Print schedule in a table format
    print("\nExam Schedule:")
    print(f"{'Course Code':<10} {'Students':<10} {'Day':<5} {'Slot':<5}")
    print("-" * 40)
    for item in schedule_data:
        print(f"{item['Course Code']:<10} {item['Students']:<10} {item['Day']:<5} {item['Slot']:<5}")

    # Print Lecture Hall in a table format
    print("\nLecture Hall Schedule:")
    print(f"{'Day':<10} {'Slot':<10} {'Course Code':<15} {'No. of Students':<15} {'Venue':<40}")
    print("-" * 80)

    # Iterate through each day and slot
    for day in range(max_days):
        for slot in range(max_slots):
            # Get the courses in the current day and slot
            courses_in_slot = schedule_lecture_hall[day][slot]
        
            # If there are courses in this day and slot, print them
            if courses_in_slot:
                for course in courses_in_slot:
                    print(f"Day {day + 1:<6} Slot {slot + 1:<6} {course['Course Code']:<15} {course['No. of Students']:<15} {course['Venue']:<40}")

    # Print Lecture Hall in a table format
    print("\nSeating Plan:")
    print(f"{'Day':<10} {'Slot':<10} {'Course Code':<15} {'Lecture Hall':<20} {'Position':<10} {'No. of seats':<10}")
    print("-" * 80)

    # Iterate through each day and slot
    for day in range(max_days):
        for slot in range(max_slots):
            # Get the courses in the current day and slot
            courses_in_slot = schedule_seating_plan[day][slot]
    
            # If there are courses in this day and slot, print them
            if courses_in_slot:
                for course in courses_in_slot:
                    print(f"Day {day + 1:<6} Slot {slot + 1:<6} {course['Course Code']:<15} {course['Lecture Hall']:<20} {course['Position']:<10} {course['No. of seats']:<10}")


    # Export the schedule to CSV
    output_to_csv(schedule_data)
    convert_lecture_hall_to_csv(max_days,max_slots,schedule_lecture_hall,'lecture_hall_schedule.csv')
    convert_seating_plan_to_csv(max_days,max_slots,schedule_seating_plan,'seating_plan.csv')

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
    days = int(sys.argv[1]) if len(sys.argv) > 0 else 8
    slots = int(sys.argv[2]) if len(sys.argv) > 0 else 2
    main(days, slots)
