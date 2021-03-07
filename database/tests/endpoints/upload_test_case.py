from enum import Enum

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate
from django.test import TestCase

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

    def test_model_upload_csv(self):
        data = open('media/model-pre.csv', 'rb')

        data = SimpleUploadedFile(content=data.read(), name=data.name, content_type='multipart/form-data')

        view = ModelUploadView.as_view()

        content_type = 'multipart/form-data'
        headers = {
            'HTTP_CONTENT_TYPE': content_type,
            'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'models_bulk_import_test.csv'
        }

        request = self.factory.post(self.Endpoints.IMPORT_MODEL.value, {'file': data}, **headers)
        force_authenticate(request, self.admin)
        response = view(request)

        return response.status_code, response.data

    def test_instrument_upload_csv(self):
        data = open('media/model-pre.csv', 'rb')

        data = SimpleUploadedFile(content=data.read(), name=data.name, content_type='multipart/form-data')

        view = ModelUploadView.as_view()

        content_type = 'multipart/form-data'
        headers = {
            'HTTP_CONTENT_TYPE': content_type,
            'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'models_bulk_import_test.csv'
        }

        request = self.factory.post(self.Endpoints.IMPORT_MODEL.value, {'file': data}, **headers)
        force_authenticate(request, self.admin)
        _ = view(request)

        data = open('media/instrument-pre.csv', 'rb')

        data = SimpleUploadedFile(content=data.read(), name=data.name, content_type='multipart/form-data')

        view = InstrumentUploadView.as_view()

        content_type = 'multipart/form-data'
        headers = {
            'HTTP_CONTENT_TYPE': content_type,
            'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'instrument-pre.csv'
        }

        request = self.factory.post(self.Endpoints.IMPORT_INSTRUMENT.value, {'file': data}, **headers)
        force_authenticate(request, self.admin)
        response = view(request)

        return response.status_code, response.data
