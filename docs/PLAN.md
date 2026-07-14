# assemble.py 리팩터링 작업 순서

`assemble.py`는 현재 모듈 전역 상태(`q0`~`q4`)와 도메인 로직(호환성 규칙, RUN/Test 판정)·CLI 프레젠테이션(메뉴 출력, 한국어 메시지, `input`/`sleep`)이 한 파일에 뒤섞여 있습니다. 아래 순서로 단계별로(각 단계 완료 후 앱 실행 가능 + 테스트 통과 유지) 패키지 구조 + pytest 기반으로 리팩터링합니다. 한 번에 전부 바꾸지 말고 커밋 단위로 하나씩 진행하세요.

## 목표 구조

```
assemblycar/
    domain/
        types.py     # Enum: CarType, Engine, Brake, Steering (Engine.BROKEN=4 포함)
        spec.py      # CarSpec dataclass (car_type, engine, brake, steering)
        rules.py     # Reason enum + incompatibilities(spec) — 5개 호환성 규칙의 유일한 출처
        assembly.py  # RunResult/TestResult + run(spec)/test(spec)
    cli/
        messages.py  # 한국어 문자열, Reason -> 한국어 문구 매핑(REASON_TEXT)
        menu.py      # show_menu, is_valid_range, delay, clear
        app.py       # main() 위저드 루프 (전역 대신 지역 CarSpec 빌더 사용)
tests/
    test_types.py / test_spec.py / test_rules.py / test_assembly.py / test_menu.py
assemble.py          # 최종적으로 얇은 진입점(shim)만 남김: assemblycar.cli.app.main() 호출
pyproject.toml       # pytest를 dev 의존성으로 선언
```

`assemble.py`는 `python assemble.py` 실행 경로를 계속 지원하기 위해 끝까지 삭제하지 않고 마지막 단계에서 얇은 shim으로만 축소합니다.

## 도메인 API 설계 원칙

- 5개 호환성 규칙은 `rules.incompatibilities(spec)` 한 곳에만 존재합니다. `assembly.run()`은 여기에 "엔진 고장" 특수 케이스를 추가로 검사하고, `assembly.test()`는 엔진 고장을 검사하지 않은 채 동일 규칙을 재사용합니다 — 규칙을 두 곳에 중복 구현하지 마세요.
- 도메인 계층은 한국어 문자열을 직접 반환하지 않고 `Reason` enum 등 구조화된 값만 반환합니다. 한국어 문구 매핑은 `cli/messages.py`가 전담(`REASON_TEXT: dict[Reason, str]`)하며, 기존 문구와 완전히 동일하게 유지합니다.
- 의존 방향은 `cli` → `domain` 단방향입니다. `domain`은 `print`/`input`/`time.sleep`을 포함하지 않습니다.

## 단계별 진행 순서

1. `pyproject.toml`(또는 `requirements-dev.txt`) 추가 — pytest를 dev 의존성으로 선언. 코드 변경 없음.
2. `tests/` 디렉터리와 pytest 설정 추가. 기존 `test_assemble.py`의 32개 케이스를 pytest 스타일로 `tests/test_assemble_legacy.py`에 그대로 이식(여전히 기존 전역 상태 기반 `assemble.py` 대상). 동등성 확인 후 루트의 `test_assemble.py` 삭제.
3. `assemblycar/domain/types.py`, `spec.py` 추가(Enum, `CarSpec`). 기존 `assemble.py`는 아직 이 모듈을 사용하지 않아도 됨(순수 추가). `tests/test_types.py`, `tests/test_spec.py` 추가.
4. `assemblycar/domain/rules.py` 추가(`Reason`, `incompatibilities`). `tests/test_rules.py`에 기존 `ValidationRuleTests`를 이식(CarSpec 기반, `assemble.py`와 독립적).
5. `assemblycar/domain/assembly.py` 추가(`run`/`test`, `RunResult`/`TestResult`). `tests/test_assembly.py`에 기존 `RunProducedCarTests`/`TestProducedCarTests`를 이식 — 문자열 대신 `Reason`/`broken_engine`/`passed` 필드로 단언.
6. `assemble.py`의 `is_valid_check`/`run_produced_car`/`test_produced_car`를 도메인 계층 호출로 교체(내부적으로 `CarSpec` 구성 후 위임, 출력 문자열은 그대로 유지). `tests/test_assemble_legacy.py`가 변경 없이 계속 통과해야 함(출력 불변 검증용 안전망).
7. `assemblycar/cli/messages.py`, `menu.py` 추출(한국어 문자열, `show_menu`, `is_valid_range`, `delay`, `clear`). `assemble.py`는 이를 import. `InputRangeValidationTests`를 `tests/test_menu.py`로 이식.
8. `assemblycar/cli/app.py` 추출(`main()`과 위저드 상태 전이, 전역 `q0~q4` 대신 지역 빌더 사용). `assemble.py`는 `from assemblycar.cli.app import main`만 남기는 shim이 됨. 내비게이션(0=뒤로가기, exit, Run/Test 화면에서 0은 0단계로) 동작이 그대로인지 수동 확인.
9. 정리: 모든 케이스가 새 계층별 테스트로 이관됐는지 원본 32개 케이스와 교차 확인 후 `tests/test_assemble_legacy.py` 삭제. CLAUDE.md의 실행/테스트 안내를 새 구조에 맞게 갱신(`pip install -e .`, `pytest` 등).

## 테스트 이식 시점

각 추출 단계(2, 4, 5, 7)에서 해당 도메인/CLI 모듈과 같은 커밋으로 테스트를 함께 이식합니다(전부 끝난 뒤 한 번에 이식하지 않음) — 테스트가 항상 초록 상태를 유지하고 각 단계가 독립적으로 되돌릴 수 있도록 하기 위함입니다. 레거시 테스트 삭제(9단계)만 별도로 마지막에 수행합니다.

## 유의사항

- `tests/test_assemble_legacy.py`는 6단계까지 출력 불변성 검증용 안전망으로 유지 후 제거합니다.
- 오늘 매직 넘버인 엔진 고장값 `4`는 3단계에서 `Engine.BROKEN`으로 명명합니다.
- 제동장치의 `BOSCH_B`와 조향장치의 `BOSCH_S`는 이름이 겹치므로 각자의 Enum 클래스 안에 네임스페이스로 분리합니다(`Brake.BOSCH` vs `Steering.BOSCH`).
- 8단계 이후 위저드 내비게이션 동작을 이 문서에 기록된 규칙과 대조해 수동 검증합니다.

> 위 9단계는 모두 완료되었습니다(`assemblycar/domain/`, `assemblycar/cli/`, `tests/` 구조로 이관 완료). 아래는 그 이후 진행한 중복 코드 정리 작업의 계획입니다.

---

# cli/ 하위 중복 코드 정리 계획

9단계 리팩터링이 끝난 뒤 `assemblycar/domain/`과 `assemblycar/cli/`를 다시 점검했습니다. `domain/`(`types.py`, `spec.py`, `rules.py`, `assembly.py`)은 호환성 규칙이 `incompatibilities()` 한 곳에만 있어 손댈 부분이 없었고, `cli/` 쪽에서 아래 3곳에 구조적으로 같은 패턴이 반복되고 있었습니다.

## 발견한 중복 지점

1. **`cli/app.py`** — `_select_car_type/_select_engine/_select_brake/_select_steering` 4개 함수와 `main()`의 4갈래 if/elif. 네 함수 모두 "enum으로 변환 → `selection`의 한 필드에 저장 → 텍스트 맵으로 문구 출력" 구조가 동일하고, `main()`의 단계 전이도 "select 함수 호출 → `delay(800)` → 다음 단계로 전진"을 4번 반복합니다. 단계별로 다른 값은 (필드명, Enum 클래스, 텍스트 맵, 출력 문구 템플릿, 다음 단계)뿐입니다.
2. **`cli/menu.py`** — `is_valid_range`의 5개 if 블록. `step`별로 "범위를 벗어나면 에러 문구를 찍고 False"라는 패턴이 반복됩니다.
3. **`cli/messages.py`** — `*_SELECT_TEXT` 맵들이 `*_TEXT` 맵에서 파생 가능한 값을 리터럴로 다시 나열하고 있습니다(`BRAKE_SELECT_TEXT`/`STEERING_SELECT_TEXT`는 대응 맵의 대문자화, `ENGINE_SELECT_TEXT`는 `ENGINE_TEXT` + `Engine.BROKEN` 한 항목).

## 변경 계획 (동작 100% 보존, 순수 리팩터링)

**`assemblycar/cli/messages.py`**
```python
ENGINE_SELECT_TEXT = {**ENGINE_TEXT, Engine.BROKEN: "고장난"}
BRAKE_SELECT_TEXT = {k: v.upper() for k, v in BRAKE_TEXT.items()}
STEERING_SELECT_TEXT = {k: v.upper() for k, v in STEERING_TEXT.items()}
```

**`assemblycar/cli/menu.py`** — `is_valid_range`를 테이블 기반으로 교체:
```python
_STEP_RANGES = {
    0: (1, 3, "ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능"),
    1: (0, 4, "ERROR :: 엔진은 1 ~ 4 범위만 선택 가능"),
    2: (0, 3, "ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능"),
    3: (0, 2, "ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능"),
    4: (0, 2, "ERROR :: Run 또는 Test 중 하나를 선택 필요"),
}

def is_valid_range(step, ans):
    low, high, error_message = _STEP_RANGES[step]
    if ans < low or ans > high:
        print(error_message)
        return False
    return True
```

**`assemblycar/cli/app.py`** — 4개 `_select_*` 함수와 `main()`의 4갈래 if/elif를 단계 설정 테이블 + 공용 헬퍼로 교체:
```python
@dataclass(frozen=True)
class _StepConfig:
    field: str
    enum_cls: type
    text_map: dict
    message: str   # "{name}" 플레이스홀더 포함
    next_step: int

_STEP_CONFIGS = {
    CAR_TYPE_Q: _StepConfig("car_type", CarType, CAR_TYPE_TEXT,
                            "차량 타입으로 {name}을 선택하셨습니다.", ENGINE_Q),
    ENGINE_Q: _StepConfig("engine", Engine, ENGINE_SELECT_TEXT,
                           "{name} 엔진을 선택하셨습니다.", BRAKE_SYSTEM_Q),
    BRAKE_SYSTEM_Q: _StepConfig("brake", Brake, BRAKE_SELECT_TEXT,
                                 "{name} 제동장치를 선택하셨습니다.", STEERING_SYSTEM_Q),
    STEERING_SYSTEM_Q: _StepConfig("steering", Steering, STEERING_SELECT_TEXT,
                                    "{name} 조향장치를 선택하셨습니다.", RUN_TEST),
}

def _apply_selection(selection, step, ans):
    cfg = _STEP_CONFIGS[step]
    value = cfg.enum_cls(ans)
    setattr(selection, cfg.field, value)
    print(cfg.message.format(name=cfg.text_map[value]))
    return cfg.next_step
```
`main()`의 4갈래 분기는 `elif step in _STEP_CONFIGS: step = _apply_selection(selection, step, ans); delay(800)` 한 갈래로 줄어듭니다. `RUN_TEST` 분기(RUN/Test 실행)는 로직이 판이하므로 그대로 유지합니다.

## SOLID 검토

- **SRP**: `_apply_selection`은 "이 단계에 대응하는 필드를 채우고 안내 문구를 출력한다"는 하나의 책임만 가지며, 기존 4개 함수가 각각 하던 일(변환→저장→출력)을 그대로 수행합니다. `_StepConfig`는 로직 없는 값 객체라 책임이 섞이지 않습니다. `is_valid_range`도 "범위 검사 + 에러 출력"이라는 원래 책임 그대로이며 표는 데이터 표현 방식만 바뀐 것입니다.
- **OCP**: 기존 if/elif 체인은 단계가 늘어나면 `main()`/`is_valid_range` 본문을 직접 수정해야 했습니다. 테이블 기반으로 바꾸면 새 단계 추가 시 설정 테이블에 항목만 추가하면 되므로 오히려 OCP를 더 잘 지키는 방향입니다.
- **LSP / ISP**: 상속이나 인터페이스가 관여하지 않는 변경(Enum·dataclass·dict 조작)이라 해당 사항 없음.
- **DIP**: `cli/app.py`는 여전히 `domain`의 `CarType`/`Engine`/`Brake`/`Steering`, `run`/`test`에만 의존하며 반대 방향 의존은 생기지 않습니다. 구체 Enum을 설정 테이블에 담는 결합도는 기존 `_select_*` 함수들과 동일한 수준입니다.

## 검증

- 세 파일 수정 후 `pytest -q` 실행 — 기존 46개 테스트가 (테스트 코드 변경 없이) 그대로 통과해야 합니다.
- `python assemble.py`를 스크립트 stdin으로 수동 구동해 RUN/Test 흐름과 뒤로가기 내비게이션 출력이 이전과 동일한지 확인합니다.
