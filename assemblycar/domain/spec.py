from dataclasses import dataclass

from assemblycar.domain.types import Brake, CarType, Engine, Steering


@dataclass(frozen=True)
class CarSpec:
    car_type: CarType
    engine: Engine
    brake: Brake
    steering: Steering
