import pandas as pd
import csv

def load_course_list(xlsx_path):
    """
    Loads the course list from list.xlsx.
    Assumes the course code is in the first column.
    Returns the DataFrame as read.
    """
    # Using openpyxl as engine
    df = pd.read_excel(xlsx_path, engine='openpyxl')
    return df

def build_common_groups(common_csv_path):
    """
    Reads common.csv using cp1252 encoding.
    Builds a mapping (dictionary) where every course code found in
    the 'combine_sub_code' column is mapped to the first code in that list.
    """
    mapping = {}
    with open(common_csv_path, 'r', newline='', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            combined = row.get("combine_sub_code", "").strip()
            if combined:
                # split by comma; the codes have no spaces
                codes = combined.split(',')
                if codes:
                    primary = codes[0]
                    # Map every code in the group to the primary code
                    for code in codes:
                        mapping[code] = primary
    return mapping

def update_course_codes(df, mapping):
    """
    Given a DataFrame and a mapping dictionary, update the course codes in the first column.
    If a course code exists in the mapping, it is replaced by its primary version.
    """
    # Identify the column that holds course codes (assumed as the first column)
    col_name = df.columns[0]
    df[col_name] = df[col_name].astype(str).str.strip().apply(lambda x: mapping.get(x, x))
    return df

def main():
    # File paths
    excel_file = 'cleaned_Book2.xlsx'
    common_csv_file = 'common.csv'
    
    # Load the course list
    df = load_course_list(excel_file)
    
    # Build the mapping from common.csv using cp1252 encoding
    course_mapping = build_common_groups(common_csv_file)
    
    # Update the course codes in the DataFrame
    df_updated = update_course_codes(df, course_mapping)
    
    # Save the updated DataFrame to a new Excel file
    updated_excel_file = 'Book3.xlsx'
    df_updated.to_excel(updated_excel_file, index=False, engine='openpyxl')
    
    # Count the number of distinct courses in the updated DataFrame
    col_name = df_updated.columns[0]
    distinct_count = df_updated[col_name].nunique()
    
    print(f"Total distinct courses after renaming: {distinct_count}")
    print(f"Updated Excel file saved as: {updated_excel_file}")

if __name__ == "__main__":
    main()
