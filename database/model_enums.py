from enum import Enum


class ModelsEnum(Enum):
    USER = "user"
    MODEL = "model"
    INSTRUMENT = "instrument"
    CALIBRATION_EVENT = "calibration event"


class UserEnum(Enum):
    PK = "pk"
    USERNAME = "username"
    NAME = "name"
    EMAIL = "email"
    PASSWORD = "password"
    ADMIN = "admin"
    ACTIVE = "active"


class CategoryEnum(Enum):
    PK = "pk"
    NAME = "name"


class ModelEnum(Enum):
    PK = "pk"
    VENDOR = "vendor"
    MODEL_NUMBER = "model_number"
    DESCRIPTION = "description"
    COMMENT = "comment"
    CALIBRATION_FREQUENCY = "calibration_frequency"
    MODEL_CATEGORIES = "model_categories"


class InstrumentEnum(Enum):
    PK = "pk"
    MODEL = "model"
    SERIAL_NUMBER = "serial_number"
    COMMENT = "comment"


class CalibrationEventEnum(Enum):
    PK = 'pk'
    INSTRUMENT = "instrument"
    DATE = "date"
    USER = "user"
    COMMENT = "comment"
