import csv
import tempfile
from datetime import timedelta
from enum import Enum

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from database.models.model import Model
from database.models.model_category import ModelCategory
from database.views import ModelViewSet
from user_portal.models import PowerUser

TEST_ROOT = "http://127.0.0.1:8000/"


class EndpointTestCase(TestCase):
    class Endpoints(Enum):
        MODELS = TEST_ROOT + "models/"
        MODEL_CATEGORIES = TEST_ROOT + "model-categories/"
        VENDORS = MODELS + "vendors/"
        MODEL_NUMBERS = MODELS + "model_numbers/?vendor={}"
        INSTRUMENTS = TEST_ROOT + "instruments/"
        EXPORT_MODELS = TEST_ROOT + "export-models/"
        EXPORT_INSTRUMENTS = TEST_ROOT + "export-instruments/"
        EXPORT_ALL = TEST_ROOT + "export/"
        IMPORT_MODELS = TEST_ROOT + "import-models/"
        IMPORT_INSTRUMENTS = TEST_ROOT + "import-instruments/"

        def fill(self, params):
            return self.value.format(*params)

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.admin = PowerUser.objects.create_superuser('admin', 'admin', 'email', 'DukeECE458', is_active=True)
        c1 = ModelCategory.objects.create(name="voltmeter")
        c2 = ModelCategory.objects.create(name="multimeter")
        c3 = ModelCategory.objects.create(name='oscilloscope')
        m1 = Model.objects.create(vendor="Fluke",
                                  model_number="86V",
                                  description="High Impedance Voltmeter",
                                  calibration_frequency=timedelta(days=90))
        m2 = Model.objects.create(vendor="Fluke",
                                  model_number="87M",
                                  description="Multimeter with temperature probes",
                                  calibration_frequency=timedelta(days=60))
        m3 = Model.objects.create(vendor="Volt",
                                  model_number="901C",
                                  description="Portable oscilloscope",
                                  calibration_frequency=timedelta(days=30))
        m1.model_categories.set([c1])
        m2.model_categories.set([c1, c2])
        m3.model_categories.set([c3])
        m1.save()
        m2.save()
        m3.save()

    def make_request(self, endpoint, data, action):
        request = self.factory.post(endpoint, data)
        force_authenticate(request, self.admin)
        view = ModelViewSet.as_view(action)
        return view(request)

    def make_import(self, endpoint, function, fields, row):
        tmpfile = tempfile.TemporaryFile("a+")
        writer = csv.writer(tmpfile)
        writer.writerow(fields)
        writer.writerow(row)
        tmpfile.seek(0)
        request = self.factory.post(endpoint, {"file": tmpfile})
        force_authenticate(request, self.admin)
        response = function(request)
        response.render()
        return response

    def none_of_model_exist(self, model):
        return model.objects.all().count() == 0
