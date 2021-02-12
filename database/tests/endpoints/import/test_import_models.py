import csv
import tempfile

from database.models import EquipmentModel
from database.services.bulk_data_services.table_enums import ModelTableColumnNames
from database.tests.test_utils import EndpointTestCase


class ImportModelsTestCase(EndpointTestCase):

    def test_import_model_happy_case(self):
        tmpfile = tempfile.TemporaryFile()
        writer = csv.writer(tmpfile)
        writer.writerow([e.value for e in ModelTableColumnNames])
        writer.writerow(["vendor",
                         "model_number",
                         "description",
                         "comment",
                         "N/A"])
        request = self.factory.post(self.Endpoints.IMPORT_MODELS.value, tmpfile)
        model = EquipmentModel.objects.get(vendor="vendor")
        if "vendor" != model.vendor \
            or "model_number" != model.model_number \
            or "description" != model.description \
            or "comment" != model.comment\
            or model.calibration_frequency is not None:
            self.fail("created model not found")