import unittest
from models.course import Course
from models.student import Student
from models.color import Color
from models.lecture_hall import LectureHall

class TestCourse(unittest.TestCase):
    def setUp(self):
        self.course_id = 1
        self.course_code = 'CS101'
        self.student_list = {'S1', 'S2', 'S3'}
        self.old_day = 0
        self.old_slot = 0
        self.course = Course(
            id=self.course_id,
            code=self.course_code,
            student_list=self.student_list,
            old_day=self.old_day,
            old_slot=self.old_slot
        )

    def test_course_initialization(self):
        self.assertEqual(self.course.id, self.course_id)
        self.assertEqual(self.course.course_code, self.course_code)
        self.assertEqual(self.course.student_list, self.student_list)
        self.assertEqual(self.course.no_of_students, len(self.student_list))
        self.assertEqual(self.course.degree, 0)
        self.assertTrue(self.course.flag)
        self.assertEqual(self.course.max_adjacency, 0)
        self.assertEqual(self.course.adjacency_list, [])
        self.assertIsNone(self.course.color)
        self.assertEqual(self.course.lecture_halls, {})
        self.assertEqual(self.course.old_day, self.old_day)
        self.assertEqual(self.course.old_slot, self.old_slot)

    def test_ordered_adjacency_list(self):
        # Setup adjacent courses
        course2 = Course(2, 'CS102', {'S2', 'S3'}, 0, 0)
        course3 = Course(3, 'CS103', {'S1'}, 0, 0)
        self.course.adjacency_list = [course2, course3]
        course2.degree = 2
        course2.max_adjacency = 5
        course3.degree = 1
        course3.max_adjacency = 3

        ordered_list = self.course.ordered_adjacency_list()
        self.assertEqual(ordered_list[0], course2)
        self.assertEqual(ordered_list[1], course3)

    def test_assign_color(self):
        color = Color(day=1, slot=2)
        self.course.assign_color(color)
        self.assertEqual(self.course.color, color)
        self.assertIn(self.course, color.courses)


class TestStudent(unittest.TestCase):
    def setUp(self):
        # Create mock courses
        self.course1 = Course(1, 'CS101', {'S1', 'S2'}, 0, 0)
        self.course2 = Course(2, 'MA101', {'S1', 'S3'}, 0, 0)
        self.courses = {self.course1, self.course2}
        self.student = Student(roll_no='S1', courses=self.courses)

    def test_student_initialization(self):
        self.assertEqual(self.student.roll_no, 'S1')
        self.assertEqual(self.student.courses_enrolled, self.courses)
        self.assertEqual(self.student.count, {})

    def test_fairness_quotient(self):
        # Implement the method in Student class if needed
        # This is a placeholder for the test
        pass

class TestColor(unittest.TestCase):
    def setUp(self):
        self.color = Color(day=2, slot=1)
        self.hall1 = LectureHall('LH1', odd_capacity=50, even_capacity=50)
        self.hall2 = LectureHall('LH2', odd_capacity=30, even_capacity=30)
        self.color.lecture_halls.extend([self.hall1, self.hall2])

    def test_color_initialization(self):
        self.assertEqual(self.color.day, 2)
        self.assertEqual(self.color.slot, 1)
        self.assertEqual(self.color.courses, [])
        self.assertEqual(len(self.color.lecture_halls), 2)

    def test_capacity_available(self):
        expected_capacity = self.hall1.total_capacity() + self.hall2.total_capacity()
        self.assertEqual(self.color.capacity_available(), expected_capacity)

    def test_lecture_hall_list(self):
        available_halls = self.color.lecture_hall_list()
        self.assertIn(self.hall1, available_halls)
        self.assertIn(self.hall2, available_halls)

        # Occupy all seats in hall1
        self.hall1.assign_seats('o')
        self.hall1.assign_seats('e')
        available_halls = self.color.lecture_hall_list()
        self.assertNotIn(self.hall1, available_halls)
        self.assertIn(self.hall2, available_halls)


class TestLectureHall(unittest.TestCase):
    def setUp(self):
        self.hall = LectureHall('LH1', odd_capacity=40, even_capacity=40)

    def test_lecture_hall_initialization(self):
        self.assertEqual(self.hall.number, 'LH1')
        self.assertEqual(self.hall.odd_capacity, 40)
        self.assertEqual(self.hall.even_capacity, 40)
        self.assertTrue(self.hall.odd_available)
        self.assertTrue(self.hall.even_available)

    def test_total_capacity(self):
        total_capacity = self.hall.total_capacity()
        self.assertEqual(total_capacity, 80)
        self.hall.assign_seats('o')
        total_capacity = self.hall.total_capacity()
        self.assertEqual(total_capacity, 40)
        self.hall.assign_seats('e')
        total_capacity = self.hall.total_capacity()
        self.assertEqual(total_capacity, 0)

    def test_has_capacity(self):
        self.assertTrue(self.hall.has_capacity())
        self.hall.assign_seats('o')
        self.hall.assign_seats('e')
        self.assertFalse(self.hall.has_capacity())

    def test_assign_seats(self):
        self.hall.assign_seats('o')
        self.assertFalse(self.hall.odd_available)
        self.assertTrue(self.hall.even_available)
        self.hall.assign_seats('e')
        self.assertFalse(self.hall.even_available)


if __name__ == '__main__':
    unittest.main()



  
