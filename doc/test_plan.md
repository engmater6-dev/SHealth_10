# SHealth BMI — Activities 3 단위 테스트 계획서

> **문서 목적:** README.md · `requirements_analysis.md` 기반 pytest 단위 테스트 범위·우선순위·TC 추적  
> **대상 코드:** `src/main/python/shealth.py`, `models.py`, `shealth_bmi.py`  
> **대상 테스트:** `src/test/python/`  
> **작성 기준일:** 2026-05-20  
> **관련:** [`task_testplan/00.index.md`](../task_testplan/00.index.md) Phase 01~09 · [`.cursorrules`](../.cursorrules)

---

## 1. 개요

### 1.1 목표

| 항목 | 목표 |
|------|------|
| 프레임워크 | **pytest** (기존 unittest 3건 병행 유지) |
| 회귀 방지 | Phase 01~08 리팩토링 후 BMI 경계·보정·CSV 로드 동작 고정 |
| 커버리지 | 라인 **≥ 90%** (`--cov-fail-under=90`) |
| 데이터 격리 | 신규 TC는 `tmp_path` + `write_health_csv` fixture 우선 |
| 금지 | `@pytest.mark.skip`로 미구현 기능 위장 금지 |

### 1.2 현재 구현 현황 (2026-05-20 측정)

```text
45 passed · TOTAL line coverage 99%
  models.py      100%
  shealth.py     100%
  shealth_bmi.py  96%  (미커버: L68 `if __name__` only)
```

| 구분 | 내용 |
|------|------|
| 테스트 건수 | **45건** (unittest 3 + pytest 42) |
| P0~P1 TC | **구현·Green** (경계·보정·로드·비율 합·공식·CLI main) |
| 갭 | TC #38~39 잘못된 행, Activities 4 (#23~35) |
| Activities 4 | TC #23~35 — 본 계획서 **P3 백로그** |

---

## 2. 범위·우선순위

### 2.1 우선순위 정의

| 우선순위 | 목적 | 대표 TC | task_testplan Phase |
|----------|------|---------|---------------------|
| **P0** | 리팩토링·버그 회귀 방지 | #8, #15~21, #10, #36~37, #42 | 03, 04, 05 (완료) |
| **P1** | 도메인 정확성·통합 | #1~2, #27~28, #31, #43 | 03, 06 (일부 갭) |
| **P2** | 확장성·CLI 품질 | Protocol 주입, 리포트 포맷, `parse_args` | 07, 05·06 (일부 완료) |
| **P3** | Activities 4 연동 백로그 | #23~35, #38~41 | 기능 구현 후 TDD |

### 2.2 P0 — 반드시 유지 (Green 게이트)

| 영역 | 검증 내용 | 테스트 파일 | TC # |
|------|-----------|-------------|------|
| BMI 경계 | 18.5→저체중, 18.500001→정상, 23.0→과체중, **25.0→비만** | `test_classify_bmi_boundaries.py`, `test_classify_bmi_unit.py` | #15~21 |
| weight=0 보정 | 동일 나이대 평균 체중 | `test_impute_weight.py` | #10 |
| 빈 행 | 중간 빈 행 `continue`, 이후 행 로드 | `test_load_records.py` | #37, #42 |
| 파일 없음 | `count=0`, `logging.ERROR`, **print 없음** | `test_cli_logging.py`, `test_shealth_bmi.py` | #36, #42 |
| 비율 범위 | `get_bmi_ratio` 0~100 | `test_shealth_bmi.py` | — |

### 2.3 P1 — Activities 3 잔여·보강

| 영역 | 검증 내용 | 권장 파일 | TC # | 상태 |
|------|-----------|-----------|------|------|
| BMI 공식 | `70/(1.75²)≈22.857`, cm→m `/100` | `test_bmi_formula.py` (신규) | #1~2 | **미구현** |
| 나이대 4종 합 | 동일 대 4범주 각 25% → 합≈100% | `test_bmi_ratio_sum.py` 또는 통합 | #27 | **미구현** |
| 빈 나이대 | 인원 0 → ratio 0.0 | 통합 TC | #28 | **미구현** |
| 건수 반환 | N행 → `calculate_bmi` return N | `test_load_records.py` 확장 | #43 | **미구현** |
| 실데이터 스모크 | `shealth.dat` count>0, 비율 0~100 | `test_shealth_bmi.py` | #31 | **구현** |

### 2.4 P2 — 설계·CLI

| 영역 | 검증 내용 | 테스트 파일 | 상태 |
|------|-----------|-------------|------|
| Protocol 주입 | `FakeClassifier` → 집계만 가짜 분류 반영 | `test_bmi_classifier.py` | **구현** |
| 리포트 포맷 | 소수 6자리 | `test_cli_logging.py` | **구현** |
| argparse | 기본·커스텀 경로 | `test_cli_logging.py` | **구현** |
| `main()` | zero records INFO, stdout 7줄 | `test_cli_main.py` (신규) | **미구현** |

### 2.5 P3 — Activities 4 백로그 (테스트 계획만)

| 기능 | TC # | 구현 선행 조건 |
|------|------|----------------|
| `height=0` 나이대 평균 보정 | #23~26 | `_impute_heights` |
| 전체 사용자 BMI 비율 | #29~30 | `get_overall_bmi_distribution` |
| 정상 범위 ID 목록 | #32~35 | `get_normal_weight_user_ids` |
| 잘못된 행·컬럼 부족 스킵 | #38~39 | 방어적 파서 + WARNING |
| Golden 스냅샷 | #44 | `shealth.dat` 기준선 fixture |

---

## 3. `@pytest.mark.parametrize` 경계값 케이스

### 3.1 BMI 분류 — 단위·모듈 (`classify_bmi` / `WhoAsiaPacificClassifier`)

| bmi_input | expected `BmiCategory` | int API | TC # | 비고 |
|-----------|------------------------|---------|------|------|
| 17.0 | UNDERWEIGHT | 100 | #15 | 일반 저체중 |
| 18.5 | UNDERWEIGHT | 100 | #19 | 상한 **포함** (`<= 18.5`) |
| 18.500001 | NORMALWEIGHT | 200 | #4, #16 | 18.5 **초과** |
| 21.0 | NORMALWEIGHT | 200 | #16 | 정상 중간 |
| 22.999 | NORMALWEIGHT | 200 | #5 | 23 **미만** |
| 23.0 | OVERWEIGHT | 300 | #6, #20 | 하한 **포함** |
| 24.999 | OVERWEIGHT | 300 | #7 | 25 **미만** |
| 25.0 | OBESITY | 400 | #8, #21 | **회귀 핵심** (`>= 25`, 구버그 `>25` 금지) |
| 30.0 | OBESITY | 400 | #18 | 고 BMI |
| 46.875 | OBESITY | 400 | #9 | w=120, h=160 극단값 |

**권장 parametrize 스켈레톤 (`test_classify_bmi_unit.py` 확장):**

```python
@pytest.mark.parametrize(
    "bmi,expected",
    [
        (17.0, BmiCategory.UNDERWEIGHT),
        (18.5, BmiCategory.UNDERWEIGHT),
        (18.500001, BmiCategory.NORMALWEIGHT),
        (21.0, BmiCategory.NORMALWEIGHT),
        (22.999, BmiCategory.NORMALWEIGHT),
        (23.0, BmiCategory.OVERWEIGHT),
        (24.999, BmiCategory.OVERWEIGHT),
        (25.0, BmiCategory.OBESITY),
        (30.0, BmiCategory.OBESITY),
    ],
)
def test_classify_bmi_param(bmi, expected): ...
```

**통합 경계 (`test_classify_bmi_boundaries.py`) — 현재 4건:**

| target_bmi (역산 weight) | expected_type | TC # | 상태 |
|--------------------------|---------------|------|------|
| 18.5 | UNDERWEIGHT | #19 | ✅ |
| 18.500001 | NORMALWEIGHT | #4 | ✅ |
| 23.0 | OVERWEIGHT | #20 | ✅ |
| 25.0 | OBESITY | #21 | ✅ |

> float 역산 시 25.0 드리프트 방지: `_weight_for_bmi`에서 `math.nextafter` 사용 (유지).

### 3.2 BMI 공식 — 전용 TC (#1~2)

| weight (kg) | height (cm) | height (m) | expected BMI | TC # |
|-------------|-------------|------------|----------------|------|
| 70 | 175 | 1.75 | ≈ 22.857143 | #1 |
| 70 | 180 | 1.80 | ≈ 21.604938 | #2 (cm→m 검증) |

```python
@pytest.mark.parametrize(
    "weight,height_cm,expected_bmi",
    [
        (70.0, 175.0, 70.0 / (1.75 ** 2)),
        (70.0, 180.0, 70.0 / (1.80 ** 2)),
    ],
)
def test_bmi_formula(weight, height_cm, expected_bmi): ...
```

### 3.3 `weight=0` 보정 — parametrize 후보

| 시나리오 | CSV 요약 (age_band) | expected | TC # | 상태 |
|----------|---------------------|----------|------|------|
| 단일 누락 | 20대: w=60, w=0 | 0→60 | #10 | ✅ |
| 다건 0 | 30대: 50,80,0,0 | 0→65 | #11 | ⬜ |
| 나이대 격리 | 20대 w=0 + 30대 w=90 | 20대만 20대 평균 | #12 | ⬜ |
| 보정 불가 | 40대 전원 w=0 | 0 유지(현재) 또는 스킵 정책 | #13 | ⬜ 정책 고정 필요 |
| 보정 후 BMI | #10 이후 | 유효 BMI, ZeroDivision 없음 | #14 | △ 통합으로 간접 |

```python
@pytest.mark.parametrize(
    "rows,age_band,check_idx,expected_weight",
    [
        ([("1",25,60,170),("2",25,0,175)], 20, 1, 60.0),
        # TC #11~12 추가
    ],
)
def test_impute_weight_param(write_health_csv, rows, ...): ...
```

### 3.4 `in_age_band` — parametrize (구현됨)

| age | age_band_start | expected | 비고 |
|-----|----------------|----------|------|
| 25 | 20 | True | 20대 |
| 19 | 20 | False | TC #40 연계 |
| 80 | 70 | False | 80세 이상 |
| 30 | 20 | False | 타 대 |

파일: `test_age_band_policy.py`

### 3.5 Activities 4 — height 보정 parametrize (백로그)

| 시나리오 | 입력 | 기대 | TC # |
|----------|------|------|------|
| 단일 키 누락 | 20대 h=170, h=0 | 0→170 | #23 |
| w·h 동시 0 | 유효 샘플 존재 | 순서: weight→height→BMI | #24 |
| height 보정 불가 | 전원 h=0 | BMI 제외 또는 ERROR | #25 |
| 보정 후 BMI | w=70, h=0→175 | ≈22.86 | #26 |

---

## 4. 예외·특이 케이스 목록

| # | 시나리오 | 입력 | 기대 동작 | caplog | TC # | 상태 | Phase |
|---|----------|------|-----------|--------|------|------|-------|
| E1 | 파일 없음 | `nonexistent.dat` | return 0, ratios 빈 값 | ERROR | #36 | ✅ | 05 |
| E2 | 헤더만 | 빈 데이터 CSV | return 0, ratio 0.0 | — | #37 | △ | 05 |
| E3 | 빈 행 중간 | row1 + blank + row2 | 2건 로드 (`continue`) | — | #42 | ✅ | 05 |
| E4 | 잘못된 행 | `"abc",x,y` | 스킵 + WARNING | WARNING | #38 | P3 | A4 |
| E5 | 컬럼 부족 | `1,20,70` (3필드) | 스킵 + WARNING | WARNING | #39 | P3 | A4 |
| E6 | 나이 19세 | age=19 | 나이대 통계 제외 | — | #40 | △ | 06 |
| E7 | 80세 이상 | age=80 | 동일 정책 | — | — | △ | 06 |
| E8 | 음수 체중 | weight=-1 | 스킵 또는 ERROR | WARNING/ERROR | #41 | P3 | A4 |
| E9 | 보정 불가 weight | 40대 전원 w=0 | 0 유지 → BMI 오류 가능 | — | #13 | ⬜ | 04 |
| E10 | height=0 미보정 | h=0 | ZeroDivision 위험 | ERROR | #25 | P3 | A4 |
| E11 | print 금지 | 파일 없음 | stdout에 도메인 print 없음 | — | #42 | ✅ | 05 |
| E12 | DictReader 파싱 실패 | 비숫자 age | 예외 전파(현재) | — | — | 현행 문서화 | — |

**E2 보강 TC 예시:**

```python
def test_header_only_returns_zero(write_health_csv):
    path = write_health_csv([])
    assert SHealth().calculate_bmi(str(path)) == 0
```

---

## 5. 커버리지 목표·측정·개선 전략

### 5.1 목표

| 범위 | 라인 커버리지 목표 | 근거 |
|------|-------------------|------|
| **전체** `src/main/python` | **≥ 90%** | `.cursorrules`, README |
| `models.py` | **100%** | dataclass — 현재 달성 |
| `shealth.py` | **≥ 95%** | 핵심 도메인 — 현재 98% |
| `shealth_bmi.py` | **≥ 85%** (권장) | CLI·`main` 분기 — 현재 63% |

### 5.2 측정 명령

```bash
# 프로젝트 루트
python -m pytest src/test/python -v

# 터미널 요약 + 미스 라인
python -m pytest src/test/python --cov=src/main/python --cov-report=term-missing --cov-fail-under=90

# HTML 리포트 (로컬 리뷰)
python -m pytest src/test/python --cov=src/main/python --cov-report=html
# → htmlcov/index.html 브라우저에서 열기
```

### 5.3 미커버 라인 ↔ 개선 전략

| 파일 | Line(s) | 유형 | 개선 전략 | 우선순위 |
|------|---------|------|-----------|----------|
| `shealth.py` | 46 `age_bands()` | 하위 호환 래퍼 | `test_age_band_policy`에서 `list(age_bands())` 호출 1건 | P2 |
| `shealth.py` | 120, 130 `ages`/`heights` property | deprecated 호환 | property 접근 assert 1건 또는 `# pragma: no cover` | P2 |
| `shealth_bmi.py` | 54-64 `main()` | CLI guard | `capsys` + `main([str(csv)])` 통합 TC | P1 |
| `shealth_bmi.py` | 68 `__main__` | entry guard | `pragma: no cover` 또는 subprocess 스모크 | P2 |

**개선 원칙**

1. **의미 있는 분기만** — 커버리지 숫자만 올리는 빈 assert 금지.
2. **도메인 우선** — `shealth.py` 95%+ 유지 후 CLI 보강.
3. **HTML 리뷰 절차** — (1) `htmlcov` 생성 → (2) 빨간 줄 → (3) TC # 매핑 → (4) 테스트 추가 → (5) `--cov-fail-under=90` 재실행.

### 5.4 커버리지 하락 시 대응

| 원인 | 조치 |
|------|------|
| 신규 분기(예: 행 스킵) | 해당 분기 입력 fixture + WARNING assert |
| 리팩토링으로 dead code 제거 | 커버리지 상승 — TC 불필요 시 정리 |
| `main()` 미테스트 | P1 `test_cli_main` 추가 |

---

## 6. 테스트 파일 ↔ TC # ↔ task_testplan Phase

| 테스트 파일 | 담당 영역 | TC # | Phase | 구현 |
|-------------|-----------|------|-------|------|
| `conftest.py` | `write_health_csv` fixture | — | 02 | ✅ |
| `test_shealth_bmi.py` | unittest 스모크, 파일 없음, 비율 범위 | #31, #36 | 02, 06 | ✅ |
| `test_classify_bmi_boundaries.py` | 경계 통합(나이대 100%) | #15~21 일부 | 03 | ✅ |
| `test_classify_bmi_unit.py` | `classify_bmi` 단위 | #15~18 | 03 | ✅ |
| `test_bmi_formula.py` | BMI 공식 전용 | #1~2 | 03 | ✅ |
| `test_impute_weight.py` | weight=0 | #10 | 04 | ✅ |
| `test_load_records.py` | 빈 행 continue | #42 | 05 | ✅ |
| `test_cli_logging.py` | ERROR 로그, 포맷, parse_args | #42, — | 05, 07 | ✅ |
| `test_age_band_policy.py` | `in_age_band`, `AGE_BANDS` | #40 일부 | 06 | ✅ |
| `test_bmi_classifier.py` | FakeClassifier 주입 | — | 07 | ✅ |
| `test_bmi_ratio_sum.py` | 4종 합 100%, 빈 대 | #27~28 | 06 | ✅ |
| `test_cli_main.py` | `main()` stdout/INFO | — | 08 | ✅ |

---

## 7. TC #1~45 추적성 매트릭스

| TC # | 시나리오 요약 | 우선순위 | 테스트 파일 / 비고 | 상태 |
|------|---------------|----------|-------------------|------|
| 1 | 표준 BMI 70/175 | P1 | `test_bmi_formula.py` | ✅ |
| 2 | cm→m 변환 | P1 | 동일 | ✅ |
| 3 | 저체중 경계 BMI | P0 | `test_classify_bmi_*` | ✅ |
| 4 | 18.500001 정상 | P0 | boundaries | ✅ |
| 5 | 22.999 정상 | P0 | unit parametrize 확장 | ✅ |
| 6 | 23.0 과체중 | P0 | boundaries | ✅ |
| 7 | 24.999 과체중 | P0 | unit 확장 | ✅ |
| 8 | 25.0 비만 | P0 | boundaries | ✅ |
| 9 | 고 BMI 극단 | P1 | unit | ✅ |
| 10 | weight=0 단일 | P0 | `test_impute_weight.py` | ✅ |
| 11 | 다건 0→평균 | P1 | impute parametrize | ✅ |
| 12 | 나이대 격리 | P1 | impute | ✅ |
| 13 | 보정 불가 | P1 | impute + 정책 문서 | ✅ |
| 14 | 보정 후 BMI | P1 | 통합 | ✅ |
| 15~18 | 분류 4범주 | P0 | unit | ✅ |
| 19~21 | 경계 18.5/23/25 | P0 | boundaries | ✅ |
| 22 | 100건 단일 범주 | P2 | 선택 | ⬜ |
| 23~26 | height=0 | P3 | Activities 4 | 백로그 |
| 27 | 4종 합 100% | P1 | `test_bmi_ratio_sum.py` | ✅ |
| 28 | 빈 나이대 0% | P1 | 동일 | ✅ |
| 29~30 | 전체 비율 | P3 | Activities 4 | 백로그 |
| 31 | shealth.dat 스모크 | P1 | `test_shealth_bmi.py` | ✅ |
| 32~35 | 정상 ID 목록 | P3 | Activities 4 | 백로그 |
| 36 | 파일 없음 | P0 | cli_logging / unittest | ✅ |
| 37 | 헤더만 | P0 | load_records 확장 | ✅ |
| 38~39 | 잘못된 행/컬럼 | P3 | Activities 4 | 백로그 |
| 40 | 나이 19세 | P1 | age_band_policy | ✅ |
| 41 | 음수 입력 | P3 | Activities 4 | 백로그 |
| 42 | 로깅·빈 행 | P0 | load + cli | ✅ |
| 43 | return N | P1 | load_records | ✅ |
| 44 | Golden 스냅샷 | P2 | `test_golden_master.py` · `src/test/golden/` | ✅ |
| 45 | 커버리지 ≥90% | 게이트 | Phase 08 | ✅ (99%) |

**범례:** ✅ 구현·Green · △ 부분 · ⬜ 미구현 · 백로그 = Activities 4

---

## 8. 실행 명령·Phase 체크리스트

### 8.1 일상 개발

```bash
pip install -r requirements-dev.txt
python -m pytest src/test/python -v
```

### 8.2 Activities 3 완료 게이트

```bash
python -m pytest src/test/python --cov=src/main/python --cov-report=term-missing --cov-fail-under=90
python -m pytest src/test/python --cov=src/main/python --cov-report=html
```

### 8.3 task_testplan Phase 체크리스트

| Phase | 파일 | 완료 조건 | 계획서 § |
|-------|------|-----------|----------|
| 01 | `01.phase_test_plan.md` | **본 문서** (`doc/test_plan.md`) | §1~8 |
| 02 | `02.phase_pytest_bootstrap.md` | `conftest.py` Green | §6 |
| 03 | `03.phase_bmi_formula_classify.md` | #1~2, parametrize 9건+ | §3.1~3.2 |
| 04 | `04.phase_impute_weight.md` | #10~14 | §3.3 |
| 05 | `05.phase_load_records_exceptions.md` | #36~37, #42 | §4 |
| 06 | `06.phase_integration_ratio_smoke.md` | #27~28, #31, #43 | §2.3 |
| 07 | `07.phase_classifier_protocol.md` | FakeClassifier | §2.4 |
| 08 | `08.phase_coverage_gate.md` | 90%+ HTML 리뷰 | §5 |
| 09 | `09.phase_register_prompt_report.md` | `prompt/05.test_case`, `report/05.test_case` | — |

### 8.4 Activities 3 잔여 작업 요약 (다음 구현 순)

1. `test_bmi_formula.py` — TC #1~2  
2. `test_bmi_ratio_sum.py` — TC #27~28  
3. `test_load_records.py` — TC #37, #43  
4. `test_impute_weight.py` parametrize — TC #11~13  
5. `test_cli_main.py` — `shealth_bmi.main` 커버리지  
6. `classify_bmi` parametrize 9건으로 `test_classify_bmi_unit.py` 확장  

---

## 9. 부록 — REQ ↔ TC 추적

| 요구 ID | 요구 요약 | 대표 TC # | P |
|---------|-----------|-----------|---|
| REQ-01 | CSV 로드 | 43, 31 | P0~P1 |
| REQ-02 | weight=0 보정 | 10~14 | P0~P1 |
| REQ-03 | height=0 보정 | 23~26 | P3 |
| REQ-04 | BMI 공식 | 1~2 | P1 |
| REQ-05 | BMI 분류 | 15~22 | P0 |
| REQ-06 | 나이대별 비율 | 27~28 | P1 |
| REQ-07 | 전체 비율 | 29~30 | P3 |
| REQ-08 | 정상 목록 | 32~35 | P3 |
| REQ-09 | 예외 처리 | 36~42 | P0~P3 |

---

*본 문서는 Phase 01 산출물이며, 구현 진행 시 §7 매트릭스 상태(✅/⬜)를 갱신한다.*
