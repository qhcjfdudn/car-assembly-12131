import dataclasses

import pytest

from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering


def make_spec(**overrides):
    defaults = dict(
        car_type=CarType.SEDAN,
        engine=Engine.GM,
        brake=Brake.MANDO,
        steering=Steering.MOBIS,
    )
    defaults.update(overrides)
    return CarSpec(**defaults)


def test_car_spec_holds_all_four_parts():
    spec = make_spec(car_type=CarType.TRUCK, engine=Engine.WIA,
                      brake=Brake.BOSCH, steering=Steering.BOSCH)
    assert spec.car_type is CarType.TRUCK
    assert spec.engine is Engine.WIA
    assert spec.brake is Brake.BOSCH
    assert spec.steering is Steering.BOSCH


def test_car_spec_is_frozen():
    spec = make_spec()
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.car_type = CarType.SUV


def test_car_specs_with_equal_fields_are_equal():
    assert make_spec() == make_spec()
