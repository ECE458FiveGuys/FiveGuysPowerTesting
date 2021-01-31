class UserError(Exception):
    def __init__(self, message):
        self.message = message


class IllegalAccessException(UserError):
    def __init__(self):
        super(IllegalAccessException, self, "This function is admin-only").__init__()


class RequiredFieldsEmptyException(UserError):
    def __init__(self, object_type, required_fields_list):
        message = ""
        for i in range(len(required_fields_list)):
            message = message+"%"
            if i < len(required_fields_list) - 1:
                message = message + ","
            message = message + " "
            message.format(required_fields_list[i])
        message += "are required fields for %s"
        message.format(object_type)
        super(RequiredFieldsEmptyException, self, format(message)).__init__()


class FieldCombinationNotUniqueException(UserError):
    def __init__(self, object_type, fields_list):
        message = "The combination of "
        for i in range(len(fields_list)):
            message = message+"% "
            if i < len(fields_list) - 1:
                message = message + "and "
            message.format(fields_list[i])
        message += " must be unique for %s"
        message.format(object_type)
        super(FieldCombinationNotUniqueException, self, format(message)).__init__()
