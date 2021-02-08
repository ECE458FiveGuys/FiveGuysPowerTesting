from database.exceptions import NULL_FIELD_ERROR_MESSAGE, RequiredFieldsEmptyException, CHARACTER_LENGTH_ERROR_MESSAGE, \
    FieldLengthException, UserError
from database.models import VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH


def handle_model_validation_error(error):
    for error_message in error.messages:
        if NULL_FIELD_ERROR_MESSAGE in error_message:
            raise RequiredFieldsEmptyException(object_type="model",
                                               required_fields_list=["vendor", "model_number", "description"])
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(VENDOR_LENGTH) in error_message:
            raise FieldLengthException("vendor", VENDOR_LENGTH)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(MODEL_NUMBER_LENGTH) in error_message:
            raise FieldLengthException("model number", MODEL_NUMBER_LENGTH)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(DESCRIPTION_LENGTH) in error_message:
            raise FieldLengthException("description", DESCRIPTION_LENGTH)
        elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
            raise FieldLengthException("commment", COMMENT_LENGTH)
        else:
            raise UserError(error.messages)