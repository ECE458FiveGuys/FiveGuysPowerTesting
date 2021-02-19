import requests

from controller.exception import UserError
from controller.requests.dtos import InstrumentDTO

from controller.requests.request_utils import RequestUtils, ModelFieldNames, InstrumentFieldNames


class InstrumentRequests:

    @staticmethod
    def get_instruments(host, token, page_num=None, vendor=None, model_number=None, description=None,
                        serial_number=None,
                        search=None, search_field=None, ordering=None):

        params = RequestUtils.build_get_instrument_params(page_num=page_num, vendor=vendor, model_number=model_number,
                                                          description=description, serial_number=serial_number,
                                                          search=search,
                                                          search_field=search_field, ordering=ordering)

        header = RequestUtils.build_token_header(token)
        instrument_data = requests.request(method="get", url='http://' + host + '/instruments/', headers=header,
                                           params=params)
        instruments_dicts = instrument_data.json()['results']
        return [InstrumentDTO.from_dict(instrument_dict) for instrument_dict in instruments_dicts]

    @staticmethod
    def retrieve_instrument(host, token, pk):
        header = RequestUtils.build_token_header(token)
        instrument_data = requests.request(method="get", url='http://' + host + '/instruments/', headers=header,
                                           params={"pk", pk})
        return InstrumentDTO.from_dict(instrument_data.json())

    @staticmethod
    def create_instrument(host, token, model_pk, serial_number, comment=None):
        header = RequestUtils.build_token_header(token)
        fields = RequestUtils.build_create_instrument_data(model_pk, serial_number, comment)
        instrument_data = requests.request(method="post", url='http://{}/instruments/'.format(host), headers=header,
                                           data=fields).json()
        try:
            return InstrumentDTO.from_dict(instrument_data)
        except KeyError:
            raise UserError(RequestUtils.parse_error_message(instrument_data))
