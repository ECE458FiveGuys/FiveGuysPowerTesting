from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.models import Model
from database.services.model_services.select_models import SelectModels
from database.tests.services.service_test_utils import create_non_admin_user


class SelectModelsTestCase(TestCase):

    def test_select_all_models(self):
        user = create_non_admin_user()
        Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                             comment="comment", calibration_frequency=1)
        try:
            SelectModels(user_id=user.id, password=user.password).execute().get(vendor="vendor")
            pass
        except ObjectDoesNotExist:
            self.fail("Added model could not be found")

    def test_select_model_by_id(self):
        user = create_non_admin_user()
        model, model2 = self.create_2_models()
        models = SelectModels(user_id=user.id, password=user.password, model_id=model.id).execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_select_model_by_vendor(self):
        model, model2 = self.create_2_models()
        user = create_non_admin_user()
        models = SelectModels(user_id=user.id, password=user.password, vendor=model.vendor).execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_select_model_by_model_number(self):
        model, model2 = self.create_2_models()
        user = create_non_admin_user()
        models = SelectModels(user_id=user.id, password=user.password, model_number=model.model_number).execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_select_model_by_description(self):
        model, model2 = self.create_2_models()
        user = create_non_admin_user()
        models = SelectModels(user_id=user.id, password=user.password, description=model.description).execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_select_model_by_calib_freq(self):
        model, model2 = self.create_2_models()
        user = create_non_admin_user()
        models = SelectModels(user_id=user.id, password=user.password, calibration_frequency=model.calibration_frequency).execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def create_2_models(self):
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                             comment="comment", calibration_frequency=1)
        model2 = Model.objects.create(vendor="vendor2", model_number="model_number2", description="description2",
                             comment="comment2", calibration_frequency=2)
        return model, model2
