import pandas as pd
import json


cbcs_df = pd.read_csv("students_cbcs_cleaned.csv")
nep_df = pd.read_csv("students_nep_cleaned.csv")
 
def normalize_course(course_code):
    return course_code[1:] if course_code.startswith("N") else course_code
 
nep_df["sub_code"] = nep_df["sub_code"].apply(normalize_course)
 
combined_df = pd.concat([cbcs_df, nep_df]).drop_duplicates()
 
student_courses = combined_df.groupby("admn_no")["sub_code"].apply(list).to_dict()
 
course_students = combined_df.groupby("sub_code")["admn_no"].apply(list).to_dict()
 
with open("students.json", "w") as f:
    json.dump(student_courses, f, indent=4)

with open("courses.json", "w") as f:
    json.dump(course_students, f, indent=4)

print("JSON files generated successfully!")
