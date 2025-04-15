import csv
import json
import os

def load_pairs_from_csv(file_path):
    """
    Reads a CSV file with headers:
    "admn_no","first_name","middle_name","last_name",
    "domain_name","sub_code","sub_name","sub_type"
    and returns a list of dictionaries containing only the admn_no and sub_code.
    """
    pairs = []
    with open(file_path, 'r', newline='', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            admn_no = row.get("admn_no", "").strip()
            sub_code = row.get("sub_code", "").strip()
            if admn_no and sub_code:
                pairs.append({"admn_no": admn_no, "sub_code": sub_code})
    return pairs

def save_json(data, file_path):
    """Saves the given data to a JSON file with indentation for readability.
       Ensures the destination directory exists."""
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    with open(file_path, 'w', encoding='cp1252') as f:
        json.dump(data, f, indent=4)

def update_pairs_with_common_courses(pairs, common_csv):
    """
    Reads common.csv which has format:
    "id","session","session_year","combine_sub_code",
    "offered_to_name","co_emp_id","emp_dept","assign_by",
    "status","created_at","updated_at"

    For each row, the 4th column (combine_sub_code) contains a comma-separated list
    of course codes (with no extra spaces).
    For each code in that list, all occurrences in pairs should be replaced with the first code.
    """
    with open(common_csv, 'r', newline='', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            combine_field = row.get("combine_sub_code", "").strip()
            if not combine_field:
                continue
            codes = combine_field.split(',')
            if not codes:
                continue
            primary_code = codes[0]  # First code from the list
           
            for code in codes:
                for pair in pairs:
                    if pair["sub_code"] == code:
                        pair["sub_code"] = primary_code
    return pairs

def build_courses_and_students(pairs):
    """
    From the pairs data (a list of dicts with keys: admn_no and sub_code),
    build two dictionaries:
    - courses: keys are course codes and values are lists of student ids.
    - students: keys are student ids and values are lists of course codes.
    """
    courses = {}
    students = {}
    
    for pair in pairs:
        admn_no = pair["admn_no"]
        sub_code = pair["sub_code"]
        courses.setdefault(sub_code, []).append(admn_no)
        students.setdefault(admn_no, []).append(sub_code)
    return courses, students

def process_student_files(nep_file_path, common_file_path, cbcs_file_path=None):
   
    

    pairs = []
    pairs.extend(load_pairs_from_csv(nep_file_path))
     
    if cbcs_file_path and os.path.exists(cbcs_file_path):
        pairs.extend(load_pairs_from_csv(cbcs_file_path))
     
    pairs_json_path = os.path.join("..", "data", "pairs.json")
    save_json(pairs, pairs_json_path)
    print(f"Initial pairs saved to {pairs_json_path}.")
 
    pairs = update_pairs_with_common_courses(pairs, common_file_path)
    save_json(pairs, pairs_json_path)
    print(f"Updated pairs with common course mappings saved to {pairs_json_path}.")
 
    courses, students = build_courses_and_students(pairs)
    courses_json_path = os.path.join("..", "data", "data_course.json")
    students_json_path = os.path.join("..", "data", "data_student.json")
    save_json(courses, courses_json_path)
    save_json(students, students_json_path)
    print(f"Courses data saved to {courses_json_path}.")
    print(f"Students data saved to {students_json_path}.")

    unique_courses_count = len(courses)
    print(f"Number of unique courses in {courses_json_path}: {unique_courses_count}")

    return unique_courses_count
 
if __name__ == "__main__":
  
    process_student_files("nep.csv", "common.csv", "cbcs.csv")
