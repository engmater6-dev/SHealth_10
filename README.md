# SHealth BMI (Python)

# Overview
- 삼성 헬스에서는 수집된 데이터를 활용하여 사용자들의 나이대(ex. 20대, 30대, 40대 등)별 저체중/정상체중/과체중/비만의 통계를 계산하고자 합니다.
- 수집 중 누락된 체중값이 있으며 같은 나이대(ex. 20대, 30대, 40대 등)의 평균을 적용합니다. 체중 0이 누락된 경우 입니다.
- 수집 데이터는 ID, 나이, 몸무게(kg), 키(cm)이며, BMI는 체중(kg) / 키(m)제곱 으로 계산합니다.
- BMI 기준으로 18.5이하 저체중, 18.5초과 23미만 정상체중, 23이상 25미만 과체중, 25이상 비만으로 판단합니다.
![BMI](./bmi.png)
- 제공된 코드에는 다양한 코드 품질 문제가 있습니다. 


## data sample
- 입력 데이터 (shealth.dat)
```
id,age,weight,height
93705,66,79.5,158.3
93708,66,53.5,150.2
93709,75,88.8,151.1
... (이하 생략)
```
- 각 라인별 ID, 나이, 체중(kg), 키(cm) 순서 입니다.


## 실행 환경

### 요구사항
- Python 3.8 이상

### 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 필요한 패키지 설치 (테스트용)
pip install pytest
```

### 실행
```bash
cd src/main/python
python shealth_bmi.py
```

### 테스트 실행
```bash
python -m pytest src/test/python/test_shealth_bmi.py -v
```

### 가상환경 비활성화
```bash
deactivate
```


## 프로젝트 구조
```
shealth.dat
src/
  main/python/
    shealth.py           - SHealth 클래스 (BMI 계산 및 통계 로직 구현)
    shealth_bmi.py       - main 함수 (프로그램 진입점)
  test/python/
    test_shealth_bmi.py  - unittest 기반 단위 테스트
doc/
  requirements_analysis.md  - 요구사항·QA 분석 문서
.cursorrules               - Cursor AI 프로젝트 규칙
prompt/                    - 단계별 프롬프트 등록
report/                    - 단계별 작업 보고서
```

> 상세 요구사항·테스트 시나리오(45건)는 [`doc/requirements_analysis.md`](doc/requirements_analysis.md) 참고.


## To-Do List

> `doc/requirements_analysis.md` 기준 작업 목록. 완료 시 `[x]`로 표시.

### 0. 준비 · 문서

- [x] Git `refactoring` 브랜치 및 원격 연동
- [x] `.cursorrules` 작성 (pytest, 커버리지 90% 등)
- [x] `doc/requirements_analysis.md` QA 분석 문서 작성
- [ ] `requirements-dev.txt` 추가 (`pytest`, `pytest-cov`)
- [ ] README 테스트·커버리지 실행 명령 갱신

### 1. 코드 분석 (Activities 1)

- [ ] `shealth.py` / `shealth_bmi.py` 구조·BMI 로직 이해
- [ ] 코드 스멜 목록화 (Long Method, 매직 넘버, 데이터 클러핑 등)
- [ ] **버그 확인:** BMI `25.0` 비만 분류 누락 (`> 25` → `>= 25`)
- [ ] `prompt/01.코드분석.md`, `report/01.report.md` 작성

### 2. 1차 리팩토링 (Activities 2)

- [ ] 네이밍 개선 (`age_class_start`, `BmiCategory` 등)
- [ ] 하드코드·매직 넘버 제거 (18.5, 23, 25, 100~400 → 상수·`Enum`)
- [ ] 함수 추출 (`load_csv`, `classify_bmi`, `impute_*`, `aggregate_*`)
- [ ] 나이대 루프·BMI 분류 **중복 제거**
- [ ] dead code·불필요 import 제거
- [ ] `print` → `logging` 전환 (도메인 계층 `print` 금지)
- [ ] 평행 리스트 → `@dataclass UserRecord` 구조 검토

### 3. 단위 테스트 · pytest (Activities 3)

- [ ] `unittest` → **pytest** 스타일로 이전 (`conftest.py`, `tmp_path` fixture)
- [ ] BMI 계산 TC (표준·cm→m 변환·경계값 18.5/23/25) — TC #1~9
- [ ] `weight=0` 나이대 평균 보정 TC — TC #10~14
- [ ] 저체중/정상/과체중/비만 분류 TC — TC #15~22
- [ ] 예외 TC (파일 없음, 빈 파일, 잘못된 행) — TC #36~42
- [ ] **라인 커버리지 90% 이상** (`--cov-fail-under=90`)
- [ ] `prompt/03.단위테스트.md`, `report/03.report.md` 작성

### 4. 기능 개선 (Activities 4)

#### 4.1 데이터 입력 · 전처리

- [x] CSV 로드 (`id, age, weight, height`)
- [x] `weight=0` → 동일 나이대 평균 체중 보정
- [ ] `height=0` → 동일 나이대 평균 키 보정 — TC #23~26
- [ ] 보정 불가 시 정책 정의 (스킵·fallback·로그 WARNING)
- [ ] 빈 행·컬럼 부족·비숫자 값 방어적 처리

#### 4.2 BMI 계산 · 분류

- [x] BMI = kg / m² (키 cm → m 변환)
- [ ] `classify_bmi()` 단일 함수로 분류 통합
- [ ] 경계값 정합: ≤18.5 / 18.5~23 / 23~25 / ≥25

#### 4.3 통계 · 조회 API

- [x] 나이대별 BMI 범주 비율 (`get_bmi_ratio`)
- [ ] 나이대 4종 비율 합 ≈ 100% 검증 — TC #27~28
- [ ] **전체 사용자** BMI 범주 비율 (`get_overall_bmi_distribution`) — TC #29~30
- [ ] **정상 범위** 사용자 ID 목록 (`get_normal_weight_user_ids`, 18.5 초과 ~ 23 미만) — TC #32~35
- [ ] 20세 미만·80세 이상 처리 정책 확정

#### 4.4 설계 (SRP)

- [ ] 책임 분리: Reader / Imputer / Calculator / Classifier / Statistics
- [ ] 모든 공개 함수·메서드 **type hint** 적용
- [ ] `prompt/04.기능개선.md`, `report/04.report.md` 작성

### 5. 회고 · 발표 (Activities 5)

- [ ] 실습 목표·달성도 정리
- [ ] 코드 품질 Before & After
- [ ] AI 활용 회고 (도움·한계)
- [ ] TC 추가가 품질에 미친 영향·작성 팁
- [ ] `prompt/05.회고.md`, `report/05.report.md` 작성

### 6. 품질 게이트 (`.cursorrules` 연동)

- [ ] 신규·변경 기능마다 pytest TC 추가
- [ ] `@pytest.mark.skip` 최소화
- [ ] PEP 8 준수
- [ ] 리팩토링 후 회귀 TC (`shealth.dat` 스냅샷) — TC #44


# 생성형AI를 활용한 Activities (6 시간)
1. 문제 코드 분석 및 코드 스멜 찾기 (1시간)
- 기본 코드구조, BMI 로직 이해 
- 코드 스멜 찾기 
2. 1차 리펙토링 (클린코드 관점, 아래 내용을 순차적으로 수행) (1시간) 
- 네이밍 개선
- 하드코드 및 전역변수 제거 
- 함수 추출
- 반복/중복 제거
3. UnitTest 작성 (1시간)
- BMI 계산 로직 TC
- Age 평균치 보정 로직 TC
- 정상/저체중/과체중/비만 분류 TC
- 예외상황 TC
4. 기능 개선 (2시간)
- SRP에 따른 책임 분리등 리팩토링 
- 특정 연령대의 BMI 분포 비율 계산 기능 추가
- Height가 0인 경우에 대한 평균치 보정 로직 추가 
- BMI 정상 범위 사용자 목록 조회 기능 추가
- 전체 사용자 대비 각 BMI 범주 비율 계산 기능 추가
5. 회고 및 발표 (1시간) 
- 실습 목표와 달성도 
- 코드 품질 Before & After
- AI를 어떻게 활용했나? 도움이 된 순간과 한계는? 
- TC를 추가해보면서 개선에 미친 영향, TC 작성 팁
- 클린코드와 리팩토링에서 느낀 장점과 어려운점


# 주의 사항
- 코드 품질을 높이기 위해 Python의 표준 라이브러리를 필요한 경우 사용하셔도 됩니다.
