from typing import List, Optional, Set, Dict
from models.color import Color
from models.lecture_hall import LectureHall


class Course:
    
    def __init__(
        self,
        id: int,
        code: str,
        student_list: Set[str],
        old_day: int = 0,
        old_slot: int = 0,
    ):
        self.id = id
        self.course_code = code
        self.student_list = student_list
        self.no_of_students = len(student_list)
        self.degree = 0
        self.flag = True
        self.max_adjacency = 0
        self.adjacency_list: List['Course'] = []
        self.color: Optional[Color] = None
        self.lecture_halls: Dict[LectureHall, str] = {}
        self.old_day = old_day
        self.old_slot = old_slot

    def ordered_adjacency_list(self) -> List['Course']:
        return sorted(
            self.adjacency_list,
            key=lambda course: (course.degree, course.max_adjacency),
            reverse=True,
        )

    def assign_color(self, color: Color):
        self.color = color
        color.courses.append(self)
        print(f"Assigned: {self.course_code} to Day {color.day}, Slot {color.slot}")

    def get_hall_list(self) -> str:
        res = ""
        for hall, info in self.lecture_halls.items():
          res += f"L{hall.id} {info} "
        return res.strip()


    def __str__(self):
        return f"{self.course_code}"