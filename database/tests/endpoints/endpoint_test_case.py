import csv
import tempfile
from enum import Enum

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from database.views import import_models
from user_portal.models import PowerUser

TEST_ROOT = "http://127.0.0.1:8000/"

class EndpointTestCase(TestCase):
    class Endpoints(Enum):
        MODELS = TEST_ROOT + "models/"
        VENDORS = TEST_ROOT + "vendors?vendor={}"
        INSTRUMENT = TEST_ROOT + "models/"
        EXPORT_MODELS = TEST_ROOT + "export-models/"
        EXPORT_INSTRUMENTS = TEST_ROOT + "export-instruments/"
        EXPORT_ALL = TEST_ROOT + "export/"
        IMPORT_MODELS = TEST_ROOT + "import-models/"
        IMPORT_INSTRUMENTS = TEST_ROOT + "import-instruments/"


        def fill(self, params):
            return self.value.format(*params)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = PowerUser.objects.create_superuser('admin', 'admin', 'email', 'DukeECE458', is_active=True)

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