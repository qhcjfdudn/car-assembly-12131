# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 개요

assemblyCar(차량 조립 프로젝트)는 사용자가 차량을 조립하는 과정(차종 → 엔진 → 제동 장치 → 조향 장치)을 안내한 뒤, 조합의 유효성을 검증하고 RUN 또는 Test를 실행할 수 있게 해주는 작은 콘솔 애플리케이션입니다.

- `assemble.py` — 단일 파일, 모듈 레벨 전역 상태(`q0`~`q4`)를 사용하는 Python 구현. 유일하게 유지되는 구현체입니다.

과거에는 Java(단일 파일 및 상태 머신/I/O 분리 리팩터링 버전 `v2/`)와 C++(GoogleMock 테스트 포함) 구현도 존재했으나, 단일 Python 구현으로 통합되며 제거되었습니다.

## 핵심 도메인 로직

조립은 5단계(0부터 시작하는 인덱스)로 진행됩니다: `CarType_Q`, `Engine_Q`, `brakeSystem_Q`, `SteeringSystem_Q`, `Run_Test`.

각 단계별 선택지:
- 차종: `SEDAN=1, SUV=2, TRUCK=3`
- 엔진: `GM=1, TOYOTA=2, WIA=3`, 그리고 `4` = 의도적으로 고장난 엔진
- 제동 장치: `MANDO=1, CONTINENTAL=2, BOSCH_B=3`
- 조향 장치: `BOSCH_S=1, MOBIS=2`

각 단계에서 `0`을 입력하면 한 단계 뒤로 돌아갑니다(마지막 Run/Test 화면에서는 0단계로 돌아감). `exit` 입력 시 프로그램이 종료됩니다. 숫자가 아니거나 범위를 벗어난 입력은 한국어 오류 메시지를 표시하고 다시 입력받습니다(짧은 지연 후 재입력).

호환되지 않는 조합 규칙(`is_valid_check` / `test_produced_car`):
- 세단 + 컨티넨탈 제동 장치 → 무효
- SUV + 도요타 엔진 → 무효
- 트럭 + WIA 엔진 → 무효
- 트럭 + 만도 제동 장치 → 무효
- 보쉬 제동 장치(`BOSCH_B`) + 보쉬가 아닌 조향 장치(`BOSCH_S`가 아닌 모든 것) → 무효

`run_produced_car`(RUN)은 조합이 무효인 경우 추가로 실패하며("자동차가 동작되지 않습니다"), 엔진이 4번(고장난 엔진)인 경우 다른 조합이 유효하더라도 "엔진이 고장나있습니다"를 보고합니다. `test_produced_car`(Test)는 대신 PASS/FAIL과 함께 FAIL의 구체적인 한국어 사유를 출력하며, 동일한 규칙을 직접 검사합니다(고장난 엔진 케이스는 검사하지 않음).

## 실행 방법

의존성은 `pyproject.toml`에 선언되어 있습니다(`pip install -e .[dev]`로 pytest 설치).

- Python: `python assemble.py`
- 단위 테스트(`tests/`, pytest): `pytest -v`

## 편집 시 참고사항

- 사용자에게 표시되는 문자열은 한국어입니다. 새 메시지를 추가할 때 기존 문구/어조와 일관성을 유지하세요.

## 리팩터링 작업 순서

`assemble.py`를 패키지 구조 + pytest 기반으로 리팩터링하는 단계별 작업 순서는 [docs/PLAN.md](docs/PLAN.md)에 정리되어 있습니다. 리팩터링 작업을 진행하기 전에 반드시 이 문서를 먼저 확인하세요.
