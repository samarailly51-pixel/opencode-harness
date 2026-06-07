import unittest

from calculator import add, divide


class CalculatorTests(unittest.TestCase):
    def test_adds_numbers(self) -> None:
        self.assertEqual(add(2, 3), 5)

    def test_divide_by_zero_raises(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)


if __name__ == "__main__":
    unittest.main()
