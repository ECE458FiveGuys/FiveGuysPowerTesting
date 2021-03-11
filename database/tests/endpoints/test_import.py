from enum import Enum

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from database.views import InstrumentUploadView, ModelUploadView
from user_portal.models import PowerUser


class ImportTestCase(TestCase):
    class Endpoints(Enum):
        IMPORT_MODEL = "http://127.0.0.1:8000/api/import_models/"
        IMPORT_INSTRUMENT = "http://127.0.0.1:8000/api/import_instruments/"

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

    def test_model_upload(self):
        response = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.status_code, 200)

    def test_incorrect_headers(self):
        response = self.import_helper('model-incorrect-headers.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.data, ['Illegal column headers. Column headers are unique and should be Vendor, '
                                         'Model-Number, Short-Description, Comment, Model-Categories, '
                                         'Load-Bank-Support, Calibration-Frequency.'])

    def test_illegal_newline_character(self):
        response = self.import_helper('model-illegal-character.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.data, ['Illegal newline character found in row 3 of column Short-Description.'])

    def test_illegal_load_bank_value(self):
        response = self.import_helper('model-illegal-load-bank-value.csv', self.Endpoints.IMPORT_MODEL.value,
                                      ModelUploadView)
        self.assertEqual(response.data, ['Illegal value in row 3 of column Load-Bank-Support. Expected Y or empty '
                                         'string but got LOAD_BANK.'])

    def test_illegal_calibration_frequency(self):
        response = self.import_helper('model-illegal-calibration-frequency.csv', self.Endpoints.IMPORT_MODEL.value,
                                      ModelUploadView)
        self.assertEqual(response.data, ['Illegal value in row 2 of column Calibration-Frequency. '
                                         'Expected positive integer but got -5.'])

    def test_instrument_upload(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-pre.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.status_code, 200)

    def test_instrument_empty_rows(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-empty-rows.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.status_code, 200)

    def test_model_extra_column(self):
        response = self.import_helper('model-extra-column.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        self.assertEqual(response.data, ['Illegal column headers. Column headers are unique and should be Vendor, '
                                         'Model-Number, Short-Description, Comment, Model-Categories, '
                                         'Load-Bank-Support, Calibration-Frequency.'])

    def test_import_model_in_instrument_endpoint(self):
        response = self.import_helper('model-extra-column.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.data, ['Illegal column headers. Column headers are unique and should be Vendor, '
                                         'Model-Number, Serial-Number, Asset-Tag-Number, Comment, Calibration-Date, '
                                         'Calibration-Comment, Instrument-Categories.'])

    def test_instrument_incorrect_date_format(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-incorrect-date-format.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.data, ['Illegal value in row 2 of column Calibration-Date. Expected format '
                                         'MM/DD/YYYY but got 03-01/2021.'])

    def test_instrument_no_vendor(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-no-vendor.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.data, ["Illegal value in row 2. Model with vendor '' and model number 'LBC21' does "
                                         "not exist in the database."])

    def test_instrument_bad_asset_tag(self):
        _ = self.import_helper('model-pre.csv', self.Endpoints.IMPORT_MODEL.value, ModelUploadView)
        response = self.import_helper('instrument-bad-asset-tag.csv', self.Endpoints.IMPORT_INSTRUMENT.value,
                                      InstrumentUploadView)
        self.assertEqual(response.data, ['Illegal value in row 2 of column Asset-Tag-Number. Ensure this value is '
                                         'greater than or equal to 100000.'])
