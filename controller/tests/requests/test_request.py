import requests
from mockito import mock, when
from requests import Response

from database.tests.endpoints.endpoint_test_case import EndpointTestCase

TOKEN = "Token token"
HOST = "127.0.0.1:8000"


class RequestTestCase(EndpointTestCase):

    def model_equals_dto(self, dto, model):
        self.assertEquals(dto.pk, model.pk)
        self.assertEquals(dto.model_number, model.model_number)
        self.assertEquals(dto.vendor, model.vendor)
        self.assertEquals(dto.comment, model.comment)
        self.assertEquals(dto.description, model.description)

    def instrument_equals_dto(self, dto, instrument):
        self.model_equals_dto(dto=dto.model, model=instrument.model)
        self.assertEquals(dto.serial_number, instrument.serial_number)

    def mock_response(self, response, rel_url, params=None, data=None, method="get"):
        header = {'Authorization': TOKEN}
        mock(response)
        fake_response = Response()
        fake_response._content = response.content
        if params is None and data is None:
            when(requests).request(method=method, url='http://' + HOST + '/' + rel_url, headers=header).thenReturn(fake_response)
        elif params is None:
            when(requests).request(method=method, url='http://' + HOST + '/' + rel_url, headers=header, data=data).thenReturn(fake_response)
        elif data is None:
            when(requests).request(method=method, url='http://' + HOST + '/' + rel_url, headers=header, params=params).thenReturn(fake_response)
        else:
            when(requests).request(method=method, url='http://' + HOST + '/' + rel_url, headers=header, data=data, params=params).thenReturn(fake_response)


