import json

 
num_halls = 700
 
lecture_halls = {f"LH{i+1}": [50, 50] for i in range(num_halls)}
 
with open("lecture_halls.json", "w") as file:
    json.dump(lecture_halls, file, indent=4)

print("lecture_halls.json file generated successfully.")
