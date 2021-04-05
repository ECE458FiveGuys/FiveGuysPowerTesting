from enum import Enum, auto


class AutoName(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return "-".join([x.capitalize() for x in name.split('_')])


class ExportFileNames(Enum):
    INSTRUMENTS = "instruments.csv"
    MODELS = "models.csv"


class ModelTableColumnNames(AutoName):
    VENDOR = auto()
    MODEL_NUMBER = auto()
    SHORT_DESCRIPTION = auto()
    COMMENT = auto()
    MODEL_CATEGORIES = auto()
    SPECIAL_CALIBRATION_SUPPORT = auto()
    CALIBRATION_FREQUENCY = auto()
    CALIBRATION_REQUIRES_APPROVAL = auto()
    CALIBRATOR_CATEGORIES = auto()


class MaxInstrumentTableColumnNames(AutoName):
    VENDOR = auto()
    MODEL_NUMBER = auto()
    SERIAL_NUMBER = auto()
    ASSET_TAG_NUMBER = auto()
    COMMENT = auto()
    CALIBRATION_DATE = auto()
    CALIBRATION_COMMENT = auto()
    INSTRUMENT_CATEGORIES = auto()
    CALIBRATION_ATTACHMENT_TYPE = auto()


class MinInstrumentTableColumnNames(AutoName):
    VENDOR = auto()
    MODEL_NUMBER = auto()
    SERIAL_NUMBER = auto()
    ASSET_TAG_NUMBER = auto()
    COMMENT = auto()
    CALIBRATION_DATE = auto()
    CALIBRATION_COMMENT = auto()
    INSTRUMENT_CATEGORIES = auto()
