import codecs
import csv
import io
import tempfile

from rest_framework.test import force_authenticate

from database.services.bulk_data_services.table_enums import ModelTableColumnNames
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.tests.test_utils import create_model_and_instrument
from database.views import export_models


class ExportModelsTestCase(EndpointTestCase):

    def test_export_models_happy_case(self):
        model, instrument = create_model_and_instrument()
        request = self.factory.get(self.Endpoints.EXPORT_MODELS.value)
        force_authenticate(request, self.admin)
        response = export_models(request)
        if response.status_code != 200:
            print(response)
            self.fail("models could not be exported")
        self.assertEquals(
                    response.get('Content-Disposition'),
                    'attachment; filename=models.csv'
                )
        new_file = tempfile.TemporaryFile()
        new_file.write(response.content)
        new_file.seek(0)
        param_file = io.TextIOWrapper(new_file)
        reader = csv.DictReader(param_file)
        if set(reader.fieldnames) != \
                set([e.value for e in ModelTableColumnNames]):
            self.fail("field names not correct")
        list_of_dict = list(reader)
        row = list_of_dict[0]
        if row[ModelTableColumnNames.VENDOR.value] != model.vendor \
            or row[ModelTableColumnNames.MODEL_NUMBER.value] != model.model_number \
            or row[ModelTableColumnNames.MODEL_DESCRIPTION.value] != model.description \
            or row[ModelTableColumnNames.CALIBRATION_FREQUENCY.value] != "N/A":
            self.fail("created model not found")

