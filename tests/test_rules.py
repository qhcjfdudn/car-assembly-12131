from assemblycar.domain.rules import Reason, incompatibilities, is_compatible
from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering


def make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
              brake=Brake.MANDO, steering=Steering.MOBIS):
    return CarSpec(car_type=car_type, engine=engine, brake=brake, steering=steering)


def test_sedan_with_continental_brake_is_invalid():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.CONTINENTAL, steering=Steering.BOSCH)
    assert not is_compatible(spec)
    assert incompatibilities(spec) == [Reason.SEDAN_CONTINENTAL]


def test_suv_with_toyota_engine_is_invalid():
    spec = make_spec(car_type=CarType.SUV, engine=Engine.TOYOTA,
                      brake=Brake.MANDO, steering=Steering.BOSCH)
    assert not is_compatible(spec)
    assert incompatibilities(spec) == [Reason.SUV_TOYOTA]


def test_truck_with_wia_engine_is_invalid():
    spec = make_spec(car_type=CarType.TRUCK, engine=Engine.WIA,
                      brake=Brake.CONTINENTAL, steering=Steering.BOSCH)
    assert not is_compatible(spec)
    assert incompatibilities(spec) == [Reason.TRUCK_WIA]


def test_truck_with_mando_brake_is_invalid():
    spec = make_spec(car_type=CarType.TRUCK, engine=Engine.GM,
                      brake=Brake.MANDO, steering=Steering.BOSCH)
    assert not is_compatible(spec)
    assert incompatibilities(spec) == [Reason.TRUCK_MANDO]


def test_bosch_brake_requires_bosch_steering():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.BOSCH, steering=Steering.MOBIS)
    assert not is_compatible(spec)
    assert incompatibilities(spec) == [Reason.BOSCH_BRAKE_NON_BOSCH_STEERING]


def test_bosch_brake_with_bosch_steering_is_valid():
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.BOSCH, steering=Steering.BOSCH)
    assert is_compatible(spec)
    assert incompatibilities(spec) == []


def test_all_compatible_combinations_are_valid():
    # 세단 + GM 엔진 + 만도 제동 장치 + 모비스 조향 장치는 어떤 규칙에도 걸리지 않는다.
    spec = make_spec(car_type=CarType.SEDAN, engine=Engine.GM,
                      brake=Brake.MANDO, steering=Steering.MOBIS)
    assert is_compatible(spec)
    assert incompatibilities(spec) == []
