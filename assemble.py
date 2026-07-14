import time
import sys

from assemblycar.domain.assembly import run as domain_run
from assemblycar.domain.assembly import test as domain_test
from assemblycar.domain.rules import Reason
from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering

CLEAR_SCREEN = "\033[H\033[2J"

CarType_Q = 0
Engine_Q = 1
brakeSystem_Q = 2
SteeringSystem_Q = 3
Run_Test = 4

SEDAN = 1
SUV = 2
TRUCK = 3

GM = 1
TOYOTA = 2
WIA = 3

MANDO = 1
CONTINENTAL = 2
BOSCH_B = 3

BOSCH_S = 1
MOBIS = 2

q0 = 0
q1 = 0
q2 = 0
q3 = 0
q4 = 0

def delay(ms):
    t = ms / 1000.0
    time.sleep(t)

def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()

def show_menu(step):
    clear()
    if step == 0:
        print("        ______________")
        print("       /|            |")
        print("  ____/_|_____________|____")
        print(" |                      O  |")
        print(" '-(@)----------------(@)--'")
        print("===============================")
        print("어떤 차량 타입을 선택할까요?")
        print("1. Sedan")
        print("2. SUV")
        print("3. Truck")
    elif step == 1:
        print("어떤 엔진을 탑재할까요?")
        print("0. 뒤로가기")
        print("1. GM")
        print("2. TOYOTA")
        print("3. WIA")
        print("4. 고장난 엔진")
    elif step == 2:
        print("어떤 제동장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. MANDO")
        print("2. CONTINENTAL")
        print("3. BOSCH")
    elif step == 3:
        print("어떤 조향장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. BOSCH")
        print("2. MOBIS")
    elif step == 4:
        print("멋진 차량이 완성되었습니다.")
        print("0. 처음 화면으로 돌아가기")
        print("1. RUN")
        print("2. Test")
    print("===============================")

def is_valid_range(step, ans):
    if step == 0:
        if ans < 1 or ans > 3:
            print("ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능")
            return False
    if step == 1:
        if ans < 0 or ans > 4:
            print("ERROR :: 엔진은 1 ~ 4 범위만 선택 가능")
            return False
    if step == 2:
        if ans < 0 or ans > 3:
            print("ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능")
            return False
    if step == 3:
        if ans < 0 or ans > 2:
            print("ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능")
            return False
    if step == 4:
        if ans < 0 or ans > 2:
            print("ERROR :: Run 또는 Test 중 하나를 선택 필요")
            return False
    return True

def select_car_type(a):
    global q0
    q0 = a
    if a == 1:
        print("차량 타입으로 Sedan을 선택하셨습니다.")
    elif a == 2:
        print("차량 타입으로 SUV을 선택하셨습니다.")
    elif a == 3:
        print("차량 타입으로 Truck을 선택하셨습니다.")

def select_engine(a):
    global q1
    q1 = a
    if a == 1:
        print("GM 엔진을 선택하셨습니다.")
    elif a == 2:
        print("TOYOTA 엔진을 선택하셨습니다.")
    elif a == 3:
        print("WIA 엔진을 선택하셨습니다.")
    elif a == 4:
        print("고장난 엔진을 선택하셨습니다.")

def select_brake(a):
    global q2
    q2 = a
    if a == 1:
        print("MANDO 제동장치를 선택하셨습니다.")
    elif a == 2:
        print("CONTINENTAL 제동장치를 선택하셨습니다.")
    elif a == 3:
        print("BOSCH 제동장치를 선택하셨습니다.")

def select_steering(a):
    global q3
    q3 = a
    if a == 1:
        print("BOSCH 조향장치를 선택하셨습니다.")
    elif a == 2:
        print("MOBIS 조향장치를 선택하셨습니다.")

CAR_TYPE_TEXT = {CarType.SEDAN: "Sedan", CarType.SUV: "SUV", CarType.TRUCK: "Truck"}
ENGINE_TEXT = {Engine.GM: "GM", Engine.TOYOTA: "TOYOTA", Engine.WIA: "WIA"}
BRAKE_TEXT = {Brake.MANDO: "Mando", Brake.CONTINENTAL: "Continental", Brake.BOSCH: "Bosch"}
STEERING_TEXT = {Steering.BOSCH: "Bosch", Steering.MOBIS: "Mobis"}

REASON_TEXT = {
    Reason.SEDAN_CONTINENTAL: "Sedan에는 Continental제동장치 사용 불가",
    Reason.SUV_TOYOTA: "SUV에는 TOYOTA엔진 사용 불가",
    Reason.TRUCK_WIA: "Truck에는 WIA엔진 사용 불가",
    Reason.TRUCK_MANDO: "Truck에는 Mando제동장치 사용 불가",
    Reason.BOSCH_BRAKE_NON_BOSCH_STEERING: "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
}

def _current_spec():
    return CarSpec(
        car_type=CarType(q0),
        engine=Engine(q1),
        brake=Brake(q2),
        steering=Steering(q3),
    )

def is_valid_check():
    return domain_test(_current_spec()).passed

def run_produced_car():
    result = domain_run(_current_spec())

    if not result.ok:
        if result.broken_engine:
            print("엔진이 고장나있습니다.")
            print("자동차가 움직이지 않습니다.")
        else:
            print("자동차가 동작되지 않습니다")
        return

    spec = result.spec
    print(f"Car Type : {CAR_TYPE_TEXT[spec.car_type]}")
    print(f"Engine   : {ENGINE_TEXT[spec.engine]}")
    print(f"Brake    : {BRAKE_TEXT[spec.brake]}")
    print(f"Steering : {STEERING_TEXT[spec.steering]}")
    print("자동차가 동작됩니다.")

def test_produced_car():
    result = domain_test(_current_spec())
    if result.passed:
        print("PASS")
        return
    print(f"FAIL\n{REASON_TEXT[result.reasons[0]]}")

def main():
    step = 0
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
            if step == 4:
                step = 0
            elif step > 0:
                step = step - 1
            continue

        if step == 0:
            select_car_type(ans)
            delay(800)
            step = 1
        elif step == 1:
            select_engine(ans)
            delay(800)
            step = 2
        elif step == 2:
            select_brake(ans)
            delay(800)
            step = 3
        elif step == 3:
            select_steering(ans)
            delay(800)
            step = 4
        elif step == 4:
            if ans == 1:
                run_produced_car()
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                test_produced_car()
                delay(2000)

if __name__ == "__main__":
    main()
