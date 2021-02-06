from database.exceptions import NULL_FIELD_ERROR_MESSAGE, RequiredFieldsEmptyException, CHARACTER_LENGTH_ERROR_MESSAGE, \
    FieldLengthException, UserError
from database.models import VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH, SERIAL_NUMBER_LENGTH


def handle_calib_event_validation_error(error):
    for error_message in error.messages:
        if NULL_FIELD_ERROR_MESSAGE in error_message:
            raise RequiredFieldsEmptyException(object_type="calibration event",
                                               required_fields_list=["instrument id", "user", "date"])
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
            raise FieldLengthException("commment", COMMENT_LENGTH)
        else:
            raise UserError(error.messages)