import csv
import pandas as pd
import json
def lecture_hall_processing(file):
    df = pd.read_csv(file)
    hall_data = {}

    for _, row in df.iterrows():
        hall_name = str(row['Lecture Hall']).strip()
        odd = int(row['double seated'])
        even = int(row['double seated'])
        single = int(row['single seated'])
        hall_data[hall_name] = [odd, even, single]

    with open('data/lecture_halls.json', 'w') as f:
        json.dump(hall_data, f, indent=4)