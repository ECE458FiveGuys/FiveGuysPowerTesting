import csv
import tempfile

from rest_framework.test import force_authenticate

from database.exceptions import InvalidCalibrationFrequencyException
from database.models import EquipmentModel
from database.services.bulk_data_services.table_enums import ModelTableColumnNames
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.views import import_models


class ImportModelsTestCase(EndpointTestCase):

    def test_import_model_happy_case(self):
        response = self.make_import(fields=[e.value for e in ModelTableColumnNames],
                                    row=["vendor",
                                         "model_number",
                                         "description",
                                         "comment",
                                         "N/A"],
                                    endpoint=self.Endpoints.IMPORT_MODELS.value,
                                    function=import_models)
        if response.status_code != 200:
            self.fail("response failed with error: {}".format(response.content))
        model = EquipmentModel.objects.get(vendor="vendor")
        if "vendor" != model.vendor \
            or "model_number" != model.model_number \
            or "description" != model.description \
            or "comment" != model.comment\
            or model.calibration_frequency is not None:
            self.fail("created model not found")


    def test_import_model_non_int_calibration_frequency(self):
        response = self.make_import(fields=[e.value for e in ModelTableColumnNames],
                                    row=["vendor",
                                         "model_number",
                                         "description",
                                         "comment",
                                         "INVALID_CALIB_FREQ"],
                                    endpoint=self.Endpoints.IMPORT_MODELS.value,
                                    function=import_models)
        if response.content.decode('utf-8') != "\"Malformed Input: Calibration frequency not a positive integer for the model with vendor 'vendor' and model number 'model_number'\"":
            self.fail("invalid calibration frequency permitted on import")

    def test_import_model_non_positive_calibration_frequency(self):
        response = self.make_import(fields=[e.value for e in ModelTableColumnNames],
                                    row=["vendor",
                                         "model_number",
                                         "description",
                                         "comment",
                                         "-1"],
                                    endpoint=self.Endpoints.IMPORT_MODELS.value,
                                    function=import_models)
        if response.content.decode('utf-8') != "\"Malformed Input: Calibration frequency not a positive integer for the model with vendor 'vendor' and model number 'model_number'\"":
            self.fail("invalid calibration frequency permitted on import")

    def test_import_model_invalid_newline(self):
        response = self.make_import(fields=[e.value for e in ModelTableColumnNames],
                                    row=["ven\ndor",
                                         "model_number",
                                         "description",
                                         "comment",
                                         "2"],
                                    endpoint=self.Endpoints.IMPORT_MODELS.value,
                                    function=import_models)
        if response.content.decode('utf-8') != "\"Malformed Input: The {} field cannot contain multiple lines\"".format(ModelTableColumnNames.VENDOR.value):
            self.fail("invalid calibration frequency permitted on import")

