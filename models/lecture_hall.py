class LectureHall:
    def __init__(self, hall_id: str, capacity: int):
        self.hall_id = hall_id
        self.capacity = capacity

    def __str__(self):
        return f"LectureHall({self.hall_id}, Capacity: {self.capacity})"

    def __repr__(self):
        return self.__str__()