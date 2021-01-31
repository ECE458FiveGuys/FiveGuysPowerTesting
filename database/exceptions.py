class UserError(Exception):
    def __init__(self, message):
        self.message = message


class IllegalAccessException(UserError):
    def __init__(self):
        super().__init__("This function is admin-only")


class NoSuchEntryExistsException(UserError):
    def __init__(self):
        super().__init__("This entry no longer exists")


class RequiredFieldsEmptyException(UserError):
    def __init__(self, object_type, required_fields_list):
        message = ""
        for i in range(len(required_fields_list)):
            message = message+"{0} "
            if i < len(required_fields_list) - 1:
                message = message + "and "
            message = message.format(required_fields_list[i])
        message += "are required fields for {0}"
        message = message.format(object_type)
        super().__init__(format(message))


class FieldCombinationNotUniqueException(UserError):
    def __init__(self, object_type, fields_list):
        message = "The combination of "
        for i in range(len(fields_list)):
            message = message+"{0} "
            if i < len(fields_list) - 1:
                message = message + "and "
            message = message.format(fields_list[i])
        message += "must be unique for {0}"
        message = message.format(object_type)
        super().__init__(format(message))
