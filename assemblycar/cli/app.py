from dataclasses import dataclass
from typing import Optional

from assemblycar.cli.menu import delay, is_valid_range, show_menu
from assemblycar.cli.messages import (
    BRAKE_SELECT_TEXT,
    BRAKE_TEXT,
    CAR_TYPE_TEXT,
    ENGINE_SELECT_TEXT,
    ENGINE_TEXT,
    REASON_TEXT,
    STEERING_SELECT_TEXT,
    STEERING_TEXT,
)
from assemblycar.domain.assembly import run as domain_run
from assemblycar.domain.assembly import test as domain_test
from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering

CAR_TYPE_Q = 0
ENGINE_Q = 1
BRAKE_SYSTEM_Q = 2
STEERING_SYSTEM_Q = 3
RUN_TEST = 4


@dataclass
class _Selection:
    car_type: Optional[CarType] = None
    engine: Optional[Engine] = None
    brake: Optional[Brake] = None
    steering: Optional[Steering] = None

    def to_spec(self) -> CarSpec:
        return CarSpec(
            car_type=self.car_type,
            engine=self.engine,
            brake=self.brake,
            steering=self.steering,
        )


@dataclass(frozen=True)
class _StepConfig:
    field: str
    enum_cls: type
    text_map: dict
    message: str
    next_step: int


_STEP_CONFIGS = {
    CAR_TYPE_Q: _StepConfig(
        "car_type", CarType, CAR_TYPE_TEXT,
        "차량 타입으로 {name}을 선택하셨습니다.", ENGINE_Q,
    ),
    ENGINE_Q: _StepConfig(
        "engine", Engine, ENGINE_SELECT_TEXT,
        "{name} 엔진을 선택하셨습니다.", BRAKE_SYSTEM_Q,
    ),
    BRAKE_SYSTEM_Q: _StepConfig(
        "brake", Brake, BRAKE_SELECT_TEXT,
        "{name} 제동장치를 선택하셨습니다.", STEERING_SYSTEM_Q,
    ),
    STEERING_SYSTEM_Q: _StepConfig(
        "steering", Steering, STEERING_SELECT_TEXT,
        "{name} 조향장치를 선택하셨습니다.", RUN_TEST,
    ),
}


def _apply_selection(selection, step, ans):
    cfg = _STEP_CONFIGS[step]
    value = cfg.enum_cls(ans)
    setattr(selection, cfg.field, value)
    print(cfg.message.format(name=cfg.text_map[value]))
    return cfg.next_step


def _run_produced_car(spec):
    result = domain_run(spec)

    if not result.ok:
        if result.broken_engine:
            print("엔진이 고장나있습니다.")
            print("자동차가 움직이지 않습니다.")
        else:
            print("자동차가 동작되지 않습니다")
        return

    print(f"Car Type : {CAR_TYPE_TEXT[result.spec.car_type]}")
    print(f"Engine   : {ENGINE_TEXT[result.spec.engine]}")
    print(f"Brake    : {BRAKE_TEXT[result.spec.brake]}")
    print(f"Steering : {STEERING_TEXT[result.spec.steering]}")
    print("자동차가 동작됩니다.")


def _test_produced_car(spec):
    result = domain_test(spec)
    if result.passed:
        print("PASS")
        return
    print(f"FAIL\n{REASON_TEXT[result.reasons[0]]}")


def main():
    step = CAR_TYPE_Q
    selection = _Selection()

    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            if step == RUN_TEST:
                step = CAR_TYPE_Q
            elif step > CAR_TYPE_Q:
                step = step - 1
            continue

        if step in _STEP_CONFIGS:
            step = _apply_selection(selection, step, ans)
            delay(800)
        elif step == RUN_TEST:
            if ans == 1:
                _run_produced_car(selection.to_spec())
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                _test_produced_car(selection.to_spec())
                delay(2000)


if __name__ == "__main__":
    main()
