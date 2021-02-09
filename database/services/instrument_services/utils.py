from database.exceptions import NULL_FIELD_ERROR_MESSAGE, RequiredFieldsEmptyException, CHARACTER_LENGTH_ERROR_MESSAGE, \
    FieldLengthException, UserError, InstrumentRequiredFieldsEmptyException, InstrumentFieldLengthException
from database.models import VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH, SERIAL_NUMBER_LENGTH


def handle_instrument_validation_error(error, vendor, model_number, serial_number):
    for error_message in error.messages:
        if NULL_FIELD_ERROR_MESSAGE in error_message:
            raise InstrumentRequiredFieldsEmptyException(vendor, model_number, serial_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(SERIAL_NUMBER_LENGTH) in error_message:
            raise InstrumentFieldLengthException("serial number", SERIAL_NUMBER_LENGTH, vendor, model_number, serial_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
            raise InstrumentFieldLengthException("commment", COMMENT_LENGTH, vendor, model_number, serial_number)
        else:
            raise UserError(error.messages)