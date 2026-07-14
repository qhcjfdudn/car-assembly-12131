import pytest

from assemblycar.domain.types import Brake, CarType, Engine, Steering


def test_car_type_values():
    assert CarType.SEDAN.value == 1
    assert CarType.SUV.value == 2
    assert CarType.TRUCK.value == 3


def test_engine_values_including_broken():
    assert Engine.GM.value == 1
    assert Engine.TOYOTA.value == 2
    assert Engine.WIA.value == 3
    assert Engine.BROKEN.value == 4


def test_brake_values():
    assert Brake.MANDO.value == 1
    assert Brake.CONTINENTAL.value == 2
    assert Brake.BOSCH.value == 3


def test_steering_values():
    assert Steering.BOSCH.value == 1
    assert Steering.MOBIS.value == 2


def test_brake_bosch_and_steering_bosch_are_distinct_members():
    # 제동장치와 조향장치의 "Bosch"는 이름은 같지만 각자의 Enum에
    # 네임스페이스로 분리되어 있어 서로 다른 멤버다.
    assert Brake.BOSCH is not Steering.BOSCH


def test_invalid_engine_value_raises():
    with pytest.raises(ValueError):
        Engine(99)
