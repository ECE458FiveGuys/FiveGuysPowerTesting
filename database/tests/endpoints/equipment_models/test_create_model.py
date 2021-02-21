from rest_framework.test import force_authenticate

from database.models.model import Model
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.views import ModelViewSet, ModelCategoryViewSet


class CreateModelTestCase(EndpointTestCase):

    def test_create_model_simple_case(self):
        request = self.factory.post(self.Endpoints.MODELS, {'vendor': 'vendor',
                                                            'model_number': 'model_number',
                                                            'description': 'description',
                                                            })
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view({'post': 'create'})
        response = view(request)
        if response.status_code != 201:
            self.fail("model not created")
        model = Model.objects.get(vendor="vendor")
        if model.vendor != 'vendor' \
                or model.model_number != 'model_number' \
                or model.description != "description":
            self.fail("created model not found")

    def test_create_model_with_categories(self):
        model_category = {"name": "multimeter"}
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['multimeter']
        }
        r1 = self.factory.post(self.Endpoints.MODEL_CATEGORIES, model_category, format='json')  # add category to db
        force_authenticate(r1, self.admin)
        v1 = ModelCategoryViewSet.as_view({'post': 'create'})
        _ = v1(r1)
        r2 = self.factory.post(self.Endpoints.MODELS, model, format='json')
        force_authenticate(r2, self.admin)
        v2 = ModelViewSet.as_view({'post': 'create'})
        response = v2(r2)
        if response.status_code != 201:
            self.fail("model not created")

    def test_create_model_with_multiple_categories(self):
        mc1 = {"name": "multimeter"}
        mc2 = {"name": "ammeter"}
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['multimeter', 'ammeter']
        }
        r1 = self.factory.post(self.Endpoints.MODEL_CATEGORIES, mc1, format='json')  # add category to db
        force_authenticate(r1, self.admin)
        v1 = ModelCategoryViewSet.as_view({'post': 'create'})
        _ = v1(r1)
        r2 = self.factory.post(self.Endpoints.MODEL_CATEGORIES, mc2, format='json')  # add category to db
        force_authenticate(r2, self.admin)
        v2 = ModelCategoryViewSet.as_view({'post': 'create'})
        _ = v2(r2)
        r3 = self.factory.post(self.Endpoints.MODELS, model, format='json')
        force_authenticate(r3, self.admin)
        v3 = ModelViewSet.as_view({'post': 'create'})
        response = v3(r3)
        if response.status_code != 201:
            self.fail("model not created")

    def test_fail_create_model_with_categories(self):
        model = {
            "vendor": "Fluke",
            "model_number": "87V",
            "description": "Multimeter with temperature probes",
            "calibration_frequency": "60",
            "model_categories": ['multimeter']
        }
        r = self.factory.post(self.Endpoints.MODELS, model)
        force_authenticate(r, self.admin)
        v = ModelCategoryViewSet.as_view({'post': 'create'})
        response = v(r)
        if response.status_code == 201:
            self.fail("Model created with nonexistent categories")

    def test_create_model_required_(self):
        request = self.factory.post(self.Endpoints.MODELS, {})
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view({'post': 'create'})
        response = view(request)
        if response.data['vendor'][0] != "This field is required." \
                or response.data['model_number'][0] != "This field is required." \
                or response.data['description'][0] != "This field is required.":
            self.fail("model created without required fields")
