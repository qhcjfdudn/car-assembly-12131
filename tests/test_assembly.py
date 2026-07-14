from assemblycar.domain.assembly import run
from assemblycar.domain.assembly import test as assembly_test
from assemblycar.domain.rules import Reason
from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering


def make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
              brake=Brake.MANDO, steering=Steering.MOBIS):
    return CarSpec(car_type=car_type, engine=engine, brake=brake, steering=steering)


# --- run() ---

def test_broken_engine_overrides_otherwise_valid_combo():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.BROKEN,
                      brake=Brake.MANDO, steering=Steering.MOBIS)
    result = run(spec)
    assert result.ok is False
    assert result.broken_engine is True
    assert result.spec is None


def test_invalid_combo_reports_failure():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.CONTINENTAL, steering=Steering.BOSCH)
    result = run(spec)
    assert result.ok is False
    assert result.broken_engine is False
    assert result.spec is None


def test_valid_combo_runs():
    spec = make_spec(car_type=CarType.SUV, engine=Engine.GM,
                      brake=Brake.MANDO, steering=Steering.BOSCH)
    result = run(spec)
    assert result.ok is True
    assert result.broken_engine is False
    assert result.spec == spec


# --- test() ---

def test_pass_on_valid_combo():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.MANDO, steering=Steering.MOBIS)
    result = assembly_test(spec)
    assert result.passed is True
    assert result.reasons == []


def test_fail_reason_sedan_continental():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.CONTINENTAL, steering=Steering.BOSCH)
    result = assembly_test(spec)
    assert result.passed is False
    assert result.reasons == [Reason.SEDAN_CONTINENTAL]


def test_fail_reason_suv_toyota():
    spec = make_spec(car_type=CarType.SUV, engine=Engine.TOYOTA,
                      brake=Brake.MANDO, steering=Steering.BOSCH)
    result = assembly_test(spec)
    assert result.reasons == [Reason.SUV_TOYOTA]


def test_fail_reason_truck_wia():
    spec = make_spec(car_type=CarType.TRUCK, engine=Engine.WIA,
                      brake=Brake.CONTINENTAL, steering=Steering.BOSCH)
    result = assembly_test(spec)
    assert result.reasons == [Reason.TRUCK_WIA]


def test_fail_reason_truck_mando():
    spec = make_spec(car_type=CarType.TRUCK, engine=Engine.GM,
                      brake=Brake.MANDO, steering=Steering.BOSCH)
    result = assembly_test(spec)
    assert result.reasons == [Reason.TRUCK_MANDO]


def test_fail_reason_bosch_brake_non_bosch_steering():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.BOSCH, steering=Steering.MOBIS)
    result = assembly_test(spec)
    assert result.reasons == [Reason.BOSCH_BRAKE_NON_BOSCH_STEERING]


def test_broken_engine_is_not_checked_by_test_mode():
    # Test 모드는 고장난 엔진 케이스를 검사하지 않는다 — 나머지 조합이
    # 유효하면 PASS(passed=True)가 나와야 한다.
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.BROKEN,
                      brake=Brake.MANDO, steering=Steering.MOBIS)
    result = assembly_test(spec)
    assert result.passed is True
    assert result.reasons == []
