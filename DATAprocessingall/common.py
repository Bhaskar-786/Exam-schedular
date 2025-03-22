import pandas as pd

 
cbcs_df = pd.read_csv("Student_cbcs.csv")
nep_df = pd.read_csv("Student_nep.csv")

 
cbcs_courses = set(cbcs_df["sub_code"].unique())
nep_courses = set(nep_df["sub_code"].unique())

 
common_courses = []
for course in cbcs_courses:
    nep_equivalent = "N" + course
    if nep_equivalent in nep_courses:
        common_courses.append((course, nep_equivalent))

 
print("Common CBCS and NEP Courses:")
for cbcs, nep in common_courses:
    print(f"CBCS: {cbcs}  <-->  NEP: {nep}")
