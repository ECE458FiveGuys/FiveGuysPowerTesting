from dataclasses import dataclass
from datetime import date


class ModelDTO:
    pass


class InstrumentDTO:
    pass


class CalibrationEventDTO:
    pass

@dataclass
class UserDTO:
    pk: int
    username: str
    name: str

    @staticmethod
    def from_dict(dict):
        return UserDTO(pk=dict["pk"],
                       username=dict["username"],
                       name=dict["name"])


@dataclass
class CalibrationEventDTO:
    pk: int
    instrument: int
    user_id: int
    date: date
    user: UserDTO = None
    comment: str = None

    @staticmethod
    def from_dict(dict):
        user_obj = None
        try:
            user_obj = UserDTO.from_dict(dict["user"])
            user_id = user_obj.pk
        except (KeyError, TypeError):
            user_id = dict["user"]
        return CalibrationEventDTO(pk=dict["pk"],
                                   instrument=None if dict.get("instrument", None) is None else InstrumentDTO.from_dict(
                                dict.get("instrument", None)),
                                   user_id=user_id,
                                   user=user_obj,
                                   date=dict["date"],
                                   comment=dict["comment"])

@dataclass
class InstrumentDTO:
    pk: int
    model_id: int
    serial_number: str
    calibration_history: list[CalibrationEventDTO]
    model: ModelDTO
    comment: str = None
    most_recent_calibration_date: date = None
    calibration_expiration_date: date = None

    @staticmethod
    def from_dict(dict):
        model = None
        try:
            model = ModelDTO.from_dict(dict["model"])
            model_id = model.pk
        except (KeyError, TypeError):
            model_id = dict.get("model", None)
        return InstrumentDTO(pk=dict["pk"],
                             model=model,
                             model_id=model_id,
                             calibration_history=[CalibrationEventDTO.from_dict(calib_event_dict) for calib_event_dict in
                                     dict.get("calibration_history", [])],
                             serial_number=dict["serial_number"],
                             comment=dict.get("comment", None),
                             most_recent_calibration_date=dict.get("most_recent_calibration_date", None),
                             calibration_expiration_date=dict.get("calibration_expiration_date", None))


@dataclass
class ModelDTO:
    pk: int
    vendor: str
    model_number: str
    description: str
    instruments: list[InstrumentDTO]
    comment: str = None
    calibration_frequency: int = None
    calibration_mode: str = "default"

    @staticmethod
    def from_dict(dict):
        return ModelDTO(pk=dict["pk"],
                        vendor=dict["vendor"],
                        model_number=dict["model_number"],
                        description=dict["description"],
                        comment=dict.get("comment", None),
                        calibration_frequency=dict.get("calibration_frequency", None),
                        calibration_mode=dict.get("calibration_mode", None),
                        instruments=[InstrumentDTO.from_dict(instrument_dict) for instrument_dict in
                                     dict.get("instruments", [])])
