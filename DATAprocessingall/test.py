import json

def validate_consistency(student_json, course_json, output_json):
    with open(student_json, 'r', encoding='utf-8') as f:
        students = json.load(f)

    with open(course_json, 'r', encoding='utf-8') as f:
        courses = json.load(f)

    student_course_pairs = set()
    course_student_pairs = set()

     
    for student, courses_list in students.items():
        for course in courses_list:
            student_course_pairs.add((student, course))

     
    for course, students_list in courses.items():
        for student in students_list:
            course_student_pairs.add((student, course))

    
    if student_course_pairs == course_student_pairs:
        print(" Data is consistent between students.json and courses.json")
    else:
        print(" Inconsistency detected!")
        extra_in_students = student_course_pairs - course_student_pairs
        extra_in_courses = course_student_pairs - student_course_pairs

        if extra_in_students:
            print("Entries in students.json but missing in courses.json:", extra_in_students)

        if extra_in_courses:
            print("Entries in courses.json but missing in students.json:", extra_in_courses)

     
    student_course_list = [{"student": student, "course": course} for student, course in sorted(student_course_pairs)]

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(student_course_list, f, indent=4)

    print(f" Student-course pairs saved in {output_json}")

 
validate_consistency('students.json', 'courses.json', 'student_course_pairs.json')
