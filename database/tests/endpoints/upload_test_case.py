from enum import Enum

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate
from django.test import TestCase

from database.models.model import Model
from database.views import FileUploadView
from user_portal.models import PowerUser


class ImportTestCase(TestCase):
    class Endpoints(Enum):
        IMPORT_MODEL = "http://127.0.0.1:8000/api/new_import_models/"

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.admin = PowerUser.objects.create_superuser('admin', 'admin', 'email', 'DukeECE458', is_active=True)
        cls.model_filename = 'models_bulk_import_test.csv'

    def test_file_upload_csv(self):
        data = open('media/models_bulk_import_test.csv', 'rb')

        data = SimpleUploadedFile(content=data.read(), name=data.name, content_type='multipart/form-data')

        view = FileUploadView.as_view()

        content_type = 'multipart/form-data'
        headers = {
            'HTTP_CONTENT_TYPE': content_type,
            'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'models_bulk_import_test.csv'
        }

        request = self.factory.put(self.Endpoints.IMPORT_MODEL.value, {'file': data}, **headers)
        force_authenticate(request, self.admin)
        response = view(request)

        return response.status_code, response.data
