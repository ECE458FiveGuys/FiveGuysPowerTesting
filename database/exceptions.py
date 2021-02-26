CHARACTER_LENGTH_ERROR_MESSAGE = "Ensure this value has at most {} characters"
NULL_FIELD_ERROR_MESSAGE = "This field cannot be null."
INVALID_DATE_FIELD_ERROR_MESSAGE = "value has an invalid date format."

MODEL_QUALIFIER = "model with vendor \'{}\' and model number \'{}\'"
INSTRUMENT_QUALIFIER = "instrument with vendor \'{}\', model number \'{}\', and serial number \'{}\'"


class UserError(Exception):
    def __init__(self, message):
        self.message = message


class IllegalAccessException(UserError):
    def __init__(self):
        super().__init__("Error: This function is admin-only")


class InvalidDateException(UserError):
    def __init__(self, date):
        super().__init__("Error: Date {} must be of the form YYYY-MM-DD".format(date))


class EntryDoesNotExistException(UserError):
    def __init__(self, entry_type, entry_id):
        super().__init__("Error: The {0} with identifier {1} no longer exists".format(entry_type, entry_id))


class InactiveUserException(UserError):
    def __init__(self):
        super().__init__("The user owning these credentials has been deleted")


class AuthenticationFailedException(UserError):
    def __init__(self):
        super().__init__("Authentication Failed")


class FieldLengthException(UserError):
    def __init__(self, field, value, object_type, qualifications):
        super().__init__("The length of the {} field cannot be greater than {} in the {} with {}"
                         .format(field, value, object_type, qualifications))


class ModelFieldLengthException(FieldLengthException):
    def __init__(self, field, value, vendor, model_number):
        super().__init__(field, value, "model", "vendor \'{}\' and model number \'{}\'"
                         .format(vendor, model_number))


class InstrumentFieldLengthException(FieldLengthException):
    def __init__(self, field, value, vendor, model_number, serial_number):
        super().__init__(field, value, "model", "vendor \'{}\' and model number \'{}\' and serial number \'{}\'"
                         .format(vendor, model_number, serial_number))


class CalibrationEventFieldLengthException(FieldLengthException):
    def __init__(self, field, value, vendor, model_number, serial_number, date):
        super().__init__(field, value, "model",
                         "vendor \'{}\' and model number \'{}\' and serial number \'{}\' and date \'{}\'"
                         .format(vendor, model_number, serial_number, date))


class RequiredFieldsEmptyException(UserError):
    def __init__(self, object_type, required_fields_list, qualifications):
        message = "Error: "
        for i in range(len(required_fields_list)):
            message = message + "{0} "
            if i < len(required_fields_list) - 1:
                message = message + "and "
            message = message.format(required_fields_list[i])
        message += "are required fields for the {0} with {1}"
        message = message.format(object_type, qualifications)
        super().__init__(format(message))


class ModelRequiredFieldsEmptyException(RequiredFieldsEmptyException):
    def __init__(self, vendor, model_number):
        super().__init__(object_type="model",
                         required_fields_list=["vendor", "model_number", "description"],
                         qualifications="vendor \'{0}\' and model number \'{1}\'".format(vendor, model_number))


class InstrumentRequiredFieldsEmptyException(RequiredFieldsEmptyException):
    def __init__(self, vendor, model_number, serial_number):
        super().__init__(object_type="instrument",
                         required_fields_list=["model", "serial_number"],
                         qualifications="vendor \'{0}\' and model number \'{1}\' and serial_number \'{2}\'"
                         .format(vendor, model_number, serial_number))


class CalibrationEventRequiredFieldsEmptyException(RequiredFieldsEmptyException):
    def __init__(self, vendor=None, model_number=None, serial_number=None, date=None):
        super().__init__(object_type="calibration event",
                         required_fields_list=["instrument id", "user", "date"],
                         qualifications="vendor \'{}\' and model number \'{}\' and serial number \'{}\' and date \'{}\'"
                         .format(vendor, model_number, serial_number, date))


class FieldCombinationNotUniqueException(UserError):
    def __init__(self, object_type, fields_list, qualifications):
        message = "Error: The combination of "
        for i in range(len(fields_list)):
            message = message + "{0} "
            if i < len(fields_list) - 1:
                message = message + "and "
            message = message.format(fields_list[i])
        message += "must be unique for the {0} with {1}"
        message = message.format(object_type, qualifications)
        super().__init__(format(message))


class ModelFieldCombinationNotUniqueException(FieldCombinationNotUniqueException):
    def __init__(self, vendor, model_number):
        super().__init__(object_type="model", fields_list=["vendor", "model_number"],
                         qualifications="vendor \'{0}\' and model number \'{1}\'".format(vendor, model_number))


class InstrumentFieldCombinationNotUniqueException(FieldCombinationNotUniqueException):
    def __init__(self, vendor, model_number, serial_number):
        super().__init__(object_type="instrument", fields_list=["model", "serial_number"],
                         qualifications="vendor \'{0}\' and model number \'{1}\' and serial_number \'{2}\'"
                         .format(vendor, model_number, serial_number))


class BulkException(UserError):
    def __init__(self, errors):
        message = "Error: {} operations failed, reporting the following errors: \n"
        for error in errors:
            message += "'{}',\n".format(error.message)
        super().__init__()


class InvalidCalibrationFrequencyException(UserError):
    def __init__(self, vendor, model_number, serial_number=None):
        super().__init__("Malformed Input: Calibration frequency not a positive integer for the {}"
                         .format(specify_model_or_instrument(vendor, model_number, serial_number)))


class DoesNotExistException(UserError):
    def __init__(self, vendor, model_number, serial_number=None):
        super().__init__("Error: The {} does not exist"
                         .format(specify_model_or_instrument(vendor, model_number, serial_number)))


class UserDoesNotExistException(UserError):
    def __init__(self, user_name):
        super().__init__("Error: The user \'{}\' does not exist".format(user_name))


class IllegalCharacterException(UserError):
    def __init__(self, field_name):
        super().__init__("Malformed Input: The {} field cannot contain multiple lines".format(field_name))


class ImpossibleCalibrationError(UserError):
    def __init__(self, vendor, model_number, serial_number=None):
        super().__init__("Error: The {} has no calibration frequency but has a calibration date"
                         .format(specify_model_or_instrument(vendor, model_number, serial_number)))


def specify_model_or_instrument(vendor, model_number, serial_number=None):
    if serial_number is None:
        return specify_model(vendor, model_number)
    else:
        return specify_instrument(vendor, model_number, serial_number)


def specify_model(vendor, model_number):
    return MODEL_QUALIFIER.format(vendor, model_number)


def specify_instrument(vendor, model_number, serial_number):
    return INSTRUMENT_QUALIFIER.format(vendor, model_number, serial_number)
