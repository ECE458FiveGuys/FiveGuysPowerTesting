from database.exceptions import NULL_FIELD_ERROR_MESSAGE, RequiredFieldsEmptyException, CHARACTER_LENGTH_ERROR_MESSAGE, \
    FieldLengthException, UserError, INVALID_DATE_FIELD_ERROR_MESSAGE, InvalidDateException, \
    CalibrationEventRequiredFieldsEmptyException, CalibrationEventFieldLengthException
from database.models import VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH, SERIAL_NUMBER_LENGTH


def handle_calib_event_validation_error(error, vendor=None, model_number=None, serial_number=None, date=None):
    for error_message in error.messages:
        if NULL_FIELD_ERROR_MESSAGE in error_message:
            raise CalibrationEventRequiredFieldsEmptyException(vendor=vendor,
                                                               model_number=model_number,
                                                               serial_number=serial_number,
                                                               date=date)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
            raise CalibrationEventFieldLengthException("commment", COMMENT_LENGTH,
                                                       vendor=vendor,
                                                       model_number=model_number,
                                                       serial_number=serial_number,
                                                       date=date)
        elif INVALID_DATE_FIELD_ERROR_MESSAGE in error_message:
            raise InvalidDateException()
        else:
            raise UserError(error.messages)