from assemblycar.domain.rules import Reason
from assemblycar.domain.types import Brake, CarType, Engine, Steering

CAR_TYPE_TEXT = {CarType.SEDAN: "Sedan", CarType.SUV: "SUV", CarType.TRUCK: "Truck"}
ENGINE_TEXT = {Engine.GM: "GM", Engine.TOYOTA: "TOYOTA", Engine.WIA: "WIA"}
BRAKE_TEXT = {Brake.MANDO: "Mando", Brake.CONTINENTAL: "Continental", Brake.BOSCH: "Bosch"}
STEERING_TEXT = {Steering.BOSCH: "Bosch", Steering.MOBIS: "Mobis"}

# 선택 직후 안내 문구("OO을 선택하셨습니다")에 쓰이는 표기 — 위의 RUN 결과 출력용
# 표기와 대소문자/문구가 달라(예: 제동장치는 대문자, 고장난 엔진은 "고장난") 별도로 둔다.
ENGINE_SELECT_TEXT = {**ENGINE_TEXT, Engine.BROKEN: "고장난"}
BRAKE_SELECT_TEXT = {k: v.upper() for k, v in BRAKE_TEXT.items()}
STEERING_SELECT_TEXT = {k: v.upper() for k, v in STEERING_TEXT.items()}

REASON_TEXT = {
    Reason.SEDAN_CONTINENTAL: "Sedan에는 Continental제동장치 사용 불가",
    Reason.SUV_TOYOTA: "SUV에는 TOYOTA엔진 사용 불가",
    Reason.TRUCK_WIA: "Truck에는 WIA엔진 사용 불가",
    Reason.TRUCK_MANDO: "Truck에는 Mando제동장치 사용 불가",
    Reason.BOSCH_BRAKE_NON_BOSCH_STEERING: "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
}
