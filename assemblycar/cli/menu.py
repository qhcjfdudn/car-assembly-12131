import sys
import time

CLEAR_SCREEN = "\033[H\033[2J"

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
