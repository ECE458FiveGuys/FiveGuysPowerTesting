from rest_framework.test import force_authenticate

from database.models.model import Model
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.views import ModelCategoryViewSet, ModelViewSet


class CreateModelTestCase(EndpointTestCase):
    def test_vendor_autocomplete(self):
        request = self.factory.get(self.Endpoints.VENDORS.value)
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view({'get': 'vendors'})
        response = view(request)
        self.assertEqual(set(response.data), {'Fluke', 'Volt'})

    def test_model_number_autocomplete(self):
        vendor = 'Fluke'
        request = self.factory.get(self.Endpoints.MODEL_NUMBERS.value.format(vendor))
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view({'get': 'model_numbers'})
        response = view(request)
        self.assertEqual(set(response.data), {'86V', '87M'})

    def test_create_model_simple_case(self):
        model = {
            'vendor': 'Dr. G',
            'model_number': '010123',
            'description': 'description',
        }
        response = self.make_request(self.Endpoints.MODELS, model, {'post': 'create'})
        if response.status_code != 201:
            self.fail("model not created")
        model = Model.objects.get(vendor='Dr. G', model_number='010123')
        if model.vendor != 'Dr. G' \
                or model.model_number != '010123' \
                or model.description != "description":
            self.fail("created model not found")

    def test_create_model_with_categories(self):
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['multimeter']
        }
        response = self.make_request(self.Endpoints.MODELS, model, {'post': 'create'})
        if response.status_code != 201:
            self.fail("model not created")

    def test_create_model_with_multiple_categories(self):
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['multimeter', 'voltmeter']
        }
        response = self.make_request(self.Endpoints.MODELS, model, {'post': 'create'})
        if response.status_code != 201:
            self.fail("model not created")

    def test_fail_create_model_with_categories(self):
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['ammeter']
        }
        response = self.make_request(self.Endpoints.MODELS, model, {'post': 'create'})
        self.assertEqual(response.status_code, 400)

    def test_incorrect_calibration_frequency(self):
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "-5"
        }
        response = self.make_request(self.Endpoints.MODELS, model, {'post': 'create'})
        self.assertEqual(response.status_code, 400)

    def test_create_model_required_(self):
        request = self.factory.post(self.Endpoints.MODELS, {})
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view({'post': 'create'})
        response = view(request)
        if response.data['vendor'][0] != "This field is required." \
                or response.data['model_number'][0] != "This field is required." \
                or response.data['description'][0] != "This field is required.":
            self.fail("model created without required fields")
