"""
assemble.py의 핵심 도메인 로직에 대한 단위 테스트.

현재 assemble.py는 모듈 레벨 전역 상태(q0~q4)를 사용하므로, 각 테스트는
전역 상태를 직접 설정한 뒤 대상 함수를 호출하는 방식으로 작성한다.

테스트 클래스는 추후 리팩터링(상태를 객체로 분리)을 염두에 두고
도메인 개념 단위로 나누어 두었다 — 리팩터링 후에도 클래스 단위 매핑이
유지되도록(예: ValidationTests -> Validator, RunTests -> Runner) 구성한다.
"""
import contextlib
import io
import unittest

import assemble


def capture_stdout(func, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


def set_state(car=0, engine=0, brake=0, steering=0):
    assemble.q0 = car
    assemble.q1 = engine
    assemble.q2 = brake
    assemble.q3 = steering


class ValidationRuleTests(unittest.TestCase):
    """is_valid_check()가 검사하는 비호환 조합 규칙."""

    def test_sedan_with_continental_brake_is_invalid(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
        self.assertFalse(assemble.is_valid_check())

    def test_suv_with_toyota_engine_is_invalid(self):
        set_state(car=assemble.SUV, engine=assemble.TOYOTA,
                   brake=assemble.MANDO, steering=assemble.BOSCH_S)
        self.assertFalse(assemble.is_valid_check())

    def test_truck_with_wia_engine_is_invalid(self):
        set_state(car=assemble.TRUCK, engine=assemble.WIA,
                   brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
        self.assertFalse(assemble.is_valid_check())

    def test_truck_with_mando_brake_is_invalid(self):
        set_state(car=assemble.TRUCK, engine=assemble.GM,
                   brake=assemble.MANDO, steering=assemble.BOSCH_S)
        self.assertFalse(assemble.is_valid_check())

    def test_bosch_brake_requires_bosch_steering(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.BOSCH_B, steering=assemble.MOBIS)
        self.assertFalse(assemble.is_valid_check())

    def test_bosch_brake_with_bosch_steering_is_valid(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.BOSCH_B, steering=assemble.BOSCH_S)
        self.assertTrue(assemble.is_valid_check())

    def test_all_compatible_combinations_are_valid(self):
        # 세단 + GM 엔진 + 만도 제동 장치 + 모비스 조향 장치는 어떤 규칙에도 걸리지 않는다.
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.MANDO, steering=assemble.MOBIS)
        self.assertTrue(assemble.is_valid_check())


class RunProducedCarTests(unittest.TestCase):
    """run_produced_car()의 RUN 동작."""

    def test_broken_engine_overrides_otherwise_valid_combo(self):
        set_state(car=assemble.SEDAN, engine=4,
                   brake=assemble.MANDO, steering=assemble.MOBIS)
        output = capture_stdout(assemble.run_produced_car)
        self.assertIn("엔진이 고장나있습니다.", output)
        self.assertIn("자동차가 움직이지 않습니다.", output)

    def test_invalid_combo_reports_failure(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.run_produced_car)
        self.assertIn("자동차가 동작되지 않습니다", output)

    def test_valid_combo_prints_spec_and_runs(self):
        set_state(car=assemble.SUV, engine=assemble.GM,
                   brake=assemble.MANDO, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.run_produced_car)
        self.assertIn("Car Type : SUV", output)
        self.assertIn("Engine   : GM", output)
        self.assertIn("Brake    : Mando", output)
        self.assertIn("Steering : Bosch", output)
        self.assertIn("자동차가 동작됩니다.", output)


class TestProducedCarTests(unittest.TestCase):
    """test_produced_car()의 Test 동작 — PASS/FAIL 사유."""

    def test_pass_on_valid_combo(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.MANDO, steering=assemble.MOBIS)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("PASS", output)

    def test_fail_reason_sedan_continental(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("FAIL", output)
        self.assertIn("Sedan에는 Continental제동장치 사용 불가", output)

    def test_fail_reason_suv_toyota(self):
        set_state(car=assemble.SUV, engine=assemble.TOYOTA,
                   brake=assemble.MANDO, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("SUV에는 TOYOTA엔진 사용 불가", output)

    def test_fail_reason_truck_wia(self):
        set_state(car=assemble.TRUCK, engine=assemble.WIA,
                   brake=assemble.CONTINENTAL, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("Truck에는 WIA엔진 사용 불가", output)

    def test_fail_reason_truck_mando(self):
        set_state(car=assemble.TRUCK, engine=assemble.GM,
                   brake=assemble.MANDO, steering=assemble.BOSCH_S)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("Truck에는 Mando제동장치 사용 불가", output)

    def test_fail_reason_bosch_brake_non_bosch_steering(self):
        set_state(car=assemble.SEDAN, engine=assemble.GM,
                   brake=assemble.BOSCH_B, steering=assemble.MOBIS)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("Bosch제동장치에는 Bosch조향장치 이외 사용 불가", output)

    def test_broken_engine_is_not_checked_by_test_mode(self):
        # Test 모드는 고장난 엔진 케이스를 검사하지 않는다 — 나머지 조합이
        # 유효하면 PASS가 나와야 한다.
        set_state(car=assemble.SEDAN, engine=4,
                   brake=assemble.MANDO, steering=assemble.MOBIS)
        output = capture_stdout(assemble.test_produced_car)
        self.assertIn("PASS", output)


class InputRangeValidationTests(unittest.TestCase):
    """is_valid_range() — 단계별 입력 허용 범위."""

    def test_car_type_step_rejects_zero(self):
        # 차종 단계는 뒤로가기가 없으므로 0은 허용되지 않는다.
        self.assertFalse(assemble.is_valid_range(0, 0))

    def test_car_type_step_accepts_1_to_3(self):
        for ans in (1, 2, 3):
            self.assertTrue(assemble.is_valid_range(0, ans))

    def test_car_type_step_rejects_out_of_range(self):
        self.assertFalse(assemble.is_valid_range(0, 4))

    def test_engine_step_accepts_0_to_4(self):
        for ans in (0, 1, 2, 3, 4):
            self.assertTrue(assemble.is_valid_range(1, ans))

    def test_engine_step_rejects_out_of_range(self):
        self.assertFalse(assemble.is_valid_range(1, 5))

    def test_brake_step_accepts_0_to_3(self):
        for ans in (0, 1, 2, 3):
            self.assertTrue(assemble.is_valid_range(2, ans))

    def test_brake_step_rejects_out_of_range(self):
        self.assertFalse(assemble.is_valid_range(2, 4))

    def test_steering_step_accepts_0_to_2(self):
        for ans in (0, 1, 2):
            self.assertTrue(assemble.is_valid_range(3, ans))

    def test_steering_step_rejects_out_of_range(self):
        self.assertFalse(assemble.is_valid_range(3, 3))

    def test_run_test_step_accepts_0_to_2(self):
        for ans in (0, 1, 2):
            self.assertTrue(assemble.is_valid_range(4, ans))

    def test_run_test_step_rejects_out_of_range(self):
        self.assertFalse(assemble.is_valid_range(4, 3))


class SelectionStateTests(unittest.TestCase):
    """select_car_type/select_engine/select_brake/select_steering — 전역 상태 반영."""

    def test_select_car_type_sets_q0(self):
        set_state()
        assemble.select_car_type(assemble.TRUCK)
        self.assertEqual(assemble.q0, assemble.TRUCK)

    def test_select_engine_sets_q1(self):
        set_state()
        assemble.select_engine(assemble.WIA)
        self.assertEqual(assemble.q1, assemble.WIA)

    def test_select_brake_sets_q2(self):
        set_state()
        assemble.select_brake(assemble.BOSCH_B)
        self.assertEqual(assemble.q2, assemble.BOSCH_B)

    def test_select_steering_sets_q3(self):
        set_state()
        assemble.select_steering(assemble.MOBIS)
        self.assertEqual(assemble.q3, assemble.MOBIS)


if __name__ == "__main__":
    unittest.main()
