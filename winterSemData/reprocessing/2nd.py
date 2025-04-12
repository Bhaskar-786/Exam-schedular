import pandas as pd
import re
 
df = pd.read_excel('courses.xlsx', header=None, names=['course'])
 
df.dropna(inplace=True)
 
def clean_course(code):
    code = str(code).strip()
    if code.startswith('N'):
        code = code[1:]
    code = re.sub(r'[^A-Za-z0-9]', '', code)  # Remove any non-alphanumeric characters
    code = code[:6]  # Take only the first 6 characters
    return code.upper()

df['course'] = df['course'].apply(clean_course)

# Regex pattern for valid course code: 3 letters + 3 digits
valid_pattern = re.compile(r'^[A-Z]{3}[0-9]{3}$')
 
invalid_courses = df[~df['course'].apply(lambda x: bool(valid_pattern.match(x)))]['course'].tolist()
 
distinct_courses = df['course'].nunique()
 
df.to_csv('processed_courses.csv', index=False)
 
print(f"Number of distinct courses: {distinct_courses}")
if invalid_courses:
    print("\n⚠️ Invalid course codes (not in 'ABC123' format):")
    for code in invalid_courses:
        print(f" - {code}")
else:
    print("✅ All course codes are valid.")


# Find repeating courses
repeating_courses = df['course'].value_counts()
repeating_courses = repeating_courses[repeating_courses > 1]

# Output repeating courses
if not repeating_courses.empty:
    print("\n🔁 Repeating course codes:")
    for course, count in repeating_courses.items():
        print(f" - {course}: {count} times")
else:
    print("\n✅ No repeating course codes found.")
