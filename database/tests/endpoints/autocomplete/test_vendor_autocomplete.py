from datetime import timedelta

from rest_framework.test import force_authenticate

from database.models import EquipmentModel
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.views import VendorAutoCompleteViewSet


class VendorAutoCompleteTestCase(EndpointTestCase):
    def test_vendor_auto_complete_happy_case(self):
        EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=timedelta(seconds=1))
        EquipmentModel.objects.create(vendor="vendor2", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=timedelta(seconds=1))
        EquipmentModel.objects.create(vendor="vendor3", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=timedelta(seconds=1))
        request = self.factory.get(self.Endpoints.VENDORS.fill("vend"))
        force_authenticate(request, self.admin)
        view = VendorAutoCompleteViewSet.as_view()
        response = view(request)
        self.assertEquals(response.data, ['vendor', 'vendor2', 'vendor3'])
