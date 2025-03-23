import csv
import json
from collections import defaultdict

def process_csv(input_csv, student_json, course_json):
    students = defaultdict(list)
    courses = defaultdict(list)
    
    with open(input_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            roll_number = row.get('admn_no', '').strip()
            course = row.get('sub_code', '').strip()
            
            # Validate roll_number and course
            if len(roll_number) == 8 and len(course) == 6:
                # Store student-course mapping
                if course not in students[roll_number]:
                    students[roll_number].append(course)
                
                # Store course-student mapping
                if roll_number not in courses[course]:
                    courses[course].append(roll_number)
    
    # Write to JSON files
    with open(student_json, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4)
    
    with open(course_json, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=4)

# Example usage
process_csv('students.csv', 'students.json', 'courses.json')
