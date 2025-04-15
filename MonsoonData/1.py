import csv
import json

def load_pairs_from_csv(file_path):
    """
    Reads a CSV file with headers:
    "admn_no","first_name","middle_name","last_name",
    "domain_name","sub_code","sub_name","sub_type"
    and returns a list of pairs containing only the admn_no and sub_code.
    """
    pairs = []
    with open(file_path, 'r', newline='', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get student id and subject code, strip any extra whitespace
            admn_no = row.get("admn_no", "").strip()
            sub_code = row.get("sub_code", "").strip()
            if admn_no and sub_code:
                pairs.append({"admn_no": admn_no, "sub_code": sub_code})
    return pairs

def save_json(data, file_path):
    """Saves the given data to a JSON file with indentation for readability."""
    with open(file_path, 'w', encoding='cp1252') as f:
        json.dump(data, f, indent=4)

def update_pairs_with_common_courses(pairs, common_csv):
    """
    Reads common.csv which has format:
    "id","session","session_year","combine_sub_code",
    "offered_to_name","co_emp_id","emp_dept","assign_by",
    "status","created_at","updated_at"
    
    For each row, the 4th column (combine_sub_code) contains a comma-separated list
    of course codes (without any extra spaces).
    For each code in that list, all occurrences in pairs should be replaced with the first code.
    """
    with open(common_csv, 'r', newline='', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            combine_field = row.get("combine_sub_code", "").strip()
            if not combine_field:
                continue
            # Split using comma; since there is no extra spaces, simple split works.
            codes = combine_field.split(',')
            if not codes:
                continue
            primary_code = codes[0]  # first code from the list
            # For each course code in the list, update pairs where it appears
            for code in codes:
                for pair in pairs:
                    if pair["sub_code"] == code:
                        pair["sub_code"] = primary_code
    return pairs

def build_courses_and_students(pairs):
    """
    From the pairs data (a list of dicts with keys: admn_no and sub_code),
    build two dictionaries:
    
    courses: keys are course codes and values are lists of student ids.
    students: keys are student ids and values are lists of course codes.
    """
    courses = {}
    students = {}
    
    for pair in pairs:
        admn_no = pair["admn_no"]
        sub_code = pair["sub_code"]
        
        # Add student to course entry
        if sub_code not in courses:
            courses[sub_code] = []
        courses[sub_code].append(admn_no)
        
        # Add course to student entry
        if admn_no not in students:
            students[admn_no] = []
        students[admn_no].append(sub_code)
        
    return courses, students

def main():
    # Step 1: Combine cbcs.csv and nep.csv into pairs
    cbcs_file = 'cbcs.csv'
    nep_file = 'nep.csv'
    
    pairs = []
    pairs.extend(load_pairs_from_csv(cbcs_file))
    pairs.extend(load_pairs_from_csv(nep_file))
    
    # Save the initial pairs to pairs.json
    pairs_json_file = 'pairs.json'
    save_json(pairs, pairs_json_file)
    print(f"Initial pairs saved to {pairs_json_file}.")
    
    # Step 2: Process common.csv and update the pairs accordingly
    common_file = 'common.csv'
    pairs = update_pairs_with_common_courses(pairs, common_file)
    
    # Overwrite the pairs.json with updated subject codes
    save_json(pairs, pairs_json_file)
    print(f"Updated pairs with common course mappings saved to {pairs_json_file}.")
    
    # Step 3: Build courses.json and students.json from the updated pairs
    courses, students = build_courses_and_students(pairs)
    
    courses_json_file = 'courses.json'
    students_json_file = 'students.json'
    
    save_json(courses, courses_json_file)
    save_json(students, students_json_file)
    
    # Print the number of unique courses found (keys in courses.json)
    unique_courses_count = len(courses)
    print(f"Courses data saved to {courses_json_file}.")
    print(f"Students data saved to {students_json_file}.")
    print(f"Number of unique courses in {courses_json_file}: {unique_courses_count}")

if __name__ == "__main__":
    main()
