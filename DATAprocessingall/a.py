import json

 
with open('student_course_pairs.json', 'r') as file:
    data = json.load(file)
 
pair_count = len(data)
 
distinct_courses = set(item['course'] for item in data)
distinct_course_count = len(distinct_courses)
 
print(f"Number of student-course pairs: {pair_count}")
print(f"Number of distinct courses: {distinct_course_count}")
