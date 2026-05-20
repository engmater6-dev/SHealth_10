# SHealth BMI — 결함 목록 (Defect List)

> **문서 목적:** Activities 1~4(코드 분석·리팩토링·단위 테스트·기능 개선) 과정에서 발견된 결함·회귀·미구현 항목 추적  
> **작성 기준일:** 2026-05-20  
> **최종 재분석:** 2026-05-20 (Activities 4 완료 후)  
> **참조:** [`requirements_analysis.md`](requirements_analysis.md) · [`test_plan.md`](test_plan.md) · [`feature_policy.md`](feature_policy.md) · [`report/05.test_case.md`](../report/05.test_case.md) · [`report/06.feature.md`](../report/06.feature.md)  
> **현재 테스트:** **64건** unit Green (+2 golden) · 커버리지 **99%**

---

## 1. 요약

| 상태 | 건수 | 설명 |
|------|------|------|
| **Fixed** | 15 | 리팩토링·Activities 4·TC로 수정·검증 완료 |
| **Open** | 0 | — |
| **Known Limitation** | 2 | 정책 확정·문서화 완료, 의도적 동작 고정 |

| Severity | Fixed | Open | Known Limitation |
|----------|-------|------|------------------|
| Critical | 1 | 0 | 0 |
| High | 6 | 0 | 0 |
| Medium | 6 | 0 | 2 |
| Low | 1 | 0 | 0 |

### Activities 4 재분석 결과 (2026-05-20)

| 변경 | Defect ID | 내용 |
|------|-----------|------|
| **Open → Fixed** | DEF-008, DEF-009 | `_impute_heights()`, `_compute_bmis` height 가드 |
| **Open → Fixed** | DEF-011, DEF-012 | `_parse_health_row()` + 행 스킵 WARNING |
| **Open → Fixed** | DEF-013, DEF-014 | `get_overall_bmi_distribution()`, `get_normal_weight_user_ids()` |
| **Open → Fixed (문서화)** | DEF-016 | [`feature_policy.md`](feature_policy.md) §2 + `test_age_out_of_band.py` |
| **Open → Fixed** | DEF-015 | 음수 weight/height → WARNING + skip (TC #41) |
| **Known Limitation 유지** | DEF-010 | 전원 weight=0 보정 불가 (height 전원 0은 TC #25로 동일 정책) |

---

## 2. 결함 상세

### DEF-001 — BMI 25.0 비만 분류 누락

| 항목 | 내용 |
|------|------|
| **ID** | DEF-001 |
| **Severity** | High |
| **ItemType** | Functional (비즈니스 규칙) |
| **Status** | **Fixed** (Phase 03, TC #8·#21) |
| **Steps** | 1. BMI가 정확히 `25.0`인 레코드 1건을 CSV에 넣는다.<br>2. `SHealth.calculate_bmi()` 실행 후 `get_bmi_ratio(age, 400)` 조회. |
| **Expected** | README 기준 **25 이상 비만** → `OBESITY`(400) 비율 100% |
| **Actual** (레거시) | `elif bmi > 25` 조건으로 **25.0은 비만 미분류** |
| **Root Cause** | 경계값 연산자 오류(`>` vs `>=`), 분류 로직 중복 |
| **Fix Summary** | `WhoAsiaPacificClassifier`·`classify_bmi()` 단일화, `bmi >= 25` → `OBESITY`. `test_classify_bmi_boundaries.py`, `test_classify_bmi_unit.py` |

---

### DEF-002 — CSV 중간 빈 행 이후 데이터 미로드

| 항목 | 내용 |
|------|------|
| **ID** | DEF-002 |
| **Severity** | High |
| **ItemType** | Data / Functional |
| **Status** | **Fixed** (Phase 04, TC #42) |
| **Steps** | 1. 헤더 + 데이터 1행 + **빈 행** + 데이터 1행 CSV.<br>2. `calculate_bmi()` 호출. |
| **Expected** | 빈 행 무시, 이후 행까지 로드 (`continue`) |
| **Actual** (레거시) | `break`로 읽기 중단 |
| **Fix Summary** | `_is_blank_row()` + `continue`. `test_load_records.py::test_load_records_skips_blank_row_in_middle` |

---

### DEF-003 — 파일 없음 시 `print` 사용

| 항목 | 내용 |
|------|------|
| **ID** | DEF-003 |
| **Severity** | Medium |
| **ItemType** | Error Handling / Observability |
| **Status** | **Fixed** (Phase 06, TC #36·#42) |
| **Steps** | 1. 존재하지 않는 경로로 `calculate_bmi()` 호출.<br>2. stdout·로그 확인. |
| **Expected** | `logging.ERROR`, `return 0`, 도메인 `print` 없음 |
| **Actual** (레거시) | `print("Failed to open file: ...")` |
| **Fix Summary** | `logger.error(...)` in `_load_records`. `test_cli_logging.py` + `caplog` |

---

### DEF-004 — BMI 경계 통합 TC float 역산 드리프트

| 항목 | 내용 |
|------|------|
| **ID** | DEF-004 |
| **Severity** | Medium |
| **ItemType** | Test / Functional |
| **Status** | **Fixed** (테스트 설계 보완) |
| **Steps** | 1. `target_bmi=25.0` weight 역산 후 `calculate_bmi`. |
| **Expected** | 비만 100% |
| **Actual** (초기 TC) | BMI `24.999…`로 과체중 assert 실패 |
| **Fix Summary** | `_weight_for_bmi()` + `math.nextafter`. `test_classify_bmi_boundaries.py` |

---

### DEF-005 — CSV `encoding` 미지정

| 항목 | 내용 |
|------|------|
| **ID** | DEF-005 |
| **Severity** | Low |
| **ItemType** | Data / Portability |
| **Status** | **Fixed** (Phase 04) |
| **Fix Summary** | `open(..., encoding="utf-8")` in `_load_records` |

---

### DEF-006 — CSV 컬럼 `row[1..3]` 인덱스 하드코딩

| 항목 | 내용 |
|------|------|
| **ID** | DEF-006 |
| **Severity** | Medium |
| **ItemType** | Maintainability / Data |
| **Status** | **Fixed** (Phase 04) |
| **Fix Summary** | `csv.DictReader` + `FIELD_*` 상수. Activities 4에서 `_parse_health_row()`로 파싱 일원화 |

---

### DEF-007 — BMI 분류 로직 중복·매직 넘버

| 항목 | 내용 |
|------|------|
| **ID** | DEF-007 |
| **Severity** | Medium |
| **ItemType** | Maintainability |
| **Status** | **Fixed** (Phase 03·05) |
| **Fix Summary** | `BmiThresholds`, `BmiCategory`, `classify_bmi()`, `WhoAsiaPacificClassifier`, Protocol 주입 |

---

### DEF-008 — `height=0` 결측 보정 미구현

| 항목 | 내용 |
|------|------|
| **ID** | DEF-008 |
| **Severity** | High |
| **ItemType** | Functional (요구사항) |
| **Status** | **Fixed** (Activities 4 Phase 02, TC #23~26) |
| **Steps** | 1. 동일 나이대 `height=0` + 유효 키 레코드 CSV.<br>2. `calculate_bmi()` 실행. |
| **Expected** | 동일 나이대 **평균 키** 보정 후 BMI 산출 |
| **Actual** (레거시) | `_impute_heights` 없음 |
| **Root Cause** | 1차 리팩토링에서 weight만 구현 |
| **Fix Summary** | `_impute_heights()` — `_impute_weights`와 대칭. `calculate_bmi`에서 weight 다음 호출. `test_impute_height.py` (5 TC). [`feature_policy.md`](feature_policy.md) §1 |

---

### DEF-009 — `height=0` + 유효 weight 시 BMI 계산 예외 위험

| 항목 | 내용 |
|------|------|
| **ID** | DEF-009 |
| **Severity** | Critical |
| **ItemType** | Functional / Robustness |
| **Status** | **Fixed** (Activities 4, DEF-008 연동, TC #25) |
| **Steps** | 1. 보정 불가(전원 `height=0`) 또는 `height=0` 유지 레코드로 `calculate_bmi()`. |
| **Expected** | ZeroDivision 없음 — 보정 또는 `bmi=0.0` |
| **Actual** (레거시) | `weight / (height_m ** 2)` → **ZeroDivisionError** |
| **Fix Summary** | `_impute_heights()` + `_compute_bmis`에서 `height==0` → `bmi=0.0`, skip 나눗셈. `test_impute_height.py::test_impute_height_all_zero_in_band_stays_zero` |

---

### DEF-010 — 동일 나이대 전원 `weight=0` 시 보정 불가

| 항목 | 내용 |
|------|------|
| **ID** | DEF-010 |
| **Severity** | Medium |
| **ItemType** | Functional / Data Quality |
| **Status** | **Known Limitation** (정책 확정, TC #13) |
| **Steps** | 1. 40대 전원 `weight=0` CSV.<br>2. `calculate_bmi()` 후 `weights`·`bmis` 확인. |
| **Expected** | 요구 미명시 — fallback / 제외 / WARNING 중 택일 |
| **Actual** | `valid_weights` 없으면 `continue` → **weight=0 유지**, BMI=0 |
| **Root Cause** | 보정 불가 시 fallback·로그 없음 |
| **Fix Summary** | **정책 1안 확정:** 0 유지, 전체 평균 fallback 없음. [`feature_policy.md`](feature_policy.md) §1. **height 전원 0**도 동일(TC #25). `test_impute_weight.py::test_impute_weight_all_zero_in_band_stays_zero` |

---

### DEF-011 — 잘못된 형식 CSV 행 시 예외 전파

| 항목 | 내용 |
|------|------|
| **ID** | DEF-011 |
| **Severity** | High |
| **ItemType** | Error Handling / Robustness |
| **Status** | **Fixed** (Activities 4 Phase 03, TC #38) |
| **Steps** | 1. 비숫자 age/weight/height 행 포함 CSV 로드. |
| **Expected** | 해당 행 **스킵** + `logging.WARNING`, 나머지 계속 |
| **Actual** (레거시) | `ValueError` → 전체 `calculate_bmi` 실패 |
| **Fix Summary** | `_parse_health_row()` + `_load_records` 행 단위 try/except + WARNING. `test_load_records_invalid.py::test_skip_non_numeric_row_with_warning` |

---

### DEF-012 — 컬럼 부족 행 처리 없음

| 항목 | 내용 |
|------|------|
| **ID** | DEF-012 |
| **Severity** | High |
| **ItemType** | Error Handling / Data |
| **Status** | **Fixed** (Activities 4, TC #39) |
| **Steps** | 1. `1,20,70` (height 누락) 행 포함 CSV. |
| **Expected** | 행 스킵 + WARNING |
| **Actual** (레거시) | `int(None)` 등 **예외** |
| **Fix Summary** | `_parse_health_row()` 필수 필드 검증. DEF-011과 동일 PR. `test_load_records_invalid.py::test_skip_short_row_with_warning` |

---

### DEF-013 — 전체 사용자 BMI 비율 API 미구현

| 항목 | 내용 |
|------|------|
| **ID** | DEF-013 |
| **Severity** | Medium |
| **ItemType** | Functional (신규 요구) |
| **Status** | **Fixed** (Activities 4 Phase 04, TC #29~30) |
| **Steps** | 1. 유효 레코드 N건 로드.<br>2. `get_overall_bmi_distribution()` 호출. |
| **Expected** | 전체 대비 4범주 비율(%) |
| **Actual** (레거시) | API 없음 |
| **Fix Summary** | `get_overall_bmi_distribution() -> dict[BmiCategory, float]`, 분모=`height>0` 건수. `test_overall_distribution.py` |

---

### DEF-014 — 정상 체중 사용자 ID 목록 API 미구현

| 항목 | 내용 |
|------|------|
| **ID** | DEF-014 |
| **Severity** | Medium |
| **ItemType** | Functional (신규 요구) |
| **Status** | **Fixed** (Activities 4 Phase 05, TC #32~35) |
| **Steps** | 1. 정상·경계 BMI 사용자 CSV.<br>2. `get_normal_weight_user_ids()` 호출. |
| **Expected** | `18.5 < BMI < 23` 인 id 목록, 입력 순서, 경계 제외 |
| **Actual** (레거시) | API 없음 |
| **Fix Summary** | `get_normal_weight_user_ids() -> list[int]`. `test_normal_weight_ids.py` |

---

### DEF-015 — 음수 weight/height 입력 검증 없음

| 항목 | 내용 |
|------|------|
| **ID** | DEF-015 |
| **Severity** | Medium |
| **ItemType** | Data Validation |
| **Status** | **Fixed** (TC #41) |
| **Steps** | 1. `weight=-1` 또는 `height=-1` 행 포함 CSV 로드. |
| **Expected** | 스킵 또는 ERROR — 요구 정책에 따름 |
| **Actual** | 그대로 로드·BMI 계산(음수 BMI 가능) |
| **Root Cause** | `_parse_health_row()`에 부호 검증 없음 |
| **Fix Summary** | `weight < 0` / `height < 0` → `ValueError` in `_parse_health_row()`, WARNING + skip in `_load_records`. `test_load_records_invalid.py::test_skip_negative_weight_or_height_with_warning` |

---

### DEF-016 — 20세 미만·80세 이상 통계 제외 정책 미문서화

| 항목 | 내용 |
|------|------|
| **ID** | DEF-016 |
| **Severity** | Low |
| **ItemType** | Functional / Specification |
| **Status** | **Fixed (Documented)** (Activities 4, TC #40) |
| **Steps** | 1. `age=19` 레코드 로드.<br>2. `get_bmi_ratio(20, *)` vs `get_overall_bmi_distribution()` 비교. |
| **Expected** | 정책 문서화 |
| **Actual** (확정) | **나이대 비율:** 20~79만 집계 → 20대 ratio 0.0<br>**전체 비율·정상 ID:** 로드된 모든 연령 포함 |
| **Fix Summary** | [`feature_policy.md`](feature_policy.md) §2. `test_age_out_of_band.py::test_age_19_excluded_from_age_band_ratios_included_in_overall` |

---

### DEF-017 — `calculate_bmi` God Method로 인한 테스트·회귀 취약

| 항목 | 내용 |
|------|------|
| **ID** | DEF-017 |
| **Severity** | Medium |
| **ItemType** | Testability / Design |
| **Status** | **Fixed** (Phase 01~08 + Activities 4) |
| **Steps** | 1. 보정·API 변경 시 단계별 검증 필요. |
| **Expected** | load / impute / compute / aggregate 분리 |
| **Actual** (레거시) | 단일 Long Method |
| **Fix Summary** | `_reset_state`, `_load_records`, `_impute_weights`, `_impute_heights`, `_compute_bmis`, `_aggregate_ratios` + 신규 공개 API. **62** pytest TC |

---

## 3. TC · 결함 추적

| Defect ID | 대표 TC # | 테스트 파일 | Status |
|-----------|-----------|-------------|--------|
| DEF-001 | #8, #21 | `test_classify_bmi_boundaries.py`, `test_classify_bmi_unit.py` | Fixed |
| DEF-002 | #42 | `test_load_records.py` | Fixed |
| DEF-003 | #36, #42 | `test_cli_logging.py` | Fixed |
| DEF-004 | #21 | `test_classify_bmi_boundaries.py` | Fixed |
| DEF-005 | — | (리팩토링 검증) | Fixed |
| DEF-006 | — | `_parse_health_row` (Activities 4) | Fixed |
| DEF-007 | #15~21 | `test_classify_bmi_unit.py` | Fixed |
| DEF-008 | #23~26 | `test_impute_height.py` | Fixed |
| DEF-009 | #25 | `test_impute_height.py` | Fixed |
| DEF-010 | #13, #25 | `test_impute_weight.py`, `test_impute_height.py` | Known Limitation |
| DEF-011 | #38 | `test_load_records_invalid.py` | Fixed |
| DEF-012 | #39 | `test_load_records_invalid.py` | Fixed |
| DEF-013 | #29~30 | `test_overall_distribution.py` | Fixed |
| DEF-014 | #32~35 | `test_normal_weight_ids.py` | Fixed |
| DEF-015 | #41 | `test_load_records_invalid.py` | Fixed |
| DEF-016 | #40 | `test_age_out_of_band.py` | Fixed (Documented) |
| DEF-017 | #43 등 | 전체 suite (62 unit) | Fixed |

---

## 4. 미해결·후속 작업

| 우선순위 | ID | 권장 조치 |
|----------|-----|-----------|
| — | DEF-010 | 제품 요구 변경 시에만 fallback/제외 정책 재검토 |

---

## 5. Golden Master · 실데이터 영향

| 항목 | 결과 |
|------|------|
| `shealth.dat` `height=0` | **0건** |
| TC #44 golden | **변경 없음** (Activities 4 후 `pytest -m golden_master` Green) |
| DEF-001(25.0) | 이전 golden 갱신 이력 — 현재 기준 파일과 일치 |

---

## 6. 변경 이력

| 일자 | 변경 |
|------|------|
| 2026-05-20 | 초안 작성 — Fixed 7건, Open 9건, Known Limitation 1건 |
| 2026-05-20 | **Activities 4 재분석** — Fixed 14건, Open 1건(DEF-015), Known Limitation 2건(DEF-010·height 대칭). DEF-008~014, DEF-016·009 해소 반영 |
| 2026-05-20 | **DEF-015 해소** — 음수 weight/height 검증(TC #41), Open 0건, Fixed 15건 |

---

*본 문서는 테스트 실패 로그·QA·pytest·코드 리뷰를 통해 식별된 결함을 기록한다. Open 항목 수정 시 Status·Fix Summary·§3 추적 표를 함께 갱신한다.*
