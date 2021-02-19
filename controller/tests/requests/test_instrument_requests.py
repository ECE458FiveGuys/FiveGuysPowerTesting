from django.utils.timezone import localtime, now
from mockito import unstub
from rest_framework.test import force_authenticate

from controller.exception import UserError
from controller.requests.instrument_requests import InstrumentRequests
from controller.requests.model_requests import ModelRequests
from controller.requests.request_utils import ParamNames, ModelFieldSearchNames, InstrumentFieldSearchNames, \
    RequestUtils
from controller.tests.requests.test_request import RequestTestCase
from database.models import Instrument, CalibrationEvent
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.tests.test_utils import create_model_and_instrument, create_non_admin_user, create_model
from database.views import EquipmentModelViewSet, EquipmentModel, InstrumentViewSet

TOKEN = "Token token"
HOST = "127.0.0.1:8000"


class InstrumentRequestsTestCase(RequestTestCase):

    def test_get_models(self):
        model1 = EquipmentModel.objects.create(vendor="B", model_number="model_number", description="desc")
        model2 = EquipmentModel.objects.create(vendor="A", model_number="model_number", description="desc")
        model3 = EquipmentModel.objects.create(vendor="C", model_number="model_number", description="desc")
        model4 = EquipmentModel.objects.create(vendor="D", model_number="model_number", description="desc2")
        model5 = EquipmentModel.objects.create(vendor="E", model_number="model_number", description="des")
        model6 = EquipmentModel.objects.create(vendor="F", model_number="model_number", description="desc")
        inst1 = Instrument.objects.create(model=model1, serial_number="serial_number")
        inst2 = Instrument.objects.create(model=model2, serial_number="serial_number")
        inst3 = Instrument.objects.create(model=model3, serial_number="serial_number")
        inst4 = Instrument.objects.create(model=model4, serial_number="serial_number")
        inst5 = Instrument.objects.create(model=model5, serial_number="serial_number")
        inst6 = Instrument.objects.create(model=model6, serial_number="serial_numb")

        request = self.factory.get(
            self.Endpoints.INSTRUMENT.value + "?serial_number=serial_number&search=desc&search_field=description&ordering=vendor")
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="instruments/", params={
            ParamNames.PAGE_NUMBER.value: None,
            ParamNames.ORDERING.value: ModelFieldSearchNames.VENDOR.value,
            ParamNames.SEARCH.value: "desc",
            ParamNames.SEARCH_FIELD.value: ModelFieldSearchNames.DESCRIPTION.value,
            ModelFieldSearchNames.VENDOR.value: None,
            ModelFieldSearchNames.MODEL_NUMBER.value: None,
            InstrumentFieldSearchNames.SERIAL_NUMBER.value: "serial_number",
            ModelFieldSearchNames.DESCRIPTION.value: None})
        instruments = InstrumentRequests.get_instruments(host=HOST, token=TOKEN,
                                                         serial_number="serial_number",
                                                         search="desc",
                                                         search_field=ModelFieldSearchNames.DESCRIPTION.value,
                                                         ordering=ModelFieldSearchNames.VENDOR.value)
        self.assertEquals(len(instruments), 4)
        self.instrument_equals_dto(dto=instruments[0], instrument=inst2)
        self.instrument_equals_dto(dto=instruments[1], instrument=inst1)
        self.instrument_equals_dto(dto=instruments[2], instrument=inst3)
        self.instrument_equals_dto(dto=instruments[3], instrument=inst4)
        unstub()

    def test_get_instrument(self):
        model, instrument = create_model_and_instrument(1)
        user = create_non_admin_user()
        latest = localtime(now()).date()
        latest = localtime(now()).date().replace(year=latest.year - 1)
        calib = CalibrationEvent.objects.create(user=user, instrument=instrument, date=latest)
        request = self.factory.get(self.Endpoints.INSTRUMENT.fill(instrument.pk.__str__()))
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=model.pk)
        response.render()
        self.mock_response(response, rel_url="instruments/", params={1, "pk"})
        ret_inst = InstrumentRequests.retrieve_instrument(host=HOST, token=TOKEN, pk=instrument.pk)
        self.instrument_equals_dto(dto=ret_inst, instrument=instrument)
        ret_calib = ret_inst.calibration_history[0]
        self.assertEquals(ret_calib.pk, calib.pk)
        self.assertEquals(ret_calib.user.username, user.username)
        self.assertEquals(ret_calib.user_id, user.pk)
        unstub()

    def test_create_instrument(self):
        model = create_model()
        fields = RequestUtils.build_create_instrument_data(model_pk=model.pk, serial_number="ser", comment="com")
        request = self.factory.post(self.Endpoints.INSTRUMENT.value, data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="instruments/", data=fields, method='post')
        ret_inst = InstrumentRequests.create_instrument(host=HOST, token=TOKEN,
                                                        model_pk=model.pk, serial_number="ser", comment="com")
        self.assertEquals(ret_inst.model_id, model.pk)
        self.assertEquals(ret_inst.serial_number, "ser")
        self.assertEquals(ret_inst.comment, "com")
        unstub()

    def test_create_invalid_instrument_throws_exception(self):
        model, instrument = create_model_and_instrument()
        fields = RequestUtils.build_create_instrument_data(model_pk=model.pk, serial_number=instrument.serial_number,
                                                           comment=instrument.comment)
        request = self.factory.post(self.Endpoints.INSTRUMENT.value, data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.mock_response(response, rel_url="instruments/", data=fields, method='post')
        try:
            InstrumentRequests.create_instrument(host=HOST, token=TOKEN,
                                                 model_pk=model.pk, serial_number=instrument.serial_number,
                                                 comment=instrument.comment)

        except UserError as e:
            self.assertEquals(e.message,
                              "non_field_errors: The fields model, serial_number must make a unique set.\n\n")
            unstub()
            pass

    def test_edit_instrument(self):
        model, instrument = create_model_and_instrument()
        fields = RequestUtils.build_create_instrument_data(model_pk=model.pk, serial_number="ser", comment="com")
        request = self.factory.put(self.Endpoints.INSTRUMENTS.value + "{}/".format(instrument.pk), data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'put': 'update'})
        response = view(request, pk=instrument.pk)
        response.render()
        self.mock_response(response, rel_url="instruments/{}/".format(instrument.pk), data=fields, method='put')
        ret_inst = InstrumentRequests.edit_instrument(host=HOST, token=TOKEN,
                                                      instrument_pk=instrument.pk,
                                                      model_pk=model.pk, serial_number="ser", comment="com")
        self.assertEquals(ret_inst.model_id, model.pk)
        self.assertEquals(ret_inst.serial_number, "ser")
        # self.assertEquals(ret_inst.comment, "com")
        unstub()

    def test_edit_nonexistant_instrument_throws_exception(self):
        model = create_model()
        fields = RequestUtils.build_create_instrument_data(model_pk=model.pk, serial_number="ser", comment="com")
        request = self.factory.put(self.Endpoints.INSTRUMENTS.value + "1/", data=fields)
        request.headers = RequestUtils.build_token_header(TOKEN)
        force_authenticate(request, self.admin)
        view = InstrumentViewSet.as_view({'put': 'update'})
        response = view(request, pk=1)
        response.render()
        self.mock_response(response, rel_url="instruments/1/", data=fields, method='put')
        try:
            InstrumentRequests.edit_instrument(host=HOST, token=TOKEN,
                                                          instrument_pk=1,
                                                          model_pk=model.pk, serial_number="ser", comment="com")

        except UserError as e:
            self.assertEquals(e.message,
                              "detail: {'detail': 'Not found.'}\n\n")
            unstub()
            pass
