from enum import Enum, auto


class AutoName(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class ModelsEnum(AutoName):
    USER = auto()
    MODEL = auto()
    INSTRUMENT = auto()
    CALIBRATION_EVENT = auto()


class UserEnum(AutoName):
    PK = auto()
    USERNAME = auto()
    NAME = auto()
    EMAIL = auto()
    PASSWORD = auto()
    ADMIN = auto()
    IS_ACTIVE = auto()


class CategoryEnum(AutoName):
    PK = auto()
    NAME = auto()


class ModelEnum(AutoName):
    PK = auto()
    VENDOR = auto()
    MODEL_NUMBER = auto()
    DESCRIPTION = auto()
    COMMENT = auto()
    CALIBRATION_FREQUENCY = auto()
    MODEL_CATEGORIES = auto()
    CALIBRATION_MODE = auto()
    APPROVAL_REQUIRED = auto()
    CALIBRATOR_CATEGORIES = auto()


class InstrumentEnum(AutoName):
    PK = auto()
    MODEL = auto()
    SERIAL_NUMBER = auto()
    COMMENT = auto()
    ASSET_TAG_NUMBER = auto()
    INSTRUMENT_CATEGORIES = auto()


class ApprovalDataEnum(AutoName):
    PK = auto()
    CALIBRATION_EVENT = auto()
    APPROVED = auto()
    APPROVER = auto()
    DATE = auto()
    COMMENT = auto()


class CalibrationEventEnum(AutoName):
    PK = auto()
    INSTRUMENT = auto()
    DATE = auto()
    USER = auto()
    COMMENT = auto()
    ADDITIONAL_EVIDENCE = auto()
    LOAD_BANK_DATA = auto()
    GUIDED_HARDWARE_DATA = auto()
    CUSTOM_DATA = auto()
    APPROVAL_DATA = auto()
    CALIBRATED_WITH = auto()
