from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from database.exceptions import FieldLengthException, RequiredFieldsEmptyException, UserError
from database.models.model import Model
from database.tests.test_utils import OVERLONG_STRING


class CreateModelTestCase(TestCase):

    def test_create_model_happy_case(self):
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        models = Model.objects
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_create_model_without_required_fields_throws_exception(self):
        with self.assertRaises(ValidationError):
            Model.objects.create(vendor=None, model_number=None, description=None).execute()

    def test_create_model_non_unique_throws_exception(self):
        message = "Model with this Vendor and Model number already exists."
        Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        with self.assertRaisesMessage(ValidationError, message):
            Model.objects.create(vendor="vendor", model_number="model_number", description="description")

    def test_overlong_vendor(self):
        try:
            Model.objects.create(vendor=OVERLONG_STRING,
                                 model_number="model_number", comment="comment", description="desc",
                                 calibration_frequency=timedelta(seconds=1)).execute()
            self.fail("overlong vendor allowed")
        except ValidationError:
            pass

    def test_overlong_model_number(self):
        try:
            Model.objects.create(vendor="vendor",
                                 model_number=OVERLONG_STRING, comment="comment", description="desc",
                                 calibration_frequency=timedelta(seconds=1)).execute()
            self.fail("overlong model_num allowed")
        except ValidationError:
            pass

    def test_overlong_comment(self):
        try:
            Model.objects.create(vendor="vendor",
                                 model_number="model_number", comment=OVERLONG_STRING, description="desc",
                                 calibration_frequency=timedelta(seconds=1)).execute()
            self.fail("overlong comment allowed")
        except ValidationError:
            pass

    def test_overlong_description(self):
        try:
            Model.objects.create(vendor="vendor",
                                 model_number="model_number", comment="comment", description=OVERLONG_STRING,
                                 calibration_frequency=timedelta(seconds=1)).execute()
            self.fail("overlong description allowed")
        except ValidationError:
            pass
