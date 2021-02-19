import requests

from controller.exception import UserError
from controller.requests.dtos import ModelDTO

from controller.requests.request_utils import RequestUtils, ModelFieldSearchNames, ModelFieldNames


class ModelRequests:

    @staticmethod
    def get_models(host, token, page_num=None, vendor=None, model_number=None, description=None,
                   search=None, search_field=None, ordering=None):
        params = RequestUtils.build_get_model_params(page_num=page_num, vendor=vendor, model_number=model_number,
                                                     description=description, search=search, search_field=search_field,
                                                     ordering=ordering)

        header = RequestUtils.build_token_header(token)
        modeldata = requests.request(method="get", url='http://{}/models/'.format(host), headers=header, params=params)
        models_dicts = modeldata.json()['results']
        return [ModelDTO.from_dict(model_dict) for model_dict in models_dicts]

    @staticmethod
    def retrieve_model(host, token, pk):
        header = RequestUtils.build_token_header(token)
        modeldata = requests.request(method="get", url='http://{}/models/'.format(host), headers=header,
                                     params={"pk", pk})
        return ModelDTO.from_dict(modeldata.json())

    @staticmethod
    def create_model(host, token, vendor, model_number, description, comment=None, calibration_frequency=None):
        return ModelRequests.__update_model(token=token, method="post", url='http://{}/models/'.format(host),
                                            vendor=vendor, model_number=model_number, description=description,
                                            comment=comment, calibration_frequency=calibration_frequency)

    @staticmethod
    def edit_model(host, token, model_pk, vendor=None, model_number=None, description=None, comment=None,
                   calibration_frequency=None):
        return ModelRequests.__update_model(token=token, method="put", url='http://{}/models/{}/'.format(host, model_pk),
                                            vendor=vendor, model_number=model_number, description=description,
                                            comment=comment, calibration_frequency=calibration_frequency)

    @staticmethod
    def delete_model(host, token, model_pk):
        header = RequestUtils.build_token_header(token)
        model_data = requests.request(method="delete", url='http://{}/models/{}/'.format(host, model_pk), headers=header)
        try:
            return ModelDTO.from_dict(model_data)
        except KeyError:
            raise UserError(RequestUtils.parse_error_message(model_data))


    # private helpers

    @staticmethod
    def __update_model(token, method, url, vendor=None, model_number=None, description=None, comment=None,
                       calibration_frequency=None):
        header = RequestUtils.build_token_header(token)
        fields = {ModelFieldNames.VENDOR.value: vendor,
                  ModelFieldNames.MODEL_NUMBER.value: model_number,
                  ModelFieldNames.DESCRIPTION.value: description,
                  ModelFieldNames.COMMENT.value: comment,
                  ModelFieldNames.CALIBRATION_FREQUENCY.value: calibration_frequency}
        fields = {k: v for k, v in fields.items() if v is not None}
        model_data = requests.request(method=method, url=url, headers=header, data=fields).json()
        try:
            return ModelDTO.from_dict(model_data)
        except KeyError:
            raise UserError(RequestUtils.parse_error_message(model_data))
