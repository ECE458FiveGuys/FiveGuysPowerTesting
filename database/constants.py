VENDOR_LENGTH = 30
MODEL_NUMBER_LENGTH = 40
SERIAL_NUMBER_LENGTH = 40
DESCRIPTION_LENGTH = 100
COMMENT_LENGTH = 2000
CALIBRATION_FREQUENCY_LENGTH = 10  # needs to be validated in manager, length not valid for integer field
CATEGORY_LENGTH = 40
INSTRUMENT_TEMPLATE = '(Model:{0.model}, Asset Tag Number:{0.asset_tag_number}, Serial Number:{0.serial_number}, ' \
                      'Comment:{0.comment})'
CALIBRATION_EVENT_TEMPLATE = '(Instrument:{0.instrument}, Date:{0.date}, User:{0.user}, Comment:{0.comment})'
MODEL_TEMPLATE = '(Vendor:{0.vendor}, Model Number:{0.model_number}, Description:{0.description}, Comment:{' \
                 '0.comment}, Calibration Frequency:{0.calibration_frequency}, Calibration Mode:{0.calibration_mode})'
