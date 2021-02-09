from django.db import IntegrityError
from django.test import TestCase
from database.models import EquipmentModel


class ModelTestCase(TestCase):

    # Integrity Tests

    def test_blank_optional_fields_no_exception(self):
        try:
            EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
            pass
        except Exception:
            self.fail("optional fields throwing error")

    def test_none_optional_fields_no_exception(self):
        try:
            EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description", comment=None,
                                          calibration_frequency=None)
            pass
        except Exception:
            self.fail("optional fields throwing error")


    def test_blank_model_number(self):
        try:
            EquipmentModel.objects.create(vendor="vendor", description="description", comment="comment", calibration_frequency=1)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_vendor(self):
        try:
            EquipmentModel.objects.create(model_number="model_number", description="description", comment="comment",
                                          calibration_frequency=1)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_description(self):
        try:
            EquipmentModel.objects.create(vendor="vendor", model_number="model_number", comment="comment",
                                          calibration_frequency=1)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    # Other tests

    def test_is_calibratable(self):
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                              comment="comment", calibration_frequency=1)
        assert model.is_calibratable()
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                              comment="comment")
        assert not model.is_calibratable()


