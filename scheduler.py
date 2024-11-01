# scheduler.py

import logging
import csv
from typing import List, Dict, Set
from constraints import Constraints
from models.course import Course
from models.color import Color
from models.student import Student
from models.lecture_hall import LectureHall


class Scheduler:
    def __init__(self, courses: List[Course], lecture_halls: List[LectureHall],
                 students: List[Student], max_days: int, time_slots: int):
        self.courses = courses
        self.lecture_halls = lecture_halls
        self.students = students
        self.max_days = max_days
        self.time_slots = time_slots
        self.logger = self.setup_logger()
        self.color_matrix = [[Color(day, slot) for slot in range(time_slots)] for day in range(max_days)]
        self.constraints = Constraints(self)
        self.course_index = {course.course_code: course for course in courses}

        # Initialize available halls for each color
        for day in range(max_days):
            for slot in range(time_slots):
                self.color_matrix[day][slot].available_halls = lecture_halls.copy()

    @staticmethod
    def setup_logger():
        logger = logging.getLogger('SchedulerLogger')
        logger.setLevel(logging.DEBUG)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('scheduler.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)

        # Create formatters and add to handlers
        c_format = logging.Formatter('%(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        if not logger.handlers:
            logger.addHandler(c_handler)
            logger.addHandler(f_handler)

        return logger

    def build_conflict_graph(self):
        """
        Constructs the conflict graph based on common students between courses.
        Updates each course's conflict set.
        """
        self.logger.debug("Building conflict graph...")
        for i, course1 in enumerate(self.courses):
            for course2 in self.courses[i+1:]:
                if course1.student_list.intersection(course2.student_list):
                    course1.conflicts.add(course2)
                    course2.conflicts.add(course1)
                    self.logger.debug(
                        f"Conflict added between {course1.course_code} and {course2.course_code}"
                    )
        self.logger.info("Conflict graph built successfully.")

    def calculate_degrees(self):
        """
        Calculates the degree (number of conflicts) for each course.
        """
        self.logger.debug("Calculating degrees for each course...")
        for course in self.courses:
            course.degree = len(course.conflicts)
            self.logger.debug(f"Course {course.course_code} has degree {course.degree}")
        self.logger.info("Degrees calculated successfully.")

    def schedule_courses(self):
        """
        Main method to schedule all courses based on constraints.
        """
        self.build_conflict_graph()
        self.calculate_degrees()

        # Sort courses by descending degree (more constrained courses first)
        sorted_courses = sorted(self.courses, key=lambda c: c.degree, reverse=True)
        self.logger.info("Courses sorted based on degree for scheduling.")

        unscheduled_courses = []

        for course in sorted_courses:
            self.logger.debug(f"Attempting to schedule course {course.course_code}")
            scheduled = False
            for day in range(self.max_days):
                for slot in range(self.time_slots):
                    color = self.color_matrix[day][slot]
                    if self.constraints.is_suitable(course, color):
                        # Assign the course to this color (day and slot)
                        color.courses.append(course)
                        course.assigned_color = color

                        # Allocate lecture halls based on capacity
                        if self.allocate_lecture_halls(course, color):
                            self.logger.info(f"Scheduled {course.course_code} on Day {day + 1}, Slot {slot + 1}")
                            scheduled = True
                            break
                        else:
                            # Unable to allocate halls even if color is suitable
                            color.courses.remove(course)
                            course.assigned_color = None
                            self.logger.debug(
                                f"Room allocation failed for {course.course_code} on Day {day + 1}, Slot {slot + 1}"
                            )
                if scheduled:
                    break
            if not scheduled:
                self.logger.error(f"Could not schedule {course.course_code}. Consider increasing days or slots.")
                unscheduled_courses.append(course)

        if unscheduled_courses:
            self.logger.warning(f"{len(unscheduled_courses)} courses could not be scheduled.")
        else:
            self.logger.info("All courses scheduled successfully.")

        return unscheduled_courses

    def allocate_lecture_halls(self, course: Course, color: Color) -> bool:
        """
        Allocates lecture halls to the course based on the number of students.
        Returns True if allocation is successful, False otherwise.
        """
        required_capacity = course.no_of_students
        allocated_halls = []

        # Sort available halls by descending capacity to minimize number of halls used
        sorted_halls = sorted(color.available_halls, key=lambda h: h.capacity, reverse=True)

        for hall in sorted_halls:
            if hall.capacity >= required_capacity:
                allocated_halls.append(hall)
                color.available_halls.remove(hall)
                required_capacity = 0
                break
            else:
                allocated_halls.append(hall)
                color.available_halls.remove(hall)
                required_capacity -= hall.capacity

            if required_capacity <= 0:
                break

        if required_capacity > 0:
            # Not enough capacity available
            self.logger.debug(
                f"Insufficient capacity for course {course.course_code} in Day {color.day + 1}, Slot {color.slot + 1}"
            )
            # Revert allocated halls back to available halls
            for hall in allocated_halls:
                color.available_halls.append(hall)
            return False

        # Assign allocated halls to the course
        course.lecture_halls = allocated_halls
        self.logger.debug(
            f"Allocated halls {[hall.hall_id for hall in allocated_halls]} to course {course.course_code}"
        )
        return True

    def output_schedule(self, filename: str = "schedule.csv"):
        """
        Outputs the final schedule to a CSV file.
        """
        self.logger.debug(f"Generating schedule output to {filename}...")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Day", "Slot", "Course Code", "Lecture Halls", "Number of Students"])

            for day in range(self.max_days):
                for slot in range(self.time_slots):
                    color = self.color_matrix[day][slot]
                    for course in color.courses:
                        hall_ids = ', '.join([hall.hall_id for hall in course.lecture_halls])
                        writer.writerow([
                            day + 1,
                            slot + 1,
                            course.course_code,
                            hall_ids,
                            course.no_of_students
                        ])
        self.logger.info(f"Schedule successfully written to {filename}.")

    def display_schedule(self):
        """
        Displays the schedule in a readable format.
        """
        print("\nFinal Schedule:")
        for day in range(self.max_days):
            for slot in range(self.time_slots):
                color = self.color_matrix[day][slot]
                if color.courses:
                    print(f"Day {day + 1}, Slot {slot + 1}:")
                    for course in color.courses:
                        hall_ids = ', '.join([hall.hall_id for hall in course.lecture_halls])
                        print(f"  - {course.course_code} | Halls: {hall_ids} | Students: {course.no_of_students}")
        print("")

    def export_schedule(self, filename: str = "schedule.csv"):
        """
        Exports the schedule to a CSV file.
        """
        self.output_schedule(filename)

    def run(self):
        """
        Executes the scheduling process.
        """
        self.logger.info("Starting the scheduling process...")
        unscheduled = self.schedule_courses()
        if not unscheduled:
            self.display_schedule()
            self.export_schedule()
        else:
            self.logger.error(f"Scheduling completed with {len(unscheduled)} unscheduled courses.")
            self.display_schedule()
            self.export_schedule()
            # Optionally, handle unscheduled courses (e.g., reschedule, notify user)


# Example usage
if __name__ == "__main__":
    # Example data initialization (Replace with actual data loading mechanisms)
    # Initialize Lecture Halls
    lecture_halls = [
        LectureHall(hall_id="LH1", capacity=100),
        LectureHall(hall_id="LH2", capacity=80),
        LectureHall(hall_id="LH3", capacity=60),
        LectureHall(hall_id="LH4", capacity=40),
    ]

    # Initialize Students
    students = [
        Student(student_id="S1", enrolled_courses={"C1", "C2", "C3"}),
        Student(student_id="S2", enrolled_courses={"C1", "C4"}),
        Student(student_id="S3", enrolled_courses={"C2", "C3"}),
        # Add more students as needed
    ]

    # Initialize Courses
    courses = [
        Course(course_code="C1", student_list={"S1", "S2"}, no_of_students=2),
        Course(course_code="C2", student_list={"S1", "S3"}, no_of_students=2),
        Course(course_code="C3", student_list={"S1", "S3"}, no_of_students=2),
        Course(course_code="C4", student_list={"S2"}, no_of_students=1),
        # Add more courses as needed
    ]

    # Initialize Scheduler
    max_days = 5  # For example, 5 days
    time_slots = 3  # For example, 3 time slots per day

    scheduler = Scheduler(
        courses=courses,
        lecture_halls=lecture_halls,
        students=students,
        max_days=max_days,
        time_slots=time_slots
    )

    # Run the scheduler
    scheduler.run()
