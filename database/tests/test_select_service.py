
from django.test import TestCase

from database.models import Model
from database.services.model_services.select_models import SelectModels
from database.tests.services.service_test_utils import create_non_admin_user


class SelectServiceTestCase(TestCase):

    # sorting

    def test_select_all_models_sorting_happy_case(self):
        user = create_non_admin_user()
        model2 = Model.objects.create(vendor="vendor2", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        model3 = Model.objects.create(vendor="vendor3", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        first_model = SelectModels(user_id=user.id, password=user.password, order_by="vendor").execute().first()
        if first_model != model:
            self.fail("model order incorrect")

    # pagination

    def test_select_all_models_pagination_happy_case(self):
        user = create_non_admin_user()
        model2 = Model.objects.create(vendor="vendor2", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        model3 = Model.objects.create(vendor="vendor3", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        models = SelectModels(user_id=user.id, password=user.password, num_per_page=2, order_by="vendor").execute()
        if models.num_pages != 2:
            self.fail("incorrect number of pages {}".format(models.page_range))
        page = models.page(1)
        if len(page.object_list) != 2:
            self.fail("incorrect number of objects on page")
        if page.object_list[0] != model:
            self.fail("incorrect first model")
        if page.object_list[1] != model2:
            self.fail("incorrect second model")