# Golden Master 회귀 테스트 설계

> **TC:** #44 · **구현:** `texttest_fixture.py`, `test_golden_master.py`  
> **작성일:** 2026-05-20

---

## 1. 비교 대상

| 항목 | 값 |
|------|-----|
| 진입점 | `shealth_bmi.main()` |
| 입력 | 프로젝트 루트 `shealth.dat` |
| 출력 | stdout 6줄 (20~70대, 소수 6자리) |
| 제외 | stderr 로그(INFO 등) |

---

## 2. 파일 경로

| 용도 | 경로 |
|------|------|
| Golden 기준 | `src/test/golden/shealth_dat_stdout.txt` |
| 캡처 헬퍼 | `src/test/python/texttest_fixture.py` |
| TC | `src/test/python/test_golden_master.py` |

---

## 3. 캡처 방식

| 방식 | 함수 | 용도 |
|------|------|------|
| in-process (기본) | `capture_cli_stdout_inprocess` | 빠른 CI·로컬, `monkeypatch`와 동일 패턴 |
| subprocess | `capture_cli_stdout_subprocess` | 실 CLI 경로 검증 (`test_golden_master_subprocess_matches_inprocess`) |

정규화: CRLF→LF, 각 줄 rstrip, 말미 빈 줄 제거 후 마지막에 단일 `\n`.

---

## 4. Approve 워크플로

1. **일반 실행:** golden과 strict equal 비교.
2. **파일 없음:** 1회 생성 후 `pytest.fail` → 커밋 필요.
3. **갱신:** `UPDATE_GOLDEN=1` 환경 변수 설정 후 golden 마커만 실행.

```bash
# Windows
set UPDATE_GOLDEN=1
python -m pytest src/test/python -m golden_master -v

# Linux/macOS
UPDATE_GOLDEN=1 python -m pytest src/test/python -m golden_master -v
```

CI에서는 `UPDATE_GOLDEN` 미설정 — golden 파일이 repo에 있어야 Green.

---

## 5. pytest 실행 프로필

| 명령 | 설명 |
|------|------|
| `python -m pytest` | `pytest.ini` — golden **제외** (기본 45+2 unit) |
| `python -m pytest -m golden_master` | Golden만 |
| `python -m pytest -m ""` | 전체 (unit + golden) |

---

## 6. 의도적 golden 변경

- DEF-001(BMI 25.0) 등 통계 변경 시 `UPDATE_GOLDEN=1`로 재생성 후 PR에 golden diff 포함.
- 리뷰어는 6줄 수치 변동이 **의도된 요구 변경**인지 확인.

---

*마지막 업데이트: 2026-05-20*
