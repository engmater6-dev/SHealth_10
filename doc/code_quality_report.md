# SHealth BMI — 코드 품질 분석 보고서

> **분석 대상:** `src/main/python/shealth.py`, `src/main/python/shealth_bmi.py`  
> **관점:** SOLID, Code Smell, Python 관용구, PEP 8  
> **작성일:** 2026-05-19  
> **분석자 역할:** 시니어 Python 아키텍트 / 클린코드 리뷰

---

## 1. 요약

| 파일 | LOC | 핵심 이슈 |
|------|-----|-----------|
| `shealth.py` | 99 | `calculate_bmi` 단일 메서드에 I/O·보정·계산·집계가 집중 (SRP/OCP 위반, Long Method) |
| `shealth_bmi.py` | 19 | 진입점이 도메인 상수·나이대 루프를 중복 하드코딩 (Duplicated Code, Magic Number) |

현재 구조는 **기능 동작은 가능**하나, 요구사항 문서(`doc/requirements_analysis.md`)에 명시된 height 보정·로깅·방어적 파싱 등은 미구현이며, 확장·테스트·유지보수 비용이 `SHealth.calculate_bmi` 한 곳에 집중되어 있다.

---

## 2. SRP / OCP 위반 지점

### 2.1 Single Responsibility Principle (SRP)

| 위치 | 위반 내용 | 근거 |
|------|-----------|------|
| `SHealth` 클래스 전체 | 데이터 로드, 결측 보정, BMI 산출, 나이대별 비율 집계, 오류 출력을 한 클래스가 담당 | 클래스 docstring은 “BMI 계산”이나 실제로는 **ETL + 통계 엔진 + 프레젠테이션 에러 처리** 역할이 혼재 |
| `calculate_bmi` | 파일 I/O(`open`/`csv`), 상태 초기화, weight imputation, BMI formula, category 집계, ratio 저장을 단일 메서드에서 수행 | 메서드가 변경되는 이유가 5가지 이상 (파일 형식 변경, 보정 규칙, BMI 공식, 분류 임계값, 출력 스키마) |
| `shealth_bmi.main` | 애플리케이션 조립 + 콘솔 포맷 출력 | 진입점이므로 어느 정도 허용되나, 포맷 문자열·나이대·타입 코드가 도메인과 중복 |

### 2.2 Open/Closed Principle (OCP)

| 위치 | 위반 내용 | 근거 |
|------|-----------|------|
| BMI 분류 `if/elif` (L79–86) | 임계값 `18.5`, `23`, `25` 및 범주 수가 메서드 내부에 고정 | 새 범주(예: “고도비만”) 추가 시 **기존 메서드 수정** 필요, 테스트·정책 주입 불가 |
| 나이대 `range(20, 80, 10)` (L48, L70, `shealth_bmi` L8) | 연령 구간 정책이 코드 전역에 산재 | 5세 단위 등 정책 변경 시 여러 파일·루프 수정 |
| CSV 컬럼 인덱스 `row[1]`, `row[2]`, `row[3]` (L39–41) | 스키마가 파서와 강결합 | 헤더 이름 기반(`DictReader`)이나 다른 소스(DB) 추가 시 `calculate_bmi` 전면 수정 |
| `UNDERWEIGHT=100` 등 정수 코드 | 의미는 Enum/타입으로 표현 가능하나 조회 키로만 사용 | 출력·저장·조회 계층이 동일 정수에 의존, 확장 시 매직 넘버 증가 |

**OCP 개선 방향 (개념):** `BmiClassifier` / `AgeBandPolicy` / `HealthRecordSource` 인터페이스(또는 `Protocol` + `__subclasshook__`)로 분리하면, 기존 `SHealth`는 조합(composition)만 변경하고 분류·구간·입력원은 교체 가능.

---

## 3. Code Smell 상세

| 스멜 | 위치 | 설명 |
|------|------|------|
| **Long Method** | `calculate_bmi` (~70행) | 읽기·보정·계산·집계가 한 흐름; 단위 테스트를 메서드 단위로 쪼개기 어려움 |
| **Magic Number** | `18.5`, `23`, `25`, `20`, `80`, `10`, `100`, `200`, `300`, `400`, `row[1..3]` | 의미 있는 상수가 이름 없이 반복 |
| **Duplicated Code** | 나이대 루프 3회 (`shealth.py` 2회 + `shealth_bmi.py` 1회) | 동일 `a <= age < a+10` 패턴·범위 반복 |
| **Duplicated Code** | BMI 타입 코드 | `SHealth` 상수 vs `main`의 `100, 200, 300, 400` 리터럴 |
| **Feature Envy / 데이터 클로킹** | `ages`, `heights`, `weights`, `bmis` 공개 리스트 + 인덱스 `i` 순회 | 레코드 단위 연산이 리스트 인덱스에 분산 |
| **Primitive Obsession** | `(age_class, bmi_type)` 튜플 키 | 도메인 객체(`AgeBand`, `BmiCategory`) 부재 |
| **Shotgun Surgery (잠재)** | 나이대·임계값·파일 경로 변경 | 여러 위치 동시 수정 필요 |
| **조건 복잡도** | 중첩 `for i` + `if a <= self.ages[i] < a + 10` | 가독성 저하, off-by-one·경계 버그 위험 |
| **잘못된 추상화 신호** | `if not row: break` (L37–38) | 빈 행에서 **전체 읽기 중단** — `continue`가 일반적; 요구 QA와 불일치 가능 |
| **Swallowed / Weak Error Handling** | `except FileNotFoundError: print(...); return 0` | 호출자가 실패 원인 구분 불가, `logging`·커스텀 예외 없음 |

---

## 4. Python 특화 이슈

| 문제 | 위치 | 설명 |
|------|------|------|
| **타입 힌트 부분 적용** | `SHealth` | `calculate_bmi`/`get_bmi_ratio`만 힌트; `ages: list[int]` 등 필드·내부 변수 미표기 |
| **타입 힌트 부재** | `shealth_bmi.main` | `-> None` 및 인자 타입 없음 |
| **문자열 하드코딩** | `"Failed to open file: {filename}"`, `"shealth.dat"`, f-string 라벨 | i18n·설정·테스트 격리 어려움 |
| **isinstance / Protocol 미활용** | 전역 | 파일 소스·분류 전략을 교체할 확장점 없음; duck typing만으로는 계약 불명확 |
| **Enum 미사용** | BMI 타입 `100~400` | `enum.IntEnum`으로 `SHealth.UNDERWEIGHT`와 출력 계층 통일 가능 |
| **dataclass 미사용** | 행 단위 데이터 | `HealthRecord(id, age, weight, height)` 없이 평행 리스트 4개 — 불변식 깨지기 쉬움 |
| **csv.reader 인덱스 접근** | L39–41 | `DictReader` + 필드명이 Pythonic하고 스키마 변경에 강함 |
| **encoding 미지정** | `open(filename, "r")` | Windows 환경에서 인코딩 이슈 가능 → `encoding="utf-8"` 권장 |
| **print로 에러 처리** | L44 | 라이브러리 코드에서 side effect; `logging` 또는 예외 전파 권장 |

---

## 5. PEP 8 / Pythonic 개선 방향

| 영역 | 현재 | 개선 방향 |
|------|------|-----------|
| 상수 | 클래스 변수 100~400 | `enum.IntEnum` 또는 `typing.Literal` + `Final` |
| 레코드 | `ages[]`, `weights[]` … | `@dataclass(frozen=True) class HealthRecord` |
| 나이대 집계 | 이중 인덱스 루프 | `itertools.groupby` 또는 `dict[AgeBand, list[HealthRecord]]` 사전 그룹핑 |
| BMI 분류 | 긴 if/elif | **전략 패턴**: `BmiCategory.classify(bmi: float) -> BmiCategory` |
| 확장점 | 없음 | `typing.Protocol` + `@runtime_checkable` / `__subclasshook__`로 `SupportsBmiClassification`, `SupportsRecordReader` 정의 |
| 파일 경로 | 문자열 | `pathlib.Path` |
| 진입점 | 하드코딩 경로 | `argparse`로 `shealth.dat`·출력 형식 주입 |
| 경계값 | `elif self.bmis[i] > 25` | 요구사항은 `>= 25` → `bmi >= 25`로 통일 (비만 경계 포함) |

**전략 패턴 스케치 (개념):**

```python
class BmiClassifier(Protocol):
    def classify(self, bmi: float) -> BmiCategory: ...

class WhoAsiaPacificClassifier:
    THIN = 18.5
    NORMAL_HI = 23
    OVER_HI = 25
    def classify(self, bmi: float) -> BmiCategory: ...
```

---

## 6. 리팩토링 우선순위 (1~5)

| 순위 | 항목 | 이유 |
|------|------|------|
| **1** | `calculate_bmi` 분해 (load → impute → compute bmi → aggregate) | SRP·Long Method 해소, 단위 테스트·90% 커버리지 달성의 전제 |
| **2** | Magic Number → Named Constant / Enum / `BmiThresholds` dataclass | 버그(경계 `> 25` vs `>= 25`) 방지, OCP 기반 마련 |
| **3** | `HealthRecord` dataclass + 나이대 그룹핑 한 곳으로 통합 | Duplicated Code 제거, height 보정 등 신규 요구 추가 용이 |
| **4** | `shealth_bmi.py`에서 `SHealth` 상수·포맷터 사용, 경로 인자화 | 진입점·도메인 불일치 제거, Smell만으로도 체감 개선 큼 |
| **5** | Protocol/전략으로 분류·Reader 교체 가능 구조 | 요구 변경 빈도 대비 투자 대비 효과는 1~4 이후가 적절 |

---

## 7. 종합 분석표

| 문제점 | 위반 원칙 / 스멜 | 영향 | 개선 방향 | 우선순위 |
|--------|------------------|------|-----------|----------|
| `calculate_bmi`가 파일 읽기·보정·BMI·비율 집계·상태 초기화를 모두 수행 | **SRP**, Long Method, God Method | 변경 영향 범위 큼, 테스트 단위 분리 불가, 가독성 저하 | private 메서드 또는 서비스 클래스 4분할: `load_records`, `impute_weights`, `compute_bmis`, `aggregate_ratios` | **1** |
| BMI 임계값·나이대 범위가 메서드/파일에 하드코딩 | **OCP**, Magic Number | 정책 변경 시 다수 수정, 경계값 불일치 위험 (`> 25` vs `>= 25`) | `BmiThresholds`/`AgeBandPolicy` 상수 모듈; 분류는 `BmiClassifier` 전략 | **2** |
| `ages`/`weights`/`heights`/`bmis` 평행 리스트 + 인덱스 루프 | Primitive Obsession, Duplicated Code | 레코드 불변식 깨짐, height 보정 추가 시 복잡도 급증 | `@dataclass HealthRecord`; `groupby_age_band(records)` | **3** |
| 나이대 필터 `for a in range(20,80,10)` 3중 반복 | Duplicated Code | 유지보수 시 누락·불일치 | 단일 `AGE_BANDS` iterable + 헬퍼 `in_band(age, band)` | **3** |
| CSV `row[1]`, `row[2]`, `row[3]` 인덱스 파싱 | **OCP**, Fragile Code | 컬럼 순서 변경 시 침묵 버그 | `csv.DictReader`, 필드명 상수 | **2** |
| `if not row: break`로 빈 행 시 파싱 중단 | 로직 스멜 / 잠재 버그 | 데이터 일부만 로드 | `if not row: continue` 또는 strip 후 검증 | **2** |
| `height == 0` 보정 미구현 | 요구 불일치 (기능) | ZeroDivisionError, 잘못된 통계 | weight와 대칭 imputation 단계 추가 | **1** |
| `FileNotFoundError` 시 `print` 후 `0` 반환 | SRP(부수효과), 타입 힌트 한계 | CLI 외 재사용·테스트 어려움 | `logging` + Optional/Result 또는 예외 재발생 | **4** |
| `UNDERWEIGHT=100` 등과 `main`의 `100,200,300,400` 중복 | Duplicated Code, Magic Number | 상수 변경 시 한쪽만 수정 위험 | `BmiCategory` IntEnum; `get_bmi_ratio(age, BmiCategory.UNDERWEIGHT)` | **4** |
| `"shealth.dat"` 하드코딩 | 문자열 하드코딩 | 배포·테스트 경로 고정 | `argparse` / 환경변수 / `Path` 기본값 | **4** |
| 공개 mutable 상태 (`self.ages` 등) | 캡슐화 약화 | 외부에서 리스트 변조 가능 | property 또는 읽기 전용 복사본 반환 | **3** |
| `open(..., "r")` encoding 미지정 | Python 환경 이슈 | Windows CP949 등 깨짐 | `encoding="utf-8"` | **5** |
| 분류·입력원 교체 불가 | **OCP**, isinstance/Protocol 미활용 | 테스트 더블·다른 데이터 소스 주입 불가 | `Protocol` + `__subclasshook__` 기반 Reader/Classifier | **5** |
| `main()` 타입 힌트·docstring 없음 | 타입 힌트 부분 적용 | 정적 분석·IDE 지원 약화 | `def main() -> None:` 및 모듈 docstring | **5** |
| f-string 출력 포맷이 `main`에 직접 | SRP(경미) | 출력 형식 변경 시 진입점 수정 | `format_age_band_report(age, ratios) -> str` | **4** |

---

## 8. 파일별 참고 코드 위치

**`shealth.py` — 책임 혼재의 중심:**

```22:94:src/main/python/shealth.py
    def calculate_bmi(self, filename: str) -> int:
        """파일에서 데이터를 읽어 BMI를 계산한다."""
        # ... 상태 초기화, CSV I/O, weight 보정, BMI 계산, 비율 집계 ...
        return self.count
```

**`shealth_bmi.py` — 도메인 상수 미사용:**

```8:14:src/main/python/shealth_bmi.py
    for age in range(20, 80, 10):
        print(
            f"{age} - underweight = {shealth.get_bmi_ratio(age, 100):.6f}, "
            f"normal = {shealth.get_bmi_ratio(age, 200):.6f}, "
            ...
```

---

## 9. 결론

현 코드는 **단일 클래스·단일 메서드 중심의 절차적 스타일**로, 소규모 과제에는 빠르지만 SOLID·확장·테스트 관점에서 기술 부채가 `calculate_bmi`에 집중되어 있다. 우선순위 **1~3**은 동작 정확성(height 보정, 경계값)과 테스트 가능 구조를 동시에 확보하고, **4~5**는 CLI·확장성·정적 타입 품질을 다듬는 단계로 권장한다.

---

*본 문서는 정적 코드 리뷰 기준이며, 실행·pytest 커버리지 결과는 포함하지 않는다.*
