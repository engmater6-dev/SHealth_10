# SHealth BMI — Activities 4 기능 정책

> **기준:** [`feature_plan.md`](feature_plan.md) Phase 01  
> **작성일:** 2026-05-20

---

## 1. 보정 순서·불가

| 순서 | 단계 | 규칙 |
|------|------|------|
| 1 | load | 유효 CSV 행만 `HealthRecord` 적재 |
| 2 | weight impute | `weight==0` → 동일 나이대 `weight>0` 평균 |
| 3 | height impute | `height==0` → 동일 나이대 `height>0` 평균 |
| 4 | BMI | `height>0` 만 계산; `height==0` → `bmi=0.0` (ZeroDivision 금지) |
| 5 | aggregate | 기존 나이대별 비율 |

**보정 불가 (나이대 유효 샘플 0건):** 값 **0 유지** (`test_impute_weight` TC #13과 동일). 전체 평균 fallback 없음.

**weight·height 동시 0 (TC #24):** weight 보정 후 height 보정. 둘 다 보정 가능하면 BMI 산출.

---

## 2. 나이대·통계 대상

| 구간 | 나이대 비율 (`get_bmi_ratio`) | 보정 (`_records_in_band`) | 전체 비율·정상 ID |
|------|------------------------------|---------------------------|-------------------|
| 20≤age<80 | 포함 | 포함 | 포함 |
| age<20, age≥80 | 제외 (0%) | 제외 | **포함** (로드된 레코드) |

---

## 3. 신규 API

### `get_overall_bmi_distribution() -> dict[BmiCategory, float]`

- **분모 N:** `height > 0` 인 레코드 수 (보정 후)
- **분자:** 각 범주 인원
- **N=0:** 네 범주 모두 `0.0`

### `get_normal_weight_user_ids() -> list[int]`

- **조건:** `18.5 < BMI < 23` (`BmiThresholds`와 동일)
- **대상:** `height > 0` 이고 BMI 계산된 레코드
- **순서:** CSV 입력 순서
- **경계:** BMI=18.5, 23.0 **제외** (TC #33)

---

## 4. CSV 예외

| 상황 | 동작 |
|------|------|
| 빈 행 | `continue` |
| 필수 키 누락·빈 값 | `logger.warning` + `continue` |
| 비숫자 변환 실패 | `logger.warning` + `continue` |
| 파일 없음 | `logger.error` + count 0 |

스킵 행은 `count`에 **포함하지 않음**.

---

## 5. Golden Master

`shealth.dat` (4822행)에 `height=0` **0건** → height 보정만으로 CLI golden **불변** 기대.

---

*마지막 업데이트: 2026-05-20*
