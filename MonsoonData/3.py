import json
import pandas as pd

def load_courses_from_json(json_file):
    """
    Reads courses.json, which is expected to be a dictionary with course codes as keys.
    Returns a set of course codes.
    """
    with open(json_file, 'r', encoding='cp1252') as f:
        data = json.load(f)
    # Keys are course codes
    return set(data.keys())

def load_courses_from_excel(excel_file):
    """
    Reads updated_list.xlsx, assumed to have the distinct course codes in the first column.
    Returns a set of course codes.
    """
    df = pd.read_excel(excel_file, engine='openpyxl')
    # Get the first column (assumed course codes), convert to string and strip any spaces.
    course_codes = df.iloc[:, 0].astype(str).str.strip()
    return set(course_codes)

def main():
    # File paths
    json_file = 'courses.json'
    excel_file = 'Book3.xlsx'
    
    # Load course codes from both sources
    courses_json_set = load_courses_from_json(json_file)
    updated_list_set = load_courses_from_excel(excel_file)
    
    # Compute differences
    json_not_in_excel = courses_json_set - updated_list_set
    excel_not_in_json = updated_list_set - courses_json_set
    
    # Print the differences
    print("Courses present in courses.json but not in updated_list.xlsx:")
    if json_not_in_excel:
        for course in sorted(json_not_in_excel):
            print(course)
    else:
        print("None")
    
    print("\nCourses present in updated_list.xlsx but not in courses.json:")
    if excel_not_in_json:
        for course in sorted(excel_not_in_json):
            print(course)
    else:
        print("None")

if __name__ == '__main__':
    main()
