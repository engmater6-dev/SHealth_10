import sys
import os
import unittest

# src/main/python을 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


class TestSHealthBMI(unittest.TestCase):
    def test_calculate_bmi_returns_count(self):
        """데이터 파일을 읽어 레코드 수를 반환하는지 확인"""
        shealth = SHealth()
        count = shealth.calculate_bmi("shealth.dat")
        self.assertGreater(count, 0)

    def test_bmi_ratio_range(self):
        """BMI 비율이 0~100 사이인지 확인"""
        shealth = SHealth()
        shealth.calculate_bmi("shealth.dat")
        for age in range(20, 80, 10):
            for bmi_type in [100, 200, 300, 400]:
                ratio = shealth.get_bmi_ratio(age, bmi_type)
                self.assertGreaterEqual(ratio, 0.0)
                self.assertLessEqual(ratio, 100.0)

    def test_invalid_file(self):
        """존재하지 않는 파일을 열면 0을 반환하는지 확인"""
        shealth = SHealth()
        count = shealth.calculate_bmi("nonexistent.dat")
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
