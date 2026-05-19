import csv


class SHealth:
    """S-Health BMI 계산 클래스"""

    # BMI 유형 상수
    UNDERWEIGHT = 100
    NORMALWEIGHT = 200
    OVERWEIGHT = 300
    OBESITY = 400

    def __init__(self):
        self.count = 0
        self.ages = []
        self.heights = []
        self.weights = []
        self.bmis = []
        # 나이대별 BMI 비율 저장 딕셔너리: {(age_class, type): ratio}
        self._bmi_ratios = {}

    def calculate_bmi(self, filename: str) -> int:
        """파일에서 데이터를 읽어 BMI를 계산한다."""
        self.count = 0
        self.ages = []
        self.heights = []
        self.weights = []
        self.bmis = []
        self._bmi_ratios = {}

        # 파일 읽기
        try:
            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # 헤더 건너뛰기
                for row in reader:
                    if not row:
                        break
                    self.ages.append(int(row[1]))
                    self.weights.append(float(row[2]))
                    self.heights.append(float(row[3]))
                    self.count += 1
        except FileNotFoundError:
            print(f"Failed to open file: {filename}")
            return 0

        # 데이터 수집 중 누락된 체중에 나이대의 평균 체중을 적용
        for a in range(20, 80, 10):
            total = 0.0
            age_count = 0
            for i in range(self.count):
                if a <= self.ages[i] < a + 10:
                    if self.weights[i] == 0.0:
                        continue
                    total += self.weights[i]
                    age_count += 1
            if age_count > 0:
                avg_weight = total / age_count
                for i in range(self.count):
                    if a <= self.ages[i] < a + 10:
                        if self.weights[i] == 0.0:
                            self.weights[i] = avg_weight

        # BMI 계산하기
        self.bmis = [
            w / ((h / 100.0) ** 2) for w, h in zip(self.weights, self.heights)
        ]

        # 나이대의 BMI기준 저체중, 정상체중, 과체중, 비만 비율 계산
        for a in range(20, 80, 10):
            underweight = 0
            normalweight = 0
            overweight = 0
            obesity = 0
            total = 0
            for i in range(self.count):
                if a <= self.ages[i] < a + 10:
                    total += 1
                    if self.bmis[i] <= 18.5:
                        underweight += 1
                    elif 18.5 < self.bmis[i] < 23:
                        normalweight += 1
                    elif 23 <= self.bmis[i] < 25:
                        overweight += 1
                    elif self.bmis[i] > 25:
                        obesity += 1

            if total > 0:
                self._bmi_ratios[(a, self.UNDERWEIGHT)] = underweight * 100 / total
                self._bmi_ratios[(a, self.NORMALWEIGHT)] = normalweight * 100 / total
                self._bmi_ratios[(a, self.OVERWEIGHT)] = overweight * 100 / total
                self._bmi_ratios[(a, self.OBESITY)] = obesity * 100 / total

        return self.count

    def get_bmi_ratio(self, age_class: int, bmi_type: int) -> float:
        """나이대와 BMI 유형에 따른 비율을 반환한다."""
        return self._bmi_ratios.get((age_class, bmi_type), 0.0)
