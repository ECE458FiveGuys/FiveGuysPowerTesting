from enum import Enum


class ParamNames(Enum):
    SEARCH = "search"
    SEARCH_FIELD = "search_field"
    ORDERING = "ordering"
    ID = "pk"
    PAGE_NUMBER = "page"


class ModelFieldNames(Enum):
    PK = "pk"
    VENDOR = "vendor"
    MODEL_NUMBER = "model_number"
    DESCRIPTION = "description"
    COMMENT = "comment"
    CALIBRATION_FREQUENCY = "calibration_frequency"


class ModelFieldSearchNames(Enum):
    VENDOR = ModelFieldNames.VENDOR.value
    MODEL_NUMBER = ModelFieldNames.MODEL_NUMBER.value
    DESCRIPTION = ModelFieldNames.DESCRIPTION.value
    COMMENT = ModelFieldNames.COMMENT.value


class InstrumentFieldNames(Enum):
    MODEL = "model"
    SERIAL_NUMBER = "serial_number"
    COMMENT = "comment"


class InstrumentFieldSearchNames(Enum):
    SERIAL_NUMBER = InstrumentFieldNames.SERIAL_NUMBER.value


class RequestUtils:

    @staticmethod
    def build_token_header(token):
        return {'Authorization': token}

    @staticmethod
    def remove_empty_fields(dict):
        return {k: v for k, v in dict.items() if v is not None}

    @staticmethod
    def build_get_model_params(page_num=None, vendor=None, model_number=None, description=None,
                               search=None, search_field=None, ordering=None):
        return {ParamNames.PAGE_NUMBER.value: page_num,
                ParamNames.ORDERING.value: ordering,
                ParamNames.SEARCH.value: search,
                ParamNames.SEARCH_FIELD.value: search_field,
                ModelFieldSearchNames.VENDOR.value: vendor,
                ModelFieldSearchNames.MODEL_NUMBER.value: model_number,
                ModelFieldSearchNames.DESCRIPTION.value: description}

    @staticmethod
    def build_get_instrument_params(page_num=None, vendor=None, model_number=None, description=None, serial_number=None,
                                    search=None, search_field=None, ordering=None):
        params = RequestUtils.build_get_model_params(page_num=page_num, vendor=vendor, model_number=model_number,
                                                     description=description, search=search, search_field=search_field,
                                                     ordering=ordering)
        params[InstrumentFieldSearchNames.SERIAL_NUMBER.value] = serial_number
        return params

    @staticmethod
    def build_create_instrument_data(model_pk, serial_number, comment):
        fields = {InstrumentFieldNames.MODEL.value: model_pk,
                  InstrumentFieldNames.SERIAL_NUMBER.value: serial_number,
                  InstrumentFieldNames.COMMENT.value: comment}

        return RequestUtils.remove_empty_fields(fields)

    @staticmethod
    def parse_error_message(data):
        message = ""
        for error_type in data:
            if isinstance(data[error_type], list):
                for mess in data[error_type]:
                    message += "{}: {}\n\n".format(error_type, mess)
            else:
                message += "{}: {}\n\n".format(error_type, data)
        return message
