class LectureHall:
    
    def __init__(self, number: str, odd_capacity: int, even_capacity: int, single_capacity: int, color):
        self.number = number
        self.color = color
        self.color.lecture_halls.append(self)

        # 1 indicates available, 0 indicates occupied
        self.odd = 1
        self.even = 1
        self.single = 1

        self.odd_capacity = odd_capacity
        self.even_capacity = even_capacity
        self.single_capacity = single_capacity

    def total_capacity(self) -> int:
        """Total available capacity based on seat availability."""
        if self.odd and self.even and self.single:
            return self.odd_capacity + self.even_capacity + self.single_capacity
        elif self.odd and self.even:
            return self.odd_capacity + self.even_capacity
        elif self.odd and self.single:
            return self.odd_capacity + self.single_capacity
        elif self.single and self.even:
            return self.single_capacity + self.even_capacity
        elif self.odd:
            return self.odd_capacity
        elif self.even:
            return self.even_capacity
        else:
            return 0

    def availability(self) -> dict:
        """Returns availability of seats in odd/even sections."""
        if self.odd and self.even and self.single:
            return {
                "total": self.odd_capacity + self.even_capacity + self.single_capacity,
                "seats": (self.odd_capacity, self.even_capacity, self.single_capacity)
            }
        elif self.odd and self.even:
            return {
                "total": self.odd_capacity + self.even_capacity,
                "seats": (self.odd_capacity, self.even_capacity, 0)
            }
        elif self.odd and self.single:
            return {
                "total": self.odd_capacity + self.single_capacity,
                "seats": (self.odd_capacity, 0, self.single_capacity)
            }
        elif self.even and self.single:
            return {
                "total": self.even_capacity + self.single_capacity,
                "seats": (0, self.even_capacity, self.single_capacity)
            }
        elif self.odd:
            return {
                "total": self.odd_capacity,
                "seats": (self.odd_capacity, 0, 0)
            }
        elif self.even:
            return {
                "total": self.even_capacity,
                "seats": (0, self.even_capacity, 0)
            }
        elif self.single:
            return {
                "total": self.single_capacity,
                "seats": (0, 0, self.single_capacity)
            }
        else:
            return {
                "total": 0,
                "seats": (0, 0, 0)
            }

    def assign_seats(self, seat_type: str):
        """Marks the specified seat type as occupied."""
        if seat_type == 'o':
            self.odd = 0
        elif seat_type == 'e':
            self.even = 0
        elif seat_type == 's':
            self.single = 0

    def __unicode__(self):
        return 'L%s' % (self.number)
