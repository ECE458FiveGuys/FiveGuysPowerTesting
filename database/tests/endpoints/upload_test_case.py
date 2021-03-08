from enum import Enum

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from database.views import InstrumentUploadView, ModelUploadView
from user_portal.models import PowerUser


class ImportTestCase(TestCase):
    class Endpoints(Enum):
        IMPORT_MODEL = "http://127.0.0.1:8000/api/new_import_models/"
        IMPORT_INSTRUMENT = "http://127.0.0.1:8000/api/new_import_instruments/"

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.admin = PowerUser.objects.create_superuser('admin', 'admin', 'email', 'DukeECE458', is_active=True)
        cls.model_filename = 'model-pre.csv'

    def import_helper(self, filename, endpoint, function):
        with open(f'database/tests/files/{filename}', 'r', newline='', encoding='utf-8-sig') as file:
            view = function.as_view()
            headers = {
                'HTTP_CONTENT_TYPE': 'multipart/form-data',
                'HTTP_CONTENT_DISPOSITION': f'attachment; filename={filename}'
            }
            request = self.factory.post(endpoint, {'file': file}, **headers)
        force_authenticate(request, self.admin)
        return view(request)

    def test_model_upload_csv(self):
        response = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.status_code, 200)

    def test_illegal_newline_character(self):
        response = self.import_helper('model-illegal-character.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.data, ['Illegal newline character found in row 3 of column Short-Description'])

    def test_instrument_upload_csv(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-pre.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)

        print(response.status_code)

        return response.status_code, response.data
