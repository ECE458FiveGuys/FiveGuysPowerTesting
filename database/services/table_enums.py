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
    SPECIAL_CALIBRATION_SUPPORT = "Special-Calibration-Support"
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
    CALIBRATION_ATTACHMENT_TYPE = "Calibration-Attachment-Type"


class MinInstrumentTableColumnNames(Enum):
    VENDOR = ModelTableColumnNames.VENDOR.value
    MODEL_NUMBER = ModelTableColumnNames.MODEL_NUMBER.value
    SERIAL_NUMBER = "Serial-Number"
    ASSET_TAG_NUMBER = "Asset-Tag-Number"
    COMMENT = "Comment"
    CALIBRATION_DATE = "Calibration-Date"
    CALIBRATION_COMMENT = "Calibration-Comment"
    INSTRUMENT_CATEGORIES = "Instrument-Categories"
