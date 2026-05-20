# SHealth BMI — Activities 4 기능 개선 진행 계획

> **문서 목적:** README.md §4 · Activities 4(2시간) 범위의 구현·테스트·회귀 **진행 계획** 정리  
> **대상 코드:** `src/main/python/shealth.py`, `models.py`, `shealth_bmi.py`  
> **대상 테스트:** `src/test/python/` (신규·보강)  
> **실행 프롬프트:** [`task_feature/00.index.md`](../task_feature/00.index.md) Phase 01~09  
> **요구·TC:** [`requirements_analysis.md`](requirements_analysis.md) §1.2~1.7, §4  
> **작성 기준일:** 2026-05-20  
> **상태:** **구현 완료** (2026-05-20) — [`report/06.feature.md`](report/06.feature.md)

---

## 1. 개요

### 1.1 목표

| 항목 | 목표 |
|------|------|
| 기능 | `height=0` 보정, 전체 BMI 비율 API, 정상 범위 ID 목록, CSV 방어 파싱 |
| 품질 | 기존 pytest·Golden Master·커버리지 90%+ **유지** |
| 문서 | `doc/feature_policy.md`(정책), `prompt/06.feature.md`, `report/06.feature.md` |
| API 호환 | `calculate_bmi`, `get_bmi_ratio` 시그니처·의미 **불변** |

### 1.2 선행 조건 (완료됨)

| 항목 | 상태 |
|------|------|
| Activities 2 리팩토링 (Phase 01~08) | 완료 |
| Activities 3 pytest (45건+, 커버리지 99%) | 완료 |
| Golden Master TC #44 | 완료 |
| `weight=0` 나이대 평균 보정 (`_impute_weights`) | 완료 |
| BMI 분류 경계 25.0 포함 | 완료 |

### 1.3 현재 갭 (README §4 기준)

| 기능 | 구현 | 대표 TC |
|------|------|---------|
| `height=0` 나이대 평균 키 보정 | ✗ | #23~26 |
| `get_overall_bmi_distribution()` | ✗ | #29~30 |
| `get_normal_weight_user_ids()` | ✗ | #32~35 |
| 잘못된 CSV 행 스킵 + WARNING | ✗ | #38~39 |
| 보정·나이 구간 **정책 문서화** | ✗ | #24~25, #40 |
| 나이대 4종 비율 합 ≈100% | ○ | #27~28 (`test_bmi_ratio_sum.py`) |

---

## 2. 범위·우선순위

### 2.1 In Scope

- `SHealth._impute_heights()` 및 `calculate_bmi` 파이프라인 연결
- 공개 API 2종: `get_overall_bmi_distribution`, `get_normal_weight_user_ids`
- `_load_records` 행 단위 예외 처리 (스킵 + `logging.warning`)
- 정책서 `doc/feature_policy.md` (보정 불가·나이 20 미만/80 이상·API 분모)
- pytest TC #23~26, #29~30, #32~35, #38~39, (선택) #40
- Golden·CI 회귀 검증 (TC #44, #45)

### 2.2 Out of Scope / 선택

| 항목 | 비고 |
|------|------|
| `SupportsRecordReader` Protocol | README YAGNI — Phase 08에서 A/B 선택 |
| Reader/Imputer/Statistics **전면** 모듈 분리 | Phase 08 선택; 미실시 시 YAGNI 기록 |
| CLI에 신규 API 출력 | README 미요구 — API·테스트만 |
| Activities 5 회고·발표 | `prompt/07.final.md` 별도 |

### 2.3 우선순위

| 우선순위 | 내용 | Phase |
|----------|------|-------|
| **P0** | 정책 확정 (보정 순서·불가·ZeroDivision) | 01 |
| **P0** | `height=0` 보정 + 파이프라인 | 02 |
| **P1** | 신규 통계 API 2종 | 04, 05 |
| **P1** | 방어적 CSV + WARNING | 03 |
| **P1** | pytest TC 일괄 추가 | 06 |
| **P0** | Golden·커버리지·CI | 07 |
| **P2** | 클래스 분리 (선택) | 08 |
| **P2** | 프롬프트·보고서·README | 09 |

---

## 3. Phase별 진행 계획

**원칙:** Phase 완료마다 `py -3 -m pytest src/test/python -v` Green. Phase 07에서 Golden·`--cov-fail-under=90`.

| Phase | task_feature | 목표 | 주요 산출물 | 예상 |
|-------|--------------|------|-------------|------|
| **01** | `01.phase_feature_policy.md` | 보정·나이대·예외·API 계약 **1안 확정** | `doc/feature_policy.md` | ~15분 |
| **02** | `02.phase_impute_heights.md` | `_impute_heights` 구현 | `shealth.py` | ~20분 |
| **03** | `03.phase_defensive_csv.md` | 잘못된 행 스킵 + WARNING | `_load_records` | ~15분 |
| **04** | `04.phase_overall_distribution.md` | 전체 BMI 비율 API | `get_overall_bmi_distribution()` | ~15분 |
| **05** | `05.phase_normal_weight_ids.md` | 정상 ID 목록 API | `get_normal_weight_user_ids()` | ~15분 |
| **06** | `06.phase_feature_tests.md` | Activities 4 pytest | `test_impute_height.py` 등 4파일 | ~25분 |
| **07** | `07.phase_golden_regression.md` | Golden·스모크·CI | golden 갱신 여부 문서화 | ~10분 |
| **08** | `08.phase_optional_class_split.md` | 모듈 분리 **또는** YAGNI | `imputer.py` 등 또는 보고서만 | ~0~20분 |
| **09** | `09.phase_register_prompt_report.md` | 실습 문서 등록 | `prompt/06`, `report/06`, README §4 | ~15분 |

**권장 구현 순서:** 01 → 02 → 03 → 04 → 05 → 06 → 07 → (08) → 09  
**TDD 변형:** 01 정책 후 02·04·05를 06 테스트와 짝으로 진행해도 됨 (Phase 06을 02 직후 부분 실행 가능).

---

## 4. 기술 설계 요약

### 4.1 파이프라인 (목표)

```text
calculate_bmi(filename)
  → _reset_state()
  → _load_records()          # 방어: 잘못된 행 skip + warning
  → _impute_weights()        # 기존
  → _impute_heights()        # 신규 (weight와 대칭)
  → _compute_bmis()
  → _aggregate_ratios()
  → return count
```

### 4.2 보정 규칙 (Phase 01에서 확정)

| 단계 | 조건 | 방법 |
|------|------|------|
| weight | `weight == 0` | 동일 나이대 `weight > 0` 평균 (기존) |
| height | `height == 0` | 동일 나이대 `height > 0` 평균 (신규) |
| 순서 | — | weight → height → BMI |
| 불가 | 나이대 유효 샘플 0건 | **정책서 1안** (0 유지 / 제외 / fallback) |
| BMI | 보정 후 `height == 0` | 계산 **금지** (ZeroDivision 방지) |

### 4.3 신규 API (초안)

```python
def get_overall_bmi_distribution(self) -> dict[BmiCategory, float]:
    """전체 유효 레코드 BMI 범주별 비율(%). 4범주 합 ≈ 100."""

def get_normal_weight_user_ids(self) -> list[int]:
    """18.5 < BMI < 23 인 id, 파일 입력 순서."""
```

- 분류: 기존 `self._classifier` / `BmiThresholds`와 동일
- `get_overall_*` 분모 N: Phase 01에서 정의 (BMI 유효 건수 권장)

### 4.4 CSV 방어 (목표)

| 상황 | 동작 |
|------|------|
| 빈 행 | `continue` (기존) |
| 필수 컬럼 누락 | `warning` + `continue` |
| 비숫자 변환 실패 | `warning` + `continue` |
| 파일 없음 | `error` + count 0 (기존) |

---

## 5. 테스트 계획

### 5.1 신규·보강 테스트 파일

| 파일 | TC # | Phase |
|------|------|-------|
| `test_impute_height.py` | #23~26 | 02, 06 |
| `test_overall_distribution.py` | #29~30 | 04, 06 |
| `test_normal_weight_ids.py` | #32~35 | 05, 06 |
| `test_load_records_invalid.py` (또는 `test_load_records.py` 확장) | #38~39 | 03, 06 |
| (선택) `test_age_out_of_band.py` | #40 | 06 |

### 5.2 기존 테스트 (유지·회귀)

| 파일 | TC # | 비고 |
|------|------|------|
| `test_bmi_ratio_sum.py` | #27~28 | **재작성 불필요** |
| `test_impute_weight.py` | #10~14 | height 보정 후에도 Green |
| `test_golden_master.py` | #44 | height가 `shealth.dat`에 없으면 golden **불변** 기대 |

### 5.3 TC 추적성 (Requirements → Test)

| 요구 ID | 요구 요약 | TC # | Phase |
|---------|-----------|------|-------|
| REQ-03 | height=0 보정 | 23~26 | 02, 06 |
| REQ-07 | 전체 비율 | 29~30 | 04, 06 |
| REQ-08 | 정상 목록 | 32~35 | 05, 06 |
| REQ-09 | 예외·방어 | 38~39 | 03, 06 |

---

## 6. Golden Master·CI

### 6.1 Golden 영향 분석 (Phase 07)

1. `shealth.dat`에서 `height=0` 건수 확인.
2. **0건:** CLI 6줄 golden **변경 없음**이 정상.
3. **1건 이상 또는 보정으로 비율 변동:** `UPDATE_GOLDEN=1` 후 `src/test/golden/shealth_dat_stdout.txt` 갱신·커밋.

```bash
py -3 -m pytest -m golden_master -v

set UPDATE_GOLDEN=1
py -3 -m pytest -m golden_master -v
```

### 6.2 품질 게이트

| 게이트 | 명령 | 기준 |
|--------|------|------|
| Unit | `py -3 -m pytest -m "not golden_master" -v` | 전건 Green |
| Coverage | `... --cov-fail-under=90` | 라인 ≥ 90% |
| Golden | `py -3 -m pytest -m golden_master -v` | TC #44 Green |
| CI | `.github/workflows/pytest.yml` | unit+cov / golden job |

---

## 7. README To-Do §4 체크리스트

구현·검증 완료 시 `[x]` 처리.

### 4.1 데이터 입력 · 전처리

- [x] CSV 로드
- [x] `weight=0` 보정
- [ ] `height=0` 보정 — TC #23~26
- [ ] 보정 불가 정책 (스킵·fallback·WARNING)
- [ ] 빈 행·컬럼 부족·비숫자 방어

### 4.2 BMI 계산 · 분류

- [x] BMI 공식·분류·경계 25.0

### 4.3 통계 · 조회 API

- [x] 나이대별 비율 (`get_bmi_ratio`)
- [x] 나이대 4종 합 ≈100% — TC #27~28
- [ ] `get_overall_bmi_distribution` — TC #29~30
- [ ] `get_normal_weight_user_ids` — TC #32~35
- [ ] 20세 미만·80세 이상 정책 확정

### 4.4 설계

- [x] load / impute / compute / aggregate 분리
- [x] Protocol·`HealthRecord`·type hint
- [ ] Reader / Imputer / Statistics 분리 (선택)
- [ ] `prompt/06.feature.md`, `report/06.feature.md`

---

## 8. 실행 명령 (프로젝트 루트)

```bash
# 전체 unit (golden 제외)
py -3 -m pytest -v

# Activities 4 신규 TC (Phase 06 이후)
py -3 -m pytest src/test/python/test_impute_height.py src/test/python/test_overall_distribution.py src/test/python/test_normal_weight_ids.py -v

# 커버리지 게이트
py -3 -m pytest -m "not golden_master" --cov=src/main/python --cov-report=term-missing --cov-fail-under=90

# Golden
py -3 -m pytest -m golden_master -v
```

---

## 9. 산출물·관련 문서

| 산출물 | 경로 | Phase |
|--------|------|-------|
| 기능 정책서 | `doc/feature_policy.md` | 01 |
| 진행 계획 (본 문서) | `doc/feature_plan.md` | — |
| Phase 프롬프트 | `task_feature/01~09.phase_*.md` | 01~09 |
| 실습 프롬프트 | `prompt/06.feature.md` | 09 |
| 실습 보고서 | `report/06.feature.md` | 09 |
| 테스트 계획 (Activities 3) | `doc/test_plan.md` | 참조 |
| Golden 설계 | `doc/golden_master_plan.md` | 07 |

---

## 10. 리스크·완화

| 리스크 | 완화 |
|--------|------|
| Golden 의도치 않은 변경 | Phase 07에서 `shealth.dat` height=0 조사 후 갱신 |
| weight/height 보정 정책 불일치 | Phase 01에서 `test_impute_weight` 정책과 대칭 명시 |
| `calculate_bmi` count 의미 변경 | 스킵 행은 count 제외 — 정책·TC #43과 정합 |
| 커버리지 하락 | Phase 06·07에서 `--cov-fail-under=90` 필수 |
| 과도한 리팩토링 | Phase 08 YAGNI(B) 허용 |

---

*마지막 업데이트: 2026-05-20*
