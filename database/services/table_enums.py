from enum import Enum


class ExportFileNames(Enum):
    INSTRUMENTS = "instruments.csv"
    MODELS = "models.csv"


class ModelTableColumnNames(Enum):
    VENDOR = "Vendor"
    MODEL_NUMBER = "Model-Number"
    DESCRIPTION = "Short-Description"
    COMMENT = "Comment"
    MODEL_CATEGORIES = "Model-Categories"
    LOAD_BANK_SUPPORT = "Load-Bank-Support"
    CALIBRATION_FREQUENCY = "Calibration-Frequency"


class MaxInstrumentTableColumnNames(Enum):
    VENDOR = ModelTableColumnNames.VENDOR.value
    MODEL_NUMBER = ModelTableColumnNames.MODEL_NUMBER.value
    SERIAL_NUMBER = "Serial-Number"
    ASSET_TAG_NUMBER = "Asset-Tag-Number"
    COMMENT = "Comment"
    CALIBRATION_DATE = "Calibration-Date"
    CALIBRATION_COMMENT = "Calibration-Comment"
    INSTRUMENT_CATEGORIES = "Instrument-Categories"
    CALIBRATION_FILE_ATTACHMENT = "Calibration-File-Attachment"
    CALIBRATION_LOAD_BANK_RESULTS_EXISTS = 'Calibration-Load-Bank-Results-Exists'


class MinInstrumentTableColumnNames(Enum):
    VENDOR = ModelTableColumnNames.VENDOR.value
    MODEL_NUMBER = ModelTableColumnNames.MODEL_NUMBER.value
    SERIAL_NUMBER = "Serial-Number"
    ASSET_TAG_NUMBER = "Asset-Tag-Number"
    COMMENT = "Comment"
    CALIBRATION_DATE = "Calibration-Date"
    CALIBRATION_COMMENT = "Calibration-Comment"
    INSTRUMENT_CATEGORIES = "Instrument-Categories"
