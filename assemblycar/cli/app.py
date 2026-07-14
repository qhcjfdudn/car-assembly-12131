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


def _select_car_type(selection, ans):
    selection.car_type = CarType(ans)
    print(f"차량 타입으로 {CAR_TYPE_TEXT[selection.car_type]}을 선택하셨습니다.")


def _select_engine(selection, ans):
    selection.engine = Engine(ans)
    print(f"{ENGINE_SELECT_TEXT[selection.engine]} 엔진을 선택하셨습니다.")


def _select_brake(selection, ans):
    selection.brake = Brake(ans)
    print(f"{BRAKE_SELECT_TEXT[selection.brake]} 제동장치를 선택하셨습니다.")


def _select_steering(selection, ans):
    selection.steering = Steering(ans)
    print(f"{STEERING_SELECT_TEXT[selection.steering]} 조향장치를 선택하셨습니다.")


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

        if step == CAR_TYPE_Q:
            _select_car_type(selection, ans)
            delay(800)
            step = ENGINE_Q
        elif step == ENGINE_Q:
            _select_engine(selection, ans)
            delay(800)
            step = BRAKE_SYSTEM_Q
        elif step == BRAKE_SYSTEM_Q:
            _select_brake(selection, ans)
            delay(800)
            step = STEERING_SYSTEM_Q
        elif step == STEERING_SYSTEM_Q:
            _select_steering(selection, ans)
            delay(800)
            step = RUN_TEST
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
