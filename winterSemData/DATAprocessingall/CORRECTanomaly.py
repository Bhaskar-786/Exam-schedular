import pandas as pd
import re

 
cbcs_df = pd.read_csv("Student_cbcs.csv")
nep_df = pd.read_csv("Student_nep.csv")

 
cbcs_course_pattern = r"^[A-Z]{3}\d{3}$"
nep_course_pattern = r"^N[A-Z]{3}\d{3}$"

 
def validate_pattern(df, column, pattern):
    return df[~df[column].astype(str).str.match(pattern, na=False)]

 
def clean_course_codes(df, column):
    df[column] = df[column].astype(str).str.strip().str.rstrip('.')

 
clean_course_codes(cbcs_df, "sub_code")
clean_course_codes(nep_df, "sub_code")

 
cbcs_course_anomalies = validate_pattern(cbcs_df, "sub_code", cbcs_course_pattern)
nep_course_anomalies = validate_pattern(nep_df, "sub_code", nep_course_pattern)
 
def print_anomalies(df, message):
    if not df.empty:
        print(message)
        print(df.to_string(index=False))

print("Anomalies detected after cleaning:")
print_anomalies(cbcs_course_anomalies, " - Invalid CBCS course codes:")
print_anomalies(nep_course_anomalies, " - Invalid NEP course codes:")

 
cbcs_df.to_csv("students_cbcs_cleaned.csv", index=False)
nep_df.to_csv("students_nep_cleaned.csv", index=False)
