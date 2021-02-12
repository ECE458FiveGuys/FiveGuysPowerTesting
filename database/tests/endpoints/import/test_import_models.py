import csv
import tempfile

from rest_framework.test import force_authenticate

from database.models import EquipmentModel
from database.services.bulk_data_services.table_enums import ModelTableColumnNames
from database.tests.test_utils import EndpointTestCase
from database.views import import_models


class ImportModelsTestCase(EndpointTestCase):

    def test_import_model_happy_case(self):
        tmpfile = tempfile.TemporaryFile("a+")
        # writer = csv.writer(tmpfile)
        # writer.writerow([e.value for e in ModelTableColumnNames])
        # writer.writerow(["vendor",
        #                  "model_number",
        #                  "description",
        #                  "comment",
        #                  "N/A"])
        # request = self.factory.post(self.Endpoints.IMPORT_MODELS.value)
        # tmpfile.seek(0)
        # request.FILES['file'] = tmpfile
        # force_authenticate(request, self.admin)
        # response = import_models(request)
        # response.render()
        # if response.status_code != 200:
        #     self.fail("response failed with error: {}".format(response.content))
        # print(response.render())
        # model = EquipmentModel.objects.get(vendor="vendor")
        # print(model)
        # if "vendor" != model.vendor \
        #     or "model_number" != model.model_number \
        #     or "description" != model.description \
        #     or "comment" != model.comment\
        #     or model.calibration_frequency is not None:
        #     self.fail("created model not found")