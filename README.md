# SHealth BMI (Python)

# Overview
- 삼성 헬스에서는 수집된 데이터를 활용하여 사용자들의 나이대(ex. 20대, 30대, 40대 등)별 저체중/정상체중/과체중/비만의 통계를 계산하고자 합니다.
- 수집 중 누락된 체중값이 있으며 같은 나이대(ex. 20대, 30대, 40대 등)의 평균을 적용합니다. 체중 0이 누락된 경우 입니다.
- 수집 데이터는 ID, 나이, 몸무게(kg), 키(cm)이며, BMI는 체중(kg) / 키(m)제곱 으로 계산합니다.
- BMI 기준으로 18.5이하 저체중, 18.5초과 23미만 정상체중, 23이상 25미만 과체중, 25이상 비만으로 판단합니다.
![BMI](./bmi.png)
- 제공된 코드에는 다양한 코드 품질 문제가 있었으며, **Phase 01~08 리팩토링**으로 구조·품질을 개선했습니다.


## 리팩토링 개선 현황 (Phase 01~08)

> 상세 프롬프트: [`task_refactoring/00.index.md`](task_refactoring/00.index.md)

### 구조·설계 (P1~P3)

| 구분 | 개선 내용 |
|------|-----------|
| **P1 SRP** | `calculate_bmi` → `_reset_state` / `_load_records` / `_impute_weights` / `_compute_bmis` / `_aggregate_ratios` 5단계 오케스트레이션 |
| **P2 상수·파서** | `BmiThresholds`, `BmiCategory` IntEnum, `csv.DictReader` + 필드명 상수, `utf-8`, 빈 행 `continue` |
| **P2 버그 수정** | BMI **25.0** 비만 분류 누락 수정 (`> 25` → `>= 25`), `classify_bmi()` / `WhoAsiaPacificClassifier` 단일화 |
| **P3 데이터 모델** | `@dataclass HealthRecord` (`models.py`), `AGE_BANDS` + `in_age_band()`, `_records_in_band()` |
| **P3 캡슐화** | `ages` / `weights` / `heights` / `bmis` → property (읽기 전용 복사) |

### CLI·확장성 (P4~P5)

| 구분 | 개선 내용 |
|------|-----------|
| **P4 CLI** | `format_age_band_report()`, `argparse` + `Path`, `BmiCategory` 사용, `main() -> None` |
| **P4 로깅** | 도메인 `print` 제거 → `logging.error` (CLI에서 `basicConfig`) |
| **P5 Protocol** | `SupportsBmiClassification`, `WhoAsiaPacificClassifier` 주입 (`SHealth(classifier=...)`) |

### 품질·테스트

| 항목 | 결과 |
|------|------|
| pytest | **45건** (unittest 3건 + pytest 42건) |
| 커버리지 | **99%** (`shealth.py` 100%, `models.py` 100%, `shealth_bmi.py` 96%) — `--cov-fail-under=90` 충족 |
| 주요 TC | BMI 경계(18.5/23/25), weight=0 보정, 빈 행 스킵, ERROR 로깅, FakeClassifier 주입 |

### 아직 미구현 (Activities 4 예정)

- `height=0` 나이대 평균 키 보정 (`impute_heights`)
- 전체 사용자 BMI 비율 API (`get_overall_bmi_distribution`)
- 정상 범위 사용자 ID 목록 (`get_normal_weight_user_ids`)
- CSV 잘못된 행 방어적 스킵 + WARNING 로그
- `SupportsRecordReader` Protocol (선택)


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

# 개발·테스트 의존성 설치
pip install -r requirements-dev.txt
```

### 실행

프로젝트 **루트**에서 실행 (권장 — `shealth.dat`가 루트에 있음):

```bash
# 기본 데이터 파일 (shealth.dat)
py -3 src/main/python/shealth_bmi.py

# 사용자 지정 CSV
py -3 src/main/python/shealth_bmi.py path/to/custom.dat
```

`src/main/python`에서 실행할 경우 데이터 파일 경로를 인자로 넘기세요:

```bash
cd src/main/python
python shealth_bmi.py ../../shealth.dat
```

출력 예 (나이대별 비율, 소수 6자리):

```
20 - underweight = 3.511053, normal = 23.797139, overweight = 11.833550, obesity = 60.858257
...
```

### 테스트 실행

프로젝트 루트에서:

```bash
py -3 -m pytest src/test/python -v
```

### 커버리지 확인 (라인 커버리지 90% 이상)
```bash
python -m pytest src/test/python --cov=src/main/python --cov-report=term-missing --cov-fail-under=90
```

### 가상환경 비활성화
```bash
deactivate
```


## 프로젝트 구조
```
requirements-dev.txt      # pytest, pytest-cov (개발·테스트용)
shealth.dat                 # 샘플 입력 데이터 (프로젝트 루트)
src/
  main/python/
    models.py               - HealthRecord dataclass
    shealth.py              - SHealth, BmiCategory, 분류·나이대 정책
    shealth_bmi.py          - CLI 진입점 (argparse, 리포트 출력)
  test/python/
    conftest.py             - tmp_path CSV fixture
    test_shealth_bmi.py     - unittest 스모크 (3건)
    test_bmi_formula.py     - BMI 공식 TC (#1~2)
    test_bmi_ratio_sum.py   - 나이대 비율 합·빈 대 TC (#27~28)
    test_classify_bmi_*.py  - BMI 경계·단위 분류 TC
    test_impute_weight.py   - weight=0 보정 TC (#10~13)
    test_load_records.py    - 빈 행·헤더만·건수 TC
    test_cli_main.py        - CLI main() 통합 TC
    test_age_band_policy.py - in_age_band / AGE_BANDS TC
    test_bmi_classifier.py  - Protocol·FakeClassifier TC
    test_cli_logging.py     - logging·리포트 포맷 TC
task_refactoring/           - Phase 01~08 리팩토링 프롬프트
task_testplan/              - Activities 3 단위 테스트 Phase 01~09 프롬프트
doc/
  test_plan.md              - Activities 3 테스트 계획서
  requirements_analysis.md  - 요구사항·QA 분석 (TC 45건)
  code_quality_report.md    - SOLID·코드 스멜 분석
.cursorrules                - Cursor AI 프로젝트 규칙
prompt/                     - Activities 단계별 프롬프트
report/                     - Activities 단계별 보고서
```

> 상세 요구사항·테스트 시나리오(45건)는 [`doc/requirements_analysis.md`](doc/requirements_analysis.md), 코드 품질 분석은 [`doc/code_quality_report.md`](doc/code_quality_report.md) 참고.


## To-Do List

> [`doc/requirements_analysis.md`](doc/requirements_analysis.md) · [`doc/code_quality_report.md`](doc/code_quality_report.md) 기준 작업 목록. 완료 시 `[x]`로 표시.  
> 리팩토링 우선순위: **P1** 구조 분해 → **P2** 상수·파서 → **P3** dataclass·그룹핑 → **P4** CLI·진입점 → **P5** Protocol·전략

### 0. 준비 · 문서

- [x] Git `refactoring` 브랜치 및 원격 연동
- [x] `.cursorrules` 작성 (pytest, 커버리지 90% 등)
- [x] `doc/requirements_analysis.md` QA 분석 문서 작성
- [x] `doc/code_quality_report.md` SOLID·코드 스멜 분석 문서 작성
- [x] `requirements-dev.txt` 추가 (`pytest`, `pytest-cov`)
- [x] README 테스트·커버리지 실행 명령 갱신

### 1. 코드 분석 (Activities 1)

- [x] `shealth.py` / `shealth_bmi.py` 구조·BMI 로직 이해
- [x] 코드 스멜 목록화 — Long Method, Magic Number, Duplicated Code, Primitive Obsession, 데이터 클로킹 등 ([`code_quality_report.md` §3](doc/code_quality_report.md))
- [x] **SRP/OCP 위반** 정리 — `calculate_bmi` 책임 혼재, BMI·나이대·CSV 스키마 하드코딩 ([§2](doc/code_quality_report.md))
- [x] **버그 수정:** BMI `25.0` 비만 분류 누락 (`> 25` → `>= 25`, Phase 03)
- [x] **잠재 버그:** 빈 행 처리 `break` → `continue` **수정 완료** (Phase 04)
- [x] Python 특화 이슈 정리 — 타입 힌트 부분 적용, `Enum`/`dataclass`/`Protocol` 미활용, `encoding` 미지정 ([§4](doc/code_quality_report.md))
- [x] `prompt/02.code_smell.md`, `report/02.code_smell.md` 작성

### 2. 1차 리팩토링 (Activities 2)

> **진행 상태 (Phase 01~08):** P1~P4·기타 **완료** · P5 선택 1건 제외 · `impute_heights`는 Activities 4로 이관

#### P1 — `calculate_bmi` 분해 (SRP, Long Method)

- [x] `_load_records` — CSV 읽기·레코드 적재 (`_load_records`)
- [x] `_reset_state()` — `calculate_bmi` 호출 전 상태 초기화 분리
- [x] `_impute_weights` — 체중(`weight=0`) 결측 보정 분리
- [ ] `_impute_heights` — 키(`height=0`) 결측 보정 (**Activities 4**, 2차 범위)
- [x] `_compute_bmis` — BMI 산출 분리
- [x] `_aggregate_ratios` — 나이대별 비율 집계 분리

#### P2 — 상수·파서·경계값 (OCP, Magic Number)

- [x] `BmiThresholds` — 임계값 18.5 / 23 / 25 단일 정의
- [x] `AGE_BANDS` + `in_age_band()` — AgeBandPolicy(20~70대, 10년 구간) 단일화
- [x] BMI 분류 `> 25` → `>= 25` 수정 (`WhoAsiaPacificClassifier`)
- [x] `classify_bmi()` 모듈 함수 + Classifier 위임 (thin wrapper)
- [x] `csv.DictReader` + 필드명 상수 (`FIELD_ID` …) — `row[1..3]` 제거
- [x] 빈 행: `break` → `continue` (`_is_blank_row`)
- [x] `BmiCategory` `IntEnum` — 집계·CLI에서 `100~400` 리터럴 제거
- [x] `open(..., encoding="utf-8")` 명시

#### P3 — 데이터 모델·중복 제거

- [x] `models.py` + `@dataclass HealthRecord` — 평행 리스트 대체
- [x] `AGE_BANDS` + `in_age_band()` — impute·aggregate 공통 사용
- [x] `_records_in_band()` — 나이대 필터 중복 제거
- [x] `ages` / `weights` / `heights` / `bmis` property — 읽기 전용 복사본 (캡슐화)

#### P4 — 진입점·에러 처리 (`shealth_bmi.py`)

- [x] `main`·리포트에서 `BmiCategory` 사용 (`100,200,300,400` 제거)
- [x] `format_age_band_report()` — 출력 포맷·소수 6자리 분리
- [x] `parse_args()` — `argparse` + `pathlib.Path` 기본값
- [x] `AGE_BANDS` import — `range(20, 80, 10)` CLI 중복 제거
- [x] `FileNotFoundError` → `logging.error` (도메인 `print` 제거)
- [x] `main() -> None` · 모듈 docstring · `logging.basicConfig` (CLI)

#### P5 — 확장성 (선택)

- [x] `typing.Protocol` — `SupportsBmiClassification`
- [x] `WhoAsiaPacificClassifier` — `SHealth(classifier=...)` 주입
- [ ] `SupportsRecordReader` — **선택, 미구현** (YAGNI, Activities 2 범위 외)

#### 기타 (README §2 · code_quality_report §3)

- [x] 네이밍 개선 (`age_band_start`, `band_size`, `valid_weight_count` 등)
- [x] 함수 추출 — `calculate_bmi` God Method 분해, `format_age_band_report`, `classify_bmi`
- [x] 하드코드 제거 — BMI 임계값·나이대·필드명·Enum 상수화
- [x] 반복/중복 제거 — `in_age_band`, `_records_in_band`, `HealthRecord` 단일 저장소
- [x] dead code·불필요 import 제거 (`typing.List`/`Dict` → builtin)
- [x] `shealth.py` / `shealth_bmi.py` public·private API type hint (Phase 08)

### 3. 단위 테스트 · pytest (Activities 3)

- [x] pytest 확장 (`conftest.py`, `tmp_path`, 42건) — unittest 3건 병행 유지
- [x] BMI 경계값 TC (18.5 / 18.500001 / 23.0 / 25.0) — TC #15~21 일부
- [x] `weight=0` 나이대 평균 보정 TC — TC #10
- [x] 분류 단위·통합 TC — `classify_bmi`, `get_bmi_ratio` 경계
- [x] 예외 TC 일부 — 파일 없음(ERROR 로그), 빈 행 continue — TC #36~37, #42
- [x] **라인 커버리지 90% 이상** (현재 **99%**, 2026-05-20 기준)
- [x] BMI 표준 계산·cm→m 전용 TC — TC #1~2 (`test_bmi_formula.py`)
- [x] 나이대 4종 합 100%·빈 나이대 TC — TC #27~28 (`test_bmi_ratio_sum.py`)
- [x] weight 보정 parametrize·보정 불가 — TC #11~13 (`test_impute_weight.py`)
- [x] 헤더만·건수 반환·`main()` CLI TC — TC #37, #43, `test_cli_main.py`
- [ ] height 보정·전체 비율·정상 ID TC — Activities 4 연동
- [ ] 잘못된 행 스킵 TC — TC #38~39
- [x] `prompt/05.test_case.md`, `report/05.test_case.md` 작성

### 4. 기능 개선 (Activities 4)

#### 4.1 데이터 입력 · 전처리

- [x] CSV 로드 (`id, age, weight, height`)
- [x] `weight=0` → 동일 나이대 평균 체중 보정
- [ ] `height=0` → 동일 나이대 평균 키 보정 — TC #23~26
- [ ] 보정 불가 시 정책 정의 (스킵·fallback·로그 WARNING)
- [ ] 빈 행·컬럼 부족·비숫자 값 방어적 처리

#### 4.2 BMI 계산 · 분류

- [x] BMI = kg / m² (키 cm → m 변환)
- [x] `classify_bmi()` / `WhoAsiaPacificClassifier` 단일 분류
- [x] 경계값 정합: ≤18.5 / 18.5~23 / 23~25 / ≥25 (25.0 포함)

#### 4.3 통계 · 조회 API

- [x] 나이대별 BMI 범주 비율 (`get_bmi_ratio`)
- [ ] 나이대 4종 비율 합 ≈ 100% 검증 — TC #27~28
- [ ] **전체 사용자** BMI 범주 비율 (`get_overall_bmi_distribution`) — TC #29~30
- [ ] **정상 범위** 사용자 ID 목록 (`get_normal_weight_user_ids`, 18.5 초과 ~ 23 미만) — TC #32~35
- [ ] 20세 미만·80세 이상 처리 정책 확정

#### 4.4 설계 (SRP · OCP)

- [x] 1차 책임 분리 — load / impute / compute / aggregate private 메서드
- [x] 분류 전략 주입 — `SHealth(classifier=SupportsBmiClassification)`
- [x] `HealthRecord` + property + **type hint** (`shealth.py`, `shealth_bmi.py`)
- [ ] Reader / Imputer / Statistics **별도 클래스** 분리 (추가 리팩토링)
- [ ] `prompt/06.feature.md`, `report/06.feature.md` 작성

### 5. 회고 · 발표 (Activities 5)

- [ ] 실습 목표·달성도 정리
- [ ] 코드 품질 Before & After
- [ ] AI 활용 회고 (도움·한계)
- [ ] TC 추가가 품질에 미친 영향·작성 팁
- [ ] `prompt/07.final.md`, `report/07.final.md` 작성

### 6. 품질 게이트 (`.cursorrules` 연동)

- [x] 리팩토링 단계마다 pytest TC 추가 (Phase 01~08)
- [x] `@pytest.mark.skip` 미사용
- [x] PEP 8·type hint 정리 (Phase 08)
- [x] `shealth.dat` 스모크·비율 0~100% 회귀 (`test_shealth_bmi`, `test_bmi_ratio_range`)
- [ ] Golden 스냅샷 자동 비교 — TC #44 전용


# 생성형AI를 활용한 Activities (6 시간)
1. 문제 코드 분석 및 코드 스멜 찾기 (1시간)
- 기본 코드구조, BMI 로직 이해 
- 코드 스멜 찾기 
2. 1차 리펙토링 (클린코드 관점, 아래 내용을 순차적으로 수행) (1시간) — **Phase 01~08 완료**
- 네이밍 개선 ✅
- 하드코드 및 전역변수 제거 ✅ (`BmiCategory`, `AGE_BANDS`, 필드명 상수)
- 함수 추출 ✅ (`calculate_bmi` 분해, `format_age_band_report`)
- 반복/중복 제거 ✅ (`in_age_band`, `_records_in_band`, `HealthRecord`)
3. UnitTest 작성 (1시간) — **완료** (pytest 45건, 커버리지 99%, [`doc/test_plan.md`](doc/test_plan.md) · [`report/05.test_case.md`](report/05.test_case.md))
- BMI 계산·경계 로직 TC ✅
- Age 평균치 보정 로직 TC ✅
- 정상/저체중/과체중/비만 분류 TC ✅
- 예외상황 TC ✅ (파일 없음, 빈 행 — 일부)
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
