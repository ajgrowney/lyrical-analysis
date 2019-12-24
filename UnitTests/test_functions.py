import unittest
from Components.utilities import get_syllables

class TestUtilities(unittest.TestCase):
    def test_get_syllables(self):
        actual = get_syllables("letters")
        expected = 2
        self.assertEqual(expected,actual)

if __name__ == '__main__':
    unittest.main()