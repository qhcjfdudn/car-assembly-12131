# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 개요

assemblyCar(차량 조립 프로젝트)는 사용자가 차량을 조립하는 과정(차종 → 엔진 → 제동 장치 → 조향 장치)을 안내한 뒤, 조합의 유효성을 검증하고 RUN 또는 Test를 실행할 수 있게 해주는 작은 콘솔 애플리케이션입니다.

- `assemblycar/domain/` — 도메인 로직(부품 Enum, `CarSpec` dataclass, 호환성 규칙, RUN/Test 판정). `print`/`input`/`time.sleep`을 포함하지 않는 순수 로직입니다.
- `assemblycar/cli/` — 콘솔 프레젠테이션(한국어 메시지, 메뉴 출력, 입력 검증, 위저드 루프). `domain`에만 의존하며 그 반대 방향 의존은 없습니다.
- `assemble.py` — 진입점 shim. `assemblycar.cli.app.main()`을 호출만 합니다(`python assemble.py`로 실행).

과거에는 Java(단일 파일 및 상태 머신/I/O 분리 리팩터링 버전 `v2/`)와 C++(GoogleMock 테스트 포함) 구현도 존재했으나 단일 Python 구현으로 통합되며 제거되었고, 이후 전역 상태 기반 단일 스크립트였던 Python 구현도 [docs/PLAN.md](docs/PLAN.md)에 정리된 순서에 따라 `domain`/`cli` 패키지로 리팩터링되었습니다.

## 핵심 도메인 로직

조립은 5단계로 진행됩니다: 차종 → 엔진 → 제동 장치 → 조향 장치 → Run/Test(`assemblycar/cli/app.py`의 `CAR_TYPE_Q`~`RUN_TEST` 상수).

각 단계별 선택지(Enum, `assemblycar/domain/types.py`):
- 차종(`CarType`): `SEDAN=1, SUV=2, TRUCK=3`
- 엔진(`Engine`): `GM=1, TOYOTA=2, WIA=3`, 그리고 `BROKEN=4` = 의도적으로 고장난 엔진
- 제동 장치(`Brake`): `MANDO=1, CONTINENTAL=2, BOSCH=3`
- 조향 장치(`Steering`): `BOSCH=1, MOBIS=2`

각 단계에서 `0`을 입력하면 한 단계 뒤로 돌아갑니다(마지막 Run/Test 화면에서는 0단계로 돌아감). `exit` 입력 시 프로그램이 종료됩니다. 숫자가 아니거나 범위를 벗어난 입력은 한국어 오류 메시지를 표시하고 다시 입력받습니다(짧은 지연 후 재입력) — 검증 로직은 `assemblycar/cli/menu.py`의 `is_valid_range`.

호환되지 않는 조합 규칙은 `assemblycar/domain/rules.py`의 `incompatibilities(spec)` 한 곳에만 존재합니다(유일한 출처):
- 세단 + 컨티넨탈 제동 장치 → 무효
- SUV + 도요타 엔진 → 무효
- 트럭 + WIA 엔진 → 무효
- 트럭 + 만도 제동 장치 → 무효
- 보쉬 제동 장치(`Brake.BOSCH`) + 보쉬가 아닌 조향 장치(`Steering.BOSCH`가 아닌 모든 것) → 무효

`assemblycar/domain/assembly.py`의 `run(spec)`(RUN)은 조합이 무효인 경우 추가로 실패하며("자동차가 동작되지 않습니다"), 엔진이 고장난 경우(`Engine.BROKEN`) 다른 조합이 유효하더라도 실패를 보고합니다("엔진이 고장나있습니다"). `test(spec)`(Test)는 대신 PASS/FAIL과 함께 FAIL의 구체적인 사유(`Reason` enum)를 반환하며, 동일한 `incompatibilities()`를 재사용합니다(고장난 엔진 케이스는 검사하지 않음). 도메인 계층은 한국어 문자열을 직접 반환하지 않고 `Reason` 등 구조화된 값만 반환하며, 한국어 문구 매핑은 `assemblycar/cli/messages.py`가 전담합니다.

## 실행 방법

의존성은 `pyproject.toml`에 선언되어 있습니다(`pip install -e .[dev]`로 pytest 설치).

- Python: `python assemble.py`
- 단위 테스트(`tests/`, pytest): `pytest -v`

## 편집 시 참고사항

- 사용자에게 표시되는 문자열은 한국어입니다. 새 메시지를 추가할 때 기존 문구/어조와 일관성을 유지하세요.
- 한국어 출력 문구는 `assemblycar/cli/messages.py`에 모여 있습니다(부품별 표기, RUN 실패/FAIL 사유 매핑). 새 문구를 추가할 때 도메인 계층(`assemblycar/domain/`)에 문자열을 직접 넣지 말고 이 파일에 추가하세요.
- 도메인 계층(`assemblycar/domain/`)은 `print`/`input`/`time.sleep`을 포함하지 않습니다. 의존 방향은 `cli` → `domain` 단방향을 유지하세요.

## 리팩터링 작업 순서

`assemble.py`를 패키지 구조 + pytest 기반으로 리팩터링하는 단계별 작업 순서는 [docs/PLAN.md](docs/PLAN.md)에 정리되어 있으며, 9단계 모두 완료되었습니다. 향후 유사한 구조 변경 작업 시 참고용으로 남겨둡니다.
