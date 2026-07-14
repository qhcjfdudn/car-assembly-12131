"""
assemble.py의 핵심 도메인 로직에 대한 pytest 기반 테스트.

현재 assemble.py는 모듈 레벨 전역 상태(q0~q4)를 사용하므로, 각 테스트는
전역 상태를 직접 설정한 뒤 대상 함수를 호출하는 방식으로 작성한다.

이 파일은 도메인 계층 추출(PLAN.md 3~5단계) 및 assemble.py의 위임 전환
(6단계)이 완료될 때까지 출력 불변성을 검증하는 안전망 역할을 하며,
계층별 테스트로의 이관이 끝나면(9단계) 삭제된다.
"""
import assemble


def set_state(car=0, engine=0, brake=0, steering=0):
    assemble.q0 = car
    assemble.q1 = engine
    assemble.q2 = brake
    assemble.q3 = steering


# --- is_valid_check()가 검사하는 비호환 조합 규칙 ---

def test_sedan_with_continental_brake_is_invalid():
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
    assert not assemble.is_valid_check()


def test_suv_with_toyota_engine_is_invalid():
    set_state(car=assemble.SUV, engine=assemble.TOYOTA,
              brake=assemble.MANDO, steering=assemble.BOSCH_S)
    assert not assemble.is_valid_check()


def test_truck_with_wia_engine_is_invalid():
    set_state(car=assemble.TRUCK, engine=assemble.WIA,
              brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
    assert not assemble.is_valid_check()


def test_truck_with_mando_brake_is_invalid():
    set_state(car=assemble.TRUCK, engine=assemble.GM,
              brake=assemble.MANDO, steering=assemble.BOSCH_S)
    assert not assemble.is_valid_check()


def test_bosch_brake_requires_bosch_steering():
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.BOSCH_B, steering=assemble.MOBIS)
    assert not assemble.is_valid_check()


def test_bosch_brake_with_bosch_steering_is_valid():
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.BOSCH_B, steering=assemble.BOSCH_S)
    assert assemble.is_valid_check()


def test_all_compatible_combinations_are_valid():
    # 세단 + GM 엔진 + 만도 제동 장치 + 모비스 조향 장치는 어떤 규칙에도 걸리지 않는다.
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.MANDO, steering=assemble.MOBIS)
    assert assemble.is_valid_check()


# --- run_produced_car()의 RUN 동작 ---

def test_broken_engine_overrides_otherwise_valid_combo(capsys):
    set_state(car=assemble.SEDAN, engine=4,
              brake=assemble.MANDO, steering=assemble.MOBIS)
    assemble.run_produced_car()
    output = capsys.readouterr().out
    assert "엔진이 고장나있습니다." in output
    assert "자동차가 움직이지 않습니다." in output


def test_invalid_combo_reports_failure(capsys):
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
    assemble.run_produced_car()
    output = capsys.readouterr().out
    assert "자동차가 동작되지 않습니다" in output


def test_valid_combo_prints_spec_and_runs(capsys):
    set_state(car=assemble.SUV, engine=assemble.GM,
              brake=assemble.MANDO, steering=assemble.BOSCH_S)
    assemble.run_produced_car()
    output = capsys.readouterr().out
    assert "Car Type : SUV" in output
    assert "Engine   : GM" in output
    assert "Brake    : Mando" in output
    assert "Steering : Bosch" in output
    assert "자동차가 동작됩니다." in output


# --- test_produced_car()의 Test 동작 — PASS/FAIL 사유 ---

def test_pass_on_valid_combo(capsys):
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.MANDO, steering=assemble.MOBIS)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "PASS" in output


def test_fail_reason_sedan_continental(capsys):
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "FAIL" in output
    assert "Sedan에는 Continental제동장치 사용 불가" in output


def test_fail_reason_suv_toyota(capsys):
    set_state(car=assemble.SUV, engine=assemble.TOYOTA,
              brake=assemble.MANDO, steering=assemble.BOSCH_S)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "SUV에는 TOYOTA엔진 사용 불가" in output


def test_fail_reason_truck_wia(capsys):
    set_state(car=assemble.TRUCK, engine=assemble.WIA,
              brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "Truck에는 WIA엔진 사용 불가" in output


def test_fail_reason_truck_mando(capsys):
    set_state(car=assemble.TRUCK, engine=assemble.GM,
              brake=assemble.MANDO, steering=assemble.BOSCH_S)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "Truck에는 Mando제동장치 사용 불가" in output


def test_fail_reason_bosch_brake_non_bosch_steering(capsys):
    set_state(car=assemble.SEDAN, engine=assemble.GM,
              brake=assemble.BOSCH_B, steering=assemble.MOBIS)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in output


def test_broken_engine_is_not_checked_by_test_mode(capsys):
    # Test 모드는 고장난 엔진 케이스를 검사하지 않는다 — 나머지 조합이
    # 유효하면 PASS가 나와야 한다.
    set_state(car=assemble.SEDAN, engine=4,
              brake=assemble.MANDO, steering=assemble.MOBIS)
    assemble.test_produced_car()
    output = capsys.readouterr().out
    assert "PASS" in output


# --- is_valid_range() — 단계별 입력 허용 범위 ---

def test_car_type_step_rejects_zero():
    # 차종 단계는 뒤로가기가 없으므로 0은 허용되지 않는다.
    assert not assemble.is_valid_range(0, 0)


def test_car_type_step_accepts_1_to_3():
    for ans in (1, 2, 3):
        assert assemble.is_valid_range(0, ans)


def test_car_type_step_rejects_out_of_range():
    assert not assemble.is_valid_range(0, 4)


def test_engine_step_accepts_0_to_4():
    for ans in (0, 1, 2, 3, 4):
        assert assemble.is_valid_range(1, ans)


def test_engine_step_rejects_out_of_range():
    assert not assemble.is_valid_range(1, 5)


def test_brake_step_accepts_0_to_3():
    for ans in (0, 1, 2, 3):
        assert assemble.is_valid_range(2, ans)


def test_brake_step_rejects_out_of_range():
    assert not assemble.is_valid_range(2, 4)


def test_steering_step_accepts_0_to_2():
    for ans in (0, 1, 2):
        assert assemble.is_valid_range(3, ans)


def test_steering_step_rejects_out_of_range():
    assert not assemble.is_valid_range(3, 3)


def test_run_test_step_accepts_0_to_2():
    for ans in (0, 1, 2):
        assert assemble.is_valid_range(4, ans)


def test_run_test_step_rejects_out_of_range():
    assert not assemble.is_valid_range(4, 3)


# --- select_car_type/select_engine/select_brake/select_steering — 전역 상태 반영 ---

def test_select_car_type_sets_q0():
    set_state()
    assemble.select_car_type(assemble.TRUCK)
    assert assemble.q0 == assemble.TRUCK


def test_select_engine_sets_q1():
    set_state()
    assemble.select_engine(assemble.WIA)
    assert assemble.q1 == assemble.WIA


def test_select_brake_sets_q2():
    set_state()
    assemble.select_brake(assemble.BOSCH_B)
    assert assemble.q2 == assemble.BOSCH_B


def test_select_steering_sets_q3():
    set_state()
    assemble.select_steering(assemble.MOBIS)
    assert assemble.q3 == assemble.MOBIS
