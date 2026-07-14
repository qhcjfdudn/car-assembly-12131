from enum import Enum


class CarType(Enum):
    SEDAN = 1
    SUV = 2
    TRUCK = 3


class Engine(Enum):
    GM = 1
    TOYOTA = 2
    WIA = 3
    BROKEN = 4


class Brake(Enum):
    MANDO = 1
    CONTINENTAL = 2
    BOSCH = 3


class Steering(Enum):
    BOSCH = 1
    MOBIS = 2
