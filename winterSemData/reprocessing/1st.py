import csv
import json
import re

# File names
cbcs_file = "students_cbcs_cleaned.csv"
nep_file = "students_nep_cleaned.csv"

# Output file
output_file = "student_course_pairs.json"

# Regex for valid 6-character course code
course_pattern = re.compile(r'^[A-Z]{3}[0-9]{3}')

# Set to store distinct course codes
distinct_courses = set()

# List to store final student-course mappings
student_course_pairs = []

# Function to clean and validate course code
def clean_course_code(code, is_nep):
    # Remove starting 'N' if NEP
    if is_nep and code.startswith('N'):
        code = code[1:]

    # Match first valid 6-character course code
    match = course_pattern.match(code)
    if match:
        return match.group(0)
    else:
        return None

# Function to process a file
def process_file(filename, is_nep):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            admn_no = row["admn_no"].strip()
            raw_code = row["sub_code"].strip()
            cleaned_code = clean_course_code(raw_code, is_nep)

            if cleaned_code:
                student_course_pairs.append({
                    "student": admn_no,
                    "course": cleaned_code
                })
                distinct_courses.add(cleaned_code)

# Process both files
process_file(cbcs_file, is_nep=False)
process_file(nep_file, is_nep=True)

# Write to JSON
with open(output_file, mode='w', encoding='utf-8') as f:
    json.dump(student_course_pairs, f, indent=4)

# Print result
print(f"Processed {len(student_course_pairs)} student-course pairs.")
print(f"Number of distinct course codes: {len(distinct_courses)}")
