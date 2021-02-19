import requests
from mockito import unstub, when, mock
from requests import Response
from rest_framework.test import force_authenticate

from controller.exception import UserError
from controller.requests.model_requests import ModelRequests
from controller.requests.request_utils import ParamNames, ModelFieldSearchNames, ModelFieldNames, RequestUtils
from controller.tests.requests.test_request import TOKEN, HOST, RequestTestCase
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.tests.test_utils import create_model_and_instrument
from database.views import EquipmentModelViewSet, EquipmentModel


class ModelRequestsTestCase(RequestTestCase):

    def test_get_models(self):
        model1 = EquipmentModel.objects.create(vendor="B", model_number="model_number", description="desc")
        model2 = EquipmentModel.objects.create(vendor="A", model_number="model_number", description="desc")
        model3 = EquipmentModel.objects.create(vendor="C", model_number="model_number", description="desc")
        model4 = EquipmentModel.objects.create(vendor="D", model_number="model_number", description="desc2")
        model5 = EquipmentModel.objects.create(vendor="E", model_number="model_number", description="des")
        model6 = EquipmentModel.objects.create(vendor="F", model_number="model_numb", description="desc")
        request = self.factory.get(
            self.Endpoints.MODELS.value + "?model_number=model_number&search=desc&search_field=description&ordering=vendor")
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="models/", params={
            ParamNames.PAGE_NUMBER.value: None,
            ParamNames.ORDERING.value: ModelFieldSearchNames.VENDOR.value,
            ParamNames.SEARCH.value: "desc",
            ParamNames.SEARCH_FIELD.value: ModelFieldSearchNames.DESCRIPTION.value,
            ModelFieldSearchNames.VENDOR.value: None,
            ModelFieldSearchNames.MODEL_NUMBER.value: "model_number",
            ModelFieldSearchNames.DESCRIPTION.value: None})
        models = ModelRequests.get_models(host=HOST, token=TOKEN,
                                          model_number="model_number",
                                          search="desc", search_field=ModelFieldSearchNames.DESCRIPTION.value,
                                          ordering=ModelFieldSearchNames.VENDOR.value)
        self.assertEquals(len(models), 4)
        self.model_equals_dto(dto=models[0], model=model2)
        self.model_equals_dto(dto=models[1], model=model1)
        self.model_equals_dto(dto=models[2], model=model3)
        self.model_equals_dto(dto=models[3], model=model4)
        unstub()

    def test_get_model(self):
        model, instrument = create_model_and_instrument()
        request = self.factory.get(self.Endpoints.MODELS.fill(model.pk.__str__()))
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=model.pk)
        response.render()
        self.mock_response(response, rel_url="models/", params={1, "pk"})
        ret_model = ModelRequests.retrieve_model(host=HOST, token=TOKEN, pk=model.pk)
        self.model_equals_dto(dto=ret_model, model=model)
        ret_instrument = ret_model.instruments[0]
        self.assertEquals(ret_instrument.serial_number, instrument.serial_number)
        self.assertEquals(ret_instrument.pk, instrument.pk)
        unstub()

    def test_create_model(self):
        fields = {ModelFieldNames.VENDOR.value: "vendor",
                  ModelFieldNames.MODEL_NUMBER.value: "model_number",
                  ModelFieldNames.DESCRIPTION.value: "desc"}
        request = self.factory.post(self.Endpoints.MODELS.value, data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="models/", data=fields, method='post')
        ret_model = ModelRequests.create_model(host=HOST, token=TOKEN,
                                               vendor="vendor",
                                               model_number="model_number",
                                               description="desc")
        self.assertEquals(ret_model.model_number, "model_number")
        self.assertEquals(ret_model.vendor, "vendor")
        self.assertEquals(ret_model.description, "desc")
        unstub()

    def test_create_invalid_model_throws_exception(self):
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="desc")
        fields = {ModelFieldNames.VENDOR.value: model.vendor,
                  ModelFieldNames.MODEL_NUMBER.value: model.model_number,
                  ModelFieldNames.DESCRIPTION.value: model.description}
        request = self.factory.post(self.Endpoints.MODELS.value, data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="models/", data=fields, method='post')
        try:
            ModelRequests.create_model(host=HOST, token=TOKEN,
                                       vendor="vendor",
                                       model_number="model_number",
                                       description="desc")
        except UserError as e:
            self.assertEquals(e.message,
                              "non_field_errors: The fields vendor, model_number must make a unique set.\n\n")
            unstub()
            pass

    def test_edit_existing_model_no_exception(self):
        model, instrument = create_model_and_instrument()
        fields = {ModelFieldNames.VENDOR.value: "vend",
                  ModelFieldNames.MODEL_NUMBER.value: "mod",
                  ModelFieldNames.DESCRIPTION.value: "desc"}
        request = self.factory.put(self.Endpoints.MODELS.value + "1/", data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'put': 'update'})
        response = view(request, pk=1)
        response.render()
        self.mock_response(response, rel_url="models/1/", data=fields, method='put')
        ret_model = ModelRequests.edit_model(host=HOST, token=TOKEN,
                                     model_pk=1,
                                     vendor="vend",
                                     model_number="mod",
                                     description="desc")
        self.assertEquals(ret_model.model_number, "mod")
        self.assertEquals(ret_model.vendor, "vend")
        self.assertEquals(ret_model.description, "desc")
        unstub()

    def test_edit_nonexisting_model_throws_exception(self):
        fields = {ModelFieldNames.VENDOR.value: "vend",
                  ModelFieldNames.MODEL_NUMBER.value: "mod",
                  ModelFieldNames.DESCRIPTION.value: "desc"}
        request = self.factory.put(self.Endpoints.MODELS.value + "1/", data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'put': 'update'})
        response = view(request, pk=1)
        response.render()
        self.mock_response(response, rel_url="models/1/", data=fields, method='put')
        try:
            ModelRequests.edit_model(host=HOST, token=TOKEN,
                                     model_pk=1,
                                     vendor="vend",
                                     model_number="mod",
                                     description="desc")
        except UserError as e:
            self.assertEquals(e.message,
                              "detail: {'detail': 'Not found.'}\n\n")
            unstub()
            pass
