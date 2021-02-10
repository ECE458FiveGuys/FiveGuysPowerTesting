from enum import Enum

class SheetNames(Enum):
    CALIBRATION_EVENTS = "Calibration Events"
    INSTRUMENTS = "Instruments"
    MODELS = "Models"

class ModelTableColumnNames(Enum):
    VENDOR = "Vendor"
    MODEL_NUMBER = "Model Number"
    MODEL_DESCRIPTION = "Short Description"
    MODEL_COMMENT = "Comment"
    CALIBRATION_FREQUENCY = "Calibration Frequency"

class InstrumentTableColumnNames(Enum):
    SERIAL_NUMBER = "Serial Number"
    INSTRUMENT_COMMENT = "Comment"

class CalibrationEventColumnNames(Enum):
    CALIBRATION_USERNAME = "Calibration Username"
    CALIBRATION_DATE = "Calibration Date"
    CALIBRATION_COMMENT = "Calibration Comment"

