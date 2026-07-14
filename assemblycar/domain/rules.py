from enum import Enum, auto

from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Brake, CarType, Engine, Steering


class Reason(Enum):
    SEDAN_CONTINENTAL = auto()
    SUV_TOYOTA = auto()
    TRUCK_WIA = auto()
    TRUCK_MANDO = auto()
    BOSCH_BRAKE_NON_BOSCH_STEERING = auto()


def incompatibilities(spec: CarSpec) -> list[Reason]:
    reasons = []

    if spec.car_type is CarType.SEDAN and spec.brake is Brake.CONTINENTAL:
        reasons.append(Reason.SEDAN_CONTINENTAL)

    if spec.car_type is CarType.SUV and spec.engine is Engine.TOYOTA:
        reasons.append(Reason.SUV_TOYOTA)

    if spec.car_type is CarType.TRUCK and spec.engine is Engine.WIA:
        reasons.append(Reason.TRUCK_WIA)

    if spec.car_type is CarType.TRUCK and spec.brake is Brake.MANDO:
        reasons.append(Reason.TRUCK_MANDO)

    if spec.brake is Brake.BOSCH and spec.steering is not Steering.BOSCH:
        reasons.append(Reason.BOSCH_BRAKE_NON_BOSCH_STEERING)

    return reasons


def is_compatible(spec: CarSpec) -> bool:
    return not incompatibilities(spec)
