import pandas as pd
import re

 
cbcs_df = pd.read_csv("students_cbcs_cleaned.csv")
nep_df = pd.read_csv("students_nep_cleaned.csv")
 
admn_no_pattern = r"^\d{2}[A-Z]{2}\d{4}$"
cbcs_course_pattern = r"^[A-Z]{3}\d{3}$"
nep_course_pattern = r"^N[A-Z]{3}\d{3}$"
 
def validate_pattern(df, column, pattern):
    return df[~df[column].astype(str).str.match(pattern, na=False)]
 
admn_no_anomalies_cbcs = validate_pattern(cbcs_df, "admn_no", admn_no_pattern)
admn_no_anomalies_nep = validate_pattern(nep_df, "admn_no", admn_no_pattern)

cbcs_course_anomalies = validate_pattern(cbcs_df, "sub_code", cbcs_course_pattern)
nep_course_anomalies = validate_pattern(nep_df, "sub_code", nep_course_pattern)
 
def print_anomalies(df, message):
    if not df.empty:
        print(message)
        print(df.to_string(index=False))

print("Anomalies detected:")
print_anomalies(admn_no_anomalies_cbcs, " - Invalid admission numbers in CBCS data:")
print_anomalies(admn_no_anomalies_nep, " - Invalid admission numbers in NEP data:")
print_anomalies(cbcs_course_anomalies, " - Invalid CBCS course codes:")
print_anomalies(nep_course_anomalies, " - Invalid NEP course codes:")
