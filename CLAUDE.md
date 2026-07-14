# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 개요

assemblyCar(차량 조립 프로젝트)는 사용자가 차량을 조립하는 과정(차종 → 엔진 → 제동 장치 → 조향 장치)을 안내한 뒤, 조합의 유효성을 검증하고 RUN 또는 Test를 실행할 수 있게 해주는 작은 콘솔 애플리케이션입니다. 동일한 프로그램이 네 가지 언어/스타일로 각각 독립적으로 네 번 구현되어 있습니다:

- `python/assemble.py` — 단일 파일, 모듈 레벨 전역 상태(`q0`~`q4`)를 사용.
- `java/assemble.java` — `stack` 배열을 사용하는 단일 파일 `Assemble` 클래스, 모든 로직이 static.
- `cpp/assemble.cpp` — 전역 `stack` 배열을 사용하는 단일 파일 C 코드. `#ifdef _DEBUG`로 보호되는 GoogleMock(`gmock`) 테스트 진입점도 포함.
- `v2/` — 상태 머신과 I/O를 분리하도록 리팩터링된 Java 버전:
  - `Assemble.java` — 모든 메뉴/검증/비즈니스 로직을 담은 추상 베이스 클래스. `print`/`println`/`readLine`/`clear`/`delay`는 추상 훅으로 남겨둠.
  - `AssembleConsole.java` — 추상 훅을 실제 콘솔 I/O(`Scanner`, `System.out`, `Thread.sleep`)에 연결하는 구체 서브클래스.
  - `AssembleTestable.java` — 스크립트로 작성된 입력 라인을 공급하고 출력을 `StringBuilder`에 캡처하는 구체 서브클래스로, 실제 터미널 없이 단위 테스트를 가능하게 함.
  - `Main.java` — 진입점. `AssembleConsole`을 실행만 함.
  - `UnitTest.java` — 미리 준비된 입력 시퀀스로 `AssembleTestable`을 구동하고 캡처된 출력 텍스트를 검증하는 JUnit 5 테스트.

이 구현들은 **공유 코드가 아닙니다** — 각각 자신의 디렉터리 안에서 독립적으로 존재합니다. 버그를 고치거나 동작을 변경할 때는, 동일한 로직이 다른 언어 버전에도 존재하는지, 사용자가 모든 곳에서 변경되길 원하는지 아니면 한 곳에서만 변경되길 원하는지 확인하세요.

## 핵심 도메인 로직 (모든 버전에서 동일)

조립은 5단계(0부터 시작하는 인덱스)로 진행됩니다: `CarType_Q`, `Engine_Q`, `BrakeSystem_Q`/`brakeSystem_Q`, `SteeringSystem_Q`, `Run_Test`.

각 단계별 선택지:
- 차종: `SEDAN=1, SUV=2, TRUCK=3`
- 엔진: `GM=1, TOYOTA=2, WIA=3`, 그리고 `4` = 의도적으로 고장난 엔진
- 제동 장치: `MANDO=1, CONTINENTAL=2, BOSCH_B=3`
- 조향 장치: `BOSCH_S=1, MOBIS=2`

각 단계에서 `0`을 입력하면 한 단계 뒤로 돌아갑니다(마지막 Run/Test 화면에서는 0단계로 돌아감). `exit` 입력 시 프로그램이 종료됩니다. 숫자가 아니거나 범위를 벗어난 입력은 한국어 오류 메시지를 표시하고 다시 입력받습니다(실제 콘솔 버전에서는 짧은 지연이 있음).

호환되지 않는 조합 규칙(`isValidCheck` / `testProducedCar`)은 모든 버전에서 일치해야 합니다:
- 세단 + 컨티넨탈 제동 장치 → 무효
- SUV + 도요타 엔진 → 무효
- 트럭 + WIA 엔진 → 무효
- 트럭 + 만도 제동 장치 → 무효
- 보쉬 제동 장치(`BOSCH_B`) + 보쉬가 아닌 조향 장치(`BOSCH_S`가 아닌 모든 것) → 무효

`RUN`은 조합이 무효인 경우 추가로 실패하며("동작되지 않습니다"), 엔진이 4번(고장난 엔진)인 경우 다른 조합이 유효하더라도 "엔진이 고장나있습니다"를 보고합니다. `Test`는 대신 PASS/FAIL과 함께 FAIL의 구체적인 한국어 사유를 출력하며, 동일한 규칙을 직접 검사합니다(고장난 엔진 케이스는 검사하지 않음).

## 실행 / 빌드 방법

저장소에는 빌드 시스템, CI, 의존성 매니페스트가 존재하지 않습니다(`pom.xml`/`package.json`/`CMakeLists.txt`/`requirements.txt` 없음). 각 버전은 수동으로 컴파일/실행합니다:

- Python: `python python/assemble.py`
- Java (단일 파일): `javac java/assemble.java && java -cp java Assemble`
- Java (v2, 리팩터링 버전): `javac v2/*.java && java -cp v2 Main`
- C++: `cpp/assemble.cpp`를 일반적으로 컴파일하면 대화형 콘솔 앱이 생성됨. `_DEBUG`를 정의하고 컴파일하면 `main()`이 대화형 앱 대신 GoogleMock 테스트 러너로 전환됨(include/link 경로에 gmock/gtest가 필요).
- 단위 테스트 (`v2/UnitTest.java`): JUnit 5(Jupiter) — 의존성을 자동으로 연결하는 빌드 파일이 없으므로, JUnit Platform Console Standalone jar를 대상으로 컴파일하거나 JUnit 5를 지원하는 IDE를 사용해야 함.

## 편집 시 참고사항

- 사용자에게 표시되는 문자열은 한국어입니다. 새 메시지를 추가할 때 기존 문구/어조와 일관성을 유지하세요.
- C++ 파일은 줄바꿈 문자를 제거하기 위해 `strtok_s`(MSVC 전용)를 사용합니다 — 이 파일은 이식 가능한 C가 아니라 Windows/MSVC 대상입니다.
- `AssembleTestable.run(String)`은 `\R`(모든 줄바꿈 문자)을 기준으로 분리하여 여러 줄 문자열을 스크립트 입력 라인으로 변환합니다 — 새 테스트를 작성할 때는 수동으로 `String[]`을 구성하는 대신 이 형태를 사용하세요.
