from database.exceptions import NULL_FIELD_ERROR_MESSAGE, RequiredFieldsEmptyException, CHARACTER_LENGTH_ERROR_MESSAGE, \
    FieldLengthException, UserError, ModelRequiredFieldsEmptyException, ModelFieldLengthException
from database.models import VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH


def handle_model_validation_error(error, vendor, model_number):
    for error_message in error.messages:
        if NULL_FIELD_ERROR_MESSAGE in error_message:
            raise ModelRequiredFieldsEmptyException(vendor=vendor, model_number=model_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(VENDOR_LENGTH) in error_message:
            raise ModelFieldLengthException("vendor", VENDOR_LENGTH, vendor, model_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(MODEL_NUMBER_LENGTH) in error_message:
            raise ModelFieldLengthException("model number", MODEL_NUMBER_LENGTH, vendor, model_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(DESCRIPTION_LENGTH) in error_message:
            raise ModelFieldLengthException("description", DESCRIPTION_LENGTH, vendor, model_number)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
            raise ModelFieldLengthException("commment", COMMENT_LENGTH, vendor, model_number)
        else:
            raise UserError(error.messages)