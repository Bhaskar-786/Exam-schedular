class LectureHall:
     
    def __init__(self, number: str, odd_capacity: int, even_capacity: int):
        self.number = number
        self.odd_capacity = odd_capacity
        self.even_capacity = even_capacity
        self.odd_available = True
        self.even_available = True

    def total_capacity(self) -> int:
        """Total available capacity."""
        capacity = 0
        if self.odd_available:
            capacity += self.odd_capacity
        if self.even_available:
            capacity += self.even_capacity
        return capacity

    def has_capacity(self) -> bool:
        """Checks if the lecture hall has any available capacity."""
        return self.odd_available or self.even_available

    def assign_seats(self, seat_type: str):
        """Marks the specified seat type as occupied."""
        if seat_type == 'o':
            self.odd_available = False
        elif seat_type == 'e':
            self.even_available = False

    def availability(self) -> dict:
        """Availability of seats."""
        return {
            'total': self.total_capacity(),
            'seats': (self.odd_capacity if self.odd_available else 0,
                      self.even_capacity if self.even_available else 0)
        }

    def __str__(self):
        return f"Lecture Hall {self.number}"
