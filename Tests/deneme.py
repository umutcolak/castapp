import unittest
from base.test_base import TestBaseWeb


class TestCheckMobileSmartRecommenderDetails(TestBaseWeb):

    def setUp(self):
        """Firs Case"""

    def test_case(self):
        self.driver.get("https://www.google.com/")

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
